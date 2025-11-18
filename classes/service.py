from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class Service(ABC):
    def __init__(self, service_name: str):
        self._service_name: str = service_name
        self._is_running: bool = False
        self._started_at: Optional[datetime] = None
    
    @abstractmethod
    def start(self) -> None:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass
    
    def is_running(self) -> bool:
        return self._is_running
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "service_name": self._service_name,
            "is_running": self._is_running,
            "started_at": self._started_at.isoformat() if self._started_at else None
        }
    
    def get_service_name(self) -> str:
        return self._service_name
