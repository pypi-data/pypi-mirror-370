from typing import Dict, Iterator, List, Optional, Union
import json
import logging
import os
import requests

from .chat import ChatBase


class ChatClaude(ChatBase):
    """
    Chat model for Anhtropic's Claude
    
    messages: List of messages to send to the model.
    system: Optional system message to send to the model.
    **kwargs: Extra arguments to pass to the API.
    
    >>> os.environ["ANTHROPIC_API_KEY"] = "xxx"
    >>> chat = ChatClaude(model_name="claude-2.1")
    
    One-shot chat.
    >>> chat("What is controlled fusion?", system="poetic", max_tokens_to_sample=256)
    
    We can iterate over the stream to get the tokens as they come in.
    >>> for token in chat.stream("What is controlled fusion?", system="answer question poeticly"):
    ...     print(token, end="")
    """
    
    payload_keys = {
        "max_tokens_to_sample": int,
    }
    api_endpoint = "https://api.anthropic.com/v1/complete"
    
    def __init__(
        self,
        model_name: str = "claude-2.1",
        api_key: Optional[str] = None,
        anthropic_version: str = "2023-06-01",
    ):
        """
        model_name: str, name of the model to use.
            model_name options can be found here:
            https://docs.anthropic.com/claude/reference/selecting-a-model
        api_key: str, api key for openai.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("api_key must be set, or set ANTHROPIC_API_KEY env var")
        
        self.model_name = model_name
        self.anthropic_version = anthropic_version

    def packing_prompt(
        self,
        messages: Union[List[Dict[str, str]], str]
    ) -> str:
        """
        messages:
        - a list of dict, each dict has two keys: role and content
            roles:
            - user: human message
            - assistant: assistant message
            - system: system message, preferrably don't use this,
                but write your role setting in the user prompt
            `user` and `assistant` must be in alternating order
            The first message must be from `human`, and the last message must be from `human`
        - a simple string
        """
        if isinstance(messages, list):
            prompt = ""
            h_and_a = []
            systems = []
            for message in messages:
                if message["role"] == "system":
                    systems.append(message["content"])
                else:
                    h_and_a.append(message)
            if (h_and_a[-1]["role"]) == "human" or (h_and_a[0]["role"]) != "human":
                raise ValueError(
                    "1st or Last message must be from human, for anthropic, "
                    "Please check https://docs.anthropic.com/claude/reference/prompt-validation "
                    "for prompt validation."
                    )
                    
            if len(systems)>0:
                combined_systems = "\n".join(systems)
                messages[-1]['content'] = f"{combined_systems}\n" + messages[-1]['content']
            
            last_role = "assitant"
            for message in h_and_a:
                if message["role"] == "user":
                    if last_role == "user":
                        raise ValueError(
                            "user must not be repeated, has to be followed by assistant, "
                            "Please check https://docs.anthropic.com/claude/reference/prompt-validation "
                            "for prompt validation."
                            )
                    prompt += f"\n\nHuman: {message['content']}"
                    last_role = "user"
                elif message["role"] == "assistant":
                    if last_role == "assistant":
                        raise ValueError(
                            "assistant must not be repeated, has to be followed by user, "
                            "Please check https://docs.anthropic.com/claude/reference/prompt-validation "
                            "for prompt validation."
                            )
                    prompt += f"\n\Assistant: {message['content']}"
                    last_role = "assistant"
                else:
                    raise ValueError(
                        "role must be either user or assistant, "
                        "for anthropic, Please check https://docs.anthropic.com/claude/reference/prompt-validation "
                        "for prompt validation."
                        )
            prompt += "\n\nAssistant:"
            return prompt
        
        if isinstance(messages, str):
            return f"\n\nHuman: {messages}\n\nAssistant:"

    def __call__(
        self,
        messages: Union[List[Dict[str, str]], str],
        system: Optional[str] = None,
        **kwargs,
    ):
        """
        Return a string reply from the model.
        """
        if "max_tokens_to_sample" not in kwargs:
            kwargs["max_tokens_to_sample"] = 4096
        if system is not None:
            if isinstance(messages, str):
                messages = f"{system}\n{messages}"
            elif isinstance(messages, list):
                messages.insert(0, dict(content=system, role="system"))
            else:
                raise ValueError(
                    "messages must be either a string or a list of dict, "
                    "for anthropic, Please check https://docs.anthropic.com/claude/reference/prompt-validation "
                    "for prompt validation."
                    )
    
        prompt = self.packing_prompt(messages)
        
        payload = {
            "prompt": prompt,
            "model": self.model_name,
        }
        
        playload_extra = self.build_extra_payload(**kwargs)
        
        payload.update(playload_extra)
        
        response = requests.post(
            self.api_endpoint,
            headers={
                "x-api-key": f"{self.api_key}",
                "anthropic-version": f"{self.anthropic_version}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(f"Anthropic API error: {e}")
            if hasattr(response, "text"):
                logging.error(f"Anthropic API response: {response.text}")
                print(response.text)
            raise e
        json_data = response.json()
        return json_data['completion']
    
    def stream(
        self,
        messages: Union[List[Dict[str, str]], str],
        system: Optional[str] = None,
        **kwargs,
    ) -> Iterator[str]:
        """
        Return a string reply from the model.
        """
        if "max_tokens_to_sample" not in kwargs:
            kwargs["max_tokens_to_sample"] = 4096
        if system is not None:
            if isinstance(messages, str):
                messages = f"{system}\n{messages}"
            elif isinstance(messages, list):
                messages.insert(0, dict(content=system, role="system"))
            else:
                raise ValueError(
                    "messages must be either a string or a list of dict, "
                    "for anthropic, Please check https://docs.anthropic.com/claude/reference/prompt-validation "
                    "for prompt validation."
                    )
            
        prompt = self.packing_prompt(messages)
        
        payload = {
            "prompt": prompt,
            "model": self.model_name,
            "stream": True
        }
        
        playload_extra = self.build_extra_payload(**kwargs)
        
        payload.update(playload_extra)
        
        response = requests.post(
            self.api_endpoint,
            headers={
                "x-api-key": f"{self.api_key}",
                "anthropic-version": f"{self.anthropic_version}",
                "Content-Type": "application/json",
            },
            json=payload,
            stream=True,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(f"Anthropic API error: {e}")
            if hasattr(response, "text"):
                logging.error(f"Anthropic API response: {response.text}")
                print(response.text)
            raise e
        for line in response.iter_lines():
            if line:
                if line[:6] == b'data: ':
                    line = line[6:]
                    json_data = json.loads(line)
                    if 'completion' in json_data:
                        yield json_data['completion']