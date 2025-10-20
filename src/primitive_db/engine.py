#!/usr/bin/env python3
import prompt

def welcome():
    print('Первая попытка запустить проект!')
    
    while True:
        print('***\n<command> exit - выйти из программы/' \
        '\n<command> help - справочная информация')
        command = prompt.string('Введите команду: ')
        match command:
            case 'exit':
                return command
            case 'help':
                return command