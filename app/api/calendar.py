from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.models.user import UserDB
from app.models.calendar_event import CalendarEventDB
from app.schemas.calendar import (
    CalendarEventRequest,
    CalendarEventUpdateRequest,
    CalendarEventResponse
)

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post(
    "/events",
    response_model=CalendarEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать событие в календаре"
)
def create_event(
    payload: CalendarEventRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.end_time and payload.end_time < payload.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )

    event = CalendarEventDB(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=payload.location,
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return CalendarEventResponse(
        id=event.id,
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat() if event.end_time else None,
        location=event.location,
        created_at=event.created_at.isoformat(),
        updated_at=event.updated_at.isoformat(),
    )


@router.get(
    "/events",
    response_model=List[CalendarEventResponse],
    summary="Получить события календаря"
)
def get_events(
    start_date: Optional[datetime] = Query(None, description="Начальная дата фильтрации"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата фильтрации"),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(CalendarEventDB).filter(CalendarEventDB.user_id == current_user.id)
    
    if start_date:
        query = query.filter(CalendarEventDB.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEventDB.start_time <= end_date)
    
    events = query.order_by(CalendarEventDB.start_time.asc()).all()
    
    return [
        CalendarEventResponse(
            id=event.id,
            user_id=event.user_id,
            title=event.title,
            description=event.description,
            start_time=event.start_time.isoformat(),
            end_time=event.end_time.isoformat() if event.end_time else None,
            location=event.location,
            created_at=event.created_at.isoformat(),
            updated_at=event.updated_at.isoformat(),
        )
        for event in events
    ]


@router.get(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
    summary="Получить событие по ID"
)
def get_event(
    event_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(CalendarEventDB).filter(
        CalendarEventDB.id == event_id,
        CalendarEventDB.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return CalendarEventResponse(
        id=event.id,
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat() if event.end_time else None,
        location=event.location,
        created_at=event.created_at.isoformat(),
        updated_at=event.updated_at.isoformat(),
    )


@router.put(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
    summary="Обновить событие"
)
def update_event(
    event_id: str,
    payload: CalendarEventUpdateRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(CalendarEventDB).filter(
        CalendarEventDB.id == event_id,
        CalendarEventDB.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if payload.title is not None:
        event.title = payload.title
    if payload.description is not None:
        event.description = payload.description
    if payload.start_time is not None:
        event.start_time = payload.start_time
    if payload.end_time is not None:
        event.end_time = payload.end_time
    if payload.location is not None:
        event.location = payload.location
    
    if event.end_time and event.end_time < event.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    
    return CalendarEventResponse(
        id=event.id,
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat() if event.end_time else None,
        location=event.location,
        created_at=event.created_at.isoformat(),
        updated_at=event.updated_at.isoformat(),
    )


@router.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить событие"
)
def delete_event(
    event_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(CalendarEventDB).filter(
        CalendarEventDB.id == event_id,
        CalendarEventDB.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(event)
    db.commit()
    
    return None


