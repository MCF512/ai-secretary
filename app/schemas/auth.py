from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=6, description="Пароль")
    telegram_id: str | None = Field(None, description="Telegram ID (опционально)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Иван Иванов",
                "email": "ivan@example.com",
                "password": "securepassword123",
                "telegram_id": None
            }
        }


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., description="Пароль")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "ivan@example.com",
                "password": "securepassword123"
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    telegram_id: str | None = None
    balance: float
    role: str

    class Config:
        from_attributes = True

