from .user import User
from .ml_model import MLModel
from .text_to_command_model import TextToCommandModel
from .ml_task import MLTask
from .prediction_history import PredictionHistory
from .calendar_event import CalendarEvent
from .calendar import Calendar
from .command import Command
from .commands import (
    CreateEventCommand,
    DeleteEventCommand,
    UpdateEventCommand,
    ListEventsCommand
)
from .service import Service
from .balance import Balance
from .transaction import Transaction, TransactionType

__all__ = [
    "User",
    "MLModel",
    "TextToCommandModel",
    "MLTask",
    "PredictionHistory",
    "CalendarEvent",
    "Calendar",
    "Command",
    "CreateEventCommand",
    "DeleteEventCommand",
    "UpdateEventCommand",
    "ListEventsCommand",
    "Service",
    "Balance",
    "Transaction",
    "TransactionType",
]

def __getattr__(name):
    if name == "SpeechToTextModel":
        from .speech_to_text_model import SpeechToTextModel
        return SpeechToTextModel
    if name == "MLService":
        from .ml_service import MLService
        return MLService
    if name == "TgBot":
        from .bot import TgBot
        return TgBot
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

