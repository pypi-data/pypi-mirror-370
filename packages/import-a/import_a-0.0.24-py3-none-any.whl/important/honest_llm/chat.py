"""
Manage GPT LLM (Casual language modeling completion tasks)
    to make the query more reliable and trackable
"""


import os
from typing import Any, Dict, List, Optional
import logging
import json


class OpenAIComplete:
    """
    OpenAI Complete wrapper
    A handler to call LLM completion model

    We might have other LLM completion models in the future,
        if there're other providers
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_max_tokens: int = 4095,
    ):
        if api_key is None:
            api_key = os.environ.get('OPENAI_API_KEY')
        if api_key is None:
            raise KeyError(
                "Please set up OPENAI_API_KEY"
            )
        # we import these packages here to avoid
        # import error when we don't have openai
        try:
            import openai
            from transformers import AutoTokenizer
        except ImportError as e:
            logging.error(
                "Please install openai and transformers"
            )
            raise e
        self.openai = openai
        self.openai.api_key = api_key
        self.tokenizer = AutoTokenizer.from_pretrained(
            "gpt2"
        )
        self.model_max_tokens = model_max_tokens

    def cap_tokens(
        self, text: str,
        ask_max_tokens: int = 3090,
    ) -> str:
        """
        Cap the number of tokens in the text
        To avoid the model from generating too long text
        """
        tokens = self.tokenizer.tokenize(text)
        if len(tokens) > ask_max_tokens:
            return self.tokenizer.convert_tokens_to_string(
                tokens[-ask_max_tokens:])
        return text

    def log_io(self, prompt: str, reply: str, **kwargs):
        """
        Log the input and output of the model API
            Feel free to overwrite this function while inheriting
        """
        logging.info(
            json.dumps(
                dict(
                    prompt=prompt,
                    reply=reply,
                    **kwargs
                )
            )
        )

    def __call__(self, prompt: str, **kwargs):
        # if answer's max_tokens is set,
        # we need to cap the prompt
        if "max_tokens" in kwargs:
            prompt = self.cap_tokens(
                prompt,
                self.model_max_tokens - kwargs["max_tokens"])
        reply = self.openai.Completion(
            prompt,
            **kwargs
        ).choices[0].text
        self.log_io(prompt, reply, **kwargs)
        return reply


class Line:
    """
    A line in a chat.
    A line can be of type human or bot.
    line.text is the text of the line.
    line.last_line is the previous line in the chat.
    line.next_line is the next line in the chat.
    """

    def __init__(
        self,
        text: str,
        line_type: str = "unkown",
        last_line: Optional["Line"] = None,
        next_line: Optional["Line"] = None,
    ):
        self.text = text
        if line_type not in ["unkown", "human", "bot"]:
            raise ValueError(
                "line_type must be one of 'unkown', 'human', 'bot'")
        self.line_type = line_type
        self.last_line = last_line
        self.next_line = next_line
        self.data = dict()

    def __repr__(self) -> str:
        return f"Text({self.line_type}): {self.text}"

    def __str__(self) -> str:
        return self.text

    def trace_back_lines(
        self,
        n: Optional[int] = None,
        type_filter: Optional[str] = None,
    ) -> List["Line"]:
        """
        Trace back n lines of type type_filter.
        If n is None, trace back all lines of type type_filter.
        If type_filter is None, trace back all lines.
        """
        if n == 0:
            return []

        if self.last_line is None:
            return []

        # if we turn on the type filter, we need to check if the last text
        # is of the right type
        if type_filter is not None \
                and self.last_line.line_type != type_filter:
            return self.last_line.trace_back_lines(
                n=n, type_filter=type_filter)
        if n is None:
            return [self.last_line] + \
                self.last_line.trace_back_lines(
                    n=None, type_filter=type_filter
            )
        else:
            return [self.last_line] + \
                self.last_line.trace_back_lines(
                    n=n - 1, type_filter=type_filter
            )

    def trace_back_lines_text(
        self,
        n: Optional[int] = None,
        type_filter: Optional[str] = None,
    ) -> List[str]:
        """
        Trace back n lines of type type_filter.
        If n is None, trace back all lines of type type_filter.
        If type_filter is None, trace back all lines.
        """
        return [line.text for line in self.trace_back_lines(
            n=n, type_filter=type_filter
        )]


class ChatBase:
    """
    Base class for chat

    Please inherit this class to implement your own chat
    You have to:
        * set `def __getitem__(self, line: Line) -> List[Dict[str, Any]]`
            to map the line to the references
        * set
            ```python
            def render_reference(
                self,
                ask: Line,
                reference: Dict[str, Any]
            ) -> str:
            ```
            to render the references and the to actual prompt
    """
    def __init__(
        self,
        last_line: Optional[Line] = None,
        complete: Optional[OpenAIComplete] = None,
    ):
        self.last_line = last_line
        if complete is None:
            complete = OpenAIComplete()
        self.complete = complete

    def update_last_line(
        self,
        new_line: Line
    ) -> Line:
        """
        Update the last line of the chat
        Build the connection between new_line and last_line
        """
        if self.last_line is not None:
            # bound the last line to the new line
            new_line.last_line = self.last_line
            self.last_line.next_line = new_line
        self.last_line = new_line
        return self.last_line

    def __getitem__(
        self, line: Line
    ) -> List[Dict[str, Any]]:
        """
        The function we have to map chat with references

        **NOTICE**
        You can leverage `self` to extract the previews data
        self.lines were the preview data
        """
        raise NotImplementedError(
            "You have to define mapping function to find reference"
        )

    def render_reference(
        self,
        ask: Line,
        references: List[Dict[str, Any]],
    ) -> str:
        """
        The function we have to render the references and the to actual prompt,
            Usually by templating
        """
        raise NotImplementedError(
            "You have to define `render_reference` function"
        )

    def __call__(
        self,
        text: str,
        openai_complete_kwargs: Dict[str, Any]
    ) -> str:
        """
        The core function to get the reply based on the last query
            we can still have access to the previous query and replies
        """
        ask = Line(text, line_type='human')
        self.update_last_line(ask)

        references = self[ask]
        ask.data['references'] = references

        prompt = self.render_reference(ask, references)
        complete_kwargs = {
            "model": "davinci-text-003",
            "max_tokens": 512,
        }
        complete_kwargs.update(
            openai_complete_kwargs)

        reply = self.complete(
            prompt=prompt,
            **complete_kwargs,
        )

        reply_line = Line(reply, line_type='bot')

        self.update_last_line(reply_line)

        return reply
