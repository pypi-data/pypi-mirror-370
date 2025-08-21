import sys
from typing import Any, AsyncGenerator, Dict, List
import aiohttp
import json

from dataclasses import dataclass

from hero_base.tokenizer import count_tokens


@dataclass
class StartChunk:
    def __post_init__(self):
        self.type = "start"


@dataclass
class CompletedChunk:
    content: str
    reasoning_content: str

    def __post_init__(self):
        self.type = "completed"


@dataclass
class ReasoningChunk:
    content: str

    def __post_init__(self):
        self.type = "reasoning"


@dataclass
class ContentChunk:
    content: str

    def __post_init__(self):
        self.type = "message"


@dataclass
class UsageChunk:
    usage: dict

    def __post_init__(self):
        self.type = "usage"


type ChatChunk = StartChunk | CompletedChunk | ContentChunk | ReasoningChunk | UsageChunk


class Usage:
    """
    使用情况
    """

    def __init__(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        reasoning_tokens: int = 0,
        content_tokens: int = 0,
        prompt_cache_hit_tokens: int = 0,
        prompt_cache_miss_tokens: int = 0,
        cache_creation_input_tokens: int = 0,
        cache_read_input_tokens: int = 0,
        cached_tokens: int = 0,
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.reasoning_tokens = reasoning_tokens
        self.content_tokens = content_tokens
        self.prompt_cache_hit_tokens = prompt_cache_hit_tokens
        self.prompt_cache_miss_tokens = prompt_cache_miss_tokens
        self.cache_creation_input_tokens = cache_creation_input_tokens
        self.cache_read_input_tokens = cache_read_input_tokens
        self.cached_tokens = cached_tokens

    def to_dict(self) -> Dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "content_tokens": self.content_tokens,
            "prompt_cache_hit_tokens": self.prompt_cache_hit_tokens,
            "prompt_cache_miss_tokens": self.prompt_cache_miss_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
            "cached_tokens": self.cached_tokens,
        }


class Model:
    def __init__(
        self,
        model_name: str = "",
        api_base: str = "",
        api_key: str = "",
        context_length: int = 128000,
        max_tokens: int = 6000,
        timeout: int = sys.maxsize,
        options: Dict[str, Any] = {},
    ):
        self.model_name = model_name
        self.context_length = context_length
        self.max_tokens = max_tokens
        self.api_base = api_base
        self.api_key = api_key
        self.timeout = timeout
        self.options = options

    def to_dict(self):
        return self.__dict__

    def __replace_prompt_params(self, prompt: str, params: dict):
        for key, value in params.items():
            if isinstance(value, str):
                prompt = prompt.replace(f"{{{{{key}}}}}", value)
            else:
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        return prompt

    async def chat(
        self,
        message: str,
        system_prompt: str = "",
        params: Dict[str, Any] = {},
        images: List[str] = [],
    ) -> AsyncGenerator[ChatChunk, None]:
        try:
            system_prompt = self.__replace_prompt_params(system_prompt, params)

            if images and len(images) > 0:
                user_message = {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        *[
                            {
                                "type": "image_url",
                                "image_url": {"url": image},
                            }
                            for image in images
                        ],
                    ],
                }
            else:
                user_message = {
                    "role": "user",
                    "content": message,
                }

            messages: List[Dict[str, Any]] = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                user_message,
            ]

            messages_content = ""
            for message_item in messages:
                messages_content += (
                    f"# {message_item['role']}: \n{message_item['content']}\n\n"
                )

            if count_tokens(messages_content) > int(
                self.context_length or 128000
            ):
                raise Exception("messages length is too long")

            max_tokens = self.max_tokens

            request_body = {
                "model": self.model_name,
                "messages": messages,
                "stream": True,
                "max_tokens": max_tokens,
                "stream_options": {
                    "include_reasoning": True,
                    "include_usage": True,
                },
            }

            if self.options:
                request_body.update(self.options)

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer { self.api_key}",
            }

            yield StartChunk()

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                async with session.post(
                    self.api_base + "/chat/completions",
                    headers=headers,
                    json=request_body,
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )

                    content_cache = ""
                    reasoning_content_cache = ""

                    async for line in response.content:
                        if line:
                            line = line.decode("utf-8").strip()
                            if line.startswith("data: "):
                                data = line[6:]
                                
                                if data == "[DONE]":
                                    break

                                try:
                                    parsed = json.loads(data)
                                    content = ""
                                    reasoning_content = ""

                                    if parsed.get("choices") and parsed["choices"][0]:
                                        delta = parsed["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        reasoning_content = delta.get("reasoning_content", "")
                                        if content:
                                            content_cache += content   
                                            yield ContentChunk(content) 
                                        if reasoning_content:
                                            reasoning_content_cache += reasoning_content
                                            yield ReasoningChunk(content=reasoning_content)

                                    if parsed.get("usage"):

                                        usage = Usage()
                                        usage_data = parsed["usage"]

                                        if "prompt_tokens" in usage_data:
                                            usage.prompt_tokens = usage_data[
                                                "prompt_tokens"
                                            ]
                                        if "completion_tokens" in usage_data:
                                            usage.completion_tokens = usage_data[
                                                "completion_tokens"
                                            ]
                                        if "total_tokens" in usage_data:
                                            usage.total_tokens = usage_data[
                                                "total_tokens"
                                            ]

                                        if "completion_tokens_details" in usage_data:
                                            details = usage_data[
                                                "completion_tokens_details"
                                            ]
                                            if "reasoning_tokens" in details:
                                                usage.reasoning_tokens = details[
                                                    "reasoning_tokens"
                                                ]
                                            if "content_tokens" in details:
                                                usage.content_tokens = details[
                                                    "content_tokens"
                                                ]

                                        # deepseek
                                        if "prompt_cache_hit_tokens" in usage_data:
                                            usage.prompt_cache_hit_tokens = usage_data[
                                                "prompt_cache_hit_tokens"
                                            ]
                                        if "prompt_cache_miss_tokens" in usage_data:
                                            usage.prompt_cache_miss_tokens = usage_data[
                                                "prompt_cache_miss_tokens"
                                            ]

                                        # claude
                                        if "cache_creation_input_tokens" in usage_data:
                                            usage.cache_creation_input_tokens = (
                                                usage_data[
                                                    "cache_creation_input_tokens"
                                                ]
                                            )
                                        if "cache_read_input_tokens" in usage_data:
                                            usage.cache_read_input_tokens = usage_data[
                                                "cache_read_input_tokens"
                                            ]

                                        # openai
                                        if "prompt_tokens_details" in usage_data:
                                            details = usage_data[
                                                "prompt_tokens_details"
                                            ]
                                            if "cached_tokens" in details:
                                                usage.cached_tokens = details[
                                                    "cached_tokens"
                                                ]

                                        yield UsageChunk(usage=usage.to_dict())

                                except json.JSONDecodeError as e:
                                    raise e
                    yield CompletedChunk(
                        content=content_cache, reasoning_content=reasoning_content_cache
                    )
        except Exception as e:
            raise e
