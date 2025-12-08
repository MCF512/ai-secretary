from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import UserDB
from app.core.security import get_current_user


def get_db_dependency() -> Session:
    return Depends(get_db)


def get_current_user_dependency() -> UserDB:
    return Depends(get_current_user)

