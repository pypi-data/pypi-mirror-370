"""Main RoWifi API client - Updated to use endpoint classes"""

import requests
import time
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from .exceptions import (
    RoWifiError, AuthenticationError, RateLimitError, 
    NotFoundError, ValidationError, ServerError
)
from .endpoints import MemberEndpoints, DenylistEndpoints, TowerEndpoints, RankEndpoints

class RoWifiClient:
    """
    RoWifi API Client
    
    Provides methods to interact with the RoWifi API for Discord-Roblox integration.
    
    Args:
        token (str): Bot token from RoWifi dashboard
        version (int): API version (default: 3)
        timeout (int): Request timeout in seconds (default: 30)
        max_retries (int): Maximum number of retries for rate limits (default: 3)
    
    Attributes:
        members: Member-related endpoints
        denylists: Denylist management endpoints  
        tower: XP/Tower system endpoints
        ranks: Rank management endpoints
    """
    
    def __init__(
        self, 
        token: str, 
        version: int = 3, 
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.token = token
        self.version = version
        self.base_url = f"https://api.rowifi.xyz/v{version}"
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bot {token}',
            'Content-Type': 'application/json',
            'User-Agent': f'rowifi-python/1.0.0'
        })
        
        # Initialize endpoint handlers
        self.members = MemberEndpoints(self)
        self.denylists = DenylistEndpoints(self)
        self.tower = TowerEndpoints(self)
        self.ranks = RankEndpoints(self)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and rate limiting"""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    timeout=self.timeout
                )
                
                # Handle different status codes
                if response.status_code == 200:
                    return response.json() if response.content else {}
                elif response.status_code == 204:
                    return {}
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise NotFoundError("Resource not found")
                elif response.status_code == 400:
                    raise ValidationError(f"Bad request: {response.text}")
                elif response.status_code == 429:
                    if attempt < self.max_retries:
                        retry_after = int(response.headers.get('Retry-After', 1))
                        time.sleep(retry_after)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded", 
                                           retry_after=response.headers.get('Retry-After'))
                elif response.status_code >= 500:
                    raise ServerError(f"Server error: {response.status_code}")
                else:
                    raise RoWifiError(f"Unexpected status code: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise RoWifiError(f"Request failed: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                raise AuthenticationError(f"Error at endpoint {endpoint} with payload {json_data}: {e}")
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
