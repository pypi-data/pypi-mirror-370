"""
llama-search Python SDK

A Python client library for the llama-search.com API.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .client import LlamaSearchClient
from .exceptions import LlamaSearchError, APIError, AuthenticationError

__all__ = [
    "LlamaSearchClient",
    "LlamaSearchError", 
    "APIError",
    "AuthenticationError",
]