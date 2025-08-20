"""
Main API class for RaceResult Web API
"""

import requests
import json
import time
from typing import Optional, Callable, Any, Dict, Union
from urllib.parse import urlencode, urljoin

from .public import Public
from .eventapi import EventAPI
from .general import General


class API:
    """Main API object for the RaceResult web API"""
    
    def __init__(self, server: str, https: bool = True, user_agent: str = ""):
        """
        Create a new API object
        
        Args:
            server: The server hostname
            https: Whether to use HTTPS
            user_agent: User agent string, defaults to "python-webapi/1.0"
        """
        self.server = server
        self.secure = https
        self.timeout_ms = 30000  # 30 seconds default
        self.user_agent = user_agent or "python-webapi/1.0"
        self.error_gen: Optional[Callable[[str, int], Exception]] = None
        
        # Initialize endpoint groups
        self._public = Public(self)
    
    def event_api(self, event_id: str) -> 'EventAPI':
        """Returns an EventAPI for the given event"""
        return EventAPI(event_id, self)
    
    def public(self) -> Public:
        """Returns the endpoint group for public servers"""
        return self._public
    
    def general(self) -> 'General':
        """Returns the endpoint group for general functions"""
        return General(self)
    
    def set_timeout(self, timeout_seconds: float):
        """Set the timeout for all following requests. Default is 30 seconds."""
        self.timeout_ms = int(timeout_seconds * 1000)
    
    def get_timeout(self) -> float:
        """Returns the current request timeout in seconds"""
        return self.timeout_ms / 1000.0
    
    def set_error_gen(self, fn: Callable[[str, int], Exception]):
        """Set a custom function used to create errors"""
        self.error_gen = fn
    
    def session_id(self) -> str:
        """Returns the session ID"""
        return self._public.session_id
    
    def _build_url(self, event_id: str, cmd: str, params: Optional[Dict] = None) -> str:
        """Build the URL for any request"""
        protocol = "https" if self.secure else "http"
        url = f"{protocol}://{self.server}"
        
        if event_id:
            url += f"/_{event_id}"
        
        url += f"/api/{cmd}"
        
        if params:
            query_string = urlencode(params)
            url += f"?{query_string}"
        
        return url
    
    def _make_request(self, method: str, event_id: str, cmd: str, 
                     params: Optional[Dict] = None, 
                     data: Any = None, 
                     content_type: Optional[str] = None) -> bytes:
        """Make an HTTP request to the API"""
        url = self._build_url(event_id, cmd, params)
        
        headers = {
            "Authorization": f"Bearer {self._public.session_id}",
            "User-Agent": self.user_agent
        }
        
        if content_type:
            headers["Content-Type"] = content_type
        
        # Prepare request data
        request_data = None
        if data is not None:
            if isinstance(data, (str, bytes)):
                request_data = data
            elif isinstance(data, dict) and content_type == "application/x-www-form-urlencoded":
                request_data = urlencode(data)
            else:
                request_data = json.dumps(data)
                if not content_type:
                    headers["Content-Type"] = "application/json"
        
        # Make the request
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=request_data,
                timeout=self.get_timeout()
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        
        # Handle response
        if response.status_code == 200:
            return response.content
        
        # Handle errors
        try:
            error_data = response.json()
            error_msg = error_data.get("Error", response.text)
        except:
            error_msg = response.text
        
        if self.error_gen:
            raise self.error_gen(error_msg, response.status_code)
        
        raise Exception(error_msg)
    
    def get(self, event_id: str, cmd: str, params: Optional[Dict] = None) -> bytes:
        """Make a GET request to the server"""
        return self._make_request("GET", event_id, cmd, params)
    
    def post(self, event_id: str, cmd: str, params: Optional[Dict] = None, 
             data: Any = None, content_type: Optional[str] = None) -> bytes:
        """Make a POST request to the server"""
        return self._make_request("POST", event_id, cmd, params, data, content_type) 