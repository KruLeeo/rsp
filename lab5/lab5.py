import logging
from flask import Flask, request, jsonify
from datetime import datetime
import os
import glob
import psycopg2 # Импорт для работы с PostgreSQL
import time # Для обработки ошибок подключения
import redis # Импорт для работы с Redis (Новое)
import json # Для работы с JSON в Redis (Новое)

# --- Настройки PostgreSQL (читаются из переменных окружения Docker Compose) ---
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'mydatabase')
DB_USER = os.environ.get('DB_USER', 'user')
DB_PASS = os.environ.get('DB_PASS', 'password')

# --- Настройки Redis (имя хоста - имя сервиса в docker-compose) --- (Новое)
REDIS_HOST = os.environ.get('REDIS_HOST', 'cache') # Имя сервиса 'cache'
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_CACHE_TIMEOUT = 30 # Кэш будет храниться 30 секунд

# --- Настройки Логирования ---
LOG_FILE = 'app.log'
MAX_LOG_SIZE = 5 * 1024  # 5 KB
BACKUP_COUNT = 3 

class SimpleFileHandler(logging.Handler):
    """Простой обработчик, который создает новые файлы вместо переименования"""
    
    def __init__(self, filename, max_size, backup_count):
        super().__init__()
        self.base_filename = filename.replace('.log', '')
        self.max_size = max_size
        self.backup_count = backup_count
        self.current_file = None
        self.current_filename = self.get_current_filename()
        self.setup_file_handler()
    
    def get_current_filename(self):
        """Определяет имя текущего файла для записи"""
        log_files = glob.glob(f"{self.base_filename}*.log")
        current_files = []
        
        for f in log_files:
            if f == f"{self.base_filename}.log":
                current_files.append((f, 0))
            else:
                try:
                    num = int(f.split('.')[-2])
                    current_files.append((f, num))
                except:
                    continue
        
        if not current_files:
            return f"{self.base_filename}.log"
        
        current_files.sort(key=lambda x: x[1])
        latest_file, latest_num = current_files[-1]
        
        if os.path.exists(latest_file) and os.path.getsize(latest_file) < self.max_size:
            return latest_file
        else:
            new_num = latest_num + 1
            self.cleanup_old_files(new_num)
            return f"{self.base_filename}.{new_num}.log"
    
    def cleanup_old_files(self, new_num):
        """Удаляет старые файлы логов если превышено максимальное количество"""
        try:
            log_files = []
            for f in glob.glob(f"{self.base_filename}*.log"):
                if f == f"{self.base_filename}.log":
                    log_files.append((f, 0))
                else:
                    try:
                        num = int(f.split('.')[-2])
                        log_files.append((f, num))
                    except:
                        continue
            
            log_files.sort(key=lambda x: x[1])
            
            while len(log_files) >= self.backup_count:
                oldest_file, oldest_num = log_files.pop(0)
                if os.path.exists(oldest_file):
                    os.remove(oldest_file)
                    
        except Exception as e:
            print(f"Ошибка при очистке старых файлов логов: {str(e)}")
    
    def setup_file_handler(self):
        """Настраивает файловый обработчик для текущего файла"""
        try:
            if hasattr(self, 'file_handler') and self.file_handler:
                self.file_handler.close()
            
            self.file_handler = logging.FileHandler(self.current_filename, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            self.file_handler.setFormatter(formatter)
            
        except Exception as e:
            print(f"Ошибка при настройке файлового обработчика: {str(e)}")
            self.file_handler = logging.StreamHandler()
    
    def should_rotate(self):
        """Проверяет, нужно ли создавать новый файл"""
        if not os.path.exists(self.current_filename):
            return False
        
        try:
            file_size = os.path.getsize(self.current_filename)
            return file_size >= self.max_size
        except:
            return False
    
    def rotate_if_needed(self):
        """Создает новый файл если текущий превысил лимит"""
        if self.should_rotate():
            if self.current_filename == f"{self.base_filename}.log":
                current_num = 0
            else:
                try:
                    current_num = int(self.current_filename.split('.')[-2])
                except:
                    current_num = 0
            
            new_num = current_num + 1
            self.current_filename = f"{self.base_filename}.{new_num}.log"
            
            self.cleanup_old_files(new_num)
            self.setup_file_handler()
            return True
        return False
    
    def emit(self, record):
        """Запись лога"""
        try:
            self.rotate_if_needed()
            self.file_handler.emit(record)
            
        except Exception as e:
            print(f"Ошибка при записи лога: {str(e)}")

def setup_logging():
    """Настройка логирования"""
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = SimpleFileHandler(LOG_FILE, MAX_LOG_SIZE, BACKUP_COUNT)
    file_handler.setLevel(logging.INFO)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

# Инициализация логгера
logger = setup_logging()

app = Flask(__name__)  

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ ---

def get_db_connection():
    """Устанавливает и возвращает соединение с БД."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Не удалось подключиться к базе данных: {DB_HOST}/{DB_NAME}. Ошибка: {e}")
        raise ConnectionError("Не удалось подключиться к базе данных.")

def init_db():
    """Пытается подключиться к БД и создает таблицу 'items', если она еще не существует."""
    max_retries = 5
    retry_delay = 5
    
    logger.info(f"Попытка подключения к БД: {DB_HOST}/{DB_NAME}")

    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR (100) NOT NULL,
                    description TEXT
                );
            """)
            
            cur.execute("SELECT count(*) FROM items;")
            if cur.fetchone()[0] == 0:
                 cur.execute(
                    "INSERT INTO items (name, description) VALUES (%s, %s), (%s, %s);",
                    (
                        "Пример предмета 1 (из БД)", "Описание предмета 1",
                        "Пример предмета 2 (из БД)", "Описание предмета 2"
                    )
                )

            conn.commit()
            cur.close()
            conn.close()
            logger.info("Таблица 'items' успешно проверена/создана и инициализирована в базе данных.")
            return

        except ConnectionError:
            logger.warning(f"Попытка {attempt + 1}/{max_retries}: Ожидание доступности базы данных...")
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Критическая ошибка инициализации базы данных: {e}")
            return

    logger.error(f"Не удалось подключиться к базе данных после {max_retries} попыток. Приложение не сможет работать.")
    
