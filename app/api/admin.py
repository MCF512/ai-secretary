from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.core.security import get_current_user
from app.models.user import UserDB
from app.schemas.transaction import DepositRequest, TransactionResponse
from app.schemas.auth import UserResponse
from app.repositories import deposit, get_transactions, get_user_by_id

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Получить список пользователей (только для админов)",
)
def list_users(
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(UserDB).order_by(UserDB.email.asc()).all()
    return users


@router.post(
    "/users/{user_id}/balance/deposit",
    response_model=TransactionResponse,
    summary="Пополнить баланс пользователя (только для админов)"
)
def admin_deposit(
    user_id: str,
    payload: DepositRequest,
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        tx = deposit(
            db=db,
            user_id=user_id,
            amount=payload.amount,
            description=payload.description or f"Пополнение баланса администратором {admin.name}",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return TransactionResponse(
        id=tx.id,
        type=tx.type.value,
        amount=tx.amount,
        description=tx.description,
        created_at=tx.created_at.isoformat(),
        balance_after=tx.balance_after,
    )


@router.get(
    "/transactions",
    response_model=List[TransactionResponse],
    summary="Получить все транзакции (только для админов)"
)
def get_all_transactions(
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество транзакций"),
    admin: UserDB = Depends(require_admin),
    db: Session = Depends(get_db)
):
    from app.models.transaction import TransactionDB
    
    txs = db.query(TransactionDB).order_by(TransactionDB.created_at.desc()).limit(limit).all()
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


