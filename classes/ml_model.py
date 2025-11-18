from abc import ABC, abstractmethod
from typing import Any


class MLModel(ABC):
    def __init__(self, model_path: str, model_type: str):
        self._model: Any = None
        self._model_path: str = model_path
        self._is_loaded: bool = False
        self._model_type: str = model_type
        
        if not self._validate_model_path(model_path):
            raise ValueError(f"Invalid model path: {model_path}")
    
    @abstractmethod
    def load_model(self) -> None:
        pass
    
    @abstractmethod
    def predict(self, input_data: Any) -> Any:
        pass
    
    @abstractmethod
    def save_model(self, path: str) -> None:
        pass
    
    def get_model_type(self) -> str:
        return self._model_type
    
    def is_loaded(self) -> bool:
        return self._is_loaded
    
    def _validate_model_path(self, path: str) -> bool:
        return path is not None and len(path) > 0
