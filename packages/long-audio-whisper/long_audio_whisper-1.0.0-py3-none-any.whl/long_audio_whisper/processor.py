import os
from openai import AsyncOpenAI
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence
import tempfile
import logging
import asyncio
import json
import datetime
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Configure logging to see progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _format_timestamp(seconds: float, separator: str = ',') -> str:
    """Formats a timestamp in seconds into HH:MM:SS,ms or HH:MM:SS.ms format."""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{milliseconds:03d}"

def _to_srt(data: dict) -> str:
    """Converts a verbose_json transcription object to SRT format."""
    srt_content = []
    for i, segment in enumerate(data['segments']):
        start = _format_timestamp(segment['start'], separator=',')
        end = _format_timestamp(segment['end'], separator=',')
        text = segment['text'].strip()
        srt_content.append(f"{i + 1}\n{start} --> {end}\n{text}\n")
    return "\n".join(srt_content)

def _to_vtt(data: dict) -> str:
    """Converts a verbose_json transcription object to VTT format."""
    vtt_content = ["WEBVTT\n"]
    for segment in data['segments']:
        start = _format_timestamp(segment['start'], separator='.')
        end = _format_timestamp(segment['end'], separator='.')
        text = segment['text'].strip()
        vtt_content.append(f"{start} --> {end}\n{text}\n")
    return "\n".join(vtt_content)


