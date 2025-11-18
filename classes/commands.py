from typing import Dict, Any, Optional, List
from datetime import datetime
from .command import Command
from .calendar_event import CalendarEvent


class CreateEventCommand(Command):
    def __init__(self, user_id: str, title: str, start_time: datetime,
                 description: Optional[str] = None,
                 end_time: Optional[datetime] = None,
                 location: Optional[str] = None,
                 reminders: Optional[List[int]] = None):
        super().__init__("create_event", user_id)
        self._title: str = title
        self._description: Optional[str] = description
        self._start_time: datetime = start_time
        self._end_time: Optional[datetime] = end_time
        self._location: Optional[str] = location
        self._reminders: List[int] = reminders or []
    
    def execute(self, calendar: 'Calendar') -> Dict[str, Any]:
        if not self.validate():
            return {"success": False, "error": "Invalid command parameters"}
        
        try:
            event = CalendarEvent(
                title=self._title,
                start_time=self._start_time,
                user_id=self._user_id,
                description=self._description,
                end_time=self._end_time,
                location=self._location
            )
            
            for minutes in self._reminders:
                event.add_reminder(minutes)
            
            added_event = calendar.add_event(event)
            
            return {
                "success": True,
                "event_id": added_event.get_event_id(),
                "event": added_event.to_dict()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate(self) -> bool:
        return (
            len(self._title.strip()) > 0 and
            self._start_time is not None and
            (self._end_time is None or self._end_time >= self._start_time)
        )


class DeleteEventCommand(Command):
    def __init__(self, user_id: str, event_id: str):
        super().__init__("delete_event", user_id)
        self._event_id: str = event_id
    
    def execute(self, calendar: 'Calendar') -> Dict[str, Any]:
        if not self.validate():
            return {"success": False, "error": "Invalid event ID"}
        
        success = calendar.delete_event(self._event_id)
        
        return {
            "success": success,
            "event_id": self._event_id,
            "message": "Event deleted" if success else "Event not found"
        }
    
    def validate(self) -> bool:
        return len(self._event_id) > 0


class UpdateEventCommand(Command):
    def __init__(self, user_id: str, event_id: str, **updates):
        super().__init__("update_event", user_id)
        self._event_id: str = event_id
        self._updates: Dict[str, Any] = updates
    
    def execute(self, calendar: 'Calendar') -> Dict[str, Any]:
        if not self.validate():
            return {"success": False, "error": "Invalid command parameters"}
        
        updated_event = calendar.update_event(self._event_id, **self._updates)
        
        if updated_event:
            return {
                "success": True,
                "event_id": self._event_id,
                "event": updated_event.to_dict()
            }
        else:
            return {
                "success": False,
                "error": "Event not found",
                "event_id": self._event_id
            }
    
    def validate(self) -> bool:
        return len(self._event_id) > 0 and len(self._updates) > 0


class ListEventsCommand(Command):
    def __init__(self, user_id: str,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None):
        super().__init__("list_events", user_id)
        self._start_date: Optional[datetime] = start_date
        self._end_date: Optional[datetime] = end_date
    
    def execute(self, calendar: 'Calendar') -> Dict[str, Any]:
        events = calendar.get_events(
            start_date=self._start_date,
            end_date=self._end_date
        )
        
        return {
            "success": True,
            "events": [event.to_dict() for event in events],
            "count": len(events)
        }
    
    def validate(self) -> bool:
        if self._start_date and self._end_date:
            return self._end_date >= self._start_date
        return True
