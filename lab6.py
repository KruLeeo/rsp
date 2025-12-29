from flask import Flask, request, jsonify
import logging
from flask_cors import CORS
import datetime
import time

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('series_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TurkishSeriesAPI')

app = Flask(__name__)
CORS(app)

# Коллекция турецких сериалов
series = [
    {"id": 1, "title": "Великолепный век", "year": 2011, "episodes": 139, "rating": 8.2},
    {"id": 2, "title": "Любовь напрокат", "year": 2020, "episodes": 52, "rating": 7.8},
    {"id": 3, "title": "Постучи в мою дверь", "year": 2020, "episodes": 52, "rating": 8.1}
]

@app.before_request
def log_request():
    """Детальное логирование запросов"""
    
    app.start_time = time.time() #время начала
    
    logger.info(f"=== ВХОДЯЩИЙ ЗАПРОС ===")
    logger.info(f"Метод: {request.method}")
    logger.info(f"Путь: {request.path}")
    logger.info(f"IP: {request.remote_addr}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Время: {datetime.datetime.now()}")

@app.after_request
def log_response(response):
    
    if hasattr(app, 'start_time'):    # вычисляем время выполнения
        execution_time = time.time() - app.start_time
        execution_time_ms = round(execution_time * 1000, 2)  
        
        logger.info(f"=== ИСХОДЯЩИЙ ОТВЕТ ===")
        logger.info(f"Статус: {response.status_code}")
        logger.info(f"Время выполнения: {execution_time_ms} мс")
        logger.info(f"======================")
        
        
        print(f"⏱️ Время выполнения запроса {request.method} {request.path}: {execution_time_ms} мс")
    else:
        logger.info(f"=== ИСХОДЯЩИЙ ОТВЕТ ===")
        logger.info(f"Статус: {response.status_code}")
        logger.info(f"======================")
    
    response.headers.add('Content-Type', 'application/json; charset=utf-8')
    return response

# 1. ПОЛУЧИТЬ ВСЕ СЕРИАЛЫ
@app.route('/series', methods=['GET'])
def get_all_series():
    start_time = time.time()
    logger.info("🔄 Обработка запроса всех сериалов")
    try:
        logger.debug(f"В базе найдено {len(series)} сериалов")
        for s in series:
            logger.debug(f" - {s['title']} (ID: {s['id']})")
        
        result = jsonify({
            "status": "success",
            "count": len(series),
            "series": series
        })
        
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ Запрос всех сериалов выполнен за {execution_time} мс")
        return result
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ Ошибка при получении сериалов за {execution_time} мс: {str(e)}")
        return jsonify({"error": "Ошибка сервера"}), 500

# 2. ПОЛУЧИТЬ ОДИН СЕРИАЛ
@app.route('/series/<int:series_id>', methods=['GET'])
def get_one_series(series_id):
    start_time = time.time()
    logger.info(f"🔍 Запрос на получение сериала ID: {series_id}")
    try:
        for s in series:
            if s['id'] == series_id:
                logger.info(f"✅ Найден сериал: '{s['title']}'")
                result = jsonify({
                    "status": "success",
                    "series": s
                })
                
                execution_time = round((time.time() - start_time) * 1000, 2)
                logger.info(f"✅ Запрос сериала {series_id} выполнен за {execution_time} мс")
                return result
        
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"⚠️ Сериал с ID {series_id} не найден за {execution_time} мс")
        return jsonify({"error": "Сериал не найден"}), 404
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ Ошибка при получении сериала {series_id} за {execution_time} мс: {str(e)}")
        return jsonify({"error": "Ошибка сервера"}), 500

# 3. ДОБАВИТЬ СЕРИАЛ
@app.route('/series', methods=['POST'])
def add_series():
    start_time = time.time()
    logger.info("🆕 Обработка добавления нового сериала")
    try:
        # Проверяем Content-Type
        if not request.is_json:
            execution_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"❌ Неверный Content-Type за {execution_time} мс. Ожидается application/json")
            return jsonify({"error": "Content-Type должен быть application/json"}), 415
            
        data = request.get_json()
        logger.info(f"Получены данные: {data}")
        
        if not data:
            execution_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"❌ Пустой запрос за {execution_time} мс")
            return jsonify({"error": "Нужны данные в формате JSON"}), 400
            
        if 'title' not in data:
            execution_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"❌ Отсутствует название сериала за {execution_time} мс")
            return jsonify({"error": "Нужно название сериала"}), 400
        
        new_id = max([s['id'] for s in series]) + 1 if series else 1
        
        new_series = {
            'id': new_id,
            'title': data['title'],
            'year': data.get('year', 0),
            'episodes': data.get('episodes', 0),
            'rating': data.get('rating', 0.0)
        }
        
        series.append(new_series)
        
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ Добавлен новый сериал за {execution_time} мс: '{new_series['title']}' (ID: {new_id})")
        logger.info(f"📊 Теперь в базе: {len(series)} сериалов")
        
        return jsonify({
            "status": "success",
            "message": "Сериал добавлен",
            "series": new_series
        }), 201
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ Ошибка при добавлении сериала за {execution_time} мс: {str(e)}")
        return jsonify({"error": "Ошибка сервера"}), 500

