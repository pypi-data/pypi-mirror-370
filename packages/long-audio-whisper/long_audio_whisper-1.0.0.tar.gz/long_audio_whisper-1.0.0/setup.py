# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()
#end
setup(
    name="long-audio-whisper",
    version="1.0.0",
    author="bokamix",
    author_email="wjaniak@jede.pl",
    description="A library to bypass OpenAI Whisper's 25MB limit by chunking long audio files, with LLM-powered text enhancement and precise timestamp reconstruction for SRT/VTT formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bokamix/long-audio-whisper",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "openai",
        "pydub",
        "tenacity",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    keywords='openai whisper transcription audio speech-to-text long-audio srt vtt',
)
