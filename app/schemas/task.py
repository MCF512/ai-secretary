from pydantic import BaseModel, Field
from typing import Optional


class MLTaskRequest(BaseModel):
    task_id: str = Field(..., description="ID задачи")
    user_id: str = Field(..., description="ID пользователя")
    task_type: str = Field(..., description="Тип задачи (text_to_command)")
    input_data: str = Field(..., description="Входные данные для обработки")
    prediction_id: str = Field(..., description="ID предсказания в БД")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "task_type": "text_to_command",
                "input_data": "Создай событие на завтра в 15:00",
                "prediction_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class MLTaskResult(BaseModel):
    task_id: str
    prediction_id: str
    output_data: Optional[str] = None
    confidence: Optional[float] = None
    status: str = Field(..., description="Статус: completed или failed")
    error: Optional[str] = None