# Инициализация базы данных при запуске
init_db()


# --- ФУНКЦИИ ДЛЯ РАБОТЫ С REDIS --- (Новое)

def get_redis_connection():
    """Устанавливает и возвращает соединение с Redis."""
    try:
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, 
                              decode_responses=True, socket_connect_timeout=1)
        r.ping() 
        return r
    except redis.exceptions.ConnectionError:
        # Логирование происходит при первом запуске
        return None

# Проверка подключения к Redis 
redis_conn_check = get_redis_connection()
if redis_conn_check:
    logger.info("Подключение к Redis успешно установлено.")
else:
    logger.warning("Приложение будет работать без кэширования Redis.")

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

app_started = False

def log_request_info():
    """Логирование информации о входящем запросе"""
    logger.info(f"Входящий запрос: {request.method} {request.path} - IP: {request.remote_addr}")
    if request.method in ['POST', 'PUT'] and request.is_json:
        logger.debug(f"Тело запроса: {request.get_json()}")

def log_response_info(response, status_code):
    """Логирование информации об исходящем ответе"""
    logger.info(f"Исходящий ответ: {status_code} для {request.method} {request.path}")
    return response

@app.before_request
def before_first_request():
    """Логирование при первом запросе"""
    global app_started
    if not app_started:
        logger.info("Flask приложение запущено и готово к запросам")
        app_started = True

# --- API РОУТЫ С ИСПОЛЬЗОВАНИЕМ PostgreSQL И Redis ---

