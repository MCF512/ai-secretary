from typing import Optional
from datetime import datetime
import uuid


class Balance:
    def __init__(self, user_id: str, initial_balance: float = 0.0):
        self._balance_id: str = self._generate_balance_id()
        self._user_id: str = user_id
        self._amount: float = initial_balance
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = datetime.now()
        
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
    
    def get_balance_id(self) -> str:
        return self._balance_id
    
    def get_user_id(self) -> str:
        return self._user_id
    
    def get_amount(self) -> float:
        return self._amount
    
    def add_funds(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self._amount += amount
        self._updated_at = datetime.now()
    
    def subtract_funds(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if self._amount < amount:
            raise ValueError("Insufficient funds")
        
        self._amount -= amount
        self._updated_at = datetime.now()
    
    def has_sufficient_funds(self, amount: float) -> bool:
        return self._amount >= amount
    
    def get_created_at(self) -> datetime:
        return self._created_at
    
    def get_updated_at(self) -> datetime:
        return self._updated_at
    
    def _generate_balance_id(self) -> str:
        return str(uuid.uuid4())
    
    def to_dict(self) -> dict:
        return {
            "balance_id": self._balance_id,
            "user_id": self._user_id,
            "amount": self._amount,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat()
        }

