from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CalendarEventRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Название события")
    description: Optional[str] = Field(None, description="Описание события")
    start_time: datetime = Field(..., description="Время начала события")
    end_time: Optional[datetime] = Field(None, description="Время окончания события")
    location: Optional[str] = Field(None, description="Место проведения события")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Встреча с командой",
                "description": "Обсуждение проекта",
                "start_time": "2024-12-12T15:00:00",
                "end_time": "2024-12-12T16:00:00",
                "location": "Офис"
            }
        }


class CalendarEventUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Название события")
    description: Optional[str] = Field(None, description="Описание события")
    start_time: Optional[datetime] = Field(None, description="Время начала события")
    end_time: Optional[datetime] = Field(None, description="Время окончания события")
    location: Optional[str] = Field(None, description="Место проведения события")


class CalendarEventResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    start_time: str
    end_time: Optional[str]
    location: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


