"""
Constants for the IndoxRouter client.
"""

# API settings
DEFAULT_API_VERSION = "v1"
DEFAULT_BASE_URL = "https://api.indoxrouter.com"  # Production server URL with HTTPS
# DEFAULT_BASE_URL = "http://localhost:8000"  # Local development server
DEFAULT_TIMEOUT = 60
USE_COOKIES = True  # Always use cookie-based authentication

# Default models
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL = "openai/text-embedding-3-small"
DEFAULT_IMAGE_MODEL = "openai/dall-e-3"
DEFAULT_TTS_MODEL = "openai/tts-1"
GOOGLE_IMAGE_MODEL = "google/imagen-3.0-generate-002"
XAI_IMAGE_MODEL = "xai/grok-2-image"
XAI_IMAGE_LATEST_MODEL = "xai/grok-2-image-latest"
XAI_IMAGE_SPECIFIC_MODEL = "xai/grok-2-image-1212"

# API endpoints
CHAT_ENDPOINT = "chat/completions"
COMPLETION_ENDPOINT = "completions"
EMBEDDING_ENDPOINT = "embeddings"
IMAGE_ENDPOINT = "images/generations"
TTS_ENDPOINT = "tts/generations"
MODEL_ENDPOINT = "models"
USAGE_ENDPOINT = "user/usage"

# Error messages
ERROR_INVALID_API_KEY = "API key must be provided either as an argument or as the INDOXROUTER_API_KEY environment variable"
ERROR_NETWORK = "Network error occurred while communicating with the IndoxRouter API"
ERROR_RATE_LIMIT = "Rate limit exceeded for the IndoxRouter API"
ERROR_PROVIDER_NOT_FOUND = "Provider not found"
ERROR_MODEL_NOT_FOUND = "Model not found"
ERROR_INVALID_PARAMETERS = "Invalid parameters provided"
ERROR_INSUFFICIENT_CREDITS = "Insufficient credits"
