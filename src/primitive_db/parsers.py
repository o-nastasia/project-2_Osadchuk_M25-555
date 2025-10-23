def parser(column, condition, metadata, table_name):
    data = metadata.copy()
    if table_name not in data:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return 1
    
    for item in data[table_name]:
        name, type = item.split(':', 1)
        if name == column:
            break    
    try:
        if type == 'int':
            condition = int(condition)
        elif type == 'str':
                condition = str(condition)
        elif type == 'bool':
            match condition.lower():
                case 'true':
                    condition = True
                case 'false':
                    condition = False
                case _:
                    raise ValueError
    except(ValueError, AttributeError):
        print(f"Ошибка: значение {condition} должно быть типа {type}")
        return 1
    output = {column: condition}
    return output

def values_parser(values):
    if not values:
        print("Ошибка: укажите значения столбцов")
        return 1
    result = []
    for value in values:
        value = value.strip()
        value = value.strip(',')
        value = value.strip('"')
        value = value.strip('\'')
        value = value.strip('(')
        value = value.strip('"')
        value = value.strip('\'')
        value = value.strip(')')
        value = value.strip('"')
        value = value.strip('\'')
        value = value.strip(',')
        result.append(value)
    if not result:
        print("Ошибка: укажите значения столбцов")
        return 1
    return result

def meta_parser(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return 1
    names = []
    for column in metadata[table_name]:
        name, type = column.split(':', 1)
        names.append(name)
    return(names)