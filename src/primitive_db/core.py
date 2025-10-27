#!/usr/bin/env python3
from .decorators import confirm_action, handle_db_errors, log_time
from .utils import load_data


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает новую таблицу с указанными столбцами."""
    data = metadata.copy()
    if table_name in data:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return 1
    if 'ID:int' not in columns:
        columns = ['ID:int'] + columns
    
    unique_names = []

    for column_def in columns:
        if not isinstance(column_def, str):
            print(f'Некорректное значение: "{column_def}". Попробуйте снова.')
            return 1
        if ':' not in column_def:
            print(f'Некорректное значение: "{column_def}". Названия стобцов должны соответсвовать формату <столбец:тип> Попробуйте снова.')#noqa: E501
            return 1
        col_name, col_type = column_def.split(':', 1)
        if col_name in unique_names:
            print('Ошибка: Названия столбцов в таблице не должны дублироваться.')
            return 1
        unique_names.append(col_name)
        if col_type not in ['int', 'str', 'bool']:
            print('Ошибка: В столбцах таблицы допустимы только типы int, str и bool')
            return 1
    
    data[table_name] = columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(columns)}')
    return data

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    data = metadata.copy()
    if table_name not in data:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return 1
    
    del data[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return data

@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Вставляет новую запись в таблицу."""
    data = metadata.copy()
    if table_name not in data:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return 1
    if len(data[table_name])-1 != len(values):
        print("Ошибка: количество значений должно совпадать с количеством столбцов.")#noqa: E501
        return 1
    types = []
    names = []
    for column in data[table_name]:
        name, type = column.split(':', 1)
        if name != 'ID':
            names.append(name)
            types.append(type)
    upd_values = []

    type_map = {'int': int, 'str': str, 'bool': bool}
    for value, type in zip(values, types):
        if not isinstance(value, type_map[type]):
            try:
                if type == 'int':
                    value = int(value)
                elif type == 'str':
                    value = str(value)
                elif type == 'bool':
                    match value.lower():
                        case 'true':
                            value = True
                        case 'false':
                            value = False
                        case _:
                            raise ValueError

            except(ValueError, AttributeError):
                print(f"Ошибка: значение {value} должно быть типа {type}")
                return 1
        upd_values.append(value)
    
    current_data = load_data(table_name)
    new_data = {}
    id = len(current_data) + 1
    new_data['ID'] = id
    for name, value in zip(names, upd_values):
        new_data[name] = value
    new_table_data = list(current_data.copy())
    new_table_data.append(new_data)
    print(f'Запись с ID={id} успешно добавлена в таблицу "{table_name}".')
    return new_table_data

@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Выбирает записи из таблицы по условию."""
    if not where_clause:
        return table_data
    column = list(where_clause.keys())[0]
    condition = where_clause[column]
    
    if not table_data:
        print("Ошибка: Таблица пустая.")
        return 1

    elif column not in table_data[0]:
        print(f"Ошибка: Столбец {column} не существует в таблице.")
        return 1

    output = []
    for line in table_data:
        if line[column] == condition:
            output.append(line)
    if len(output) == 0:
        print("Ошибка: Таблица пустая.")
        return 1
    return output

@handle_db_errors
def update(table_data, set_clause, where_clause, table_name):
    """Обновляет записи в таблице по условию."""
    if not where_clause:
        print("Ошибка: Не указано условие where.")
        return 1
    
    if not table_data:
        print("Ошибка: Таблица пустая.")
        return 1
    
    if not set_clause:
        print("Ошибка: Не задан параметр set.")
        return 1

    column_where = list(where_clause.keys())[0]
    condition = where_clause[column_where]

    column_set = list(set_clause.keys())[0]
    setting = set_clause[column_set]

    if column_where not in table_data[0] or column_set not in table_data[0]:
        print("Ошибка: Одного из указанных столбцов нет в таблице.")
        return 1

    new_data = table_data.copy()
    output = []
    ids_upd = []
    for line in new_data:
        if line[column_where] == condition:
            line[column_set] = setting
            ids_upd.append(str(line['ID']))
        output.append(line)
    if not ids_upd:
        print("Записи, соответствующие условию, не найдены.")
        return 1
    elif len(ids_upd) > 1:
        print(f'Записи с ID={", ".join(ids_upd)} в таблице {table_name} успешно обновлены.')#noqa: E501
    else:
        print(f'Запись с ID={ids_upd[0]} в таблице {table_name} успешно обновлена.')

    return output

@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause, table_name):
    """Удаляет записи из таблицы по условию."""
    if not where_clause:
        print("Ошибка: Не указано условие where.")
        return 1
    if not table_data:
        print("Ошибка: Таблица пустая.")
        return 1
    
    column = list(where_clause.keys())[0]
    condition = where_clause[column]

    if column not in table_data[0]:
        print(f"Ошибка: столбца {column} нет в таблице.")
        return 1
    
    new_data = table_data.copy()
    output = []
    ids_upd = []
    
    for line in new_data:
        if line[column] == condition:
            ids_upd.append(str(line['ID']))
        elif line[column] != condition:
            output.append(line)
    
    if not ids_upd:
        print("Записи, соответствующие условию, не найдены.")
        return 1
    elif len(ids_upd) > 1:
        print(f"Записи с ID={', '.join(ids_upd)} успешно удалены из таблицы '{table_name}'.")#noqa: E501
    else:
        print(f"Запись с ID={ids_upd[0]} успешно удалена из таблицы '{table_name}'.")#noqa: E501
    return output

