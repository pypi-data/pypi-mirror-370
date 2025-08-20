"""
Public API endpoints for RaceResult Web API
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class EventListItem:
    """Event list item data structure"""
    id: str
    user_id: int
    user_name: str
    checked_out: bool
    participants: int
    not_activated: int
    event_name: str
    event_date: datetime
    event_date2: Optional[datetime]
    event_location: str
    event_country: int


class Public:
    """Contains all API endpoints regarding functions on public servers"""
    
    def __init__(self, api):
        self.api = api
        self.session_id = "0"
    
    def login(self, api_key: str = None, user: str = None, password: str = None,
              sign_in_as: str = None, totp: str = None, rr_user_token: str = None) -> None:
        """
        Create a new session
        
        Args:
            api_key: API key for authentication
            user: Username for login
            password: Password for login
            sign_in_as: Sign in as another user
            totp: Time-based one-time password
            rr_user_token: RaceResult user token
        """
        data = {}
        
        if api_key:
            data["apikey"] = api_key
        if user:
            data["user"] = user
            data["pw"] = password or ""
        if sign_in_as:
            data["signinas"] = sign_in_as
        if totp:
            data["totp"] = totp
        if rr_user_token:
            data["rruser_token"] = rr_user_token
        
        response = self.api.post("", "public/login", None, data, "application/x-www-form-urlencoded")
        self.session_id = response.decode('utf-8')
    
    def logout(self) -> None:
        """Terminate the session"""
        if not self.session_id or self.session_id == "0":
            raise Exception("not logged in")
        
        self.api.get("", "public/logout", None)
        self.session_id = "0"
    
    def event_list(self, year: int = 0, filter_str: str = "") -> List[EventListItem]:
        """
        Returns a list of events
        
        Args:
            year: Filter by year (0 for all years)
            filter_str: Filter string
            
        Returns:
            List of EventListItem objects
        """
        params = {
            "year": year,
            "filter": filter_str,
            "addsettings": "EventName,EventDate,EventDate2,EventLocation,EventCountry"
        }
        
        response = self.api.get("", "public/eventlist", params)
        data = json.loads(response.decode('utf-8'))
        
        events = []
        for item in data:
            # Parse dates
            event_date = datetime.fromisoformat(item["EventDate"].replace("Z", "+00:00")) if item.get("EventDate") else None
            event_date2 = datetime.fromisoformat(item["EventDate2"].replace("Z", "+00:00")) if item.get("EventDate2") else None
            
            event = EventListItem(
                id=item["ID"],
                user_id=item["UserID"],
                user_name=item["UserName"],
                checked_out=item["CheckedOut"],
                participants=item["Participants"],
                not_activated=item["NotActivated"],
                event_name=item.get("EventName", ""),
                event_date=event_date,
                event_date2=event_date2,
                event_location=item.get("EventLocation", ""),
                event_country=item.get("EventCountry", 0)
            )
            events.append(event)
        
        return events
    
    def create_event(self, event_name: str, event_date: datetime, event_country: int = 840,
                    copy_of: int = 0, template_id: int = 0, mode: int = 0, laps: int = 0):
        """
        Create a new event (online server only) and returns the new event API
        
        Args:
            event_name: Name of the event
            event_date: Date of the event
            event_country: Country code (default 840 for USA)
            copy_of: Event ID to copy from
            template_id: Template ID to use
            mode: Event mode
            laps: Number of laps
            
        Returns:
            EventAPI instance for the newly created event
        """
        params = {
            "name": event_name,
            "date": event_date.isoformat(),
            "country": event_country,
            "copyOf": copy_of,
            "templateID": template_id,
            "mode": mode,
            "laps": laps
        }
        
        response = self.api.get("", "public/createevent", params)
        event_id = response.decode('utf-8')
        
        from .eventapi import EventAPI
        return EventAPI(event_id, self.api)
    
    def delete_event(self, event_id: str) -> None:
        """
        Delete an event, use with care!
        
        Args:
            event_id: ID of the event to delete
        """
        params = {"eventID": event_id}
        self.api.get("", "public/deleteevent", params)
    
    def user_info(self) -> Dict[str, Any]:
        """
        Returns ID + name of current user
        
        Returns:
            Dictionary with user information
        """
        response = self.api.get("", "public/userinfo", None)
        return json.loads(response.decode('utf-8'))
    
    def get_session_id(self) -> str:
        """Returns the current session ID"""
        return self.session_id 