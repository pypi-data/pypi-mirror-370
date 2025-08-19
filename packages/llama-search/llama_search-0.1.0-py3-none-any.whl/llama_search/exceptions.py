"""
Custom exceptions for the llama-search SDK
"""


class LlamaSearchError(Exception):
    """Base exception for all llama-search SDK errors."""
    pass


class APIError(LlamaSearchError):
    """Exception raised for API-related errors."""
    pass


class AuthenticationError(LlamaSearchError):
    """Exception raised for authentication failures."""
    pass