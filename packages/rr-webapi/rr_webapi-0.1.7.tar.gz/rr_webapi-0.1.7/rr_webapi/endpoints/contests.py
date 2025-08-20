"""
Contests API endpoints for RaceResult Web API
"""

import json
from typing import Dict, Any, List, Optional


class Contest:
    """Contest data structure"""
    
    def __init__(self, name: str = "", **kwargs):
        self.name = name
        self.id = kwargs.get("id", 0)
        # Add other contest fields as needed
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contest to dictionary"""
        return {
            "Name": self.name,
            "ID": getattr(self, "id", 0)
        }


class Contests:
    """Contains all API endpoints regarding contests"""
    
    def __init__(self, event_api):
        self.event_api = event_api
    
    def save(self, contest: Contest, version: int = 0) -> int:
        """
        Save a contest
        
        Args:
            contest: Contest object to save
            version: Version number for optimistic locking
            
        Returns:
            Contest ID of the saved contest
        """
        data = contest.to_dict()
        if version > 0:
            data["Version"] = version
        
        response = self.event_api.post("contests/save", None, data)
        return int(response.decode('utf-8'))
    
    def delete(self, contest_id: int) -> None:
        """
        Delete a contest
        
        Args:
            contest_id: ID of the contest to delete
        """
        params = {"id": contest_id}
        self.event_api.get("contests/delete", params)
    
    def list(self) -> List[Dict[str, Any]]:
        """
        Get list of all contests
        
        Returns:
            List of contest dictionaries
        """
        response = self.event_api.get("contests/get", None)
        return json.loads(response.decode('utf-8'))
    
    def get(self, contest_id: int) -> Dict[str, Any]:
        """
        Get a specific contest by ID
        
        Args:
            contest_id: ID of the contest
            
        Returns:
            Contest dictionary
        """
        params = {"id": contest_id}
        response = self.event_api.get("contests/get", params)
        return json.loads(response.decode('utf-8')) 