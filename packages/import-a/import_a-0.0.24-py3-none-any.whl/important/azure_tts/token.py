from datetime import datetime
from typing import Dict

import aiohttp

from .config import (
    AZURE_SPEECH_KEY, AZURE_TTS_ISSUETOKEN_ENDPOINT)


async def get_token():
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-type": "application/x-www-form-urlencoded",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            AZURE_TTS_ISSUETOKEN_ENDPOINT,
                headers=headers) as response:
            return await response.text()


class TokenDeposit:
    """
    Since the API requires to refresh token every 10 minutes.
        This is a handler that can store token for 9 minutes, if time's up
        We'll refersh the token automatically
    """
    def __init__(self):
        self.token = None
        self.expires = 540  # 10 minutes
        self.last_fetch = None

    async def __call__(self) -> str:
        if self.last_fetch is None or \
                (datetime.now() - self.last_fetch).seconds > self.expires:
            self.token = await get_token()
            self.last_fetch = datetime.now()
        return self.token


token_deposit = TokenDeposit()


async def auth_header() -> Dict[str, str]:
    """
    Get auth header for HTTP request
    """
    token = await token_deposit()
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Authorization": f"Bearer {token}",
        }
    return headers
