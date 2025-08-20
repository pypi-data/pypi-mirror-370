# IndoxRouter

A unified client for various AI providers, including OpenAI, anthropic, Google, and Mistral.

## Features

- **Unified API**: Access multiple AI providers through a single API
- **Simple Interface**: Easy-to-use methods for chat, completion, embeddings, image generation, and text-to-speech
- **Error Handling**: Standardized error handling across providers
- **Authentication**: Secure cookie-based authentication

## Installation

```bash
pip install indoxrouter
```

## Usage

### Initialization

```python
from indoxrouter import Client

# Initialize with API key
client = Client(api_key="your_api_key")

# Using environment variables
# Set INDOX_ROUTER_API_KEY environment variable
import os
os.environ["INDOX_ROUTER_API_KEY"] = "your_api_key"
client = Client()
```

### Authentication

IndoxRouter uses cookie-based authentication with JWT tokens. The client handles this automatically by:

1. Taking your API key and exchanging it for JWT tokens using the server's authentication endpoints
2. Storing the JWT tokens in cookies
3. Using the cookies for subsequent requests
4. Automatically refreshing tokens when they expire

```python
# Authentication is handled automatically when creating the client
client = Client(api_key="your_api_key")
```

### Chat Completions

```python
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
    model="openai/gpt-4o-mini",  # Provider/model format
    temperature=0.7
)

print(response["data"])
```

### Text Completions

```python
response = client.completion(
    prompt="Once upon a time,",
    model="openai/gpt-4o-mini",
    max_tokens=100
)

print(response["data"])
```

### Embeddings

```python
response = client.embeddings(
    text=["Hello world", "AI is amazing"],
    model="openai/text-embedding-3-small"
)

print(f"Dimensions: {len(response['data'][0]['embedding'])}")
print(f"First embedding: {response['data'][0]['embedding'][:5]}...")
```

### Image Generation

```python
# OpenAI Image Generation
response = client.images(
    prompt="A serene landscape with mountains and a lake",
    model="openai/dall-e-3",
    size="1024x1024",
    quality="standard",  # Options: standard, hd
    style="vivid"  # Options: vivid, natural
)

print(f"Image URL: {response['data'][0]['url']}")


# Access base64 encoded image data
if "b64_json" in response["data"][0]:
    b64_data = response["data"][0]["b64_json"]
    # Use the base64 data (e.g., to display in HTML or save to file)
```

### Text-to-Speech

```python
# Generate audio from text
response = client.text_to_speech(
    input="Hello, welcome to IndoxRouter!",
    model="openai/tts-1",
    voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
    response_format="mp3",  # Options: mp3, opus, aac, flac
    speed=1.0  # Range: 0.25 to 4.0
)

print(f"Audio generated successfully: {response['success']}")
print(f"Audio data available: {'data' in response}")
```

### Streaming Responses

```python
for chunk in client.chat(
    messages=[{"role": "user", "content": "Write a short story."}],
    model="openai/gpt-4o-mini",
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Getting Available Models

```python
# Get all providers and models
providers = client.models()
for provider in providers:
    print(f"Provider: {provider['name']}")
    for model in provider["models"]:
        print(f"  - {model['id']}: {model['description'] or ''}")

# Get models for a specific provider
openai_provider = client.models("openai")
print(f"OpenAI models: {[m['id'] for m in openai_provider['models']]}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
