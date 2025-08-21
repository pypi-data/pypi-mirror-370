"""OpenAI model implementation for the LLM.

This module provides an implementation of the BaseAIModel for OpenAI's API.
It includes classes and methods for both synchronous and asynchronous chat
and JSON completions using OpenAI's language models.
"""

# Standard library imports
from pathlib import Path
from typing import Any, Callable, Optional

import httpx
from pydantic import BaseModel

# project imports
from alea_llm_client.core.logging import LoggerMixin
from alea_llm_client.llms.models.base_ai_model import (
    JSONModelResponse,
    ModelResponse,
)
from alea_llm_client.llms.models.openai_compatible_model import OpenAICompatibleModel
from alea_llm_client.llms.utils.api_keys import get_openai_api_key

DEFAULT_ENDPOINT = "https://api.openai.com/"
DEFAULT_CACHE_PATH = Path.home() / ".alea" / "cache" / "openai"


class OpenAIModel(OpenAICompatibleModel, LoggerMixin):
    """
    OpenAI model implementation.

    This class implements the BaseAIModel for OpenAI's API, providing methods
    for both synchronous and asynchronous chat and JSON completions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-5-chat-latest",
        endpoint: str = DEFAULT_ENDPOINT,
        formatter: Optional[Callable] = None,
        cache_path: Optional[Path] = DEFAULT_CACHE_PATH,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the OpenAIModel.

        Args:
            api_key: The API key for OpenAI. If None, it will be retrieved from environment variables.
            model: The name of the OpenAI model to use.
            endpoint: The API endpoint URL (if different from default).
            formatter: A function to format input messages.
            cache_path: The path to the cache directory for storing model responses.
        """
        OpenAICompatibleModel.__init__(
            self,
            api_key=api_key,
            model=model,
            endpoint=endpoint,
            formatter=formatter,
            cache_path=cache_path,
            **kwargs,
        )
        self.logger.info(f"Initialized OpenAIModel with model: {model} and endpoint: {endpoint}")

    def get_api_key(self) -> str:
        """
        Retrieve the API key for OpenAI from the environment.

        Returns:
            The OpenAI API key.

        Raises:
            ValueError: If the OPENAI_API_KEY is not found in environment variables.
        """
        return get_openai_api_key(self.init_kwargs)

    def _json(self, *args: Any, **kwargs: Any) -> JSONModelResponse:
        """
        Perform a JSON completion with the OpenAI model.

        Args:
            *args: The input arguments to pass to the model.
            **kwargs: The input keyword arguments to pass to the model.

        Returns:
            JSONModelResponse: The response from the model.
        """
        # add response_format to kwargs and call super method
        kwargs["response_format"] = {"type": "json_object"}
        return super()._json(*args, **kwargs)

    async def _json_async(self, *args: Any, **kwargs: Any) -> JSONModelResponse:
        """
        Perform an asynchronous JSON completion with the OpenAI model.

        Args:
            *args: The input arguments to pass to the model.
            **kwargs: The input keyword arguments to pass to the model.

        Returns:
            JSONModelResponse: The response from the model.
        """
        # add response_format to kwargs and call super method
        kwargs["response_format"] = {"type": "json_object"}
        return await super()._json_async(*args, **kwargs)

    def _pydantic(self, *args: Any, **kwargs: Any) -> BaseModel:
        """
        Perform a Pydantic completion with the OpenAI model.

        Args:
            *args: The input arguments to pass to the model.
            **kwargs: The input keyword arguments to pass to the model.

        Returns:
            BaseModel: The response from the model.
        """
        # add response_format to kwargs and call super method
        kwargs["response_format"] = {"type": "json_object"}
        return super()._pydantic(*args, **kwargs)

    async def _pydantic_async(self, *args: Any, **kwargs: Any) -> BaseModel:
        """
        Perform an asynchronous Pydantic completion with the OpenAI model.

        Args:
            *args: The input arguments to pass to the model.
            **kwargs: The input keyword arguments to pass to the model.

        Returns:
            BaseModel: The response from the model.
        """
        # add response_format to kwargs and call super method
        kwargs["response_format"] = {"type": "json_object"}
        return await super()._pydantic_async(*args, **kwargs)

    def _handle_chat_response(self, response: httpx.Response) -> ModelResponse:
        """
        Handle the response from the chat completion.
        Enhanced to extract reasoning tokens for o-series models.

        Args:
            response: The response from the chat completion.

        Returns:
            The model response with reasoning tokens populated for o-series models.
        """
        self.logger.debug("Handling OpenAI chat response")
        response_data = response.json()
        choices = self._get_chat_choices(response_data)

        # Extract usage information and check for reasoning tokens (o-series models)
        usage = response_data.get("usage", {})
        reasoning_tokens = usage.get("reasoning_tokens")

        model_response = ModelResponse(
            choices=choices,
            metadata={"model": self.model, "usage": usage},
            text=choices[0] if len(choices) > 0 else "",
            reasoning_tokens=reasoning_tokens,
        )

        if reasoning_tokens:
            self.logger.debug(f"OpenAI model response used {reasoning_tokens} reasoning tokens")

        return model_response
