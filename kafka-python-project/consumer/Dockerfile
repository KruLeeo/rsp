# consumer/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Копируем requirements.txt из корня контекста сборки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем consumer.py из его подпапки
COPY consumer/consumer.py .

CMD ["python", "consumer.py"]