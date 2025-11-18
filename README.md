# ИИ-секретарь
Идея приложения - взаимодействие с календарем (возможно еще со списком дел) с помощью телеграм-бота с ML-моделью. 
Будет использована модель [whisper-podlodka](https://huggingface.co/bond005/whisper-podlodka-turbo) для расшивровки голосовых сообщений от пользователя в текст. Также планируется использование llm для взаимодействия с командами календаря (добавить, удалить).

- source venv/bin/avtivate
- pip install -r requirements.txt
- uvicorn main:app --reload