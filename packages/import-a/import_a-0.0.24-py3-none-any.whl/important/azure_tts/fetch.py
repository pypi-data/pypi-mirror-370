from pathlib import Path, PosixPath
from typing import Union, Optional, Dict, Any, List

import aiohttp
import asyncio

from .token import auth_header
from .config import (
    AZURE_SPEECH_KEY, AZURE_TTS_VOICE_LIST, AZURE_TTS_SERVICE)


async def get_voice_list():
    """
    Get voice list

    You can use the following code to analyze the response:
    voices_df = pd.DataFrame(await get_voice_list())
    """
    headers = {"Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            AZURE_TTS_VOICE_LIST,
                headers=headers) as response:
            print(response.status)
            return await response.json()


class VoiceBank:
    """
    Voice bank that holds the config to all voices
    """
    def __init__(self, locale: Optional[str] = None,
                 voice_list=List[Dict[str, Any]]):
        """
        locale: str, optional
            Locale of the voice, e.g. "en-US", "zh-CN"
        voice_list: list of dict
            List of voice config
            """
        self.language = locale
        self.voice_list = voice_list
        if locale is not None:
            if locale[-1] == "*":
                locale = locale[:-1]
                self.voice_list = [
                    voice for voice in self.voice_list
                    if voice["Locale"].startswith(locale)]
            else:
                self.voice_list = [
                    voice for voice in self.voice_list
                    if voice["Locale"] == locale]

    @classmethod
    async def from_azure(cls, locale: Optional[str] = None):
        """
        Get voice bank from Azure
        """
        voice_list = await get_voice_list()
        return cls(locale, voice_list)

    def __call__(self, voice_name: str) -> Dict[str, Any]:
        """
        Get voice by name
        """
        for voice in self.voice_list:
            if voice["DisplayName"] == voice_name:
                return voice
            elif voice["ShortName"] == voice_name:
                return voice
        raise ValueError(f"Voice {voice_name} not found")

    def name_list(self) -> List[str]:
        """
        Get all voice names
        """
        return [voice["DisplayName"] for voice in self.voice_list]

    def __repr__(self):
        allnames = ",".join(
            self.name_list())
        return (
            f"VoiceBank({self.language})" +
            f"[{len(self.voice_list)} voices]:\n" +
            allnames
        )


async def text_to_speech(
        text,
        voice_kwargs,
        style=None,
        output_format="audio-16khz-128kbitrate-mono-mp3",
        user_agent="important"
        ) -> bytes:
    """
    Convert text to speech
    """
    headers = await auth_header()
    headers["Content-Type"] = "application/ssml+xml"
    headers["X-Microsoft-OutputFormat"] = output_format
    headers["User-Agent"] = user_agent

    locale = voice_kwargs.get("Locale", "en-US")
    gender = voice_kwargs.get('Gender')
    short_name = voice_kwargs.get('ShortName')

    style = "" if style is None else f"style='{style}'"

    ssml = f"""<speak version='1.0' xml:lang='{locale}'>
    <voice xml:lang='{locale}' xml:gender='{gender}' {style}
        name='{short_name}'>{text}</voice></speak>"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            AZURE_TTS_SERVICE, headers=headers, data=ssml
                ) as response:
            if response.status // 100 == 2:
                return await response.read()
            else:
                raise ConnectionError(
                    f"🔌 CODE:{response.status}, {await response.text()}")


def save_audio_bytes(
        data: bytes,
        directory: Union[PosixPath, str],
        file_stem: str,
        output_format="audio-16khz-128kbitrate-mono-mp3",) -> str:
    """
    Save audio bytes to file
    """
    filename = f"{file_stem}.{output_format.split('-')[-1]}"
    directory = Path(directory)
    directory.mkdir(
        parents=True, exist_ok=True
    )
    save_path = directory / filename
    with open(save_path, 'wb') as f:
        f.write(data)
    return save_path
