from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transactions = relationship(
        "TransactionDB",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    predictions = relationship(
        "PredictionDB",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    calendar_events = relationship(
        "CalendarEventDB",
        back_populates="user",
        cascade="all, delete-orphan",
    )

