from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

from db import SessionLocal, Base, engine
from db_models import UserDB
from repositories import (
    create_user,
    get_user_by_telegram_id,
    deposit,
    get_transactions,
    get_user_balance,
    get_predictions,
    add_prediction,
)
from sqlalchemy.orm import Session


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Secretary API",
    version="1.0.0",
    tags_metadata=[
        {
            "name": "health",
            "description": "Проверка работоспособности API",
        },
        {
            "name": "auth",
            "description": "Регистрация и авторизация пользователей",
        },
        {
            "name": "balance",
            "description": "Управление балансом пользователя",
        },
        {
            "name": "transactions",
            "description": "История транзакций",
        },
        {
            "name": "predictions",
            "description": "Работа с ML-предсказаниями",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email")
    telegram_id: Optional[str] = Field(None, description="Telegram ID (опционально)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Иван Иванов",
                "email": "ivan@example.com",
                "telegram_id": None
            }
        }


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    telegram_id: Optional[str] = None
    balance: float
    role: str

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "ivan@example.com"
            }
        }


class BalanceResponse(BaseModel):
    balance: float


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


class TransactionResponse(BaseModel):
    id: str
    type: str
    amount: float
    description: Optional[str]
    created_at: str
    balance_after: float


class PredictionRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя")
    text: str = Field(..., min_length=1, description="Текст для обработки ML-моделью")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "text": "Создай событие на завтра в 15:00"
            }
        }


class PredictionResponse(BaseModel):
    id: str
    user_id: str
    input_data: str
    output_data: Optional[str]
    model_type: str
    confidence: Optional[float]
    created_at: str

    class Config:
        from_attributes = True


@app.get("/", tags=["health"], summary="Главная")
async def root():
    return {"message": "Hello World"}


@app.get("/health", tags=["health"], summary="Проверка работоспособности API")
async def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя в системе. Telegram ID опционален"
)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
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
        role="user",
        initial_balance=0.0,
    )
    return user


@app.post(
    "/auth/login",
    response_model=UserResponse,
    tags=["auth"],
    summary="Авторизация пользователя",
    description="авторизация по email"
)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@app.get(
    "/users/{user_id}/balance",
    response_model=BalanceResponse,
    tags=["balance"],
    summary="текущий баланс пользователя"
)
def get_balance(user_id: str, db: Session = Depends(get_db)):
    try:
        balance_value = get_user_balance(db, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return BalanceResponse(balance=balance_value)


@app.post(
    "/users/{user_id}/balance/deposit",
    response_model=TransactionResponse,
    tags=["balance"],
    summary="Пополнить баланс",
    description="Добавляет средства на баланс и создает транзакцию"
)
def add_funds(user_id: str, payload: DepositRequest, db: Session = Depends(get_db)):
    try:
        tx = deposit(
            db=db,
            user_id=user_id,
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


@app.get(
    "/users/{user_id}/transactions",
    response_model=List[TransactionResponse],
    tags=["transactions"],
    summary="Получить историю транзакций",
    description="список транзакций"
)
def list_transactions(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="Максимальное количество транзакций"),
    db: Session = Depends(get_db)
):
    txs = get_transactions(db, user_id=user_id, limit=limit)
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


@app.post(
    "/predict/text",
    response_model=PredictionResponse,
    tags=["predictions"],
    summary="Отправить текст на обработку ML-моделью",
    description="Обрабатывает текст через ML-модель и сохраняет результат в историю предсказаний"
)
def predict_text(payload: PredictionRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == payload.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Заглушка
    output = f"Predicted command for text: {payload.text}"

    prediction = add_prediction(
        db=db,
        user_id=payload.user_id,
        input_data=payload.text,
        output_data=output,
        model_type="text_to_command_stub",
        confidence=None,
    )

    return PredictionResponse(
        id=prediction.id,
        user_id=prediction.user_id,
        input_data=prediction.input_data,
        output_data=prediction.output_data,
        model_type=prediction.model_type,
        confidence=prediction.confidence,
        created_at=prediction.created_at.isoformat(),
    )


@app.get(
    "/users/{user_id}/predictions",
    response_model=List[PredictionResponse],
    tags=["predictions"],
    summary="Получить историю предсказаний",
    description="Возвращает список всех предсказаний юзера"
)
def list_predictions(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="Максимальное количество предсказаний"),
    db: Session = Depends(get_db),
):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    predictions = get_predictions(db, user_id=user_id, limit=limit)
    return [
        PredictionResponse(
            id=p.id,
            user_id=p.user_id,
            input_data=p.input_data,
            output_data=p.output_data,
            model_type=p.model_type,
            confidence=p.confidence,
            created_at=p.created_at.isoformat(),
        )
        for p in predictions
    ]
