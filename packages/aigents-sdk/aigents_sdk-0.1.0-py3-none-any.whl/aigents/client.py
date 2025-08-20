"""
AIgents Client Core
==================

Main client class with resource managers, inspired by OpenAI client design.
"""

import requests
from typing import Optional, Dict, Any, List
from .exceptions import APIError, AuthenticationError
from .resources import Applications, Chat


class AIgentsClient:
    """
    AIgents Platform Python Client
    
    Simple and elegant client for interacting with the AIgents platform,
    inspired by the OpenAI Python client design.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 60
    ):
        """
        Initialize the AIgents client.
        
        Args:
            api_key: Your AIgents API key
            base_url: Base URL of the AIgents server
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Initialize resource managers
        self.applications = Applications(self)
        self.chat = Chat(self)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the AIgents API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: URL query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            APIError: For API errors
            AuthenticationError: For authentication errors
        """
        url = f"{self.base_url}/api/v1{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or expired token")
            
            # Handle other HTTP errors
            if not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', f'HTTP {response.status_code}')
                except:
                    error_message = f'HTTP {response.status_code}: {response.text}'
                raise APIError(error_message, status_code=response.status_code)
            
            # Return JSON response
            try:
                return response.json()
            except:
                return {"status": "success"}
                
        except requests.exceptions.Timeout:
            raise APIError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise APIError(f"Failed to connect to {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint)