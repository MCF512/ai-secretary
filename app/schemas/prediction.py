from pydantic import BaseModel, Field
from typing import Optional


class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Текст для обработки ML-моделью")

    class Config:
        json_schema_extra = {
            "example": {
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

