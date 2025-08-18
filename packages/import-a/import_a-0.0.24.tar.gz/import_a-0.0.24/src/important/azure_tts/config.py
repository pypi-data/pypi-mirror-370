import os
import logging


try:
    AZURE_REGION = os.environ['AZURE_REGION']
    AZURE_TTS_ISSUETOKEN_ENDPOINT = os.environ['AZURE_TTS_ISSUETOKEN_ENDPOINT']
    AZURE_SPEECH_KEY = os.environ['AZURE_SPEECH_KEY']


    AZURE_TTS_VOICE_LIST = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list"
    AZURE_TTS_SERVICE = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

except KeyError as e:
    logging.error("Please setup env variable 1st")
    raise e


AUDIO_FORMATS = [
    "amr-wb-16000hz",
    "audio-16khz-16bit-32kbps-mono-opus",
    "audio-16khz-32kbitrate-mono-mp3",
    "audio-16khz-64kbitrate-mono-mp3",
    "audio-16khz-128kbitrate-mono-mp3",
    "audio-24khz-16bit-24kbps-mono-opus",
    "audio-24khz-16bit-48kbps-mono-opus",
    "audio-24khz-48kbitrate-mono-mp3",
    "audio-24khz-96kbitrate-mono-mp3",
    "audio-24khz-160kbitrate-mono-mp3",
    "audio-48khz-96kbitrate-mono-mp3",
    "audio-48khz-192kbitrate-mono-mp3",
    "ogg-16khz-16bit-mono-opus",
    "ogg-24khz-16bit-mono-opus",
    "ogg-48khz-16bit-mono-opus",
    "raw-8khz-8bit-mono-alaw",
    "raw-8khz-8bit-mono-mulaw",
    "raw-8khz-16bit-mono-pcm",
    "raw-16khz-16bit-mono-pcm",
    "raw-16khz-16bit-mono-truesilk",
    "raw-22050hz-16bit-mono-pcm",
    "raw-24khz-16bit-mono-pcm",
    "raw-24khz-16bit-mono-truesilk",
    "raw-44100hz-16bit-mono-pcm",
    "raw-48khz-16bit-mono-pcm",
    "webm-16khz-16bit-mono-opus",
    "webm-24khz-16bit-24kbps-mono-opus",
    "webm-24khz-16bit-mono-opus",
]