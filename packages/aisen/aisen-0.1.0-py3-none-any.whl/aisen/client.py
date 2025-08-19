"""
Aisen API Client
"""

from typing import Dict, Any, Optional, List
import requests
from .exceptions import AisenError, APIError, AuthenticationError


class AisenClient:
    """Main client for interacting with the aisen.vn API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.aisen.vn"):
        """
        Initialize the Aisen client.
        
        Args:
            api_key: Your API key for aisen.vn
            base_url: Base URL for the API (default: https://api.aisen.vn)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'aisen-python/0.1.0'
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
            raise AisenError(f"Request failed: {str(e)}")
    
    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Model to use for completion
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response from the API
        """
        data = {
            'messages': messages,
            'model': model,
            **kwargs
        }
        return self._make_request('POST', '/chat/completions', json=data)
    
    def generate_text(self, prompt: str, model: str = "text-davinci-003", **kwargs) -> Dict[str, Any]:
        """
        Generate text completion.
        
        Args:
            prompt: Text prompt for generation
            model: Model to use for generation
            **kwargs: Additional parameters
            
        Returns:
            Text generation response from the API
        """
        data = {
            'prompt': prompt,
            'model': model,
            **kwargs
        }
        return self._make_request('POST', '/completions', json=data)
    
    def get_models(self) -> Dict[str, Any]:
        """Get list of available models."""
        return self._make_request('GET', '/models')
    
    def get_status(self) -> Dict[str, Any]:
        """Get API status and health check."""
        return self._make_request('GET', '/status')