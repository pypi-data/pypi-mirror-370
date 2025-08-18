import os
from pathlib import Path
import math
from typing import List, Iterator

import openai
from pydub import AudioSegment

from important.shell.color import cprint

MAX_BYTES = 26000000  # 25MB limit for OpenAI API
MODEL_NAME = "whisper-1"


class Transcribe:
    """
    Transcribe a video file to string
    """

    def __init__(self, video_filepath: str, lang: str, verbose: bool = False):
        self.verbose = verbose
        self.lang = lang
        self.video_filepath = video_filepath
        self.mp4_to_mp3()
        self.audio_size = os.path.getsize(self.audio_filepath)
        self.num_chunks = math.ceil(self.audio_size / MAX_BYTES)

        if self.verbose > 0:
            cprint(f"Language: {self.lang}", color="blue")
            cprint(f"Max size:\t{MAX_BYTES}", color="blue")
            cprint(f"Audio size:\t{self.audio_size}", color="blue")
            cprint(f"Number of chunks:\t{self.num_chunks}", color="blue")

    def get_audio(self):
        return AudioSegment.from_file(self.video_filepath, format=Path(self.video_filepath).suffix[1:])

    @property
    def audio_filepath(self) -> str:
        """
        Returns the filepath of the audio file
        """
        return self.video_filepath.replace(Path(self.video_filepath).suffix, ".mp3")

    def mp4_to_mp3(self) -> None:
        """
        Extracts the audio from the video file and saves it as an mp3
        """
        self.get_audio().export(self.audio_filepath)

    def get_audio_chunk_paths(self) -> Iterator:
        if self.audio_size >= MAX_BYTES:
            audio = self.get_audio()
            chunk_duration_ms = math.ceil(audio.duration_seconds * 1000 / self.num_chunks)
            for i in range(self.num_chunks):
                start_ms = i * chunk_duration_ms
                end_ms = start_ms + chunk_duration_ms
                chunk = audio[start_ms:end_ms]
                chunk_filepath = "__".join([self.audio_filepath.split(".")[0], str(start_ms), str(end_ms)]) + ".mp3"
                chunk.export(chunk_filepath)
                yield chunk_filepath
        else:
            yield self.audio_filepath

    @staticmethod
    def audio_transcribe(chunk_filepath: str, language: str) -> str:
        """
        Transcribes an audio file according to the language
        """
        with open(chunk_filepath, "rb") as audio_file:
            transcript = openai.Audio.transcribe(file=audio_file, model=MODEL_NAME, language=language)
        return transcript.text

    def __call__(self) -> str:
        transcription = ""
        for i, chunk_filepath in enumerate(self.get_audio_chunk_paths()):
            text_chunk = self.audio_transcribe(chunk_filepath, self.lang)

            if self.verbose > 1:
                cprint(f"[{self.lang.upper()}]\tTranscription Chunk {i+1}", color="meganta")
                cprint(text_chunk, color="cyan")

            transcription += text_chunk

        return transcription
