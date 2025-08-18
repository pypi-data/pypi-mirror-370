from typing import Dict, Iterator, List, Optional, Union
import json
import os
import requests

from .chat import ChatBase


class ChatGroq(ChatBase):
    """
    Chat model for Groq's inference API.
    Without any extra package installation

    >>> os.environ["GROQ_API_KEY"] = "xxx"
    >>> chat = ChatGroq(model_name="mixtral-8x7b-32768")

    One-shot chat.
    >>> chat("What is controlled fusion?", system="poetic", temperature=0.9)

    We can iterate over the stream to get the tokens as they come in.
    >>> for token in chat.stream("What is controlled fusion?", system="poetic"):
    ...     print(token, end="")

    You can see the quick start documentation here
    https://console.groq.com/docs/quickstart

    """

    payload_keys = {
        "temperature": float,
        "max_tokens": int,
        "top_p": float,
    }
    api_endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        model_name: str = "mixtral-8x7b-32768",
        api_key: Optional[str] = None,
    ):
        """
        model_name: str, name of the model to use.
        api_key: str, api key for groq.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("api_key must be set, or set GROQ_API_KEY env var")

        self.model_name = model_name

    def __repr__(self):
        return f"ChatGroq(model_name={self.model_name})"

    def __call__(
        self,
        messages: Union[List[Dict[str, str]], str],
        system: Optional[str] = None,
        json_response: bool = False,
        **kwargs,
    ) -> str:
        """
        Return a string reply from the model.

        messages: List of messages to send to the model.
            It can be a string, we'll wrap it in a list.
        system: Optional, a role the bot will play in the conversation.
        json_response: bool, Should the response be returned as a json object
        kwargs: Extra parameters to pass to the model.
        """
        payload_extra = self.build_extra_payload(**kwargs)

        # wrap messages in a list if it's a string
        if isinstance(messages, str):
            messages = [dict(content=messages, role="user")]

        if system is not None:
            messages.insert(0, dict(content=system, role="system"))

        payload = {
            "model": self.model_name,
            "messages": messages,
        }

        if json_response:
            payload["response_format"] = {"type": "json_object"}

        payload.update(payload_extra)

        response = requests.post(
            self.api_endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
        )

        response.raise_for_status()

        json_data = response.json()

        if "choices" in json_data:
            return_text = json_data["choices"][0]["message"]["content"]
            return return_text
        else:
            raise ValueError(f"Invalid response: {response.text}")

    def stream(
        self,
        messages: Union[List[Dict[str, str]], str],
        system: Optional[str] = None,
        json_response: bool = False,
        **kwargs,
    ) -> Iterator[str]:
        """
        This is a generator function that streams the response from the model.

        messages: List of messages to send to the model.
            It can be a string, we'll wrap it in a list.
        system: Optional, a role the bot will play in the conversation.
        json_response: bool, Should the response be returned as a json object
        kwargs: Extra parameters to pass to the model.
        """
        payload_extra = self.build_extra_payload(**kwargs)

        # wrap messages in a list if it's a string
        if isinstance(messages, str):
            messages = [dict(content=messages, role="user")]

        if system is not None:
            messages.insert(0, dict(content=system, role="system"))

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
        }

        if json_response:
            payload["response_format"] = {"type": "json_object"}

        payload.update(payload_extra)

        response = requests.post(
            self.api_endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            stream=True,
        )

        response.raise_for_status()

        for chunk in response.iter_lines():
            text = chunk.decode("utf-8")
            if text == "data: [DONE]":
                break
            if text.startswith("data: "):
                text = json.loads(text[6:])
                delta = text["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]
