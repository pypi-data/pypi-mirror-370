import json
import os
import warnings
from typing import Dict, List, Optional

from openai import OpenAI

from memory.llms.base import LLMBase
from memory.configs.llms.base import BaseLlmConfig


class SoikastackLLMConfig(BaseLlmConfig):
    def __init__(
        self,
        model: str = "llama3.3",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        api_key: Optional[str] = None,
        soikastack_base_url: Optional[str] = None,
    ):
        super().__init__()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.api_key = api_key
        self.soikastack_base_url = soikastack_base_url


class SoikaStackLLM(LLMBase):
    def __init__(self, config: Optional[BaseLlmConfig] = None):
        super().__init__(config)

        if not self.config:
            self.config = SoikastackLLMConfig()

        api_key = self.config.api_key or os.getenv("SOIKASTACK_API_KEY")
        if not api_key:
            raise ValueError("Soikastack API key not provided. Please provide it in config or set SOIKASTACK_API_KEY environment variable.")

        base_url = (
            self.config.soikastack_base_url
            or os.getenv("SOIKASTACK_API_BASE_URL")
            or "https://localhost:4141/v1"
        )

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _parse_response(self, response, tools):
        """
        Process the response based on whether tools are used or not.

        Args:
            response: The raw response from API.
            tools: The list of tools provided in the request.

        Returns:
            str or dict: The processed response.
        """
        if tools:
            processed_response = {
                "content": response.choices[0].message.content,
                "tool_calls": [],
            }
            # Check if tool_calls exists and is not None
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    processed_response["tool_calls"].append(
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": tool_call.function,
                        }
                    )
            return processed_response
        else:
            return response.choices[0].message.content
        
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
    ):
        """
        Generate a JSON response based on the given messages using OpenAI.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.
            response_format (str or object, optional): Format of the response. Defaults to "text".
            tools (list, optional): List of tools that the model can call. Defaults to None.
            tool_choice (str, optional): Tool choice method. Defaults to "auto".

        Returns:
            json: The generated response.
        """
        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
        }

        if response_format:
            params["response_format"] = response_format
        if tools:  # TODO: Remove tools if no issues found with new memory addition logic
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**params)
        return self._parse_response(response, tools)
