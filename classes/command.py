from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class Command(ABC):
    def __init__(self, command_type: str, user_id: str):
        self._command_type: str = command_type
        self._user_id: str = user_id
        self._timestamp: datetime = datetime.now()
    
    @abstractmethod
    def execute(self, calendar: 'Calendar') -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        pass
    
    def get_command_type(self) -> str:
        return self._command_type
    
    def get_user_id(self) -> str:
        return self._user_id
    
    def get_timestamp(self) -> datetime:
        return self._timestamp
