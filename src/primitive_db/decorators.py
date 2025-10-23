# src/decorators.py
import time
from functools import wraps

import prompt


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база данных не инициализирована.")#noqa: E501
            return 1
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            return 1
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return 1
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return 1
    return wrapper

def confirm_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            confirmation = prompt.string(f'Вы уверены, что хотите выполнить {action_name}? [y/n]: ')#noqa: E501
            if confirmation.lower() != 'y':
                print(f'Операция {action_name} отменена.')
                return 1
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        print(f'Функция {func.__name__} выполнилась за {end_time - start_time:.3f} секунд.')#noqa: E501
        return result
    return wrapper

def create_cacher():
    cache = {}
    def cache_result(key, value_func):
        if key in cache:
            print(f"Результат получен из кэша для ключа: {key}")
            return cache[key]
        result = value_func()
        cache[key] = result
        return result
    def clear_cache(table_name):
        keys_to_remove = [key for key in cache if key.startswith(f"{table_name}:")]
        for key in keys_to_remove:
            del cache[key]
        #print(f"Кэш для таблицы {table_name} очищен.")
    return cache_result, clear_cache