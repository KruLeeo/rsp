import os

import json

import time

from kafka import KafkaConsumer, KafkaProducer



# Конфигурация

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')

INPUT_TOPIC = os.environ.get('INPUT_TOPIC', 'input_topic')

OUTPUT_TOPIC = os.environ.get('OUTPUT_TOPIC', 'output_topic')

GROUP_ID = 'stream-processor-group'



# Создание Producer и Consumer

def create_kafka_clients():

    producer = KafkaProducer(

        bootstrap_servers=[KAFKA_BROKER],

        value_serializer=lambda v: json.dumps(v).encode('utf-8')

    )

    consumer = KafkaConsumer(

        INPUT_TOPIC,

        bootstrap_servers=[KAFKA_BROKER],

        group_id=GROUP_ID,

        auto_offset_reset='earliest',

        value_deserializer=lambda x: json.loads(x.decode('utf-8'))

    )

    print(f"✅ Stream Processor запущен. Чтение из '{INPUT_TOPIC}', запись в '{OUTPUT_TOPIC}'")

    return producer, consumer



# Задание 4: Логика преобразования

def transform_message(original_data):

    """

    1. Преобразует (меняет формат, добавляет доп. поля).

    Например, добавляет поле 'processed_at' и меняет ключ 'value' на 'metric_value'.

    """

    transformed_data = {

        'source_id': original_data.get('id'),

        'metric_value': original_data.get('value'),

        'original_status': original_data.get('status'),

        'processed_at': int(time.time() * 1000), # Дополнительное поле

        'unit': 'EUR' # Дополнительное поле

    }

    return transformed_data



def run_stream_processor():

    producer, consumer = create_kafka_clients()



    for message in consumer:

        original_data = message.value

       

        # 1. Читает данные из одной темы

        print(f"  > ⬅️ Получено из '{INPUT_TOPIC}': {original_data}")



        # 2. Преобразует их

        transformed_data = transform_message(original_data)

       

        # 3. Отправляет результат в другую тему

        try:

            producer.send(OUTPUT_TOPIC, transformed_data)

            producer.flush()

            print(f"  > ➡️ Отправлено в '{OUTPUT_TOPIC}': {transformed_data}")

        except Exception as e:

            print(f"❌ Ошибка при отправке в OUTPUT_TOPIC: {e}")



if __name__ == '__main__':

    run_stream_processor()