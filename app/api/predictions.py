from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.models.user import UserDB
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.repositories import add_prediction, get_predictions, withdraw
from app.rabbitmq.publisher import publisher

router = APIRouter(prefix="", tags=["predictions"])

PREDICTION_COST = 10.0


@router.post(
    "/predict/text",
    response_model=PredictionResponse,
    summary="Отправить текст на обработку ML-моделью",
)
def predict_text(
    payload: PredictionRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.refresh(current_user)
    
    if current_user.balance < PREDICTION_COST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds. Required: {PREDICTION_COST}, Available: {current_user.balance}",
        )

    task_id = str(uuid.uuid4())
    prediction_id = str(uuid.uuid4())
    
    prediction = add_prediction(
        db=db,
        id=prediction_id,
        user_id=current_user.id,
        input_data=payload.text,
        output_data=None,
        model_type="text_to_command",
        confidence=None,
        task_id=task_id,
    )

    try:
        withdraw(
            db=db,
            user_id=current_user.id,
            amount=PREDICTION_COST,
            description=f"Оплата предсказания #{prediction.id}",
        )
    except ValueError as e:
        db.delete(prediction)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    task_data = {
        'task_id': task_id,
        'user_id': current_user.id,
        'task_type': 'text_to_command',
        'input_data': payload.text,
        'prediction_id': prediction.id
    }

    if not publisher.publish_task(task_data):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish task to queue"
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


@router.get(
    "/users/me/predictions",
    response_model=List[PredictionResponse],
    summary="Получить историю предсказаний",
)
def list_predictions(
    limit: int = Query(20, ge=1, le=100, description="Максимальное количество предсказаний"),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    predictions = get_predictions(db, user_id=current_user.id, limit=limit)
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

