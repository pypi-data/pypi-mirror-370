import os
from typing import Any, List, Optional

import aiohttp

from important.xilabs.utils import get_xi_api_key


async def aget_voices(xi_api_key: Optional[str] = None):
    """
    Get a list of list options

    You may see the voice you cloned!

    :param xi_api_key: the xi_api_key

    Return:
        a list of voices
        each voice a dictionary, example voice:
        {'voice_id': '21m00Tcm4TlvDq8ikWAM',
        'name': 'Rachel',
        'samples': None,
        'category': 'premade',
        'fine_tuning': {'language': None,
        'is_allowed_to_fine_tune': False,
        'fine_tuning_requested': False,
        'finetuning_state': 'not_started',
        'verification_attempts': None,
        'verification_failures': [],
        'verification_attempts_count': 0,
        'slice_ids': None,
        'manual_verification': None,
        'manual_verification_requested': False},
        'labels': {'accent': 'american',
        'description': 'calm',
        'age': 'young',
        'gender': 'female',
        'use case': 'narration'},
        'description': None,
        'preview_url': 'https://storage.googleapis.com/eleven-public-prod/premade/voices/21m00Tcm4TlvDq8ikWAM/df6788f9-5c96-470d-8312-aab3b3d8f50a.mp3',
        'available_for_tiers': [],
        'settings': None,
        'sharing': None,
        'high_quality_base_model_ids': []}
    """
    xi_api_key = get_xi_api_key(xi_api_key)

    headers = {
        "xi-api-key": xi_api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.elevenlabs.io/v1/voices", headers=headers) as res:
            res.raise_for_status()

            return (await res.json())["voices"]


async def axi_tts(
    text: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # "Rachel's voice id"
    output_format: str = "pcm_24000",
    stability: float = 0.0,
    similarity_boost: float = 1.0,
    style: float = 1.0,
    pitch: float = 1.0,
    xi_api_key: Optional[str] = None,
) -> bytes:
    """
    - text
        The text to synthesize

    - output_format: str, optional
        The output format of the audio.
        Output format of the generated audio. Must be one of:
        - mp3_44100_64 - output format, mp3 with 44.1kHz sample rate at 64kbps.
        - mp3_44100_96 - output format, mp3 with 44.1kHz sample rate at 96kbps.
        - mp3_44100_128 - default output format,
            mp3 with 44.1kHz sample rate at 128kbps.
        - mp3_44100_192 - output format, mp3 with 44.1kHz sample rate at 192kbps.
            Requires you to be subscribed to ⭐️💰 Creator tier or above.
        - pcm_16000 - PCM format (S16LE) with 16kHz sample rate.
        - pcm_22050 - PCM format (S16LE) with 22.05kHz sample rate.
        - pcm_24000 - PCM format (S16LE) with 24kHz sample rate.
        - pcm_44100 - PCM format (S16LE) with 44.1kHz sample rate.
            Requires you to be subscribed to ⭐️💰 Independent Publisher tier or above.
        - ulaw_8000 - μ-law format (sometimes written mu-law,
            often approximated as u-law) with 8kHz sample rate.
            Note that this format is commonly used for Twilio audio inputs.

    - stability: float, optional
        The stability slider determines how stable the voice is
        and the randomness between each generation.
        Lowering this slider introduces a broader emotional range
        for the voice. As mentioned before, this is also influenced
        heavily by the original voice.
        - Setting the slider too LOW may result in odd performances
            that are overly random and cause the character to speak too quickly.
        - On the other hand, setting it too HIGH can lead to a monotonous voice with limited emotion.

    - similarity_boost: float, optional
        The similarity slider dictates how closely the AI should
        adhere to the original voice when attempting to replicate it
        If the original audio is of poor quality and
        the similarity slider is set too HIGH, the AI may reproduce
        **artifacts** or background noise when trying to mimic the voice
        if those were present in the original recording.

    - style: float, optional
        With the introduction of the newer models,
        we also added a style exaggeration setting.
        This setting attempts to amplify the style of the original speaker.
        It does consume additional computational resources
        and might increase latency if set to anything other than 0.
        It’s important to note that using this setting has shown
        to make the model slightly less stable, as it strives to
        emphasize and imitate the style of the original voice.

        In general, we recommend keeping this setting at 0 at all times.

    - voice_id: str, optional
        Some voice id to choose from:
        - Rachel : "21m00Tcm4TlvDq8ikWAM"
        - Drew : "29vD33N1CtxCmqQRPOHJ"
        - Clyde : "2EiwWnXFnvU5JabPnv8n"
        - Paul : "5Q0t7uMcjvnagumLfvZi"
        - Domi : "AZnzlk1XvdvUeBnXmlld"
        - Dave : "CYw3kZ02Hs0563khs1Fj"
        - Fin : "D38z5RcWu1voky8WS1ja"
        - Bella : "EXAVITQu4vr4xnSDxMaL"
        - Antoni : "ErXwobaYiN019PkySvjV"
        - Thomas : "GBv7mTt0atIp3Br8iCZE"
        - Charlie : "IKne3meq5aSn9XLyUdCD"
        - George : "JBFqnCBsd6RMkjVDRZzb"
        - Emily : "LcfcDJNUP1GQjkzn1xUU"
        - Elli : "MF3mGyEYCl7XYWbV9V6O"
        - Callum : "N2lVS1w4EtoT3dr4eOWO"
        - Patrick : "ODq5zmih8GrVes37Dizd"
        - Harry : "SOYHLrjzK2X1ezoPC6cr"
        - Liam : "TX3LPaxmHKxFdv7VOQHJ"
        - Dorothy : "ThT5KcBeYPX3keUQqHPh"
        - Josh : "TxGEqnHWrfWFTfGW9XjX"
        - Arnold : "VR6AewLTigWG4xSOukaG"
        - Charlotte : "XB0fDUnXU5powFXDhCwa"
        - Matilda : "XrExE9yKIg1WjnnlVkGX"
        - Matthew : "Yko7PKHZNXotIFUBG7I9"
        - James : "ZQe5CZNOzWyzPSCn5a3c"
        - Joseph : "Zlb1dXrM653N07WRdFW3"
        - Jeremy : "bVMeCyTHy58xNoL34h3p"
        - Michael : "flq6f7yk4E4fJM5XTYuZ"
        - Ethan : "g5CIjZEefAph4nQFvHAz"
        - Gigi : "jBpfuIE2acCO8z3wKNLl"
        - Freya : "jsCqWAovK2LkecY7zXl4"
        - 🎅 Santa Claus : "knrPHWnBmmDHMoiMeP3l"
        - Grace : "oWAxZDx7w5VEj9dCyTzz"
        - Daniel : "onwK4e9ZLuTAKqWW03F9"
        - Lily : "pFZP5JQG7iQjIQuC4Bku"
        - Serena : "pMsXgVXv3BLzUgSXRplE"
        - Adam : "pNInz6obpgDQGcFmaJgB"
        - Nicole : "piTKgcLEGmPE4e6mEKli"
        - Bill : "pqHfZKP75CvOlQylNhV4"
        - Jessie : "t0jbNlBVZ17f02VDIeMI"
        - Ryan : "wViXBPUzp2ZZixB1xQuM"
        - Sam : "yoZ06aMxZJJ28mfd3POQ"
        - Glinda : "z9fAnlkpzviPz146aGWa"
        - Giovanni : "zcAOhNBS3c14rBihAFp1"
        - Mimi : "zrHiDhphv9ZnVXBqCLjz"
        - Jason : "WPLvqrCYdebjGQ5ixit8"
        - Nelson : "htiOXBurACx1mzJhsD7l"
        - Jason2 : "o5cTvIOrzMSBwOHvA5Tp"
    """
    headers = {
        "xi-api-key": get_xi_api_key(xi_api_key),
        "Accept": "application/json",
        "Content-Type": "application/json",
        # "optimize_streaming_latency": "3",
        "output-format": output_format,
    }

    voice_settings = {
        "stability": stability,
        "similarity_boost": similarity_boost,
        "style": style,
        "pitch": pitch,
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": voice_settings,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers=headers,
            json=payload,
        ) as res:
            res.raise_for_status()

            return await res.read()