# 4. ИЗМЕНИТЬ СЕРИАЛ
@app.route('/series/<int:series_id>', methods=['PUT'])
def update_series(series_id):
    start_time = time.time()
    logger.info(f"✏️ Запрос на обновление сериала ID: {series_id}")
    try:
        # Проверяем Content-Type
        if not request.is_json:
            execution_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"❌ Неверный Content-Type за {execution_time} мс. Ожидается application/json")
            return jsonify({
                "error": "Content-Type должен быть application/json",
                "hint": "Добавьте заголовок: Content-Type: application/json"
            }), 415
            
        data = request.get_json()
        logger.info(f"Получены данные для обновления: {data}")
        
        for s in series:
            if s['id'] == series_id:
                old_data = s.copy()
                
                # Обновляем только переданные поля
                if 'title' in data:
                    s['title'] = data['title']
                if 'year' in data:
                    s['year'] = data['year']
                if 'episodes' in data:
                    s['episodes'] = data['episodes']
                if 'rating' in data:
                    s['rating'] = data['rating']
                
                execution_time = round((time.time() - start_time) * 1000, 2)
                logger.info(f"✅ Сериал обновлен за {execution_time} мс: ID {series_id}")
                logger.info(f"📝 Изменения: {old_data} -> {s}")
                
                return jsonify({
                    "status": "success",
                    "message": "Сериал обновлен",
                    "series": s
                })
        
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"⚠️ Сериал с ID {series_id} не найден за {execution_time} мс")
        return jsonify({"error": "Сериал не найден"}), 404
        
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ Ошибка при обновлении сериала {series_id} за {execution_time} мс: {str(e)}")
        return jsonify({"error": "Ошибка сервера"}), 500

# 5. УДАЛИТЬ СЕРИАЛ
@app.route('/series/<int:series_id>', methods=['DELETE'])
def delete_series(series_id):
    start_time = time.time()
    logger.info(f"🗑️ Запрос на удаление сериала ID: {series_id}")
    try:
        for i, s in enumerate(series):
            if s['id'] == series_id:
                deleted = series.pop(i)
                
                execution_time = round((time.time() - start_time) * 1000, 2)
                logger.info(f"✅ Удален сериал за {execution_time} мс: '{deleted['title']}' (ID: {series_id})")
                logger.info(f"📊 Осталось сериалов: {len(series)}")
                
                return jsonify({
                    "status": "success",
                    "message": "Сериал удален", 
                    "deleted_series": deleted
                })
        
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"⚠️ Сериал с ID {series_id} не найден за {execution_time} мс")
        return jsonify({"error": "Сериал не найден"}), 404
    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ Ошибка при удалении сериала {series_id} за {execution_time} мс: {str(e)}")
        return jsonify({"error": "Ошибка сервера"}), 500

# 6. ПРОВЕРКА СЕРВЕРА
@app.route('/health', methods=['GET'])
def health():
    start_time = time.time()
    logger.info("❤️ Проверка здоровья сервера")
    result = jsonify({
        "status": "OK", 
        "message": "Сервер работает нормально",
        "series_count": len(series),
        "timestamp": datetime.datetime.now().isoformat()
    })
    
    execution_time = round((time.time() - start_time) * 1000, 2)
    logger.info(f"✅ Проверка здоровья выполнена за {execution_time} мс")
    return result

# 7. ГЛАВНАЯ СТРАНИЦА
@app.route('/', methods=['GET'])
def home():
    start_time = time.time()
    logger.info("🏠 Запрос главной страницы")
    result = jsonify({
        "message": "Добро пожаловать в API турецких сериалов!",
        "total_series": len(series),
        "endpoints": {
            "GET /series": "Получить все сериалы",
            "GET /series/<id>": "Получить один сериал",
            "POST /series": "Добавить сериал (требует Content-Type: application/json)",
            "PUT /series/<id>": "Обновить сериал (требует Content-Type: application/json)", 
            "DELETE /series/<id>": "Удалить сериал",
            "GET /health": "Проверить сервер"
        },
        "timestamp": datetime.datetime.now().isoformat()
    })
    
    execution_time = round((time.time() - start_time) * 1000, 2)
    logger.info(f"✅ Главная страница отдана за {execution_time} мс")
    return result

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🚀 ЗАПУСК СЕРВЕРА ТУРЕЦКИХ СЕРИАЛОВ")
    logger.info(f"📊 Начальное количество сериалов: {len(series)}")
    logger.info("📍 Сервер доступен по: http://localhost:5000")
    logger.info("⏱️ Включено измерение времени выполнения методов")
    logger.info("=" * 50)
    
    print("✅ Сервер запущен! Тестируйте запросы:")
    print("1. GET  http://localhost:5000/")
    print("2. GET  http://localhost:5000/series") 
    print("3. GET  http://localhost:5000/series/1")
    print("4. POST http://localhost:5000/series")
    print("5. PUT  http://localhost:5000/series/1")
    print("6. DELETE http://localhost:5000/series/2")
    print("7. GET  http://localhost:5000/health")
    print("⏱️ Время выполнения будет выводиться в консоль")
    print("-" * 50)
    
    app.run(debug=True, port=5000)