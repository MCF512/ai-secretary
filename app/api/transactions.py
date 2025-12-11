from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.models.user import UserDB
from app.schemas.transaction import TransactionResponse
from app.repositories import get_transactions

router = APIRouter(prefix="/users/me", tags=["transactions"])


@router.get(
    "/transactions",
    response_model=List[TransactionResponse],
    summary="Получить историю транзакций",
)
def list_transactions(
    limit: int = Query(20, ge=1, le=100, description="Максимальное количество транзакций"),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    txs = get_transactions(db, user_id=current_user.id, limit=limit)
    return [
        TransactionResponse(
            id=tx.id,
            type=tx.type.value,
            amount=tx.amount,
            description=tx.description,
            created_at=tx.created_at.isoformat(),
            balance_after=tx.balance_after,
        )
        for tx in txs
    ]

