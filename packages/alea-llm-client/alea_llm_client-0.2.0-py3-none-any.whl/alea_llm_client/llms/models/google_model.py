"""Google Vertex API implementation for the ALEA LLM client.

This module provides an implementation of the BaseAIModel for the Google Vertex API.
"""

# Standard library imports
import hashlib
import os
from pathlib import Path
from typing import Any, Callable, Optional, List, Dict

# packages
import httpx
from pydantic import BaseModel

# Local imports
from alea_llm_client.core.exceptions import ALEAModelError, ALEAAuthenticationError
from alea_llm_client.llms.models.base_ai_model import (
    BaseAIModel,
    ModelResponse,
    JSONModelResponse,
)


# default cache path if a custom path is not provided
DEFAULT_CACHE_PATH = Path.home() / ".alea" / "cache" / "gemini"
DEFAULT_KEY_PATH = Path.home() / ".alea" / "keys" / "gemini"


# set a default api key; do NOT prefix with sk for scanning false positives
DEFAULT_API_KEY = "key"

# set default timeouts
DEFAULT_TIMEOUT = 600


class GoogleModel(BaseAIModel):
    """
    Google model implementation for the ALEA LLM client.

    This module provides an implementation of the BaseAIModel for the Google Vertex API.
    """

    def __init__(
        self,
        model: str = "gemini-2.0-flash-exp",
        endpoint: str = "https://generativelanguage.googleapis.com",
        api_key: Optional[str] = None,
        formatter: Optional[Callable[[str], str]] = None,
        cache_path: Optional[Path] = DEFAULT_CACHE_PATH,
        **kwargs: Any,
    ):
        """
        Initialize the GoogleModel.

        Args:
            model (str): The model name.
            endpoint (str): The API endpoint (the full endpoint including project and location)
            api_key (str): The API key (access token for Vertex).
            formatter (Callable): The formatter function.
            cache_path (Path): The cache path.
            **kwargs: Additional keyword arguments.
        """
        # normalize the endpoint to ensure no trailing slash
        endpoint = endpoint.strip().rstrip("/")
        self.location_id = kwargs.get("location_id", "us-central1")
        self.project_id = kwargs.get(
            "project_id", "test-project"
        )  # Default for testing

        # append to the cache path if cache_path is provided
        if cache_path is not None:
            endpoint_hash = hashlib.blake2b(endpoint.encode()).hexdigest()
            model_hash = hashlib.blake2b(model.encode()).hexdigest()
            cache_path = cache_path / endpoint_hash / model_hash
            cache_path.mkdir(parents=True, exist_ok=True)

        # save the kwargs for later
        self.init_kwargs = kwargs.copy()
        self.init_kwargs.update(
            {
                "model": model,
                "endpoint": endpoint,
                "api_key": api_key,
                "formatter": formatter,
                "cache_path": cache_path,
            }
        )

        # initialize the model
        BaseAIModel.__init__(
            self,
            api_key=api_key,
            model=model,
            endpoint=endpoint,
            formatter=formatter,
            cache_path=cache_path,
            ignore_cache=kwargs.get("ignore_cache", False),
        )

    def get_api_key(self) -> str:
        """
        Get the API key.

        Returns:
            str: The API key.
        """
        # check if api_key is set
        api_key = self.init_kwargs.get("api_key", None)
        if api_key and api_key.strip():
            return api_key

        self.logger.debug("Attempting to get Gemini API key from environment variables")
        # Try GOOGLE_API_KEY first (more common), then VERTEX_API_KEY
        api_key = os.environ.get("GOOGLE_API_KEY", None)
        if api_key and api_key.strip():
            return api_key

        api_key = os.environ.get("VERTEX_API_KEY", None)
        if api_key and api_key.strip():
            return api_key

        # try to load from key path
        self.logger.debug("Attempting to get Gemini API key from key file")
        if DEFAULT_KEY_PATH.exists():
            api_key = DEFAULT_KEY_PATH.read_text().strip()
            if len(api_key) > 0:
                return api_key

        raise ValueError(
            "Gemini API key not found. Please set one of the following:\n"
            "1. Pass api_key parameter when initializing GoogleModel\n"
            "2. Set GOOGLE_API_KEY environment variable\n"
            "3. Set VERTEX_API_KEY environment variable\n"
            f"4. Create a key file at {DEFAULT_KEY_PATH}\n"
            "\nTo get an API key, visit: https://console.cloud.google.com/apis/credentials"
        )

    def _initialize_client(self) -> httpx.Client:
        """
        Initialize and return the HTTPX client.

        Returns:
            An instance of the HTTPX client.
        """
        self.logger.debug("Initializing httpx client")
        return httpx.Client(
            base_url=self.endpoint,
            http2=True,
            timeout=self.init_kwargs.get("timeout", DEFAULT_TIMEOUT),
        )

    def _initialize_async_client(self) -> httpx.AsyncClient:
        """
        Initialize and return the asynchronous HTTPX client.

        Returns:
            An instance of the asynchronous HTTPX client.
        """
        self.logger.debug("Initializing httpx async client")
        return httpx.AsyncClient(
            base_url=self.endpoint,
            http2=True,
            timeout=self.init_kwargs.get("timeout", DEFAULT_TIMEOUT),
        )

    def get_completion_endpoint(self) -> str:
        """
        Get the completion endpoint.

        Returns:
            str: The completion endpoint.
        """
        # Check if this is Vertex AI (aiplatform.googleapis.com) or Generative AI (generativelanguage.googleapis.com)
        if "aiplatform.googleapis.com" in self.endpoint:
            # Vertex AI format
            return (
                f"{self.endpoint}/v1/projects/{self.project_id}/locations/{self.location_id}"
                + f"/publishers/google/models/{self.model}:generateContent"
            )
        else:
            # Generative AI format
            return f"{self.endpoint}/v1beta/models/{self.model}:generateContent"

    def get_stream_endpoint(self) -> str:
        """
        Get the stream endpoint.

        Returns:
            str: The stream endpoint.
        """
        # Check if this is Vertex AI (aiplatform.googleapis.com) or Generative AI (generativelanguage.googleapis.com)
        if "aiplatform.googleapis.com" in self.endpoint:
            # Vertex AI format
            return (
                f"{self.endpoint}/v1/projects/{self.project_id}/locations/{self.location_id}"
                + f"/publishers/google/models/{self.model}:streamGenerateContent"
            )
        else:
            # Generative AI format
            return f"{self.endpoint}/v1beta/models/{self.model}:streamGenerateContent"

    def format(self, args: Any, kwargs: Any) -> List[Dict[str, str]]:
        """
        Format inputs or outputs using the specified formatter.

        Args:
            args: Positional arguments passed to the chat method.
            kwargs: Keyword arguments passed to the chat method.

        Returns:
            A list of formatted message dictionaries.

        Raises:
            ValueError: If no messages are provided for chat completion.
        """
        self.logger.debug("Formatting input for Google API")
        if self.formatter:
            return self.formatter(args, kwargs)

        messages = kwargs.pop("messages", None)
        if not messages:
            if len(args) > 0:
                messages = [{"role": "user", "parts": [{"text": args[0]}]}]
            else:
                self.logger.error("No messages provided for chat completion")
                raise ValueError("No messages provided for chat completion.")

        formatted_messages = []
        formatted_messages.extend(messages)

        self.logger.debug(f"Formatted messages: {formatted_messages}")
        return formatted_messages

    def _make_request(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """
        Make a request to the API.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the API.
        """
        # we must have a url to proceed
        url = kwargs.pop("url", args[0] if len(args) > 0 else None)
        if not url:
            raise ValueError(
                "No URL provided for request; must provide either as args[0] or url=... keyword arg."
            )

        # pop headers from kwargs
        headers = kwargs.pop("headers", {})

        # set Authorization based on API type
        if "Authorization" not in headers:
            if "aiplatform.googleapis.com" in self.endpoint:
                # Vertex AI uses Bearer token
                headers["Authorization"] = f"Bearer {self.get_api_key()}"
            # Generative AI uses API key as query parameter - add it to URL
            elif "generativelanguage.googleapis.com" in self.endpoint:
                if "?" in url:
                    url += f"&key={self.get_api_key()}"
                else:
                    url += f"?key={self.get_api_key()}"

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        self.logger.debug("Making request to the API")
        try:
            # make and raise here
            response = self.client.post(
                url,
                json={
                    **kwargs,
                },
                headers=headers,
            )

            # check for 400 to return the right ALEA error
            if response.status_code == 400:
                error_message = (
                    response.json().get("error", {}).get("message", response.json())
                )
                raise ALEAModelError(f"Model error: {error_message}")

            # check for 401 to return the right ALEA error
            if response.status_code == 401:
                error_message = (
                    response.json().get("error", {}).get("message", response.json())
                )
                raise ALEAAuthenticationError(f"Authentication error: {error_message}")

            # check for 404
            if response.status_code == 404:
                raise ALEAModelError(f"Model not found: {response.json()}")

            response.raise_for_status()
            return response
        except httpx.ConnectError as e:
            self.logger.error(f"Error connecting to the API: {str(e)}")
            raise ALEAModelError(f"Error connecting to the API: {str(e)}")
        except (ALEAModelError, ALEAAuthenticationError) as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error in request: {str(e)}")
            raise ALEAModelError(f"Error in request: {str(e)}") from e

    async def _make_request_async(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """
        Make an asynchronous request to the API.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the API.
        """
        # we must have a url to proceed
        url = kwargs.pop("url", args[0] if len(args) > 0 else None)
        if not url:
            raise ValueError(
                "No URL provided for request; must provide either as args[0] or url=... keyword arg."
            )

        # pop headers from kwargs
        headers = kwargs.pop("headers", {})

        # set Authorization based on API type
        if "Authorization" not in headers:
            if "aiplatform.googleapis.com" in self.endpoint:
                # Vertex AI uses Bearer token
                headers["Authorization"] = f"Bearer {self.get_api_key()}"
            # Generative AI uses API key as query parameter - add it to URL
            elif "generativelanguage.googleapis.com" in self.endpoint:
                if "?" in url:
                    url += f"&key={self.get_api_key()}"
                else:
                    url += f"?key={self.get_api_key()}"

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        self.logger.debug("Making asynchronous request to the API")
        try:
            # make and raise here
            response = await self.async_client.post(
                url,
                json={
                    **kwargs,
                },
                headers=headers,
            )

            # check for 400 to return the right ALEA error
            if response.status_code == 400:
                error_message = (
                    response.json().get("error", {}).get("message", response.json())
                )
                raise ALEAModelError(f"Model error: {error_message}")

            # check for 401 to return the right ALEA error
            if response.status_code == 401:
                error_message = (
                    response.json().get("error", {}).get("message", response.json())
                )
                raise ALEAAuthenticationError(f"Authentication error: {error_message}")

            # check for 404
            if response.status_code == 404:
                raise ALEAModelError(f"Model not found: {response.json()}")

            response.raise_for_status()
            return response
        except httpx.ConnectError as e:
            self.logger.error(f"Error connecting to the API: {str(e)}")
            raise ALEAModelError(f"Error connecting to the API: {str(e)}")
        except (ALEAModelError, ALEAAuthenticationError) as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error in asynchronous request: {str(e)}")
            raise ALEAModelError(f"Error in asynchronous request: {str(e)}") from e

    @staticmethod
    def _get_complete_choices(response_data: dict) -> List[str | dict]:
        """
        Get the response choices from the response data.

        Args:
            response_data: The response data.

        Returns:
            The response choices.
        """
        return [
            candidate.get("content", {}).get("parts", [])[0].get("text", "")
            for candidate in response_data.get("candidates", [])
        ]

    @staticmethod
    def _get_chat_choices(response_data: dict) -> List[str | dict]:
        """
        Get the chat response choices from the response data.

        Args:
            response_data: The response data.

        Returns:
            The response choices.
        """
        return [
            candidate.get("content", {}).get("parts", [])[0].get("text", "")
            for candidate in response_data.get("candidates", [])
        ]

    def _handle_complete_response(self, response: httpx.Response) -> ModelResponse:
        """
        Handle the response from the completion.

        Args:
            response: The response from the completion.

        Returns:
            The model response from the completion.
        """
        self.logger.debug("Handling completion response")
        response_data = response.json()
        choices = self._get_complete_choices(response_data)
        model_response = ModelResponse(
            choices=choices,
            metadata={
                "model": self.model,
                "usage": response_data.get("usageMetadata", {}),
            },
            text=choices[0] if len(choices) > 0 else "",
        )
        self.logger.debug(f"Model response: {model_response}")
        return model_response

    def _complete(self, *args: Any, **kwargs: Any) -> ModelResponse:
        """
        Synchronous completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the completion.
        """
        self.logger.debug("Initiating synchronous completion")
        prompt = kwargs.pop("prompt", None) or (args[0] if len(args) > 0 else None)
        if not prompt:
            raise ValueError("No prompt provided for completion.")
        return self._handle_complete_response(
            self._make_request(
                url=self.get_completion_endpoint(),
                contents=self.format(args, kwargs),
                **kwargs,
            )
        )

    async def _complete_async(self, *args: Any, **kwargs: Any) -> ModelResponse:
        """
        Asynchronous completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the completion.
        """
        self.logger.debug("Initiating asynchronous completion")
        prompt = kwargs.pop("prompt", None) or (args[0] if len(args) > 0 else None)
        if not prompt:
            raise ValueError("No prompt provided for completion.")
        return self._handle_complete_response(
            await self._make_request_async(
                url=self.get_completion_endpoint(),
                contents=self.format(args, kwargs),
                **kwargs,
            )
        )

    def _handle_chat_response(self, response: httpx.Response) -> ModelResponse:
        """
        Handle the response from the chat completion.

        Args:
            response: The response from the chat completion.

        Returns:
            The model response from the chat completion.
        """
        self.logger.debug("Handling chat response")
        response_data = response.json()
        choices = self._get_chat_choices(response_data)
        model_response = ModelResponse(
            choices=choices,
            metadata={
                "model": self.model,
                "usage": response_data.get("usageMetadata", {}),
            },
            text=choices[0] if len(choices) > 0 else "",
        )
        self.logger.debug(f"Model response: {model_response}")
        return model_response

    def _chat(self, *args: Any, **kwargs: Any) -> ModelResponse:
        """
        Synchronous chat completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the chat completion.
        """
        self.logger.debug("Initiating synchronous chat completion")
        return self._handle_chat_response(
            self._make_request(
                url=self.get_completion_endpoint(),
                contents=self.format(args, kwargs),
                **kwargs,
            )
        )

    async def _chat_async(self, *args: Any, **kwargs: Any) -> ModelResponse:
        """
        Asynchronous chat completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the chat completion.
        """
        self.logger.debug("Initiating asynchronous chat completion")
        messages = self.format(args, kwargs)
        return self._handle_chat_response(
            await self._make_request_async(
                url=self.get_completion_endpoint(),
                contents=messages,
                **kwargs,
            )
        )

    def _handle_json_response(self, response: httpx.Response) -> JSONModelResponse:
        """
        Handle the response from the JSON completion.

        Args:
            response: The response from the JSON completion.

        Returns:
            The JSON response from the JSON completion.
        """
        self.logger.debug("Handling JSON response")

        # get response and raw response choice output
        response_data = response.json()
        choices = self._get_chat_choices(response_data)
        try:
            raw_json = choices[0]
        except IndexError:
            raw_json = "{}"
        json_data = self.parse_json(raw_json)
        json_model_response = JSONModelResponse(
            choices=choices,
            metadata={
                "model": self.model,
                "usage": response_data.get("usageMetadata", {}),
            },
            text=raw_json,
            data=json_data,
        )
        self.logger.debug(f"JSON model response: {json_model_response}")
        return json_model_response

    def _json(self, *args: Any, **kwargs: Any) -> JSONModelResponse:
        """
        Synchronous JSON completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The JSON response from the completion.
        """
        self.logger.debug("Initiating synchronous JSON completion")
        kwargs.pop("completion", False)

        response = self._make_request(
            url=self.get_completion_endpoint(),
            contents=self.format(args, kwargs),
            **kwargs,
        )

        return self._handle_json_response(response)

    async def _json_async(self, *args: Any, **kwargs: Any) -> JSONModelResponse:
        """
        Asynchronous JSON completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The JSON response from the completion.
        """
        self.logger.debug("Initiating asynchronous JSON completion")

        return self._handle_json_response(
            await self._make_request_async(
                url=self.get_completion_endpoint(),
                contents=self.format(args, kwargs),
                **kwargs,
            )
        )

    def _handle_pydantic_response(
        self, response: httpx.Response, pydantic_model: BaseModel
    ) -> BaseModel:
        """
        Handle the response from the Pydantic completion.

        Args:
            response: The response from the Pydantic completion.
            pydantic_model: The Pydantic model to validate the response.

        Returns:
            The Pydantic model response from the Pydantic completion.
        """
        self.logger.debug("Handling Pydantic response")

        # get response and raw response choice output
        response_data = response.json()
        choices = self._get_chat_choices(response_data)
        try:
            raw_json = choices[0]
        except IndexError:
            raw_json = "{}"
        json_data = self.parse_json(raw_json)
        pydantic_response = pydantic_model.model_validate(json_data)
        self.logger.debug("Pydantic completion successful")
        return pydantic_response

    def _pydantic(self, *args: Any, **kwargs: Any) -> BaseModel:
        """
        Synchronous Pydantic completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The Pydantic model response from the completion.

        Raises:
            ValueError: If Pydantic model is not provided.
        """
        self.logger.debug("Initiating synchronous Pydantic completion")

        # pydantic model with result field
        pydantic_model: Optional[BaseModel] = kwargs.pop("pydantic_model", None)
        if not pydantic_model:
            raise ValueError("Pydantic model not provided for Pydantic completion.")

        # get the response
        return self._handle_pydantic_response(
            self._make_request(
                url=self.get_completion_endpoint(),
                contents=self.format(args, kwargs),
                **kwargs,
            ),
            pydantic_model,
        )

    async def _pydantic_async(self, *args: Any, **kwargs: Any) -> BaseModel:
        """
        Asynchronous Pydantic completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The Pydantic model response from the completion.

        Raises:
            ValueError: If Pydantic model is not provided.
        """
        self.logger.debug("Initiating asynchronous Pydantic completion")

        # pydantic model with result field
        pydantic_model: Optional[BaseModel] = kwargs.pop("pydantic_model", None)
        if not pydantic_model:
            raise ValueError("Pydantic model not provided for Pydantic completion.")

        # get the response
        kwargs.pop("completion", False)
        return self._handle_pydantic_response(
            await self._make_request_async(
                url=self.get_completion_endpoint(),
                contents=self.format(args, kwargs),
                **kwargs,
            ),
            pydantic_model,
        )

    def _responses(self, *args: Any, **kwargs: Any) -> ModelResponse:
        """
        Synchronous responses completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the responses completion.
        """
        self.logger.debug("Initiating synchronous responses completion")
        # For Google AI, responses completion is the same as chat completion
        return self._chat(*args, **kwargs)

    async def _responses_async(self, *args: Any, **kwargs: Any) -> ModelResponse:
        """
        Asynchronous responses completion method.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the responses completion.
        """
        self.logger.debug("Initiating asynchronous responses completion")
        # For Google AI, responses completion is the same as chat completion
        return await self._chat_async(*args, **kwargs)
