from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.models.user import UserDB
from app.schemas.transaction import BalanceResponse, DepositRequest, TransactionResponse
from app.repositories import deposit, get_user_balance

router = APIRouter(prefix="/users/me", tags=["balance"])


@router.get(
    "/balance",
    response_model=BalanceResponse,
    summary="Текущий баланс пользователя"
)
def get_balance(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        balance_value = get_user_balance(db, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return BalanceResponse(balance=balance_value)


@router.post(
    "/balance/deposit",
    response_model=TransactionResponse,
    summary="Пополнить баланс",
    description="Добавляет средства на баланс и создает транзакцию"
)
def add_funds(
    payload: DepositRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can deposit funds"
        )

    try:
        tx = deposit(
            db=db,
            user_id=current_user.id,
            amount=payload.amount,
            description=payload.description,
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

