import threading
import time
import sys

class CounterNoSync:
    def __init__(self):
        self.value = 0

class CounterSync:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()
    
    def increment(self):
        with self.lock:
            self.value += 1
    
    def decrement(self):
        with self.lock:
            self.value -= 1

class CounterReentrantLock:
    def __init__(self):
        self.value = 0
        self.lock = threading.RLock()
    
    def increment(self):
        with self.lock:
            self.value += 1
    
    def decrement(self):
        with self.lock:
            self.value -= 1

def increment_worker_no_sync(counter, iterations):
    for _ in range(iterations):
        local_value = counter.value
        local_value += 1
        counter.value = local_value

def decrement_worker_no_sync(counter, iterations):
    for _ in range(iterations):
        local_value = counter.value
        local_value -= 1
        counter.value = local_value

def increment_worker_sync(counter, iterations):
    for _ in range(iterations):
        counter.increment()

def decrement_worker_sync(counter, iterations):
    for _ in range(iterations):
        counter.decrement()

def run_experiment(version, n, m, iterations=100000):
    if version == "no_sync":
        counter = CounterNoSync()
        inc_worker = increment_worker_no_sync
        dec_worker = decrement_worker_no_sync
    elif version == "sync":
        counter = CounterSync()
        inc_worker = increment_worker_sync
        dec_worker = decrement_worker_sync
    elif version == "reentrant":
        counter = CounterReentrantLock()
        inc_worker = increment_worker_sync
        dec_worker = decrement_worker_sync
    else:
        raise ValueError("Неизвестная версия")
    
    threads = []
    start_time = time.time()
    
    # Создаем инкрементирующие потоки
    for _ in range(n):
        t = threading.Thread(target=inc_worker, args=(counter, iterations))
        threads.append(t)
        t.start()
    
    # Создаем декрементирующие потоки
    for _ in range(m):
        t = threading.Thread(target=dec_worker, args=(counter, iterations))
        threads.append(t)
        t.start()
    
    # Ждем завершения всех потоков
    for t in threads:
        t.join()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return counter.value, execution_time

def main():
    if len(sys.argv) != 3:
        print("Использование: python Lab3All.py <n> <m>\nгде n - количество инкрементирующих потоков\n      m - количество декрементирующих потоков\n\nПример: python Lab3All.py 5 5")
        return
    
    n = int(sys.argv[1])
    m = int(sys.argv[2])
    iterations = 100000
    
    header = f"""
{'=' * 60}
ЭКСПЕРИМЕНТ С МНОГОПОТОЧНОСТЬЮ
Инкрементирующих потоков (n): {n}
Декрементирующих потоков (m): {m}
Итераций на поток: {iterations}
{'=' * 60}
"""
    print(header)
    
    # 1.1. Без синхронизации
    final_value, time_taken = run_experiment("no_sync", n, m, iterations)
    expected = (n - m) * iterations
    no_sync_result = f"""
1.1. БЕЗ СИНХРОНИЗАЦИИ (Lab3NoSync)
Финальное значение счетчика: {final_value}
Время выполнения: {time_taken:.4f} секунд
Ожидаемое значение: {expected}
Расхождение: {final_value - expected}
"""
    print(no_sync_result)
    
    # 1.2. С синхронизацией (Lock)
    final_value, time_taken = run_experiment("sync", n, m, iterations)
    sync_result = f"""
1.2. С СИНХРОНИЗАЦИЕЙ (synchronized/Lock)
Финальное значение счетчика: {final_value}
Время выполнения: {time_taken:.4f} секунд
Ожидаемое значение: {expected}
"""
    print(sync_result)
    
    # 1.3. С ReentrantLock
    final_value, time_taken = run_experiment("reentrant", n, m, iterations)
    reentrant_result = f"""
1.3. С REENTRANT LOCK
Финальное значение счетчика: {final_value}
Время выполнения: {time_taken:.4f} секунд
Ожидаемое значение: {expected}
"""
    print(reentrant_result)
    

def run_specific_test():
    """Функция для запуска конкретного теста"""
    print("Запуск теста с n=5, m=5...")
    main_test(5, 5)

def main_test(n, m):
    """Основная логика тестирования"""
    iterations = 100000
    
    versions = [
        ("no_sync", "БЕЗ СИНХРОНИЗАЦИИ"),
        ("sync", "С СИНХРОНИЗАЦИЕЙ (Lock)"),
        ("reentrant", "С REENTRANT LOCK")
    ]
    
    for version, description in versions:
        final_value, time_taken = run_experiment(version, n, m, iterations)
        expected = (n - m) * iterations
        
        result_text = f"""
--- {description} ---
Финальное значение: {final_value}
Время выполнения: {time_taken:.4f} сек
Ожидаемое значение: {expected}"""
        
        if version == "no_sync":
            error = final_value - expected
            if error != 0:
                result_text += f"\n⚠️  Ошибка из-за состояния гонки: {error}"
        
        print(result_text)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Запуск с аргументами командной строки
        n = int(sys.argv[1])
        m = int(sys.argv[2])
        
        test_header = f"""
Демонстрация работы многопоточных счетчиков
Запуск с n={n}, m={m}
{'=' * 40}
"""
        print(test_header)
        main_test(n, m)
        
    elif len(sys.argv) == 1:
        # Демонстрационный запуск
        demo_header = """
Демонстрация работы многопоточных счетчиков
"""
        print(demo_header)
        
        print("Запуск с n=3, m=3:")
        print('-' * 30)
        main_test(3, 3)
        
        print("\n" + "="*50)
        
        print("Запуск с n=5, m=5:")
        print('-' * 30)
        main_test(5, 5)
    else:
        print("Использование: python Lab3All.py [n m]\n  без аргументов - демонстрационный запуск\n  с аргументами - python Lab3All.py 5 5")