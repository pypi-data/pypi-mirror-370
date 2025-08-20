"""
RawData API endpoints for RaceResult Web API
"""

import json
from typing import Dict, Any, List


class RawData:
    """Contains all API endpoints regarding raw data entries"""
    
    def __init__(self, event_api):
        self.event_api = event_api
    
    def get_by_bib(self, bib: int) -> List[Dict[str, Any]]:
        """
        Get raw data entries for a specific bib number
        
        Args:
            bib: Bib number to get raw data for
            
        Returns:
            List of raw data entries
        """
        params = {
            "bib": bib,
            "filter": "",
            "rdFilter": "{}",
            "addFields": [],
            "firstRow": 0,
            "maxRows": 0,
            "sortBy": ""
        }
        response = self.event_api.get("rawdata/get", params)
        return json.loads(response.decode('utf-8'))
    
    def get_by_pid(self, pid: int) -> List[Dict[str, Any]]:
        """
        Get raw data entries for a specific participant ID (PID)
        
        Args:
            pid: Participant ID to get raw data for
            
        Returns:
            List of raw data entries
        """
        params = {
            "pid": pid,
            "filter": "",
            "rdFilter": "{}",
            "addFields": [],
            "firstRow": 0,
            "maxRows": 0,
            "sortBy": ""
        }
        response = self.event_api.get("rawdata/get", params)
        return json.loads(response.decode('utf-8'))
    
    def list(self, filter_str: str = "", offset: int = 0, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get list of raw data entries
        
        Args:
            filter_str: Filter expression
            offset: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of raw data entries
        """
        params = {
            "filter": filter_str,
            "offset": offset,
            "limit": limit
        }
        
        response = self.event_api.get("rawdata/list", params)
        return json.loads(response.decode('utf-8'))
    
    def count(self, filter_str: str = "") -> int:
        """
        Get count of raw data entries matching filter
        
        Args:
            filter_str: Filter expression
            
        Returns:
            Number of raw data entries
        """
        params = {"filter": filter_str} if filter_str else {}
        response = self.event_api.get("rawdata/count", params)
        return int(response.decode('utf-8'))
    
    def save(self, raw_data: Dict[str, Any]) -> int:
        """
        Save a raw data entry
        
        Args:
            raw_data: Raw data entry to save
            
        Returns:
            ID of the saved raw data entry
        """
        response = self.event_api.post("rawdata/save", None, raw_data)
        return int(response.decode('utf-8'))
    
    def delete(self, raw_data_id: int) -> None:
        """
        Delete a raw data entry
        
        Args:
            raw_data_id: ID of the raw data entry to delete
        """
        params = {"id": raw_data_id}
        self.event_api.get("rawdata/delete", params)
    
    def add_manual(self, timing_point: str, identifier_name: str, identifier_value: int, 
                   time: float, add_t0: bool = False) -> None:
        """
        Add a raw data entry manually
        
        Args:
            timing_point: Name of the timing point
            identifier_name: Type of identifier ('bib' or 'pid')
            identifier_value: Value of the identifier (bib number or participant ID)
            time: Time value (in decimal seconds)
            add_t0: Whether to add T0 (start time offset)
        """
        params = {
            "timingPoint": timing_point,
            identifier_name: identifier_value,
            "time": time,
            "addT0": add_t0
        }
        self.event_api.get("rawdata/addmanual", params) 