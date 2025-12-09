from typing import List
import uuid

from sqlalchemy.orm import Session

from classes import User, Balance, Transaction, TransactionType
from app.models.user import UserDB
from app.models.transaction import TransactionDB, TransactionTypeDB
from app.models.prediction import PredictionDB
from app.core.security import get_password_hash


def create_user(
    db: Session,
    telegram_id: str | None,
    name: str,
    email: str,
    password: str,
    role: str = "user",
    initial_balance: float = 0.0,
) -> UserDB:
    user = User(telegram_id=telegram_id, name=name, email=email)

    user_db = UserDB(
        id=user.get_user_id(),
        telegram_id=telegram_id,
        name=name,
        email=email,
        hashed_password=get_password_hash(password),
        role=role,
        balance=initial_balance,
        is_active=user.is_active(),
    )

    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


def get_user_by_email(db: Session, email: str) -> UserDB | None:
    return db.query(UserDB).filter(UserDB.email == email).first()


def get_user_by_telegram_id(db: Session, telegram_id: str) -> UserDB | None:
    return db.query(UserDB).filter(UserDB.telegram_id == telegram_id).first()


def _add_transaction(
    db: Session,
    user: UserDB,
    tx_type: TransactionTypeDB,
    amount: float,
    description: str | None = None,
) -> TransactionDB:
    domain_tx = Transaction(
        user_id=user.id,
        transaction_type=TransactionType.DEPOSIT
        if tx_type == TransactionTypeDB.DEPOSIT
        else TransactionType.WITHDRAWAL,
        amount=amount,
        description=description,
    )

    tx = TransactionDB(
        id=domain_tx.get_transaction_id(),
        user_id=user.id,
        type=tx_type,
        amount=amount,
        description=description,
        balance_after=user.balance,
    )
    db.add(tx)
    return tx


def deposit(
    db: Session,
    user_id: str,
    amount: float,
    description: str | None = None,
) -> TransactionDB:
    if amount <= 0:
        raise ValueError("Amount must be positive")

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    balance = Balance(user_id=user.id, initial_balance=user.balance)
    balance.add_funds(amount)
    user.balance = balance.get_amount()

    tx = _add_transaction(
        db,
        user=user,
        tx_type=TransactionTypeDB.DEPOSIT,
        amount=amount,
        description=description or "Пополнение баланса",
    )

    db.commit()
    db.refresh(user)
    db.refresh(tx)
    return tx


def withdraw(
    db: Session,
    user_id: str,
    amount: float,
    description: str | None = None,
) -> TransactionDB:
    if amount <= 0:
        raise ValueError("Amount must be positive")

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    balance = Balance(user_id=user.id, initial_balance=user.balance)
    balance.subtract_funds(amount)
    user.balance = balance.get_amount()

    tx = _add_transaction(
        db,
        user=user,
        tx_type=TransactionTypeDB.WITHDRAWAL,
        amount=amount,
        description=description or "Списание с баланса",
    )

    db.commit()
    db.refresh(user)
    db.refresh(tx)
    return tx


def get_transactions(db: Session, user_id: str, limit: int = 20) -> List[TransactionDB]:
    q = (
        db.query(TransactionDB)
        .filter(TransactionDB.user_id == user_id)
        .order_by(TransactionDB.created_at.desc())
    )
    if limit > 0:
        q = q.limit(limit)
    return q.all()


def get_user_balance(db: Session, user_id: str) -> float:
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    return user.balance


def add_prediction(
    db: Session,
    user_id: str,
    input_data: str,
    output_data: str | None,
    model_type: str,
    confidence: float | None = None,
    task_id: str | None = None,
) -> PredictionDB:
    prediction = PredictionDB(
        id=str(uuid.uuid4()),
        user_id=user_id,
        task_id=task_id,
        input_data=input_data,
        output_data=output_data,
        model_type=model_type,
        confidence=confidence,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def get_predictions(
    db: Session,
    user_id: str,
    limit: int = 20,
) -> List[PredictionDB]:
    q = (
        db.query(PredictionDB)
        .filter(PredictionDB.user_id == user_id)
        .order_by(PredictionDB.created_at.desc())
    )
    if limit > 0:
        q = q.limit(limit)
    return q.all()

