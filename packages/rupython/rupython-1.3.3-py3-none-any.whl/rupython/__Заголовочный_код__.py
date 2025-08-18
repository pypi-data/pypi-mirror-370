import gc
import ctypes

import sys as Система
import os as ОС

from _io import BufferedReader, BufferedWriter, TextIOWrapper

def Установить_поле(класс, атрибут, значение):
    сл = gc.get_referents(класс.__dict__)[0]
    сл[атрибут] = значение
    if callable(значение):
        сл[атрибут].__name__ = значение.__name__
        сл[атрибут].__qualname__ = значение.__qualname__
        сл[атрибут].__kwdefaults__ = значение.__kwdefaults__
    ctypes.pythonapi.PyType_Modified(ctypes.py_object(класс))

Встроенные_поля = {
    ('str', 'bytes', 'bytearray'): {
        'find': 'Найти',
        'rfind': 'Найти_с_конца',
        'index': 'Положение',
        'rindex': 'Положение_с_конца',
        'replace': 'Заменить',
        'split': 'Разбить',
        'isdigit': 'Из_цифр',
        'isalpha': 'Из_букв',
        'isalnum': 'Из_цифробукв',
        'islower': 'Из_строчных',
        'isupper': 'Из_заглавных',
        'isspace': 'Из_пробелов',
        'istitle': 'Слова_с_заглавных',
        'upper': 'В_заглавные',
        'lower': 'В_строчные',
        'startswith': 'Начинается',
        'endswith': 'Кончается',
        'join': 'Сцепить',
        'capitalize': 'Начать_с_заглавной',
        'center': 'Отцентровать',
        'count': 'Число_вхождений',
        'expandtabs': 'Табуляции_в_пробелы',
        'lstrip': 'Удалить_в_начале',
        'rstrip': 'Удалить_в_конце',
        'strip': 'Удалить_по_бокам',
        'partition': 'Разбить',
        'rpartition': 'Разбить_с_конца',
        'swapcase': 'Обратить_регистр',
        'title': 'Начать_слова_с_заглавных',
        'zfill': 'Дополнить_нулями',
        'ljust': 'Дополнить_справа',
        'rjust': 'Дополнить_слева'
    },
    'str': {
        'format': 'Формат',
        'encode': 'Закодовать'
    },
    ('bytes', 'bytearray'): {
        'decode': 'Раскодовать'
    },
    ('list', 'bytearray'): {
        'append': 'Добавить',
        'clear': 'Очистить',
        'copy': 'Копия',
        'count': 'Число_вхождений',
        'extend': 'Дополнить',
        'index': 'Положение',
        'insert': 'Вставить',
        'pop': 'Вытащить',
        'remove': 'Удалить',
        'reverse': 'Обратить'
    },
    'list': {
        'sort': ( 'Упорядочить', { 'key': 'ключ', 'reverse': 'обратно' } )
    },
    'dict': {
        'clear': 'Очистить',
        'copy': 'Копия',
        'fromkeys': 'Из_ключей',
        'get': 'Получить',
        'items': 'Элементы',
        'keys': 'Ключи',
        'values': 'Значения',
        'pop': 'Вытащить',
        'popitem': 'Вытащить_последнее',
        'setdefault': 'Получить_или_добавить',
        'update': 'Обновить',
        'values': 'Значения'
    },
    'tuple': {
        'index': 'Положение',
        'count': 'Число_вхождений'
    },
    ('set', 'frozenset'): {
        'isdisjoint': 'Не_пересекаются',
        'issubset': 'Подмножество',
        'issuperset': 'Надмножество',
        'union': 'Объединение',
        'intersection': 'Пересечение',
        'difference': 'Разница',
        'symmetric_difference': 'СимметрРазница',
        'copy': 'Копия'
    },
    'set': {
        'update': 'Дополнить',
        'intersection_update': 'Пересечь',
        'difference_update': 'Вычесть',
        'symmetric_difference_update': 'СимметрВычесть',
        'add': 'Добавить',
        'remove': 'Удалить',
        'discard': 'Убрать',
        'pop': 'Вытащить',
        'clear': 'Очистить'
    },
    'int': {
        'bit_length': 'Длина_в_битах',
        'to_bytes': ( 'В_байты', { 'length': 'длина', 'byteorder': 'порядок', 'signed': 'со_знаком' }, { (2, 'byteorder'): { 'МлСт': 'little', 'СтМл': 'big' } } ),
        'from_bytes': ( 'Из_байтов', { 'bytes': 'байты', 'byteorder': 'порядок', 'signed': 'со_знаком' }, { (1, 'byteorder'): { 'МлСт': 'little', 'СтМл': 'big' } } ),
        '.numerator': 'числитель',
        '.denominator': 'знаменатель'
    },
    'float': {
        'is_integer': 'Целое',
        'hex': 'В_шестн',
        'fromhex': 'Из_шестн'
    },
    ('int', 'float'): {
        'as_integer_ratio': 'В_дробь'
    },
    ('int', 'float', 'complex'): {
        '.real': 'действ_часть',
        '.imag': 'мнимая_часть',
        'conjugate': 'Cопряжённое'
    },
    ('BufferedReader', 'BufferedWriter', 'TextIOWrapper'): {
        'read': 'Читать',
        'readline': 'Читать_строку',
        'write': 'Писать',
        'tell': 'Позиция',
        'seek': 'Задать_позицию',
        'truncate': 'Изменить_размер',
        'detach': 'Отделить',
        'close': 'Закрыть',
        '.closed': 'закрыт'
    }
}

