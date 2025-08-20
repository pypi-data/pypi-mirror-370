"""
IndoxRouter: A unified client for various AI providers.

This package provides a client for interacting with the IndoxRouter server,
which serves as a unified interface to multiple AI providers and models.

Example:
    ```python
    from indoxrouter import Client

    # Initialize client with API key
    client = Client(api_key="your_api_key")

    # Generate a chat completion
    response = client.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ], model="openai/gpt-4o-mini")

    print(response["data"])
    ```

For custom server URLs:
    ```python
    # Connect to a specific server
    client = Client(
        api_key="your_api_key",
        base_url="http://your-custom-server:8000"
    )
    ```
"""

from .client import Client, IndoxRouter
from .exceptions import (
    IndoxRouterError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError,
    ModelNotFoundError,
    ProviderNotFoundError,
    ModelNotAvailableError,
    InvalidParametersError,
    RequestError,
    InsufficientCreditsError,
    ValidationError,
    APIError,
)

__version__ = "0.1.26"
__all__ = [
    "Client",
    "IndoxRouter",
    "IndoxRouterError",
    "AuthenticationError",
    "NetworkError",
    "RateLimitError",
    "ProviderError",
    "ModelNotFoundError",
    "ProviderNotFoundError",
    "ModelNotAvailableError",
    "InvalidParametersError",
    "RequestError",
    "InsufficientCreditsError",
    "ValidationError",
    "APIError",
]