# GET - получить все предметы
@app.route('/items', methods=['GET'])
def get_items():
    log_request_info()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, name, description FROM items ORDER BY id;")
        db_items = cur.fetchall()
        
        items_list = []
        for row in db_items:
            items_list.append({"id": row[0], "name": row[1], "description": row[2]})
        
        cur.close()
        conn.close()
        
        logger.info(f"Запрос на получение всех предметов. Найдено: {len(items_list)}")
        response = jsonify(items_list)
        log_response_info(response, 200)
        return response
        
    except ConnectionError:
        return jsonify({"error": "Сервис базы данных недоступен"}), 503
    except Exception as e:
        logger.error(f"Ошибка при получении всех предметов: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# GET - получить предмет по ID (с кэшированием)
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    log_request_info()
    
    redis_conn = get_redis_connection()
    cache_key = f"item:{item_id}"
    
    # 1. Попытка получить из кэша (Новое)
    if redis_conn:
        cached_item_json = redis_conn.get(cache_key)
        if cached_item_json:
            item = json.loads(cached_item_json)
            logger.info(f"Предмет ID={item_id} получен из кэша Redis.")
            response = jsonify(item)
            log_response_info(response, 200)
            return response
    
    # 2. Если нет в кэше, получаем из БД
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, name, description FROM items WHERE id = %s;", (item_id,))
        item_row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if item_row:
            item = {"id": item_row[0], "name": item_row[1], "description": item_row[2]}
            logger.info(f"Предмет с ID {item_id} найден в БД: {item['name']}")
            
            # 3. Сохраняем в кэш (Новое)
            if redis_conn:
                redis_conn.set(cache_key, json.dumps(item), ex=REDIS_CACHE_TIMEOUT)
                logger.info(f"Предмет ID={item_id} сохранен в кэш Redis на {REDIS_CACHE_TIMEOUT} сек.")
                
            response = jsonify(item)
            log_response_info(response, 200)
            return response
        else:
            logger.warning(f"Предмет с ID {item_id} не найден")
            return jsonify({"error": "Предмет не найден"}), 404
            
    except ConnectionError:
        return jsonify({"error": "Сервис базы данных недоступен"}), 503
    except Exception as e:
        logger.error(f"Ошибка при получении предмета {item_id}: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# POST - создать новый предмет (сброс кэша)
@app.route('/items', methods=['POST'])
def create_item():
    log_request_info()
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            logger.warning("Попытка создания предмета без указания названия")
            return jsonify({"error": "Необходимо указать название предмета"}), 400
        
        name = data['name']
        description = data.get('description', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id;",
            (name, description)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        # Сброс кэша для созданного предмета (Новое)
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.delete(f"item:{new_id}")
            logger.info(f"Сброшен кэш для нового предмета ID={new_id}")

        new_item = {"id": new_id, "name": name, "description": description}
        logger.info(f"Создан новый предмет: ID={new_id}, Название='{name}'")
        
        response = jsonify(new_item)
        log_response_info(response, 201)
        return response, 201
        
    except ConnectionError:
        return jsonify({"error": "Сервис базы данных недоступен"}), 503
    except Exception as e:
        logger.error(f"Ошибка при создании предмета: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# PUT - обновить предмет (сброс кэша)
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    log_request_info()
    try:
        data = request.get_json()
        logger.info(f"Запрос на обновление предмета ID={item_id} с данными: {data}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        update_fields = []
        update_values = []
        if 'name' in data:
            update_fields.append("name = %s")
            update_values.append(data['name'])
        if 'description' in data:
            update_fields.append("description = %s")
            update_values.append(data['description'])
            
        if not update_fields:
            return jsonify({"error": "Нет данных для обновления"}), 400
            
        update_query = f"UPDATE items SET {', '.join(update_fields)} WHERE id = %s RETURNING id, name, description;"
        update_values.append(item_id)
        
        cur.execute(update_query, tuple(update_values))
        
        updated_row = cur.fetchone()
        
        if not updated_row:
            conn.close()
            logger.warning(f"Попытка обновления несуществующего предмета ID={item_id}")
            return jsonify({"error": "Предмет не найден"}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Сброс кэша для обновленного предмета (Новое)
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.delete(f"item:{item_id}")
            logger.info(f"Сброшен кэш для предмета ID={item_id}")
        
        updated_item = {"id": updated_row[0], "name": updated_row[1], "description": updated_row[2]}
        logger.info(f"Предмет ID={item_id} успешно обновлен.")
        
        response = jsonify(updated_item)
        log_response_info(response, 200)
        return response
        
    except ConnectionError:
        return jsonify({"error": "Сервис базы данных недоступен"}), 503
    except Exception as e:
        logger.error(f"Ошибка при обновлении предмета {item_id}: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# DELETE - удалить предмет (сброс кэша)
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    log_request_info()
    try:
        logger.info(f"Запрос на удаление предмета с ID: {item_id}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM items WHERE id = %s RETURNING name;", (item_id,))
        deleted_item_name = cur.fetchone()
        
        if not deleted_item_name:
            conn.close()
            logger.warning(f"Попытка удаления несуществующего предмета ID={item_id}")
            return jsonify({"error": "Предмет не найден"}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Сброс кэша для удаленного предмета (Новое)
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.delete(f"item:{item_id}")
            logger.info(f"Сброшен кэш для предмета ID={item_id}")
        
        logger.info(f"Предмет ID={item_id} ('{deleted_item_name[0]}') успешно удален")
        
        response = jsonify({"message": "Предмет удален"})
        log_response_info(response, 200)
        return response, 200
        
    except ConnectionError:
        return jsonify({"error": "Сервис базы данных недоступен"}), 503
    except Exception as e:
        logger.error(f"Ошибка при удалении предмета {item_id}: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# --- СТАРЫЕ ВСПОМОГАТЕЛЬНЫЕ РОУТЫ И ЛОГИРОВАНИЕ ---

# Обработчик ошибок для несуществующих маршрутов
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Запрос к несуществующему маршруту: {request.path}")
    return jsonify({"error": "Маршрут не найден"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    logger.warning(f"Неподдерживаемый метод {request.method} для маршрута {request.path}")
    return jsonify({"error": "Метод не разрешен"}), 405

# Эндпоинт для получения информации о логах (оставлен без изменений)
@app.route('/logs/info', methods=['GET'])
def get_logs_info():
    """Получение информации о файлах логов"""
    try:
        base_name = LOG_FILE.replace('.log', '')
        log_files = []
        
        for f in glob.glob(f"{base_name}*.log"):
            file_size = os.path.getsize(f)
            log_files.append({
                "filename": os.path.basename(f),
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "is_current": f == getattr(logger.handlers[0], 'current_filename', '')
            })
        
        log_files.sort(key=lambda x: x['filename'])
        
        return jsonify({
            "max_size_mb": MAX_LOG_SIZE / (1024 * 1024),
            "backup_count": BACKUP_COUNT,
            "log_files": log_files
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Ошибка при получении информации о логах: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info("Запуск Flask приложения...")
    logger.info(f"Максимальный размер файла логов: {MAX_LOG_SIZE / (1024 * 1024)} MB")
    logger.info(f"Количество бэкап-файлов: {BACKUP_COUNT}")
    logger.info("Flask приложение запускается...")
    app.run(host='0.0.0.0', port=5000, debug=True)