for классы, таблица in Встроенные_поля.items():
    if type(классы) != tuple: классы = [классы]
    for класс in классы:
        for название, замена in таблица.items():
            if type(замена) == tuple:
                замещающая_функция = 'def __' + класс + '_' + название + '__(*ПА, **ИА):\n'
                for н, з in замена[1].items():
                    замещающая_функция += '    if "' + з + '" in ИА: ИА["' + н + '"] = ИА.pop("' + з + '")\n'
                if len(замена) > 2:
                    for зам_арг, знач_зам in замена[2].items():
                        if зам_арг[0] != -1:
                            замещающая_функция += '    if len(ПА) > ' + str(зам_арг[0]) + ' and ПА[' + str(зам_арг[0]) + '] in ' + str(list(знач_зам.keys())) + ':\n'
                            замещающая_функция += '        ПА = ПА[:' + str(зам_арг[0]) + '] + tuple([' + str(знач_зам) + '[ПА[' + str(зам_арг[0]) + ']]]) + ПА[' + str(зам_арг[0] + 1) + ':]\n'
                        if зам_арг[1] != '':
                            замещающая_функция += '    if "' + зам_арг[1] + '" in ИА.keys() and ИА["' + зам_арг[1] + '"] in ' + str(list(знач_зам.keys())) + ':\n'
                            замещающая_функция += '        ИА["' + зам_арг[1] + '"] = ' + str(знач_зам) + '[ИА["' + зам_арг[1] + '"]]\n'
                замещающая_функция += '    return ' + класс + '.' + название + '(*ПА, **ИА)'
                exec(замещающая_функция)
                exec("Установить_поле(" + класс + ", '" + замена[0] + "', __" + класс + "_" + название + "__)")
                exec('del __' + класс + '_' + название + '__')
            else:
                if название[0] == '.':
                    eval("Установить_поле(" + класс + ", '" + замена + "', " + класс + название + ")")
                else:
                    eval("Установить_поле(" + класс + ", '" + замена + "', lambda *ПА, **ИА: " + класс + "." + название + "(*ПА, **ИА))")

Система.path.insert(0, ОС.path.dirname(__file__) + '/Модули')
Система.path.insert(0, ОС.path.dirname(__file__) + '/Модули/Дополнительно')

