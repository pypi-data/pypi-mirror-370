"""
Data API endpoints for RaceResult Web API
"""

import json
from typing import List, Dict, Any, Optional


class Data:
    """Contains all API endpoints regarding data"""
    
    def __init__(self, event_api):
        self.event_api = event_api
    
    def count(self, filter_str: str = "") -> int:
        """
        Get count of participants matching filter
        
        Args:
            filter_str: Filter expression
            
        Returns:
            Number of participants
        """
        params = {"filter": filter_str} if filter_str else {}
        response = self.event_api.get("data/count", params)
        return int(response.decode('utf-8'))
    
    def list(self, fields: List[str], filter_str: str = "", 
             sort_fields: List[str] = None, offset: int = 0, limit: int = 0,
             group_by: List[str] = None, having: str = "", 
             distinct: str = "") -> List[Dict[str, Any]]:
        """
        Get list of data records
        
        Args:
            fields: List of field names to retrieve
            filter_str: Filter expression
            sort_fields: List of fields to sort by
            offset: Number of records to skip
            limit: Maximum number of records to return
            group_by: List of fields to group by
            having: Having clause for grouped results
            distinct: Distinct field
            
        Returns:
            List of data records
        """
        # Format fields as JSON array string (like in the web app)
        import json as json_module
        fields_json = json_module.dumps(fields) if fields else "[]"
        
        params = {
            "lang": "en",
            "fields": fields_json,
            "filter": filter_str,
            "filterbib": 0,
            "filtercontest": 0,
            "filtersex": "",
            "sort": sort_fields[0] if sort_fields else "",
            "listformat": "jSON",
            "pw": 0
        }
        
        if offset > 0:
            params["offset"] = offset
        if limit > 0:
            params["limit"] = limit
        if group_by:
            params["groupby"] = ",".join(group_by)
        if having:
            params["having"] = having
        if distinct:
            params["distinct"] = distinct
        
        response = self.event_api.get("data/list", params)
        return json.loads(response.decode('utf-8')) 