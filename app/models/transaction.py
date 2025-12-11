from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


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

