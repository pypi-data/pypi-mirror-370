"""
LlamaSearch API Client
"""

from typing import Dict, Any, Optional, List
import requests
from .exceptions import LlamaSearchError, APIError, AuthenticationError


class LlamaSearchClient:
    """Main client for interacting with the llama-search.com API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.llama-search.com"):
        """
        Initialize the LlamaSearch client.
        
        Args:
            api_key: Your API key for llama-search.com
            base_url: Base URL for the API (default: https://api.llama-search.com)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'llama-search-python/0.1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 400:
                raise APIError(f"Bad request: {response.text}")
            else:
                raise APIError(f"HTTP {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise LlamaSearchError(f"Request failed: {str(e)}")
    
    def search(self, query: str, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Perform a search query.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            Search results from the API
        """
        params = {
            'query': query,
            'limit': limit,
            **kwargs
        }
        return self._make_request('GET', '/search', params=params)
    
    def get_status(self) -> Dict[str, Any]:
        """Get API status and health check."""
        return self._make_request('GET', '/status')