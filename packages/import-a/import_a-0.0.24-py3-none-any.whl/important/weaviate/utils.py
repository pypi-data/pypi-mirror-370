import datetime
from typing import Any

import numpy as np


def _json_serializable(value: Any) -> Any:
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    return value


def _capitalize_first_letter(string: str) -> str:
    if len(string) == 1:
        return string.capitalize()
    return string[0].capitalize() + string[1:]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate the cosine similarity between two vectors.

    Return scalar value between -1 and 1.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
