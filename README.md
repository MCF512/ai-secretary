# ИИ-секретарь
Идея приложения - взаимодействие с календарем (возможно еще со списком дел) с помощью телеграм-бота с ML-моделью. 
Будет использована модель [whisper-podlodka](https://huggingface.co/bond005/whisper-podlodka-turbo) для расшивровки голосовых сообщений от пользователя в текст. Также планируется использование llm для взаимодействия с командами календаря (добавить, удалить).

- source venv/bin/activate
- pip install -r requirements.txt
- uvicorn main:app --reload

# ENV example

```
POSTGRES_DB=ai_secretary
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@database:5432/ai_secretary

RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

APP_HOST=0.0.0.0
APP_PORT=8000
```