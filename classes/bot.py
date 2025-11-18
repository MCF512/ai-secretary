from typing import Dict, Optional, Any
from datetime import datetime
from .service import Service
from .ml_service import MLService
from .calendar import Calendar
from .user import User
from .command import Command
from .commands import CreateEventCommand, DeleteEventCommand


class TgBot(Service):
    def __init__(self, bot_token: str, ml_service: MLService, calendar: Calendar):
        super().__init__("TgBot")
        self._bot: Any = None
        self._bot_token: str = bot_token
        self._ml_service: MLService = ml_service
        self._calendar: Calendar = calendar
        self._users: Dict[str, User] = {}
        self._pending_confirmations: Dict[str, Command] = {}
    
    def start(self) -> None:
        if not self._bot_token or len(self._bot_token) < 10:
            raise ValueError("Invalid bot token")
        
        self._is_running = True
        self._started_at = datetime.now()
        print(f"{self._service_name} started")
    
    def stop(self) -> None:
        self._is_running = False
        self._pending_confirmations.clear()
        print(f"{self._service_name} stopped")
    
    def handle_voice_message(self, message: Any) -> None:
        if not self._is_running:
            return
        
        telegram_id = str(message.from_user.id)
        user = self._get_user(telegram_id)
        
        if not user:
            user = self._register_user(telegram_id, message.from_user.first_name)
        
        audio_data = b"fake_audio_data"
        
        try:
            command = self._ml_service.process_voice_message(audio_data, user.get_user_id())
            
            if isinstance(command, (CreateEventCommand, DeleteEventCommand)):
                self.request_confirmation(user.get_user_id(), command)
            else:
                self._execute_command(user.get_user_id(), command)
                
        except Exception as e:
            self.send_message(user.get_user_id(), f"Ошибка: {str(e)}")
    
    def handle_text_message(self, message: Any) -> None:
        if not self._is_running:
            return
        
        telegram_id = str(message.from_user.id)
        user = self._get_user(telegram_id)
        
        if not user:
            user = self._register_user(telegram_id, message.from_user.first_name)
        
        text = message.text
        
        try:
            command = self._ml_service.process_text_message(text, user.get_user_id())
            
            if isinstance(command, (CreateEventCommand, DeleteEventCommand)):
                self.request_confirmation(user.get_user_id(), command)
            else:
                self._execute_command(user.get_user_id(), command)
                
        except Exception as e:
            self.send_message(user.get_user_id(), f"Ошибка: {str(e)}")
    
    def send_message(self, user_id: str, text: str) -> None:
        print(f"Message to {user_id}: {text}")
    
    def request_confirmation(self, user_id: str, command: Command) -> None:
        self._pending_confirmations[user_id] = command
        
        command_description = self._get_command_description(command)
        message = f"Подтвердите действие:\n{command_description}\n\nОтправьте 'да' для подтверждения или 'нет' для отмены."
        self.send_message(user_id, message)
    
    def handle_confirmation(self, user_id: str, confirmed: bool) -> None:
        command = self._pending_confirmations.pop(user_id, None)
        
        if not command:
            self.send_message(user_id, "Нет ожидающих подтверждения команд.")
            return
        
        if confirmed:
            self._execute_command(user_id, command)
            self.send_message(user_id, "Действие выполнено.")
        else:
            self.send_message(user_id, "Действие отменено.")
    
    def get_user_calendar(self, user_id: str) -> Optional[Calendar]:
        return self._calendar
    
    def _register_user(self, telegram_id: str, name: str) -> User:
        email = f"{telegram_id}@telegram.local"
        user = User(telegram_id=telegram_id, name=name, email=email)
        self._users[user.get_user_id()] = user
        return user
    
    def _get_user(self, telegram_id: str) -> Optional[User]:
        for user in self._users.values():
            if user.get_telegram_id() == telegram_id:
                return user
        return None
    
    def _execute_command(self, user_id: str, command: Command) -> None:
        try:
            result = command.execute(self._calendar)
            
            if result.get("success"):
                self.send_message(user_id, f"Команда выполнена успешно: {command.get_command_type()}")
            else:
                error = result.get("error", "Unknown error")
                self.send_message(user_id, f"Ошибка выполнения команды: {error}")
        except Exception as e:
            self.send_message(user_id, f"Ошибка: {str(e)}")
    
    def _get_command_description(self, command: Command) -> str:
        command_type = command.get_command_type()
        
        if command_type == "create_event":
            return f"Создать событие: {command._title}"
        elif command_type == "delete_event":
            return f"Удалить событие: {command._event_id}"
        elif command_type == "update_event":
            return f"Обновить событие: {command._event_id}"
        else:
            return f"Выполнить команду: {command_type}"
