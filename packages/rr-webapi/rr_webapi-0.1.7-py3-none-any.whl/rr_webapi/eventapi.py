"""
Event API endpoints for RaceResult Web API
"""

import json
from typing import Dict, Any, List, Optional


class EventAPI:
    """Contains all API functions for a specific event"""
    
    def __init__(self, event_id: str, api):
        self.event_id = event_id
        self.api = api
    
    def get_event_id(self) -> str:
        """Returns the event ID"""
        return self.event_id
    
    def data(self):
        """Returns the Data endpoint group"""
        from .endpoints.data import Data
        return Data(self)
    
    def contests(self):
        """Returns the Contests endpoint group"""
        from .endpoints.contests import Contests
        return Contests(self)
    
    def participants(self):
        """Returns the Participants endpoint group"""
        from .endpoints.participants import Participants
        return Participants(self)
    
    def raw_data(self):
        """Returns the RawData endpoint group"""
        from .endpoints.rawdata import RawData
        return RawData(self)
    
    def file(self):
        """Returns the File endpoint group"""
        from .endpoints.file import File
        return File(self)
    
    def history(self):
        """Returns the History endpoint group"""
        from .endpoints.history import History
        return History(self)
    
    def get(self, cmd: str, params: Optional[Dict] = None) -> bytes:
        """Make a GET request for this event"""
        return self.api.get(self.event_id, cmd, params)
    
    def post(self, cmd: str, params: Optional[Dict] = None, data: Any = None) -> bytes:
        """Make a POST request for this event"""
        return self.api.post(self.event_id, cmd, params, data)
    
    def multi_request(self, requests: List[str]) -> Dict[str, Any]:
        """
        Execute multiple requests in a single call
        
        Args:
            requests: List of request URIs
            
        Returns:
            Dictionary with results for each request
        """
        # Send requests array directly (like Go library), not wrapped in an object
        response = self.post("multirequest", None, requests)
        return json.loads(response.decode('utf-8')) 