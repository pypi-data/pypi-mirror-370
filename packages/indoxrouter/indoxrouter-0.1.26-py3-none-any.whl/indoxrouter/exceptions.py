"""
Exceptions for the IndoxRouter client.
"""

from datetime import datetime
from typing import Optional


class IndoxRouterError(Exception):
    """Base exception for all IndoxRouter errors."""

    pass


class AuthenticationError(IndoxRouterError):
    """Raised when authentication fails."""

    pass


class NetworkError(IndoxRouterError):
    """Raised when a network error occurs."""

    pass


class RateLimitError(IndoxRouterError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str, reset_time: Optional[datetime] = None):
        super().__init__(message)
        self.reset_time = reset_time


class ProviderError(IndoxRouterError):
    """Raised when a provider returns an error."""

    pass


class ProviderNotFoundError(ProviderError):
    """Raised when a requested provider is not found."""

    pass


class ModelNotFoundError(ProviderError):
    """Raised when a requested model is not found."""

    pass


class ModelNotAvailableError(ProviderError):
    """Raised when a model is disabled or not supported by the provider."""

    pass


class InvalidParametersError(IndoxRouterError):
    """Raised when invalid parameters are provided."""

    pass


class RequestError(IndoxRouterError):
    """Raised when a request to a provider fails."""

    pass


class InsufficientCreditsError(IndoxRouterError):
    """Raised when the user doesn't have enough credits."""

    pass


class ValidationError(IndoxRouterError):
    """Raised when request validation fails."""

    pass


class APIError(IndoxRouterError):
    """Raised when the API returns an error."""

    pass
