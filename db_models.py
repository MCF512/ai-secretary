from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from db import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="user", nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transactions = relationship(
        "TransactionDB",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class TransactionTypeDB(PyEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    type = Column(Enum(TransactionTypeDB), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    balance_after = Column(Float, nullable=False)

    user = relationship("UserDB", back_populates="transactions")


