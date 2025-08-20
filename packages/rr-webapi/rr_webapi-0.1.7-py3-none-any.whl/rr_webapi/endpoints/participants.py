"""
Participants API endpoints for RaceResult Web API
"""

import json
from typing import Dict, Any, List, Optional, Union


class Participants:
    """Contains all API endpoints regarding participants"""
    
    def __init__(self, event_api):
        self.event_api = event_api
    
    def get_fields(self, identifier: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """
        Get fields of one participant
        
        Args:
            identifier: Dictionary with identifier name and value (e.g., {"PID": 123} or {"Bib": 456})
            fields: List of field names to retrieve
            
        Returns:
            Dictionary with field values
        """
        # Build parameters - identifier name and value are separate parameters
        params = {}
        
        # Add identifier to parameters (use lowercase for parameter names)
        for key, value in identifier.items():
            params[key.lower()] = value
        
        # Add fields as JSON-encoded array (like Go does)
        if fields:
            params["fields"] = json.dumps(fields)
        
        # Debug: print the actual request details
        print(f"🔍 Debug - Request params: {params}")
        
        response = self.event_api.get("part/getfields", params)
        
        # Debug: print response length
        print(f"🔍 Debug - Response length: {len(response)} bytes")
        if len(response) < 500:  # Only print short responses
            print(f"🔍 Debug - Response content: {response.decode('utf-8')}")
        
        return json.loads(response.decode('utf-8'))
    
    def save_fields(self, bib: int, values: Dict[str, Any], create_if_not_exists: bool = False) -> None:
        """
        Save participant fields
        
        Args:
            bib: Bib number of the participant
            values: Dictionary of field values to save
            create_if_not_exists: Whether to create participant if not exists
        """
        data = {
            "bib": bib,
            "values": values,
            "createIfNotExists": create_if_not_exists
        }
        
        self.event_api.post("participants/savefields", None, data)
    
    def save(self, participants: List[Dict[str, Any]], create_if_not_exists: bool = False) -> None:
        """
        Save multiple participants
        
        Args:
            participants: List of participant dictionaries
            create_if_not_exists: Whether to create participants if not exists
        """
        data = {
            "participants": participants,
            "createIfNotExists": create_if_not_exists
        }
        
        self.event_api.post("participants/save", None, data)
    
    def delete(self, filter_str: str, bib: int = 0, version: int = 0) -> None:
        """
        Delete participants
        
        Args:
            filter_str: Filter expression for participants to delete
            bib: Specific bib number to delete (alternative to filter)
            version: Version for optimistic locking
        """
        params = {
            "filter": filter_str,
            "bib": bib,
            "version": version
        }
        
        self.event_api.get("participants/delete", params)
    
    def get(self, bib: int) -> Dict[str, Any]:
        """
        Get a specific participant by bib number
        
        Args:
            bib: Bib number of the participant
            
        Returns:
            Participant dictionary
        """
        # Use data list to get participant by bib
        data = self.event_api.api.event_api(self.event_api.event_id).data().list(
            fields=["ID", "Bib", "FirstName", "LastName", "Contest.Name"],
            filter_str=f"[Bib]={bib}",
            sort_fields=[],
            offset=0,
            limit=1
        )
        
        if data and len(data) > 0:
            return data[0]
        else:
            raise Exception(f"No participant found with bib {bib}")
    
    def list(self, filter_str: str = "", offset: int = 0, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get list of participants
        
        Args:
            filter_str: Filter expression
            offset: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of participant dictionaries
        """
        params = {
            "filter": filter_str,
            "offset": offset,
            "limit": limit
        }
        
        response = self.event_api.get("participants/list", params)
        return json.loads(response.decode('utf-8')) 