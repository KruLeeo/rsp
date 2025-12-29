# producer/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Копируем requirements.txt из корня контекста сборки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем producer.py из его подпапки
COPY producer/producer.py .

EXPOSE 5000 

CMD ["python", "producer.py"]