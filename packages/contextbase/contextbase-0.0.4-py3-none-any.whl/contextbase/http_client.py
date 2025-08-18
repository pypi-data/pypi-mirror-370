import os
import requests
from typing import Dict, Any, Optional
from .http_response import ContextbaseResponse

class HttpClient:
    """
    HTTP client for making requests to the Contextbase API.
    
    Handles authentication, request formatting, and response wrapping.
    
    Attributes:
        api_key: The API key for authentication
        base_url: The base URL for the Contextbase API
    """
    
    BASE_URL = os.environ.get("CONTEXTBASE_API_URL", "https://api.contextbase.dev")

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the HTTP client.
        
        Args:
            api_key: API key for authentication. If None, uses CONTEXTBASE_API_KEY 
                    environment variable.
                    
        Raises:
            ValueError: If no API key is provided and CONTEXTBASE_API_KEY is not set
        """
        self.api_key = api_key or os.environ.get("CONTEXTBASE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as a parameter or set CONTEXTBASE_API_KEY environment variable."
            )
        self.base_url = self.BASE_URL.rstrip('/')

    def post(self, path: str, data: Dict[str, Any] = None) -> ContextbaseResponse:
        """
        Make a POST request to the API.
        
        Args:
            path: API endpoint path (should start with /)
            data: JSON data to send in the request body
            
        Returns:
            ContextbaseResponse: Wrapped response object
            
        Raises:
            requests.RequestException: If the HTTP request fails
        """
        if data is None:
            data = {}
            
        url = f"{self.base_url}{path}"
        
        try:
            response = requests.post(
                url,
                json=data,
                headers=self._build_headers(),
                timeout=30
            )
            return ContextbaseResponse(response)
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to make request to {url}: {e}") from e

    def _build_headers(self) -> Dict[str, str]:
        """
        Build HTTP headers for API requests.
        
        Returns:
            Dictionary of HTTP headers
        """
        return {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'contextbase-python-sdk/1.0.0'
        }