class WhisperProcessor:
    """
    A class to process large audio files using the Whisper API by splitting them into chunks,
    transcribing them, and optionally correcting the transcription with an LLM.
    It supports timestamp reconstruction for formats like SRT and VTT even for large files.
    """
    def __init__(self, api_key: str, llm_model: str = "gpt-4o"):
        """
        Initializes the processor with an OpenAI API key and a selected LLM model.

        Args:
            api_key (str): Your OpenAI API key.
            llm_model (str): The LLM to use for post-processing (e.g., "gpt-4o", "gpt-3.5-turbo").
        """
        if not api_key:
            raise ValueError("An OpenAI API key is required.")
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.llm_model = llm_model
        logging.info(f"WhisperProcessor initialized with LLM: {self.llm_model}")

    def _split_audio_for_text(self, file_path: str, min_silence_len: int, silence_thresh: int) -> list:
        """
        Splits an audio file into smaller chunks based on silence.
        Used for text-based transcriptions where precise global timestamps are not required.
        """
        logging.info(f"Loading audio file: {file_path}")
        audio = AudioSegment.from_file(file_path)
        
        logging.info(f"Splitting audio into chunks based on silence (min_silence_len={min_silence_len}ms, silence_thresh={silence_thresh}dBFS)...")
        chunks = split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            keep_silence=300
        )
        logging.info(f"Split audio into {len(chunks)} chunks for text processing.")
        return chunks

    def _get_audio_chunks_with_timestamps(self, file_path: str, min_silence_len: int, silence_thresh: int) -> list:
        """
        Splits an audio file into chunks and returns each chunk with its start timestamp in the original audio.
        This is crucial for reconstructing accurate, timestamped transcriptions (e.g., SRT, VTT).
        """
        logging.info(f"Loading audio file for timestamped splitting: {file_path}")
        audio = AudioSegment.from_file(file_path)
        
        logging.info(f"Detecting non-silent parts to create chunks with timestamps...")
        silence_ranges = detect_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh
        )

        # Invert silence ranges to get non-silent (speech) ranges
        last_end = 0
        speech_ranges = []
        for start, end in silence_ranges:
            if start > last_end:
                speech_ranges.append((last_end, start))
            last_end = end
        if last_end < len(audio):
            speech_ranges.append((last_end, len(audio)))
        
        chunks_info = []
        padding = 300  # ms, padding to avoid cutting words at the edges of chunks
        for i, (start, end) in enumerate(speech_ranges):
            chunk_start = max(0, start - padding)
            chunk_end = min(len(audio), end + padding)
            chunk = audio[chunk_start:chunk_end]
            chunks_info.append({
                "chunk": chunk,
                "start_ms": chunk_start,
                "index": i
            })
            
        logging.info(f"Created {len(chunks_info)} chunks with timestamps.")
        return chunks_info

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    async def _transcribe_chunk_text(self, chunk: AudioSegment, chunk_index: int) -> str:
        """
        Transcribes a single audio chunk and returns the plain text. Retries on failure.
        """
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
            tmp_filename = tmpfile.name
            chunk.export(tmp_filename, format="mp3")
        
        logging.info(f"Transcribing chunk {chunk_index+1} for text...")
        try:
            with open(tmp_filename, "rb") as audio_file:
                transcription = await self.async_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="json"
                )
            return transcription.text
        finally:
            os.remove(tmpfile.name)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    async def _transcribe_chunk_verbose(self, chunk_info: dict) -> dict:
        """
        Transcribes a chunk and returns a structured (verbose JSON) response.
        This data is used for reconstructing timestamped transcriptions. Retries on failure.
        """
        chunk = chunk_info["chunk"]
        chunk_index = chunk_info["index"]
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
            tmp_filename = tmpfile.name
            chunk.export(tmp_filename, format="mp3")
            
        logging.info(f"Transcribing chunk {chunk_index + 1} for verbose output...")
        try:
            with open(tmp_filename, "rb") as audio_file:
                transcription = await self.async_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
            return {
                "start_ms": chunk_info["start_ms"],
                "data": transcription.model_dump()
            }
        except Exception as e:
            logging.error(f"Error transcribing chunk {chunk_index + 1}: {e}")
            return None  # Return None on failure to filter out later
        finally:
            os.remove(tmp_filename)

    def _reconstruct_transcription(self, chunk_results: list) -> dict:
        """
        Stitches together verbose transcription results from multiple chunks into a single,
        coherent transcription object with corrected global timestamps.
        """
        logging.info("Reconstructing full transcription from chunks...")
        full_text = []
        all_segments = []
        
        for result in sorted(chunk_results, key=lambda r: r['start_ms']):
            if result and result.get('data'):
                data = result['data']
                start_offset_s = result['start_ms'] / 1000.0
                
                full_text.append(data['text'])
                
                for segment in data.get('segments', []):
                    segment['start'] += start_offset_s
                    segment['end'] += start_offset_s
                    if 'words' in segment:
                        for word in segment['words']:
                            word['start'] += start_offset_s
                            word['end'] += start_offset_s
                    all_segments.append(segment)
        
        # Merge overlapping segments by sorting them. A more advanced merging strategy
        # could be implemented here if needed (e.g., merging text of overlapping segments).
        all_segments.sort(key=lambda s: s['start'])
        
        final_data = {
            "text": " ".join(full_text),
            "segments": all_segments,
            "language": chunk_results[0]['data']['language'] if chunk_results and chunk_results[0].get('data') else "unknown"
        }
        logging.info("Reconstruction complete.")
        return final_data

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def _post_process_transcription(self, full_text: str, system_prompt: str) -> str:
        """
        Corrects and formats the raw transcription text using an LLM. Retries on failure.
        """
        logging.info("Starting post-processing of transcription with LLM...")
        
        try:
            response = await self.async_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_text}
                ]
            )
            logging.info("Post-processing completed successfully.")
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"An error occurred during post-processing: {e}")
            return f"POST-PROCESSING FAILED: Raw text: {full_text}"

    async def process(self, audio_file_path: str, min_silence_len: int = 700, silence_thresh: int = -40, system_prompt: str = None, response_format: str = "text") -> str:
        """
        Processes an audio file by splitting it, transcribing chunks concurrently,
        and formatting the output according to the specified response format.

        This method acts as the main entry point and orchestrates the entire workflow.

        Args:
            audio_file_path (str): The path to the audio file.
            min_silence_len (int): The minimum length of silence (in ms) to be used for splitting the audio.
            silence_thresh (int): The silence threshold in dBFS. Audio below this level is considered silent.
            system_prompt (str, optional): A custom system prompt for the LLM post-processor.
                                           Only used for 'text' and 'json' formats. Defaults to a standard prompt.
            response_format (str): The desired output format ('json', 'text', 'srt', 'verbose_json', 'vtt').

        Returns:
            str: The final transcription in the requested format.
        """
        if system_prompt is None:
            system_prompt = (
                "You are a highly advanced text editor. Your task is to take a raw, "
                "combined transcription and transform it into a readable, well-formatted text. "
                "Correct grammatical errors, add appropriate punctuation (periods, commas, question marks), "
                "divide the text into paragraphs, and ensure correct capitalization. "
                "Preserve the original meaning and vocabulary of the speech. Return only the corrected text, "
                "without any additional comments."
            )

        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)

        # Path 1: Small files (<25MB) for timestamped formats can be processed directly without chunking.
        if file_size_mb <= 25 and response_format in ["srt", "vtt", "verbose_json"]:
            logging.info(f"File size is under 25MB, processing '{response_format}' directly.")
            with open(audio_file_path, "rb") as audio_file:
                transcription = await self.async_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format=response_format
                )
            if response_format == 'verbose_json':
                return transcription.model_dump_json(indent=2)
            return transcription

        # Path 2: Large files (>25MB) for timestamped formats require chunking and timestamp reconstruction.
        if response_format in ["srt", "vtt", "verbose_json"]:
            logging.info("Processing large file for timestamped format by chunking and stitching...")
            chunks_info = self._get_audio_chunks_with_timestamps(audio_file_path, min_silence_len, silence_thresh)
            if not chunks_info:
                logging.warning("No audio chunks found to transcribe.")
                return ""
                
            transcription_tasks = [self._transcribe_chunk_verbose(info) for info in chunks_info]
            chunk_results = await asyncio.gather(*transcription_tasks)
            
            # Filter out failed transcriptions before reconstruction
            successful_results = [r for r in chunk_results if r is not None]
            if not successful_results:
                logging.error("All transcription chunks failed.")
                return "ERROR: Transcription failed for all chunks."

            reconstructed_data = self._reconstruct_transcription(successful_results)
            
            if response_format == "verbose_json":
                return json.dumps(reconstructed_data, indent=2)
            elif response_format == "srt":
                return _to_srt(reconstructed_data)
            elif response_format == "vtt":
                return _to_vtt(reconstructed_data)

        # Path 3: Text or simple JSON formats (any size) use chunking and LLM post-processing.
        if response_format in ["json", "text"]:
            logging.info("Processing file for text-based format...")
            audio_chunks = self._split_audio_for_text(audio_file_path, min_silence_len, silence_thresh)
            if not audio_chunks:
                logging.warning("No audio chunks found to transcribe.")
                return ""

            transcription_tasks = [self._transcribe_chunk_text(chunk, i) for i, chunk in enumerate(audio_chunks)]
            transcription_results = await asyncio.gather(*transcription_tasks)
            
            full_raw_text = " ".join(filter(None, transcription_results))
            logging.info("Combined all transcriptions into one text.")
            
            final_transcription = await self._post_process_transcription(full_raw_text, system_prompt)
            
            if response_format == "json":
                return json.dumps({"text": final_transcription}, indent=2)
            return final_transcription
        
        # Fallback for any unknown or unhandled response format.
        raise ValueError(f"Unknown response_format: {response_format}")
