## ИИ-секретарь
Идея приложения — взаимодействие с календарём (и, возможно, списком дел) через Telegram‑бота с ML‑моделью.

Для распознавания речи используется модель  
[`bond005/whisper-podlodka-turbo`](https://huggingface.co/bond005/whisper-podlodka-turbo).

### Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

На macOS/Linux желательно установить `ffmpeg`, чтобы `transformers` мог читать аудио:

```bash
brew install ffmpeg
```

### Запуск FastAPI

```bash
uvicorn main:app --reload
```

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
