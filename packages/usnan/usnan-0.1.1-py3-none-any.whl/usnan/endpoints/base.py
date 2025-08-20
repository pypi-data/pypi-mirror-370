"""Base endpoint class"""

from typing import TYPE_CHECKING, Dict, Any, List, Optional, Union

if TYPE_CHECKING:
    from ..client import USNANClient


class BaseEndpoint:
    """Base class for API endpoints"""

    _last_fetch_time: float

    def __init__(self, client: 'USNANClient'):
        self.client = client
        self._last_fetch_time = 0
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Any]]:
        """Make a GET request and return JSON response"""
        response = self.client._make_request('GET', endpoint, params=params)
        return response.json()
    
    def _post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request and return JSON response"""
        response = self.client._make_request('POST', endpoint, json=json)
        return response.json()
    
    def _put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request and return JSON response"""
        response = self.client._make_request('PUT', endpoint, json=json)
        return response.json()
    
    def _delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request and return JSON response"""
        response = self.client._make_request('DELETE', endpoint)
        return response.json()
