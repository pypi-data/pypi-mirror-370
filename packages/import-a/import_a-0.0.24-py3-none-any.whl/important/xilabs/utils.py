import os
from typing import Optional


def get_xi_api_key(xi_api_key: Optional[str] = None) -> str:
    """
    Get the xi_api_key from the environment variable or the function argument
    """
    if xi_api_key is None:
        xi_api_key = os.getenv("XI_API_KEY")

    if xi_api_key is None:
        raise ValueError("xi_api_key is not set")

    return xi_api_key
