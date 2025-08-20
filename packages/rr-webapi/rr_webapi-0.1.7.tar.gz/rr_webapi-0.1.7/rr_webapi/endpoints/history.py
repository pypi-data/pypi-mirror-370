"""
History API endpoints for RaceResult Web API
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class History:
    """Contains all API endpoints regarding history entries"""
    
    def __init__(self, event_api):
        self.event_api = event_api
    
    def get(self, bib: Optional[int] = None, pid: Optional[int] = None, 
            contest: Optional[int] = None, field: Optional[str] = None,
            date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
            filter_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get history entries matching the given filters
        
        Args:
            bib: Bib number to filter by
            pid: Participant ID to filter by  
            contest: Contest ID to filter by
            field: Field name to filter by
            date_from: Start date for filtering
            date_to: End date for filtering
            filter_str: Additional filter expression
            
        Returns:
            List of history entries
        """
        params = {}
        
        # Add identifier (bib or pid)
        if bib is not None:
            params["bib"] = bib
        elif pid is not None:
            params["pid"] = pid
            
        # Add optional filters
        if contest is not None:
            params["contest"] = contest
        if field is not None:
            params["field"] = field
        if date_from is not None:
            params["dateForm"] = date_from.isoformat()
        if date_to is not None:
            params["dateTo"] = date_to.isoformat()
        if filter_str is not None:
            params["filter"] = filter_str
        
        response = self.event_api.get("history/get", params)
        return json.loads(response.decode('utf-8'))
    
    def count(self, bib: Optional[int] = None, pid: Optional[int] = None,
              contest: Optional[int] = None, field: Optional[str] = None,
              date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
              filter_str: Optional[str] = None) -> int:
        """
        Count history entries matching the given filters
        
        Args:
            bib: Bib number to filter by
            pid: Participant ID to filter by
            contest: Contest ID to filter by
            field: Field name to filter by
            date_from: Start date for filtering
            date_to: End date for filtering
            filter_str: Additional filter expression
            
        Returns:
            Number of matching history entries
        """
        params = {}
        
        # Add identifier (bib or pid)
        if bib is not None:
            params["bib"] = bib
        elif pid is not None:
            params["pid"] = pid
            
        # Add optional filters
        if contest is not None:
            params["contest"] = contest
        if field is not None:
            params["field"] = field
        if date_from is not None:
            params["dateForm"] = date_from.isoformat()
        if date_to is not None:
            params["dateTo"] = date_to.isoformat()
        if filter_str is not None:
            params["filter"] = filter_str
        
        response = self.event_api.get("history/count", params)
        return int(response.decode('utf-8'))
    
    def excel_export(self, bib: Optional[int] = None, pid: Optional[int] = None,
                     lang: str = "en") -> bytes:
        """
        Export history entries as CSV/Excel file
        
        Args:
            bib: Bib number to filter by
            pid: Participant ID to filter by
            lang: Language for export
            
        Returns:
            File content as bytes
        """
        params = {"lang": lang}
        
        # Add identifier (bib or pid)
        if bib is not None:
            params["bib"] = bib
        elif pid is not None:
            params["pid"] = pid
        
        return self.event_api.get("history/excelexport", params)
    
    def delete(self, bib: Optional[int] = None, pid: Optional[int] = None,
               contest: Optional[int] = None, field: Optional[str] = None,
               date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
               filter_str: Optional[str] = None) -> None:
        """
        Delete history entries matching the given filters
        
        Args:
            bib: Bib number to filter by
            pid: Participant ID to filter by
            contest: Contest ID to filter by
            field: Field name to filter by
            date_from: Start date for filtering
            date_to: End date for filtering
            filter_str: Additional filter expression
        """
        params = {}
        
        # Add identifier (bib or pid)
        if bib is not None:
            params["bib"] = bib
        elif pid is not None:
            params["pid"] = pid
            
        # Add optional filters
        if contest is not None:
            params["contest"] = contest
        if field is not None:
            params["field"] = field
        if date_from is not None:
            params["dateForm"] = date_from.isoformat()
        if date_to is not None:
            params["dateTo"] = date_to.isoformat()
        if filter_str is not None:
            params["filter"] = filter_str
        
        self.event_api.get("history/delete", params) 