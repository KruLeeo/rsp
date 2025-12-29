import os
import json
import time
from kafka import KafkaConsumer

# Конфигурация
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')
INPUT_TOPIC = os.environ.get('INPUT_TOPIC', 'input_topic')
GROUP_ID = os.environ.get('GROUP_ID', 'my-consumer-group')
DLQ_TOPIC = os.environ.get('DLQ_TOPIC', 'dlq_topic') # Dead Letter Queue Topic

# Пользовательская логика обработки (Задание 3.2: Обработка сообщений с применением пользовательской логики)
def custom_processing_logic(data):
    """Пример логики: подсчет статистики и фильтрация."""
    # Фильтрация: Обрабатываем только сообщения со статусом 'SUCCESS'
    if data.get('status') != 'SUCCESS':
        print(f"    ➡️ Сообщение отфильтровано (статус: {data.get('status')})")
        return False
    
    # Подсчет статистики: Условная "тяжелая" обработка
    if data.get('value', 0) > 50:
        print(f"    ✅ Обработка: Значение {data['value']} выше 50. Регистрируем как 'важную транзакцию'.")
    else:
        print(f"    ✅ Обработка: Значение {data['value']} ниже или равно 50. Регистрируем как 'обычную транзакцию'.")
        
    return True

# Создание консьюмера
def create_kafka_consumer():
    try:
        consumer = KafkaConsumer(
            INPUT_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            group_id=GROUP_ID,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            # Задание 6: Логирование ошибок при подключении
            api_version=(0, 10, 1) 
        )
        print(f"✅ Kafka Consumer '{GROUP_ID}' подключен к {KAFKA_BROKER} и слушает топик '{INPUT_TOPIC}'")
        return consumer
    except Exception as e:
        # Задание 6: Логирование ошибок при подключении
        print(f"❌ Ошибка подключения Kafka Consumer: {e}")
        time.sleep(5)
        return create_kafka_consumer()

def run_consumer():
    consumer = create_kafka_consumer()

    for message in consumer:
        # Задание 3.1: Читает сообщения из указанной темы
        data = message.value
        print(f"⬅️ Получено сообщение: офсет={message.offset}, данные={data}")
        
        try:
            # Задание 3.1: Обрабатывает полученные данные (выводит в консоль)
            if custom_processing_logic(data):
                 print(f"    ⭐ Обработка завершена для ID: {data['id']}")

        except Exception as e:
            # Задание 6: Реализация обработки ошибок / Использование DLQ
            print(f"❌ Критическая ошибка при обработке данных: {e}. Отправка в DLQ.")
            # В реальном приложении здесь нужно отправить сообщение в DLQ_TOPIC с помощью отдельного Producer
            # Для простоты:
            print(f"    ⚠️ Сообщение отправлено в 'виртуальный' DLQ: {DLQ_TOPIC}")

if __name__ == '__main__':
    run_consumer()