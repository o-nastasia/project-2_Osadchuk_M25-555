#!/usr/bin/env python3
import shlex

import prompt

from .core import create_table, drop_table
from .utils import load_metadata, save_metadata


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    filepath = 'db_meta.json'
    while True:
        user_input = prompt.string('Введите команду: ')
        args = shlex.split(user_input)
        if not args:
            command = 'empty'
        command = args[0]
        match command:
            case 'create_table':
                if len(args) < 3:
                    print('Некорректное значение: отсутствуют названия \
                          столбцов. Попробуйте снова.')
                    continue
                data = load_metadata(filepath)
                table_name = args[1]
                columns = args[2:]
                table = create_table(data, table_name, columns)
                if table == 1:
                    continue
                save_metadata(filepath, table)
            case 'list_tables':
                data = load_metadata(filepath)
                if data == {}:
                    print("У вас пока нет таблиц.")
                    continue
                print('\n'.join(f'- {name}' for name in data))
            case 'drop_table':
                if len(args) < 2:
                    print('Некорректное значение: отсутствует \
                          название таблицы. Попробуйте снова.')
                    continue
                data = load_metadata(filepath)
                table_name = args[1]
                result = drop_table(data, table_name)
                if result == 1:
                    continue
                save_metadata(filepath, result)
            case 'exit':
                return
            case 'help':
                print_help()
            case 'empty':
                continue
            case _:
                print(f'Функции {command} нет. Попробуйте снова.')
                print_help()

