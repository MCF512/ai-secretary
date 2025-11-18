from typing import List, Any
from datetime import datetime
from .service import Service
from .speech_to_text_model import SpeechToTextModel
from .text_to_command_model import TextToCommandModel
from .ml_task import MLTask
from .prediction_history import PredictionHistory
from .commands import Command, CreateEventCommand, DeleteEventCommand, UpdateEventCommand, ListEventsCommand


class MLService(Service):
    def __init__(self, speech_model_path: str, command_model_path: str, user_id: str):
        super().__init__("MLService")
        self._speech_to_text_model: SpeechToTextModel = SpeechToTextModel(speech_model_path)
        self._text_to_command_model: TextToCommandModel = TextToCommandModel(command_model_path)
        self._task_queue: List[MLTask] = []
        self._history: PredictionHistory = PredictionHistory(user_id)
        self._user_id: str = user_id
    
    def start(self) -> None:
        self._initialize_models()
        self._is_running = True
        self._started_at = datetime.now()
        print(f"{self._service_name} started")
    
    def stop(self) -> None:
        self._is_running = False
        self._task_queue.clear()
        print(f"{self._service_name} stopped")
    
    def process_voice_message(self, audio_data: bytes, user_id: str) -> Command:
        if not self._is_running:
            raise RuntimeError("Service is not running")
        
        speech_task = MLTask("speech_to_text", audio_data, user_id)
        self.add_task(speech_task)
        
        text = self.process_task(speech_task)
        
        self._history.add_record(
            task_id=speech_task.get_task_id(),
            input_data=audio_data,
            output_data=text,
            model_type="speech_to_text",
            confidence=0.9
        )
        
        return self.process_text_message(text, user_id)
    
    def process_text_message(self, text: str, user_id: str) -> Command:
        if not self._is_running:
            raise RuntimeError("Service is not running")
        
        command_task = MLTask("text_to_command", text, user_id)
        self.add_task(command_task)
        
        command_data = self.process_task(command_task)
        
        self._history.add_record(
            task_id=command_task.get_task_id(),
            input_data=text,
            output_data=command_data,
            model_type="text_to_command",
            confidence=command_data.get("confidence", 0.8)
        )
        
        return self._create_command_from_data(command_data, user_id)
    
    def add_task(self, task: MLTask) -> None:
        self._task_queue.append(task)
    
    def process_task(self, task: MLTask) -> Any:
        if task.get_task_type() == "speech_to_text":
            audio_data = task._input_data
            text = self._speech_to_text_model.predict(audio_data)
            task._output_data = text
            task.set_status("completed")
            return text
        
        elif task.get_task_type() == "text_to_command":
            text = task._input_data
            command_data = self._text_to_command_model.predict(text)
            task._output_data = command_data
            task.set_status("completed")
            return command_data
        
        else:
            task.set_status("failed")
            raise ValueError(f"Unknown task type: {task.get_task_type()}")
    
    def get_history(self) -> PredictionHistory:
        return self._history
    
    def _initialize_models(self) -> None:
        self._speech_to_text_model.load_model()
        self._text_to_command_model.load_model()
    
    def _process_task_queue(self) -> None:
        while self._task_queue:
            task = self._task_queue.pop(0)
            try:
                self.process_task(task)
            except Exception as e:
                task.set_status("failed")
                print(f"Task {task.get_task_id()} failed: {e}")
    
    def _create_command_from_data(self, command_data: dict, user_id: str) -> Command:
        command_type = command_data.get("command_type")
        parameters = command_data.get("parameters", {})
        
        if command_type == "create_event":
            return CreateEventCommand(
                user_id=user_id,
                title=parameters.get("title", "Новое событие"),
                start_time=parameters.get("start_time", datetime.now()),
                description=parameters.get("description"),
                end_time=parameters.get("end_time"),
                location=parameters.get("location")
            )
        elif command_type == "delete_event":
            return DeleteEventCommand(
                user_id=user_id,
                event_id=parameters.get("event_id", "")
            )
        elif command_type == "update_event":
            updates = {k: v for k, v in parameters.items() if k != "event_id"}
            return UpdateEventCommand(
                user_id=user_id,
                event_id=parameters.get("event_id", ""),
                **updates
            )
        elif command_type == "list_events":
            return ListEventsCommand(
                user_id=user_id,
                start_date=parameters.get("start_date"),
                end_date=parameters.get("end_date")
            )
        else:
            raise ValueError(f"Unknown command type: {command_type}")
