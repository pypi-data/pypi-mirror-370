# aisen Python SDK

A Python client library for the [aisen.vn](https://aisen.vn) API - Vietnam's AI platform.

## Installation

```bash
pip install aisen
```

## Quick Start

```python
from aisen import AisenClient

# Initialize the client with your API key
client = AisenClient(api_key="your-api-key-here")

# Chat completion
response = client.chat([
    {"role": "user", "content": "Xin chào! Bạn có thể giúp tôi không?"}
])
print(response)

# Text generation
response = client.generate_text("Viết một bài thơ về Việt Nam")
print(response)

# Get available models
models = client.get_models()
print(models)

# Check API status
status = client.get_status()
print(status)
```

## Authentication

You'll need an API key from [aisen.vn](https://aisen.vn). Sign up for an account and generate your API key from the dashboard.

## API Reference

### AisenClient

The main client class for interacting with the aisen.vn API.

#### `__init__(api_key, base_url="https://api.aisen.vn")`

Initialize the client with your API key.

- `api_key` (str): Your API key from aisen.vn
- `base_url` (str, optional): Base URL for the API

#### `chat(messages, model="gpt-3.5-turbo", **kwargs)`

Send a chat completion request.

- `messages` (List[Dict]): List of message objects with 'role' and 'content'
- `model` (str): Model to use for completion
- `**kwargs`: Additional parameters

Returns a dictionary containing the chat completion response.

#### `generate_text(prompt, model="text-davinci-003", **kwargs)`

Generate text completion.

- `prompt` (str): Text prompt for generation
- `model` (str): Model to use for generation
- `**kwargs`: Additional parameters

Returns a dictionary containing the generated text.

#### `get_models()`

Get list of available models.

#### `get_status()`

Get API status and health check information.

## Error Handling

The SDK includes custom exceptions:

- `AisenError`: Base exception for all SDK errors
- `APIError`: Raised for API-related errors
- `AuthenticationError`: Raised for authentication failures

```python
from aisen import AisenClient, AuthenticationError, APIError

try:
    client = AisenClient(api_key="invalid-key")
    response = client.chat([{"role": "user", "content": "Hello"}])
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
```

## Vietnamese Language Support

The aisen.vn platform is optimized for Vietnamese language processing:

```python
# Vietnamese chat
response = client.chat([
    {"role": "system", "content": "Bạn là một trợ lý AI thông minh và hữu ích."},
    {"role": "user", "content": "Giải thích về trí tuệ nhân tạo bằng tiếng Việt."}
])

# Vietnamese text generation
poem = client.generate_text(
    "Viết một bài thơ về mùa thu Hà Nội",
    model="vietnamese-poet-v1"
)
```

## Development

See [instructions.md](instructions.md) for development setup and contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.