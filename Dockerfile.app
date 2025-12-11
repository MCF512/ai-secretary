FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements-base.txt requirements-app.txt ./
RUN pip install --no-cache-dir -r requirements-app.txt

COPY app/ ./app/
COPY classes/ ./classes/
COPY .env* ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

