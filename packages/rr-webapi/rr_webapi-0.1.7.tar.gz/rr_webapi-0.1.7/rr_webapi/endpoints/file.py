"""
File API endpoints for RaceResult Web API
"""

import json
from typing import Tuple


class File:
    """Contains all API endpoints regarding file operations"""
    
    def __init__(self, event_api):
        self.event_api = event_api
    
    def get_file(self) -> bytes:
        """
        Get the event file content
        
        Returns:
            File content as bytes
        """
        return self.event_api.get("file/getfile", None)
    
    def mod_job_id(self) -> int:
        """
        Get the current modification job ID of the file
        
        Returns:
            Current ModJobID
        """
        response = self.event_api.get("file/modjobid", None)
        return int(response.decode('utf-8'))
    
    def mod_job_ids(self) -> Tuple[int, int]:
        """
        Get both the normal ModJobID and settings ModJobID of the file
        
        Returns:
            Tuple of (ModJobID, ModJobIDSettings)
        """
        response = self.event_api.get("file/modjobids", None)
        parts = response.decode('utf-8').split(';')
        if len(parts) != 2:
            raise ValueError("Invalid response format for ModJobIDs")
        
        mod_job_id = int(parts[0])
        mod_job_id_settings = int(parts[1])
        return mod_job_id, mod_job_id_settings
    
    def filename(self) -> str:
        """
        Get the filename of the event file
        
        Returns:
            Event filename
        """
        response = self.event_api.get("file/filename", None)
        return response.decode('utf-8')
    
    def owner(self) -> int:
        """
        Get the user ID of the owner of the event (online server only)
        
        Returns:
            Owner user ID
        """
        response = self.event_api.get("file/owner", None)
        return int(json.loads(response.decode('utf-8')))
    
    def is_owner(self) -> bool:
        """
        Check if the current user owns the event (online server only)
        
        Returns:
            True if user owns the event
        """
        response = self.event_api.get("file/isowner", None)
        return json.loads(response.decode('utf-8'))
    
    def rights(self) -> str:
        """
        Get the user rights code for this event (online server only)
        
        Returns:
            User rights code
        """
        response = self.event_api.get("file/rights", None)
        return response.decode('utf-8') 