def Заменить_преобразование_в_строку(класс, функция):
    class Объект_типа(ctypes.Structure): pass
    Объект_типа._fields_ = [
        ('', ctypes.c_ssize_t * 17), ('tp_str', ctypes.CFUNCTYPE(ctypes.py_object, ctypes.py_object))
    ]
    def Выполнить(класс, функция):
        ф = ctypes.CFUNCTYPE(ctypes.py_object, ctypes.py_object)(функция)
        Объект_типа._fields_.append(ф)
        setattr(Объект_типа.from_address(id(класс)), 'tp_str', Объект_типа._fields_[-1])
    Выполнить(класс, функция)

Обёртка__Вещ_в_стр = lambda экземпляр: Вещ_в_стр(экземпляр).replace('.', ',').replace('inf', 'Бскн')
Вещ_в_стр = float.__str__
Заменить_преобразование_в_строку(float, Обёртка__Вещ_в_стр)

Обёртка__Логич_в_стр = lambda экземпляр: Логич_в_стр(экземпляр).replace('True', 'Да').replace('False', 'Нет')
Логич_в_стр = bool.__str__
Заменить_преобразование_в_строку(bool, Обёртка__Логич_в_стр)

Обёртка__Пусто_в_стр = lambda экземпляр: Пусто_в_стр(экземпляр).replace('None', 'Пусто')
Пусто_в_стр = type(None).__str__
Заменить_преобразование_в_строку(type(None), Обёртка__Пусто_в_стр)

def Проверить_существование(код, местн, общ):
    try: eval(код, местн, общ)
    except Exception as ошибка:
        if type(ошибка) in (NameError, KeyError, AttributeError):
            print(ошибка)
            return False
        else: raise ошибка
    return True

def Заменить_ключи_в_словаре(словарь, замены):
    новый = {}
    for н, з in словарь.items():
        новый.setdefault(замены[н] if н in замены.keys() else н, з)
    return новый

def Свёртка(функция, перебираемое, нач_знач = None):
    рез = нач_знач if нач_знач else перебираемое[0]
    for эл in перебираемое: рез = функция(рез, эл)
    return рез

class ТрЛогич:
    _instance_map = {}

    def __new__(класс, название):
        if название not in класс._instance_map:
            класс._instance_map[название] = super().__new__(класс)
            класс._instance_map[название]._name = название
        return класс._instance_map[название]

    def __and__(экземпляр, значение):
        if not isinstance(значение, ТрЛогич):
            raise TypeError("Операция 'И' возможна только между троичными логическими значениями.")
        if экземпляр is Ложь or значение is Ложь: return Ложь
        if экземпляр is Истина and значение is Истина: return Истина
        return Неопр

    def __or__(экземпляр, значение):
        if not isinstance(значение, ТрЛогич):
            raise TypeError("Операция 'Или' возможна только между троичными логическими значениями.")
        if экземпляр is Истина or значение is Истина: return Истина
        if экземпляр is Ложь and значение is Ложь: return Ложь
        return Неопр

    def __invert__(экземпляр):
        if экземпляр is Истина: return Ложь
        if экземпляр is Ложь: return Истина
        return Неопр

    def __eq__(экземпляр, значение):
        if not isinstance(значение, ТрЛогич): return NotImplemented
        return экземпляр is значение

    def __bool__(экземпляр):
        if экземпляр is Истина: return True
        elif экземпляр is Ложь: return False
        else:
            raise TypeError("Невозможно преобразовать 'Неопр' в двоичное логическое значение.")

    def __repr__(экземпляр):
        return f"Троичное({экземпляр._name})"

    def __str__(экземпляр):
        return экземпляр._name

__builtins__.update(
    __Проверить_существование__ = Проверить_существование,
    Свёртка = Свёртка,
    Истина = ТрЛогич("Истина"), Ложь = ТрЛогич("ТрЛогич"), Неопр = ТрЛогич("Неопр")
)
