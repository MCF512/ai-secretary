from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class Transaction:
    def __init__(self, user_id: str, transaction_type: TransactionType, 
                 amount: float, description: Optional[str] = None):
        self._transaction_id: str = self._generate_transaction_id()
        self._user_id: str = user_id
        self._transaction_type: TransactionType = transaction_type
        self._amount: float = amount
        self._description: Optional[str] = description
        self._created_at: datetime = datetime.now()
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
    
    def get_transaction_id(self) -> str:
        return self._transaction_id
    
    def get_user_id(self) -> str:
        return self._user_id
    
    def get_transaction_type(self) -> TransactionType:
        return self._transaction_type
    
    def get_amount(self) -> float:
        return self._amount
    
    def get_description(self) -> Optional[str]:
        return self._description
    
    def set_description(self, description: str) -> None:
        self._description = description
    
    def get_created_at(self) -> datetime:
        return self._created_at
    
    def is_deposit(self) -> bool:
        return self._transaction_type == TransactionType.DEPOSIT
    
    def is_withdrawal(self) -> bool:
        return self._transaction_type == TransactionType.WITHDRAWAL
    
    def _generate_transaction_id(self) -> str:
        return str(uuid.uuid4())
    
    def to_dict(self) -> dict:
        return {
            "transaction_id": self._transaction_id,
            "user_id": self._user_id,
            "transaction_type": self._transaction_type.value,
            "amount": self._amount,
            "description": self._description,
            "created_at": self._created_at.isoformat()
        }

