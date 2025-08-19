# llama-search Python SDK

A Python client library for the [llama-search.com](https://llama-search.com) API.

## Installation

```bash
pip install llama-search
```

## Quick Start

```python
from llama_search import LlamaSearchClient

# Initialize the client with your API key
client = LlamaSearchClient(api_key="your-api-key-here")

# Perform a search
results = client.search("python programming")
print(results)

# Check API status
status = client.get_status()
print(status)
```

## Authentication

You'll need an API key from [llama-search.com](https://llama-search.com). Sign up for an account and generate your API key from the dashboard.

## API Reference

### LlamaSearchClient

The main client class for interacting with the llama-search API.

#### `__init__(api_key, base_url="https://api.llama-search.com")`

Initialize the client with your API key.

- `api_key` (str): Your API key from llama-search.com
- `base_url` (str, optional): Base URL for the API

#### `search(query, limit=10, **kwargs)`

Perform a search query.

- `query` (str): Search query string
- `limit` (int): Maximum number of results to return (default: 10)
- `**kwargs`: Additional search parameters

Returns a dictionary containing search results.

#### `get_status()`

Get API status and health check information.

## Error Handling

The SDK includes custom exceptions:

- `LlamaSearchError`: Base exception for all SDK errors
- `APIError`: Raised for API-related errors
- `AuthenticationError`: Raised for authentication failures

```python
from llama_search import LlamaSearchClient, AuthenticationError, APIError

try:
    client = LlamaSearchClient(api_key="invalid-key")
    results = client.search("test query")
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
```

## Development

See [instructions.md](instructions.md) for development setup and contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.