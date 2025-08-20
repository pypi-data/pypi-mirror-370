"""
IndoxRouter Client Module

This module provides a client for interacting with the IndoxRouter API, which serves as a unified
interface to multiple AI providers and models. The client handles authentication, rate limiting,
error handling, and provides a standardized response format across different AI services.

IMPORTANT: The IndoxRouter server now supports only cookie-based authentication. This client
automatically handles authentication by exchanging your API key for a JWT token through the login endpoint.

The Client class offers methods for:
- Authentication and session management
- Making API requests with automatic token refresh
- Accessing AI capabilities: chat completions, text completions, embeddings, image generation, and text-to-speech
- Retrieving information about available providers and models
- Monitoring usage statistics and credit consumption

Usage example:
    ```python
    from indoxRouter import Client

    # Initialize client with API key
    client = Client(api_key="your_api_key")

    # Get available models
    models = client.models()

    # Generate a chat completion
    response = client.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ], model="openai/gpt-4o-mini")

    # Generate text embeddings
    embeddings = client.embeddings("This is a sample text", model="openai/text-embedding-ada-002")

    # Generate text-to-speech audio
    audio = client.text_to_speech("Hello, welcome to IndoxRouter!", model="openai/tts-1", voice="alloy")

    # Clean up resources when done
    client.close()
    ```

The client can also be used as a context manager:
    ```python
    with Client(api_key="your_api_key") as client:
        response = client.chat([{"role": "user", "content": "Hello!"}], model="openai/gpt-4o-mini")
    ```
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import requests
import json

from .exceptions import (
    AuthenticationError,
    NetworkError,
    ProviderNotFoundError,
    ModelNotFoundError,
    ModelNotAvailableError,
    InvalidParametersError,
    RateLimitError,
    ProviderError,
    RequestError,
    InsufficientCreditsError,
    ValidationError,
    APIError,
)
from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_IMAGE_MODEL,
    DEFAULT_TTS_MODEL,
    CHAT_ENDPOINT,
    COMPLETION_ENDPOINT,
    EMBEDDING_ENDPOINT,
    IMAGE_ENDPOINT,
    TTS_ENDPOINT,
    MODEL_ENDPOINT,
    USAGE_ENDPOINT,
    USE_COOKIES,
)

logger = logging.getLogger(__name__)


class Client:
    """
    Client for interacting with the IndoxRouter API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the client.

        Args:
            api_key: API key for authentication. If not provided, the client will look for the
                INDOX_ROUTER_API_KEY environment variable.
            timeout: Request timeout in seconds.
            base_url: Base URL for the API. If not provided, the client will use the default URL.
        """

        use_cookies = USE_COOKIES
        self.api_key = api_key or os.environ.get("INDOX_ROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as an argument or as the INDOX_ROUTER_API_KEY environment variable."
            )

        self.base_url = base_url if base_url is not None else DEFAULT_BASE_URL

        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")

        self.timeout = timeout
        self.use_cookies = use_cookies
        self.session = requests.Session()

        # Authenticate and get JWT tokens
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with the server and get JWT tokens.
        This uses the /auth/token endpoint to get JWT tokens using the API key.
        """
        try:
            # First try with the dedicated API key endpoint
            logger.debug("Authenticating with dedicated API key endpoint")
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/api-key",
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout,
            )

            if response.status_code != 200:
                # If dedicated endpoint fails, try using the API key as a username
                logger.debug("API key endpoint failed, trying with API key as username")
                response = self.session.post(
                    f"{self.base_url}/api/v1/auth/token",
                    data={
                        "username": self.api_key,
                        "password": self.api_key,  # Try using API key as both username and password
                    },
                    timeout=self.timeout,
                )

                if response.status_code != 200:
                    # Try one more method - the token endpoint with different format
                    logger.debug("Trying with API key as token parameter")
                    response = self.session.post(
                        f"{self.base_url}/api/v1/auth/token",
                        data={
                            "username": "pip_client",
                            "password": self.api_key,
                        },
                        timeout=self.timeout,
                    )

            if response.status_code != 200:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"detail": response.text}

                raise AuthenticationError(
                    f"Authentication failed: {error_data.get('detail', 'Unknown error')}"
                )

            # Check if we have a token in the response body
            try:
                response_data = response.json()
                if "access_token" in response_data:
                    # Store token in the session object for later use
                    self.access_token = response_data["access_token"]
                    logger.debug("Retrieved access token from response body")
            except:
                # If we couldn't parse JSON, that's fine - we'll rely on cookies
                logger.debug("No token found in response body, will rely on cookies")

            # At this point, the cookies should be set in the session
            logger.debug("Authentication successful")

            # Check if we have the cookies we need
            if "access_token" not in self.session.cookies:
                logger.warning(
                    "Authentication succeeded but no access_token cookie was set"
                )

        except requests.RequestException as e:
            logger.error(f"Authentication request failed: {str(e)}")
            raise NetworkError(f"Network error during authentication: {str(e)}")

    def _get_domain(self):
        """
        Extract domain from the base URL for cookie setting.
        """
        try:
            from urllib.parse import urlparse

            parsed_url = urlparse(self.base_url)
            return parsed_url.netloc
        except Exception:
            # If parsing fails, return a default value
            return ""

    def enable_debug(self, level=logging.DEBUG):
        """
        Enable debug logging for the client.

        Args:
            level: Logging level (default: logging.DEBUG)
        """
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.debug("Debug logging enabled")

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Any:
        """
        Make a request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            stream: Whether to stream the response

        Returns:
            Response data
        """
        # Add API version prefix if not already present
        if not endpoint.startswith("api/v1/") and not endpoint.startswith("/api/v1/"):
            endpoint = f"api/v1/{endpoint}"

        # Remove any leading slash for consistent URL construction
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        # Add Authorization header if we have an access token
        if hasattr(self, "access_token") and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        # logger.debug(f"Making {method} request to {url}")
        # if data:
        #     logger.debug(f"Request data: {json.dumps(data, indent=2)}")

        # Diagnose potential issues with the request
        if method == "POST" and data:
            diagnosis = self.diagnose_request(endpoint, data)
            if not diagnosis["is_valid"]:
                issues_str = "\n".join([f"- {issue}" for issue in diagnosis["issues"]])
                logger.warning(f"Request validation issues:\n{issues_str}")
                # We'll still send the request, but log the issues

        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                json=data,
                timeout=self.timeout,
                stream=stream,
            )

            if stream:
                return response

            # Check if we need to reauthenticate (401 Unauthorized)
            if response.status_code == 401:
                logger.debug("Received 401, attempting to reauthenticate")
                self._authenticate()

                # Update Authorization header with new token if available
                if hasattr(self, "access_token") and self.access_token:
                    headers["Authorization"] = f"Bearer {self.access_token}"

                # Retry the request after reauthentication
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout,
                    stream=stream,
                )

                if stream:
                    return response

            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
                logger.error(f"HTTP error response: {json.dumps(error_data, indent=2)}")
            except (ValueError, AttributeError):
                error_data = {"detail": str(e)}
                logger.error(f"HTTP error (no JSON response): {str(e)}")

            status_code = getattr(e.response, "status_code", 500)
            error_message = error_data.get("detail", str(e))

            if status_code == 401:
                raise AuthenticationError(f"Authentication failed: {error_message}")
            elif status_code == 404:
                if "provider" in error_message.lower():
                    raise ProviderNotFoundError(error_message)
                elif "model" in error_message.lower():
                    # Check if it's a model not found vs model not available
                    if (
                        "not supported" in error_message.lower()
                        or "disabled" in error_message.lower()
                        or "unavailable" in error_message.lower()
                    ):
                        raise ModelNotAvailableError(error_message)
                    else:
                        raise ModelNotFoundError(error_message)
                else:
                    raise APIError(f"Resource not found: {error_message} (URL: {url})")
            elif status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {error_message}")
            elif status_code == 400:
                # Check if it's a validation error or invalid parameters
                if (
                    "validation" in error_message.lower()
                    or "invalid format" in error_message.lower()
                ):
                    raise ValidationError(f"Request validation failed: {error_message}")
                else:
                    raise InvalidParametersError(f"Invalid parameters: {error_message}")
            elif status_code == 402:
                raise InsufficientCreditsError(f"Insufficient credits: {error_message}")
            elif status_code == 422:
                # Unprocessable Entity - typically validation errors
                raise ValidationError(f"Request validation failed: {error_message}")
            elif status_code == 503:
                # Service Unavailable - model might be temporarily unavailable
                if "model" in error_message.lower():
                    raise ModelNotAvailableError(
                        f"Model temporarily unavailable: {error_message}"
                    )
                else:
                    raise APIError(f"Service unavailable: {error_message}")
            elif status_code == 500:
                # Provide more detailed information for server errors
                error_detail = error_data.get("detail", "No details provided")
                # Include the request data in the error message for better debugging
                request_data_str = json.dumps(data, indent=2) if data else "None"
                raise RequestError(
                    f"Server error (500): {error_detail}. URL: {url}.\n"
                    f"Request data: {request_data_str}\n"
                    f"This may indicate an issue with the server configuration or a problem with the provider service."
                )
            elif status_code >= 400 and status_code < 500:
                # Client errors
                raise APIError(f"Client error ({status_code}): {error_message}")
            else:
                # Server errors
                raise RequestError(f"Server error ({status_code}): {error_message}")
        except requests.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise NetworkError(f"Network error: {str(e)}")

    def _format_model_string(self, model: str) -> str:
        """
        Format the model string in a way that the server expects.

        The server might be expecting a different format than "provider/model".
        This method handles different formatting requirements.

        Args:
            model: Model string in the format "provider/model"

        Returns:
            Formatted model string
        """
        if not model or "/" not in model:
            return model

        # The standard format is "provider/model"
        # But the server might be expecting something different
        provider, model_name = model.split("/", 1)

        # For now, return the original format as it seems the server
        # is having issues with JSON formatted model strings
        return model

    def _format_image_size_for_provider(
        self, size: str, provider: str, model: str
    ) -> str:
        """
        Format the image size parameter based on the provider's requirements.

        Google requires aspect ratios like "1:1", "4:3", etc. while OpenAI uses pixel dimensions
        like "1024x1024", "512x512", etc.

        Args:
            size: The size parameter (e.g., "1024x1024")
            provider: The provider name (e.g., "google", "openai")
            model: The model name

        Returns:
            Formatted size parameter appropriate for the provider
        """
        if provider.lower() == "google":
            # Google uses aspect ratios instead of pixel dimensions
            # Convert common pixel dimensions to aspect ratios
            size_to_aspect_ratio = {
                "1024x1024": "1:1",
                "512x512": "1:1",
                "256x256": "1:1",
                "1024x768": "4:3",
                "768x1024": "3:4",
                "1024x1536": "2:3",
                "1536x1024": "3:2",
                "1792x1024": "16:9",
                "1024x1792": "9:16",
            }

            # Check if size is already in aspect ratio format (contains a colon)
            if ":" in size:
                return size

            # Convert to aspect ratio if we have a mapping, otherwise use default 1:1
            return size_to_aspect_ratio.get(size, "1:1")

        # For other providers, return the original size
        return size

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion.

        Args:
            messages: List of messages in the conversation
            model: Model to use in the format "provider/model" (e.g., "openai/gpt-4o-mini")
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        data = {
            "messages": messages,
            "model": formatted_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "additional_params": filtered_kwargs,
        }

        if stream:
            response = self._request("POST", CHAT_ENDPOINT, data, stream=True)
            return self._handle_streaming_response(response)
        else:
            return self._request("POST", CHAT_ENDPOINT, data)

    def completion(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a text completion.

        Args:
            prompt: Text prompt
            model: Model to use in the format "provider/model" (e.g., "openai/gpt-4o-mini")
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        data = {
            "prompt": prompt,
            "model": formatted_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "additional_params": filtered_kwargs,
        }

        if stream:
            response = self._request("POST", COMPLETION_ENDPOINT, data, stream=True)
            return self._handle_streaming_response(response)
        else:
            return self._request("POST", COMPLETION_ENDPOINT, data)

    def embeddings(
        self,
        text: Union[str, List[str]],
        model: str = DEFAULT_EMBEDDING_MODEL,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate embeddings for text.

        Args:
            text: Text to embed (string or list of strings)
            model: Model to use in the format "provider/model" (e.g., "openai/text-embedding-ada-002")
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data with embeddings
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        data = {
            "text": text if isinstance(text, list) else [text],
            "model": formatted_model,
            "additional_params": filtered_kwargs,
        }

        return self._request("POST", EMBEDDING_ENDPOINT, data)

    def images(
        self,
        prompt: str,
        model: str = DEFAULT_IMAGE_MODEL,
        size: Optional[str] = None,
        n: Optional[int] = None,
        quality: Optional[str] = None,
        style: Optional[str] = None,
        # Standard parameters
        response_format: Optional[str] = None,
        user: Optional[str] = None,
        # OpenAI-specific parameters
        background: Optional[str] = None,
        moderation: Optional[str] = None,
        output_compression: Optional[int] = None,
        output_format: Optional[str] = None,
        # Google-specific parameters
        negative_prompt: Optional[str] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
        safety_filter_level: Optional[str] = None,
        person_generation: Optional[str] = None,
        include_safety_attributes: Optional[bool] = None,
        include_rai_reason: Optional[bool] = None,
        language: Optional[str] = None,
        output_mime_type: Optional[str] = None,
        add_watermark: Optional[bool] = None,
        enhance_prompt: Optional[bool] = None,
        # Google-specific direct parameters
        aspect_ratio: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate images from a prompt.

        Args:
            prompt: Text prompt
            model: Model to use in the format "provider/model" (e.g., "openai/dall-e-3", "google/imagen-3.0-generate-002")

            # Provider-specific parameters - will only be included if explicitly provided
            # Note: Different providers support different parameters
            size: Image size - For OpenAI: "1024x1024", "512x512", etc. For Google: use aspect_ratio instead
            n: Number of images to generate
            quality: Image quality (e.g., "standard", "hd") - supported by some providers
            style: Image style (e.g., "vivid", "natural") - supported by some providers

            # Standard parameters
            response_format: Format of the response - "url" or "b64_json"
            user: A unique identifier for the end-user

            # OpenAI-specific parameters
            background: Background style - "transparent", "opaque", or "auto"
            moderation: Moderation level - "low" or "auto"
            output_compression: Compression quality for output images (0-100)
            output_format: Output format - "png", "jpeg", or "webp"

            # Google-specific parameters
            negative_prompt: Description of what to discourage in the generated images
            guidance_scale: Controls how much the model adheres to the prompt
            seed: Random seed for image generation
            safety_filter_level: Filter level for safety filtering
            person_generation: Controls generation of people ("dont_allow", "allow_adult", "allow_all")
            include_safety_attributes: Whether to report safety scores of generated images
            include_rai_reason: Whether to include filter reason if the image is filtered
            language: Language of the text in the prompt
            output_mime_type: MIME type of the generated image
            add_watermark: Whether to add a watermark to the generated images
            enhance_prompt: Whether to use prompt rewriting logic
            aspect_ratio: Aspect ratio for Google models (e.g., "1:1", "16:9") - preferred over size

            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data with image URLs
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Extract provider and model name from model string if present
        provider = "openai"  # Default provider
        model_name = model
        if "/" in model:
            provider, model_name = model.split("/", 1)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        # Create the base request data with only the required parameters
        data = {
            "prompt": prompt,
            "model": formatted_model,
        }

        # Add optional parameters only if they are explicitly provided
        if n is not None:
            data["n"] = n

        # Handle size/aspect_ratio parameters based on provider
        if provider.lower() == "google":
            # For Google, use aspect_ratio instead of size
            if aspect_ratio is not None:
                # Google's imagen-3 has specific supported aspect ratios
                if model_name == "imagen-3.0-generate-002" and aspect_ratio not in [
                    "1:1",
                    "3:4",
                    "4:3",
                    "9:16",
                    "16:9",
                ]:
                    aspect_ratio = "1:1"  # Default to 1:1 if not supported
                data["aspect_ratio"] = aspect_ratio
            elif size is not None:
                # Convert size to aspect_ratio
                formatted_size = self._format_image_size_for_provider(
                    size, provider, model_name
                )
                data["aspect_ratio"] = formatted_size
            else:
                # Default aspect_ratio for Google
                data["aspect_ratio"] = "1:1"
        elif provider.lower() == "xai":
            # xAI doesn't support size parameter - do not include it
            pass
        elif size is not None and provider.lower() != "xai":
            # For other providers (like OpenAI), use size as is
            data["size"] = size

        if quality is not None:
            data["quality"] = quality
        if style is not None:
            data["style"] = style

        # Add standard parameters if provided
        if response_format is not None:
            # Only add response_format if explicitly provided by the user
            data["response_format"] = response_format

        if user is not None:
            data["user"] = user

        # Add OpenAI-specific parameters if provided
        if background is not None:
            data["background"] = background
        if moderation is not None:
            data["moderation"] = moderation
        if output_compression is not None:
            data["output_compression"] = output_compression
        if output_format is not None:
            data["output_format"] = output_format

        # Add Google-specific parameters if provided
        if negative_prompt is not None:
            data["negative_prompt"] = negative_prompt
        if guidance_scale is not None:
            data["guidance_scale"] = guidance_scale
        if seed is not None:
            data["seed"] = seed
        if safety_filter_level is not None:
            data["safety_filter_level"] = safety_filter_level
        if person_generation is not None:
            data["person_generation"] = person_generation
        if include_safety_attributes is not None:
            data["include_safety_attributes"] = include_safety_attributes
        if include_rai_reason is not None:
            data["include_rai_reason"] = include_rai_reason
        if language is not None:
            data["language"] = language
        if output_mime_type is not None:
            data["output_mime_type"] = output_mime_type
        if add_watermark is not None:
            data["add_watermark"] = add_watermark
        if enhance_prompt is not None:
            data["enhance_prompt"] = enhance_prompt

        # Add any remaining parameters
        if filtered_kwargs:
            data["additional_params"] = filtered_kwargs

        # Special case handling for specific models and providers
        # Only include parameters supported by each model based on their JSON definitions
        if provider.lower() == "openai" and "gpt-image" in model_name.lower():
            # For OpenAI's gpt-image models, don't automatically add response_format
            if "response_format" in data and response_format is None:
                del data["response_format"]

        if provider.lower() == "xai" and "grok-2-image" in model_name.lower():
            # For xAI's grok-2-image models, ensure size is not included
            if "size" in data:
                del data["size"]

        # Clean up any parameters that shouldn't be sent to specific providers
        # This ensures we only send parameters that each provider supports
        supported_params = self._get_supported_parameters_for_model(
            provider, model_name
        )
        if supported_params:
            for param in list(data.keys()):
                if param not in ["prompt", "model"] and param not in supported_params:
                    del data[param]

        return self._request("POST", IMAGE_ENDPOINT, data)

    def text_to_speech(
        self,
        input: str,
        model: str = DEFAULT_TTS_MODEL,
        voice: Optional[str] = None,
        response_format: Optional[str] = None,
        speed: Optional[float] = None,
        instructions: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate audio from text using text-to-speech models.

        Args:
            input: The text to generate audio for
            model: Model to use in the format "provider/model" (e.g., "openai/tts-1")
            voice: Voice to use for the audio generation (provider-specific)
            response_format: Format of the audio response (e.g., "mp3", "opus", "aac", "flac")
            speed: Speed of the generated audio (0.25 to 4.0)
            instructions: Optional instructions for the TTS generation
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response data with audio content

        Examples:
            Basic usage:
                response = client.text_to_speech("Hello, world!")

            With specific voice and format:
                response = client.text_to_speech(
                    "Hello, world!",
                    model="openai/tts-1",
                    voice="alloy",
                    response_format="mp3",
                    speed=1.0
                )

            For different providers (when available):
                response = client.text_to_speech(
                    "Hello, world!",
                    model="provider/model-name",
                    voice="provider-specific-voice"
                )
        """
        # Format the model string
        formatted_model = self._format_model_string(model)

        # Filter out problematic parameters
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["return_generator"]:  # List of parameters to exclude
                filtered_kwargs[key] = value

        # Create the base request data with required parameters
        data = {
            "input": input,
            "model": formatted_model,
        }

        # Add optional parameters only if they are explicitly provided
        if voice is not None:
            data["voice"] = voice
        if response_format is not None:
            data["response_format"] = response_format
        if speed is not None:
            data["speed"] = speed
        if instructions is not None and instructions.strip():
            data["instructions"] = instructions

        # Add any additional parameters from kwargs
        if filtered_kwargs:
            data["additional_params"] = filtered_kwargs

        return self._request("POST", TTS_ENDPOINT, data)

    def _get_supported_parameters_for_model(
        self, provider: str, model_name: str
    ) -> List[str]:
        """
        Get the list of supported parameters for a specific model.
        This helps avoid sending unsupported parameters to providers.

        Args:
            provider: The provider name (e.g., 'openai', 'google', 'xai')
            model_name: The model name (e.g., 'gpt-image-1', 'imagen-3.0-generate-002')

        Returns:
            List of parameter names supported by the model
        """
        # Define supported parameters for specific models
        if provider.lower() == "openai" and "gpt-image" in model_name.lower():
            return [
                "prompt",
                "size",
                "quality",
                "n",
                "user",
                "background",
                "moderation",
                "output_compression",
                "output_format",
                "style",
            ]

        elif provider.lower() == "google" and "imagen" in model_name.lower():
            return [
                "prompt",
                "n",
                "negative_prompt",
                "aspect_ratio",
                "guidance_scale",
                "seed",
                "safety_filter_level",
                "person_generation",
                "include_safety_attributes",
                "include_rai_reason",
                "language",
                "output_mime_type",
                "output_compression_quality",
                "add_watermark",
                "enhance_prompt",
                "response_format",
            ]

        elif provider.lower() == "xai" and "grok-2-image" in model_name.lower():
            return ["prompt", "n", "response_format"]

        # Default case - allow all parameters
        return []

    def models(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available models.

        Args:
            provider: Provider to filter by

        Returns:
            List of available models with pricing information
        """
        endpoint = MODEL_ENDPOINT
        if provider:
            endpoint = f"{MODEL_ENDPOINT}/{provider}"

        return self._request("GET", endpoint)

    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            provider: Provider ID
            model: Model ID

        Returns:
            Model information including pricing
        """
        return self._request("GET", f"{MODEL_ENDPOINT}/{provider}/{model}")

    def get_usage(self) -> Dict[str, Any]:
        """
        Get usage statistics for the current user.

        Returns:
            Usage statistics
        """
        return self._request("GET", USAGE_ENDPOINT)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the server and return server status information.

        This method can be used to diagnose connection issues and verify that
        the server is accessible and properly configured.

        Returns:
            Dictionary containing server status information
        """
        try:
            # Try to access the base URL
            response = self.session.get(self.base_url, timeout=self.timeout)

            # Try to get server info if available
            server_info = {}
            try:
                if response.headers.get("Content-Type", "").startswith(
                    "application/json"
                ):
                    server_info = response.json()
            except:
                pass

            return {
                "status": "connected",
                "url": self.base_url,
                "status_code": response.status_code,
                "server_info": server_info,
                "headers": dict(response.headers),
            }
        except requests.RequestException as e:
            return {
                "status": "error",
                "url": self.base_url,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def diagnose_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose potential issues with a request before sending it to the server.

        This method checks for common issues like malformed model strings,
        invalid message formats, or missing required parameters.

        Args:
            endpoint: API endpoint
            data: Request data

        Returns:
            Dictionary with diagnosis results
        """
        issues = []
        warnings = []

        # Check if this is a chat request
        if endpoint == CHAT_ENDPOINT:
            # Check model format
            if "model" in data:
                model = data["model"]
                # Check if the model is already formatted as JSON
                if (
                    isinstance(model, str)
                    and model.startswith("{")
                    and model.endswith("}")
                ):
                    try:
                        model_json = json.loads(model)
                        if (
                            not isinstance(model_json, dict)
                            or "provider" not in model_json
                            or "model" not in model_json
                        ):
                            issues.append(f"Invalid model JSON format: {model}")
                    except json.JSONDecodeError:
                        issues.append(f"Invalid model JSON format: {model}")
                elif not isinstance(model, str):
                    issues.append(f"Model must be a string, got {type(model).__name__}")
                elif "/" not in model:
                    issues.append(
                        f"Model '{model}' is missing provider prefix (should be 'provider/model')"
                    )
                else:
                    provider, model_name = model.split("/", 1)
                    if not provider or not model_name:
                        issues.append(
                            f"Invalid model format: '{model}'. Should be 'provider/model'"
                        )
            else:
                warnings.append("No model specified, will use default model")

            # Check messages format
            if "messages" in data:
                messages = data["messages"]
                if not isinstance(messages, list):
                    issues.append(
                        f"Messages must be a list, got {type(messages).__name__}"
                    )
                elif not messages:
                    issues.append("Messages list is empty")
                else:
                    for i, msg in enumerate(messages):
                        if not isinstance(msg, dict):
                            issues.append(
                                f"Message {i} must be a dictionary, got {type(msg).__name__}"
                            )
                        elif "role" not in msg:
                            issues.append(f"Message {i} is missing 'role' field")
                        elif "content" not in msg:
                            issues.append(f"Message {i} is missing 'content' field")
            else:
                issues.append("No messages specified")

        # Check if this is a completion request
        elif endpoint == COMPLETION_ENDPOINT:
            # Check model format (same as chat)
            if "model" in data:
                model = data["model"]
                if not isinstance(model, str):
                    issues.append(f"Model must be a string, got {type(model).__name__}")
                elif "/" not in model:
                    issues.append(
                        f"Model '{model}' is missing provider prefix (should be 'provider/model')"
                    )
            else:
                warnings.append("No model specified, will use default model")

            # Check prompt
            if "prompt" not in data:
                issues.append("No prompt specified")
            elif not isinstance(data["prompt"], str):
                issues.append(
                    f"Prompt must be a string, got {type(data['prompt']).__name__}"
                )

        # Return diagnosis results
        return {
            "endpoint": endpoint,
            "issues": issues,
            "warnings": warnings,
            "is_valid": len(issues) == 0,
            "data": data,
        }

    def _handle_streaming_response(self, response):
        """
        Handle a streaming response.

        Args:
            response: Streaming response

        Returns:
            Generator yielding response chunks
        """
        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            # Parse JSON chunk
                            chunk = json.loads(data)

                            # For chat responses, return the processed chunk
                            # with data field for backward compatibility
                            if "choices" in chunk:
                                # For delta responses (streaming)
                                choice = chunk["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    # Add a data field for backward compatibility
                                    chunk["data"] = choice["delta"]["content"]
                                # For text responses (completion)
                                elif "text" in choice:
                                    chunk["data"] = choice["text"]

                            yield chunk
                        except json.JSONDecodeError:
                            # For raw text responses
                            yield {"data": data}
        finally:
            response.close()

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()

    def set_base_url(self, base_url: str) -> None:
        """
        Set a new base URL for the API.

        Args:
            base_url: New base URL for the API.
        """
        self.base_url = base_url
        logger.debug(f"Base URL set to {base_url}")


IndoxRouter = Client
