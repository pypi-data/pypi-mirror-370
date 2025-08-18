import re
from typing import Any, Dict, List, Optional, Union
import logging

from pydantic import BaseModel
import tiktoken
import openai

from .config import (
    MODEL_TOKEN_CONFIGS, OPENAI_API_KEY
    )


class TokenLengthGuard:
    """
    A class to guard against token length,
    to prevent from hitting the openai api limit
    """
    def __init__(
        self,
        model: str,
        hard_roof: int,
        preserve_preference: str = "head",
        safe_buffer: int = 16,
        force_assistant_muffle: bool = False,
    ):
        """
        model: name of the model we're going to connect
        hard_roof:
            the maximum length of tokens
            combining the question and answer
        preserve_preference:
            head or tail, which part of the tokens to preserve
        safe_buffer:
            the buffer to prevent from hitting the hard roof
            in case our tokenization is not entirely accurate
        force_assistant_muffle:
            whether to force the muffle the content from role: assistant
                (take out the middle part of the paragraph)
        """
        self.hard_roof = hard_roof
        assert preserve_preference in ["head", "tail"], \
            "preserve_preference must be one of head, tail"
        self.preserve_preference = preserve_preference
        self.safe_buffer = safe_buffer
        self.model = model
        # load the official tokenize to assimulate the openai tokenizing count
        self.tokenizer = tiktoken.encoding_for_model(model)
        self.force_assistant_muffle = force_assistant_muffle

    def slicing(
        self, tokens: List[str], remain_length: int = 512
    ) -> List[str]:
        """
        Slice the tokens to the desired length
        Could be cutting from head or tail
        """
        if self.preserve_preference == "head":
            return tokens[:remain_length]
        else:
            return tokens[-remain_length:]

    def guard_prompt(
        self, prompt: int,
        min_answer_tokens: int = 512
    ) -> Dict[str, Union[int, str]]:
        """
        Guard the prompt length
        """
        token_ids = self.tokenizer.encode(prompt)
        original_length = len(token_ids)
        if original_length > self.hard_roof - min_answer_tokens:
            logging.debug(
                f"[CUT]{original_length} cut to "
                f"preserve `{self.preserve_preference}`"
            )
            sliced = self.slicing(
                token_ids,
                remain_length=self.hard_roof - min_answer_tokens-self.safe_buffer)
            prompt = self.tokenizer.decode(
                sliced
            )
            return {
                "prompt": prompt,
                "max_tokens":
                    self.hard_roof - len(sliced) - self.safe_buffer,
            }
        else:
            return {
                "prompt": prompt,
                "max_tokens":
                    self.hard_roof - original_length - self.safe_buffer,
            }

    def sum_msg_len(self, messages: List[Dict[str, str]]) -> int:
        """
        Calculate the total length of message length
        According to Ray's reverse engineering result on
        how the chatgpt API calculate the same number
        ```latex
        N = \Sigma(Content_{i} + 5) + 2
        ```
        """
        return sum(
            map(
                lambda x: len(x) + 5,
                self.tokenizer.encode_batch(
                    list(i['content'] for i in messages)
                )
            )
        ) + 2

    @staticmethod
    def select_role(
        messages: List[Dict[str, str]],
        role: str
    ) -> List[Dict[str, str]]:
        """
        Filter the messages by role
        """
        if role not in ['user', 'assistant', 'system']:
            raise ValueError(f"Role `{role}` not supported")
        return list(filter(lambda x: x['role'] == role, messages))

    def body_muffle(
        self, text: str,
    ):
        """
        Muffle long text's body, leave the head and tail sentences
        """
        # split sentence by '\n' or '.' or '?'
        sentences = re.split(r'[\n\.?]', text.strip("\n").strip("."))
        if len(sentences) < 3:
            return text
        else:
            return "\n".join(
                [sentences[0], sentences[-1]]
            )

    def iter_body_muffle_a_role(
        self, messages: Dict[str, str], role: str
    ) -> Dict[str, str]:
        """
        Muffle the body of a role
        """
        if role == 'user':
            iter_list = messages[:-1]
        else:
            iter_list = messages
        for msg in iter_list:
            if msg['role'] == role:
                original_length = len(
                    self.tokenizer.encode(msg['content'])) + 5
                msg['content'] = self.body_muffle(msg['content'])
                token_length_diff = original_length - (len(
                    self.tokenizer.encode(msg['content'])) + 5)
                yield msg, token_length_diff
            else:
                yield msg, 0

    def prepare_result(
        self,
        messages: List[Dict[str, str]],
        total: int,
        strategy: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare the return result
        """
        result = dict(
            messages=messages,
            max_tokens=self.hard_roof - total - self.safe_buffer,
            prompt_length=total,
        )
        if strategy is not None:
            result.update(dict(strategy=strategy))
        return result

    def guard_messages(
        self, messages: List[Dict[str, str]],
        min_answer_room: int = 512,
    ) -> List[Dict[str, str]]:
        """
        Guard the messages length
            this input format is for chat completion
        """
        # check the validation for min_answer_room
        if min_answer_room + self.safe_buffer > self.hard_roof:
            raise ValueError(
                "min_answer_room + safe_buffer > hard_roof, "
                "please adjust the parameters"
            )

        if self.force_assistant_muffle:
            messages = list(msg for msg, _
                             in self.iter_body_muffle_a_role(
                                messages, 'assistant')
                                )
        total = self.sum_msg_len(messages)
        if total <= self.hard_roof - min_answer_room - self.safe_buffer:
            return self.prepare_result(
                messages, total, strategy=(
                    "force_assitant_muffle"
                    if self.force_assistant_muffle else "no muffle"))

        # still too long
        # try muffle body for assistant role
        if self.force_assistant_muffle is False:
            for msg, diff in self.iter_body_muffle_a_role(
                    messages, 'assistant'):
                total -= diff
                if total <= (
                        self.hard_roof
                        - min_answer_room - self.safe_buffer):
                    return self.prepare_result(
                        messages, total,
                        strategy="1by1_assistant_muffle")

        # still too long
        # try to muffle body for user role
        for msg, diff in self.iter_body_muffle_a_role(
                messages, 'user'):
            total -= diff
            if total <= (
                    self.hard_roof
                    - min_answer_room - self.safe_buffer):
                return self.prepare_result(
                    messages, total,
                    strategy="1by1_user_muffle")

        total = self.sum_msg_len(messages)

        # still too long trucate assistant
        messages = list(
            msg for msg
            in messages if msg['role'] != 'assistant')

        total = self.sum_msg_len(messages)
        if total <= self.hard_roof - min_answer_room - self.safe_buffer:
            return self.prepare_result(
                messages, total,
                "no_assistant")

        # still too long
        # save last user input, remove all other user input
        last_input = messages[-1]
        messages = list(
            msg for msg in messages[:-1]
            if msg['role'] != "user") + [last_input, ]

        total = self.sum_msg_len(messages)
        if total <= self.hard_roof - min_answer_room - self.safe_buffer:
            return self.prepare_result(
                messages, total,
                "only_last_user_input")

        # still too long
        # muffle the body of the last user input
        last_msg = messages[-1]
        last_msg['content'] = self.body_muffle(last_msg['content'])
        total = self.sum_msg_len(messages)
        if total <= self.hard_roof - min_answer_room - self.safe_buffer:
            return self.prepare_result(
                messages, total,
                "muffle_last_user_input"
                )

        # still too long

        raise ValueError(
            "The message is still too long to be processed, "
            "we've tried all the strategies: "
            "we even removed any answer from the model"
            "we kept only last user input, "
            "we kept only the 1st and the last sentence "
            "of the last user input. "
            f"current total token length: {total}, "
            f"hard roof for all the tokens: {self.hard_roof}, "
            f"minimun room for answer tokens: {min_answer_room}, "
            f"safe buffer tokens: {self.safe_buffer}"
        )


class ChatLine(BaseModel):
    content: str
    role: str = "user"


class ChatConnection:
    kwargs_filter = [
        "model",
        "temperature",
        "top_p",
        "n",
        "stream",
        "stop",
        "presence_penalty",
        "frequency_penalty",
        "logit_bias",
        "user",
        "min_answer_room",
    ]

    def __init__(
        self,
        model: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        system_role: Optional[Union[str, List[str]]] = None,
        min_answer_room: Optional[int] = None,
    ) -> None:
        if model is None:
            model = "gpt-3.5-turbo"
        self.model = model
        if openai_api_key is None:
            if OPENAI_API_KEY == "not set":
                raise KeyError(
                    "Please set OPENAI_API_KEY system env"
                    " or pass in openai_api_key")
            openai_api_key = OPENAI_API_KEY
        openai.api_key = openai_api_key
        if system_role is None:
            system_role = (
                "You are the universal customer service agent "
                "who can answer any knowledge about any product "
                "in detail"
            )
        self.system_role = system_role

        model_config = MODEL_TOKEN_CONFIGS[model]

        if min_answer_room is None:
            min_answer_room = model_config["min_answer_room"]
        self.min_answer_room = min_answer_room

        self.token_guard = TokenLengthGuard(
            model=model,
            hard_roof=model_config["hard_roof"],
            safe_buffer=model_config["safe_buffer"],
        )

    def unpack_system_role(
            self, system_role: Optional[Union[str, List[str]]] = None,
            ) -> List[Dict[str, str]]:
        """
        Make sure system role is set to default format
        """
        if system_role is None:
            system_role = self.system_role
        if isinstance(system_role, list):
            if len(system_role) == 0:
                return []
            elif type(system_role[0]) is str:
                return list(
                    {"role": "system", "content": i}
                    for i in system_role)
            else:
                return system_role
        elif isinstance(system_role, str):
            return [{"role": "system", "content": system_role}]
        else:
            raise ValueError("system_role must be a string or a list")

    def prepare_messages(
            self, texts: List[Dict[str, str]],
            system_role: Optional[Union[str, List[str]]] = None,
            ) -> List[Dict[str, str]]:
        """
        Make sure messages is set to default format
        """
        system_role: List[ChatLine] = self.unpack_system_role(system_role)

        if isinstance(texts, str):
            messages = [dict(role="user", content=texts)]
        elif isinstance(texts, list):
            messages = []
            for msg in texts:
                if isinstance(msg, str):
                    messages.append(dict(role="user", content=msg))
                elif isinstance(msg, dict):
                    if "role" not in msg:
                        msg["role"] = "user"
                    if set(msg.keys()) != {"role", "content"}:
                        raise KeyError(
                            "dict in texts must only have role and content")
                    messages.append(msg)
                else:
                    raise ValueError(
                        "texts must be a list of strings or dicts")
        else:
            raise ValueError("texts must be a string or a list")

        # insert system role back into messages
        if len(system_role) > 0:
            messages = messages[:-1] + system_role + messages[-1:]

        guarded = self.token_guard.guard_messages(
            messages, min_answer_room=self.min_answer_room)
        return guarded

    def __call__(
        self,
        texts: Union[
            str, List[ChatLine]],
        system_role: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> str:
        """
        Send chat request to openapi
        """

        guarded = self.prepare_messages(texts, system_role)

        messages = guarded["messages"]
        max_tokens = guarded["max_tokens"]

        input_kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        for k, v in kwargs.items():
            if k in self.kwargs_filter:
                input_kwargs[k] = v

        logging.debug(f"input_kwargs: {input_kwargs}")

        res = openai.ChatCompletion.create(**input_kwargs)

        if "choices" not in res:
            logging.error(f"openai api returned invalid response: {res}")
            raise ConnectionError("openai api returned invalid response")

        return res["choices"][0]["message"]["content"]

    async def acreate(
        self,
        texts: Union[
            str, List[ChatLine]],
        system_role: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> str:
        """
        Send chat request to openapi
        """

        guarded = self.prepare_messages(texts, system_role)

        messages = guarded["messages"]
        max_tokens = guarded["max_tokens"]

        input_kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        for k, v in kwargs.items():
            if k in self.kwargs_filter:
                input_kwargs[k] = v

        logging.debug(f"input_kwargs: {input_kwargs}")

        res = await openai.ChatCompletion.acreate(**input_kwargs)

        if "choices" not in res:
            logging.error(f"openai api returned invalid response: {res}")
            raise ConnectionError("openai api returned invalid response")

        return res["choices"][0]["message"]["content"]

