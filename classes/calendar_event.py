from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class CalendarEvent:
    def __init__(self, title: str, start_time: datetime, user_id: str,
                 description: Optional[str] = None,
                 end_time: Optional[datetime] = None,
                 location: Optional[str] = None):
        self._event_id: str = self._generate_event_id()
        self._title: str = title
        self._description: Optional[str] = description
        self._start_time: datetime = start_time
        self._end_time: Optional[datetime] = end_time
        self._location: Optional[str] = location
        self._reminders: List[Dict[str, Any]] = []
        self._user_id: str = user_id
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = datetime.now()
        
        if not self._validate_event():
            raise ValueError("Invalid event data")
    
    def get_event_id(self) -> str:
        return self._event_id
    
    def get_title(self) -> str:
        return self._title
    
    def set_title(self, title: str) -> None:
        self._title = title
        self._updated_at = datetime.now()
    
    def get_description(self) -> Optional[str]:
        return self._description
    
    def set_description(self, description: str) -> None:
        self._description = description
        self._updated_at = datetime.now()
    
    def get_start_time(self) -> datetime:
        return self._start_time
    
    def set_start_time(self, start_time: datetime) -> None:
        self._start_time = start_time
        self._updated_at = datetime.now()
    
    def get_end_time(self) -> Optional[datetime]:
        return self._end_time
    
    def set_end_time(self, end_time: datetime) -> None:
        self._end_time = end_time
        self._updated_at = datetime.now()
    
    def get_location(self) -> Optional[str]:
        return self._location
    
    def set_location(self, location: str) -> None:
        self._location = location
        self._updated_at = datetime.now()
    
    def add_reminder(self, minutes_before: int) -> None:
        reminder = {
            "minutes_before": minutes_before,
            "created_at": datetime.now()
        }
        self._reminders.append(reminder)
        self._updated_at = datetime.now()
    
    def get_reminders(self) -> List[Dict[str, Any]]:
        return self._reminders.copy()
    
    def get_user_id(self) -> str:
        return self._user_id
    
    def get_created_at(self) -> datetime:
        return self._created_at
    
    def get_updated_at(self) -> datetime:
        return self._updated_at
    
    def _generate_event_id(self) -> str:
        return str(uuid.uuid4())
    
    def _validate_event(self) -> bool:
        if not self._title or len(self._title.strip()) == 0:
            return False
        if self._end_time and self._end_time < self._start_time:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self._event_id,
            "title": self._title,
            "description": self._description,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "location": self._location,
            "reminders": self._reminders,
            "user_id": self._user_id,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat()
        }
