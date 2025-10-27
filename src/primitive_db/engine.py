#!/usr/bin/env python3
import shlex

import prompt
from prettytable import PrettyTable

from .core import create_table, delete, drop_table, insert, select, update
from .decorators import create_cacher
from .parsers import meta_parser, parser, values_parser
from .utils import load_data, load_metadata, save_data, save_metadata

META_FILE = "db_meta.json"

def print_help():
    """Выводит справочное сообщение о доступных командах."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print('\n***Операции с данными***')
    print('Функции:')
    print('<command> insert_into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.')#noqa: E501
    print('<command> select_from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.')#noqa: E501
    print('<command> select_from <имя_таблицы> - прочитать все записи.')#noqa: E501
    print('<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.')#noqa: E501
    print('<command> delete_from <имя_таблицы> where <столбец> = <значение> - удалить запись.')#noqa: E501
    print('<command> info <имя_таблицы> - вывести информацию о таблице.')#noqa: E501
        
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    """Запускает основной цикл обработки команд для работы с базой данных."""
    filepath = META_FILE
    cacher, clear_cache = create_cacher()
    while True:
        data = load_metadata(filepath)
        user_input = prompt.string('Введите команду: ')
        args = shlex.split(user_input)
        if not args:
            command = 'empty'
        command = args[0]
        match command:
            case 'create_table':
                """Создает новую таблицу с указанными столбцами."""
                if len(args) < 3:
                    print('Некорректное значение: отсутствуют названия таблицы или столбцов. Попробуйте снова.')#noqa: E501
                    continue
                table_name = args[1]
                columns = args[2:]
                table = create_table(data, table_name, columns)
                if table == 1:
                    continue
                save_metadata(filepath, table)
            case 'list_tables':
                """Выводит список всех таблиц."""
                if data == {}:
                    print("У вас пока нет таблиц.")
                    continue
                print('\n'.join(f'- {name}' for name in data))
            case 'drop_table':
                """Удаляет указанную таблицу."""
                if len(args) != 2:
                    print('Некорректное значение: отсутствует \
                          название таблицы. Попробуйте снова.')
                    continue
                table_name = args[1]
                result = drop_table(data, table_name)
                if result == 1:
                    continue
                save_metadata(filepath, result)
            case 'insert_into':
                """Вставляет новую запись в таблицу."""
                if len(args) < 4 or args[2] != 'values':
                    print('Некорректное значение функции. Попробуйте снова.')
                    continue
                table_name = args[1]
                values = args[3:]
                values = values_parser(values)
                if values == 1:
                    continue
                table_data = load_data(table_name)
                result = insert(data, table_name, values)
                if result == 1:
                    continue
                save_data(table_name, result)
                clear_cache(table_name)
            case 'update':
                """Обновляет записи в таблице по заданному условию."""
                if len(args) != 10 or args[2] != 'set' or args[4] != '=' \
                    or args[6] != 'where' or args[8] != '=':
                    print('Некорректное значение функции. Попробуйте снова.')
                    continue
                table_name, column_set, condition_set, column_where, condition_where\
                    = args[1], args[3], args[5], args[7], args[9]
                set_clause = parser(column_set, condition_set, data, table_name)
                where_clause = parser(column_where, condition_where, data, table_name)
                if set_clause == 1 or where_clause == 1:
                    continue
                table_data = load_data(table_name)
                result = update(table_data, set_clause, where_clause, table_name)
                if result == 1:
                    continue
                save_data(table_name, result)
                clear_cache(table_name)
            case 'delete_from':
                """Удаляет записи из таблицы по заданному условию."""
                if len(args) != 6 or args[2] != 'where' or args[4] != '=':
                    print('Некорректное значение функции. Попробуйте снова.')
                    continue
                table_name, column, condition = args[1], args[3], args[5]
                where_clause = parser(column, condition, data, table_name)
                if where_clause == 1:
                    continue
                table_data = load_data(table_name)
                result = delete(table_data, where_clause, table_name)
                if result == 1:
                    continue
                save_data(table_name, result)
                clear_cache(table_name)
            case 'select_from':
                """Выбирает записи из таблицы по условию или все записи."""
                if len(args) == 6 and args[2] == 'where' and args[4] == '=':
                    table_name = args[1]
                    if table_name not in data:
                        print (f'Таблицы {table_name} не существует.')
                        continue
                    table_data = load_data(table_name)
                    condition = parser(args[3], args[5], data, table_name)
                    if condition == 1:
                        continue

                    cache_key = f"{table_name}:{args[3]}={args[5]}"
                    rows = cacher(cache_key, lambda: select(table_data, condition))
                    if rows == 1:
                        continue
                    table = PrettyTable()
                    table.field_names = table_data[0].keys()
                    for row in rows:
                        table.add_row(list(row.values()))
                    print(table)
                    
                elif len(args) == 2:
                    table_name = args[1]
                    table_data = load_data(table_name)
                    if table_data == []:
                        columns = meta_parser(data, table_name)
                        if columns == 1:
                            continue
                        table = PrettyTable(columns)
                        print(table)
                    
                    cache_key = f"{table_name}:all"
                    rows = cacher(cache_key, lambda: select(table_data))
                    table = PrettyTable()
                    table.field_names = table_data[0].keys()
                    for row in rows:
                            table.add_row(list(row.values()))
                    print(table)

                else:
                    print('Некорректное значение функции. Попробуйте снова.')
                    continue
            case 'info':
                """Выводит информацию о структуре таблицы."""
                if len(args) != 2:
                    print('Некорректное значение: \
                          отсутствует название таблицы. Попробуйте снова.')
                table_name = args[1]
                columns = meta_parser(data, table_name)
                if columns == 1:
                    continue
                table = PrettyTable(columns)
                print(table)
            case 'exit':
                """Завершает выполнение программы."""
                return
            case 'help':
                """Выводит справочную информацию."""
                print_help()
            case 'empty':
                continue
            case _:
                print(f'Функции {command} нет. Попробуйте снова.')
                print_help()