from typing import List, Dict, Any, Optional
from datetime import datetime


class PredictionHistory:
    def __init__(self, user_id: str, max_records: int = 1000):
        self._history: List[Dict[str, Any]] = []
        self._user_id: str = user_id
        self._max_records: int = max_records
    
    def add_record(self, task_id: str, input_data: Any, output_data: Any,
                   model_type: str, confidence: float) -> None:
        record = {
            "task_id": task_id,
            "input_data": input_data,
            "output_data": output_data,
            "model_type": model_type,
            "confidence": confidence,
            "timestamp": datetime.now(),
            "user_id": self._user_id
        }
        
        self._history.append(record)
        
        if len(self._history) > self._max_records:
            self._cleanup_old_records()
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._history[-limit:] if limit > 0 else self._history.copy()
    
    def get_record_by_task_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        for record in self._history:
            if record["task_id"] == task_id:
                return record
        return None
    
    def clear_history(self) -> None:
        self._history.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        if not self._history:
            return {
                "total_records": 0,
                "average_confidence": 0.0,
                "models_used": []
            }
        
        confidences = [r["confidence"] for r in self._history]
        models_used = list(set(r["model_type"] for r in self._history))
        
        return {
            "total_records": len(self._history),
            "average_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
            "models_used": models_used,
            "user_id": self._user_id
        }
    
    def _cleanup_old_records(self) -> None:
        records_to_remove = len(self._history) - self._max_records
        self._history = self._history[records_to_remove:]
