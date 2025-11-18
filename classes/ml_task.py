from typing import Any, Optional
from datetime import datetime
import uuid
from .ml_model import MLModel


class MLTask(MLModel):
    def __init__(self, task_type: str, input_data: Any, user_id: str):
        super().__init__(model_path="", model_type=task_type)
        self._task_id: str = self._generate_task_id()
        self._task_type: str = task_type
        self._input_data: Any = input_data
        self._output_data: Any = None
        self._status: str = "pending"
        self._created_at: datetime = datetime.now()
        self._completed_at: Optional[datetime] = None
        self._user_id: str = user_id
    
    def execute(self) -> Any:
        if not self._validate_task():
            raise ValueError("Invalid task")
        
        self._status = "processing"
        self._output_data = self._input_data
        self._status = "completed"
        self._completed_at = datetime.now()
        
        return self._output_data
    
    def get_task_id(self) -> str:
        return self._task_id
    
    def get_status(self) -> str:
        return self._status
    
    def get_output(self) -> Any:
        return self._output_data
    
    def set_status(self, status: str) -> None:
        valid_statuses = ["pending", "processing", "completed", "failed"]
        if status in valid_statuses:
            self._status = status
            if status in ["completed", "failed"]:
                self._completed_at = datetime.now()
        else:
            raise ValueError(f"Invalid status: {status}")
    
    def load_model(self) -> None:
        pass
    
    def predict(self, input_data: Any) -> Any:
        return self.execute()
    
    def save_model(self, path: str) -> None:
        pass
    
    def _generate_task_id(self) -> str:
        return str(uuid.uuid4())
    
    def _validate_task(self) -> bool:
        return (
            self._task_type in ["speech_to_text", "text_to_command"] and
            self._input_data is not None and
            len(self._user_id) > 0
        )
