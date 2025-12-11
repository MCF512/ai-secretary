from pydantic import BaseModel, Field
from typing import Optional


class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма пополнения")
    description: Optional[str] = Field(None, description="Описание транзакции")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 100.0,
                "description": "Пополнение баланса"
            }
        }


class BalanceResponse(BaseModel):
    balance: float


class TransactionResponse(BaseModel):
    id: str
    type: str
    amount: float
    description: Optional[str]
    created_at: str
    balance_after: float

