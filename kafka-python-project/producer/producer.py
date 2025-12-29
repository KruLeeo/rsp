import os

import time

import json

import random

from kafka import KafkaProducer

from flask import Flask, request, jsonify



# Конфигурация

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')

INPUT_TOPIC = os.environ.get('INPUT_TOPIC', 'input_topic')

FLASK_PORT = 5000



# Создание продюсера

def create_kafka_producer():

    try:

        producer = KafkaProducer(

            bootstrap_servers=[KAFKA_BROKER],

            value_serializer=lambda v: json.dumps(v).encode('utf-8'),

            # Задание 6: Логирование ошибок при подключении

            api_version=(0, 10, 1)

        )

        print(f"✅ Kafka Producer подключен к {KAFKA_BROKER}")

        return producer

    except Exception as e:

        # Задание 6: Логирование ошибок при подключении

        print(f"❌ Ошибка подключения Kafka Producer: {e}")

        time.sleep(5)

        return create_kafka_producer() # Попытка переподключения



producer = create_kafka_producer()

app = Flask(__name__)



# Функция для генерации случайных данных

def generate_message():

    user_id = random.randint(100, 999)

    return {

        'id': user_id,

        'timestamp': int(time.time() * 1000),

        'value': random.uniform(10.0, 100.0),

        'status': random.choice(['SUCCESS', 'FAILURE', 'PENDING'])

    }



# Функция для отправки сообщения в Kafka

def send_to_kafka(data, topic):

    try:

        # Задание 2.1: Создает тему (если не существует) - Kafka сделает это автоматически при первой отправке

        future = producer.send(topic, data)

        producer.flush() # Ждем подтверждения

        record_metadata = future.get(timeout=10) # Задание 6: Добавление обработки ошибок

        print(f"➡️ Отправлено в топик: {record_metadata.topic}, партиция: {record_metadata.partition}, офсет: {record_metadata.offset}. Данные: {data}")

    except Exception as e:

        print(f"❌ Ошибка при отправке сообщения: {e}. Данные: {data}")

# Задание 2.2: Добавление возможности отправки сообщений с использованием HTTP API

@app.route('/api/send', methods=['POST'])

def http_send_message():

    if request.is_json:

        data = request.get_json()

        send_to_kafka(data, INPUT_TOPIC)

        return jsonify({"status": "Message sent", "data": data}), 200

    return jsonify({"error": "Request must be JSON"}), 400



# Главный цикл для автоматической отправки

def auto_send_loop():

    while True:

        message = generate_message()

        send_to_kafka(message, INPUT_TOPIC)

        time.sleep(random.uniform(1, 3))



# Запуск Flask и цикла автоматической отправки

if __name__ == '__main__':

    import threading

    threading.Thread(target=auto_send_loop, daemon=True).start()


    print(f"🌐 Producer HTTP API запущен на порту {FLASK_PORT}")

    app.run(host='0.0.0.0', port=FLASK_PORT)