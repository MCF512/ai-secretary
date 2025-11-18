from typing import Any, Dict, List
from .ml_model import MLModel


class TextToCommandModel(MLModel):
    def __init__(self, model_path: str):
        super().__init__(model_path, "text_to_command")
        self._command_types: List[str] = [
            "create_event",
            "delete_event",
            "update_event",
            "list_events"
        ]
        self._confidence_threshold: float = 0.7
    
    def load_model(self) -> None:
        self._model = "loaded_command_model"
        self._is_loaded = True
        print("TextToCommandModel loaded")
    
    def predict(self, text: str) -> Dict[str, Any]:
        if not self._is_loaded:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
        
        command_data = self._parse_command(text)
        
        return {
            "command_type": command_data.get("command_type"),
            "parameters": command_data.get("parameters", {}),
            "confidence": command_data.get("confidence", 0.9)
        }
    
    def save_model(self, path: str) -> None:
        print(f"TextToCommandModel saved to {path}")
    
    def get_supported_commands(self) -> List[str]:
        return self._command_types.copy()
    
    def set_confidence_threshold(self, threshold: float) -> None:
        if 0.0 <= threshold <= 1.0:
            self._confidence_threshold = threshold
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
    
    def _parse_command(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["создай", "добавь", "запланируй", "create", "add"]):
            return {
                "command_type": "create_event",
                "parameters": {"title": text},
                "confidence": 0.9
            }
        elif any(word in text_lower for word in ["удали", "убери", "отмени", "delete", "remove"]):
            return {
                "command_type": "delete_event",
                "parameters": {},
                "confidence": 0.85
            }
        elif any(word in text_lower for word in ["измени", "обнови", "update", "change"]):
            return {
                "command_type": "update_event",
                "parameters": {},
                "confidence": 0.8
            }
        elif any(word in text_lower for word in ["покажи", "список", "события", "show", "list"]):
            return {
                "command_type": "list_events",
                "parameters": {},
                "confidence": 0.9
            }
        
        return {
            "command_type": "unknown",
            "parameters": {},
            "confidence": 0.0
        }
