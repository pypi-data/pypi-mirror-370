# Long Audio Whisper

**A Python library to effortlessly transcribe long audio files using OpenAI's Whisper API.**

`long-audio-whisper` solves a key limitation of OpenAI's Whisper API: the 25MB file size limit. It enables you to transcribe audio files of any length by intelligently splitting them into smaller chunks based on silence. For text-based outputs (`text`, `json`), it enhances the final transcription using an LLM for superior punctuation and formatting. For subtitle formats (`srt`, `vtt`), it masterfully reconstructs precise, word-level timestamps, ensuring professional-grade synchronization even for multi-hour recordings.

It supports a wide range of output formats: `json`, `text`, `srt`, `verbose_json`, and `vtt`.

## Key Features

- **Transcribe Audio of Any Length**: Seamlessly process audio files far exceeding the 25MB API limit.
- **Accurate Timestamp Reconstruction**: Generate precise SRT, VTT, and `verbose_json` outputs for long audio files by intelligently chunking audio and stitching the results back together.
- **Multiple Output Formats**: Choose from a variety of formats:
    - `text`: Plain text, optionally enhanced by an LLM.
    - `json`: Simple JSON object with the transcription text.
    - `srt` / `vtt`: Subtitle files with accurate timing, even for large audio.
    - `verbose_json`: Detailed JSON with word-level timestamps and segment data.
- **LLM-Powered Enhancement**: For `text` and `json` outputs, use a model like GPT-4o to automatically correct punctuation, capitalization, and formatting.
- **Asynchronous & Efficient**: Built with `asyncio` for concurrent processing of audio chunks, maximizing speed and efficiency.
- **Command-Line Interface**: Comes with a ready-to-use example script that functions as a powerful CLI.

## Installation

You can install the library directly from the source code.

First, clone the repository:
```bash
git clone https://github.com/bokamix/long-audio-whisper.git
cd long-audio-whisper
```

Then, install the package in editable mode:
```bash
pip install -e .
```

## Usage

The library includes an example script that can be used as a command-line tool.

### Prerequisites

Before you begin, make sure you have your OpenAI API key. You can set it as an environment variable:
```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```
Alternatively, you can pass the key directly using the `--api-key` argument.

### Command-Line Example

To transcribe an audio file, navigate to the `examples` directory and run the `main.py` script.

```bash
cd examples
python main.py /path/to/your/audio.mp3 --format srt
```

**Arguments:**

- `audio_file`: (Required) The path to your audio file.
- `--format`: (Optional) The desired output format. Choose from `json`, `text`, `srt`, `verbose_json`, `vtt`. Defaults to `text`.
- `--api-key`: (Optional) Your OpenAI API key. Defaults to the `OPENAI_API_KEY` environment variable.
- `--prompt`: (Optional) A custom system prompt for the LLM post-processor (used for `text` and `json` formats).

### Library Usage

You can also import `WhisperProcessor` directly into your own Python scripts.

```python
import asyncio
from long_audio_whisper import WhisperProcessor

async def transcribe_audio():
    processor = WhisperProcessor(api_key="YOUR_OPENAI_API_KEY")
    
    transcription = await processor.process(
        audio_file_path="/path/to/your/audio.mp3",
        response_format="text" # or "json", "srt", "vtt", "verbose_json"
    )
    
    print(transcription)

if __name__ == "__main__":
    asyncio.run(transcribe_audio())
```

## How It Works

The library employs a sophisticated workflow tailored to the output format:

1.  **For `text` and `json` formats**:
    - The audio is split into chunks based on detected silence.
    - Each chunk is transcribed into plain text concurrently.
    - The resulting text snippets are combined.
    - An LLM (e.g., GPT-4o) post-processes the full text to improve formatting and punctuation.

2.  **For `srt`, `vtt`, and `verbose_json` formats**:
    - For files under 25MB, the transcription is done in a single API call to ensure maximum accuracy.
    - For files over 25MB, the audio is split into chunks, but this time, the **exact start time** of each chunk is recorded.
    - Each chunk is transcribed using the `verbose_json` format to get word-level timestamps.
    - The library then reconstructs the full transcription, carefully **adjusting all timestamps** based on the original start time of each chunk.
    - Finally, it formats the reconstructed data into the desired `srt`, `vtt`, or `verbose_json` output.

This dual-path approach ensures both the highest quality text output and the most accurate timestamp synchronization, regardless of file size.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.