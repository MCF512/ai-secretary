import re
import uuid
from typing import Optional


class User:
    def __init__(self, telegram_id: str | None, name: str, email: str):
        self._user_id: str = self._generate_user_id()
        self._telegram_id: Optional[str] = telegram_id
        self._name: str = name
        self._email: str = email
        self._is_active: bool = True
        
        if not self._validate_email(email):
            raise ValueError(f"Invalid email: {email}")
    
    def get_user_id(self) -> str:
        return self._user_id
    
    def get_telegram_id(self) -> Optional[str]:
        return self._telegram_id
    
    def get_name(self) -> str:
        return self._name
    
    def get_email(self) -> str:
        return self._email
    
    def activate(self) -> None:
        self._is_active = True
    
    def deactivate(self) -> None:
        self._is_active = False
    
    def is_active(self) -> bool:
        return self._is_active
    
    def _validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _generate_user_id(self) -> str:
        return str(uuid.uuid4())
