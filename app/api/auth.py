from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.repositories import create_user, get_user_by_email
from app.core.security import verify_password, create_access_token, get_current_user
from app.core.config import settings
from app.models.user import UserDB

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    from app.models.user import UserDB
    existing = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = create_user(
        db=db,
        telegram_id=payload.telegram_id,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role="user",
        initial_balance=0.0,
    )
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        telegram_id=user.telegram_id,
        balance=user.balance,
        role=user.role,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    tags=["auth"],
    summary="Авторизация пользователя"
)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Информация о текущем пользователе"
)
def get_current_user_info(
    current_user: UserDB = Depends(get_current_user)
):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        telegram_id=current_user.telegram_id,
        balance=current_user.balance,
        role=current_user.role,
    )

