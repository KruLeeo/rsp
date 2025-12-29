# stream-processor/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Копируем requirements.txt из корня контекста сборки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем stream_processor.py из его подпапки
COPY stream-processor/stream_processor.py .

CMD ["python", "stream_processor.py"]