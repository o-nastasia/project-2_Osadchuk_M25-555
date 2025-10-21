#!/usr/bin/env python3

def create_table(metadata, table_name, columns):
    data = metadata.copy()
    if table_name in data:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return 1
    if 'ID:int' not in columns:
        columns = ['ID:int'] + columns
    
    for column_def in columns:
        if not isinstance(column_def, str):
            print(f'Некорректное значение: "{column_def}". Попробуйте снова.')
            return 1
        if ':' not in column_def:
            print(f'Некорректное значение: "{column_def}". Названия стобцов должны соответсвовать формату <столбец:тип> Попробуйте снова.')#noqa: E501
            return 1
        col_name, col_type = column_def.split(':', 1)
        if col_type not in ['int', 'str', 'bool']:
            print('Ошибка: В столбцах таблицы допустимы только типы int, str и bool')
            return 1
    
    data[table_name] = columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(columns)}')
    return data

def drop_table(metadata, table_name):
    data = metadata.copy()
    if table_name not in data:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return 1
    
    del data[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return data