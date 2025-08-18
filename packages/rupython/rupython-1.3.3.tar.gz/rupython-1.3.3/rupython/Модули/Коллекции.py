import collections
import collections.abc
from rupython import __Общие_функции__

_Последовательность = collections.abc.Sequence
_Изменяемая_последовательность = collections.abc.MutableSequence
_Отображение = collections.abc.Mapping
_Изменяемое_отображение = collections.abc.MutableMapping
_Множество = collections.abc.Set
_Изменяемое_множество = collections.abc.MutableSet

Словарь_параметров = {
    'имя': 'name',
    'поля': 'fields',
    'перебираемый': 'iterable',
    'максимальная_длина': 'maxlen',
    'функция_по_умолчанию': 'default_factory',
    'словари': 'maps',
    'ключ': 'key',
    'значение': 'value',
    'по_умолчанию': 'default',
    'количество': 'n'
}

class Именованный_кортеж(_Последовательность):
    def __init__(экземпляр, имя, поля):
        экземпляр._namedtuple = collections.namedtuple(имя, поля)

    def __call__(экземпляр, *ПА, **ИА):
        return экземпляр._namedtuple(*ПА, **ИА)

    def __getattr__(экземпляр, имя):
        return getattr(экземпляр._namedtuple, имя)

    def __getitem__(экземпляр, индекс):
        return экземпляр._namedtuple.__getitem__(индекс)

    def __len__(экземпляр):
        return len(экземпляр._namedtuple)

    def __iter__(экземпляр):
        return iter(экземпляр._namedtuple)

    def __contains__(экземпляр, элемент):
        return элемент in экземпляр._namedtuple

    def __reversed__(экземпляр):
        return reversed(экземпляр._namedtuple)

    def __str__(экземпляр):
        return str(экземпляр._namedtuple)

class Двусторонняя_очередь(_Изменяемая_последовательность):
    def __init__(экземпляр, перебираемый = None, максимальная_длина = None):
        ИА = {}
        if перебираемый is not None:
            ИА['iterable'] = перебираемый
        if максимальная_длина is not None:
            ИА['maxlen'] = максимальная_длина
        экземпляр._deque = collections.deque(**ИА)

    def Добавить_в_начало(экземпляр, элемент):
        экземпляр._deque.appendleft(элемент)

    def Добавить_в_конец(экземпляр, элемент):
        экземпляр._deque.append(элемент)

    def Удалить_с_начала(экземпляр):
        if not экземпляр._deque:
            raise IndexError("Очередь пуста")
        return экземпляр._deque.popleft()

    def Удалить_с_конца(экземпляр):
        if not экземпляр._deque:
            raise IndexError("Очередь пуста")
        return экземпляр._deque.pop()

    def Очистить(экземпляр):
        экземпляр._deque.clear()

    def Длина(экземпляр):
        return len(экземпляр._deque)

    def Расширить_в_начало(экземпляр, перебираемый):
        экземпляр._deque.extendleft(перебираемый)

    def Расширить_в_конец(экземпляр, перебираемый):
        экземпляр._deque.extend(перебираемый)

    def Повернуть(экземпляр, количество):
        экземпляр._deque.rotate(количество)

    def Перевернуть(экземпляр):
        экземпляр._deque.reverse()

    def Количество(экземпляр, элемент):
        return sum(1 for x in экземпляр._deque if x == элемент)

    def Индекс(экземпляр, элемент, начало = 0, конец = None):
        if конец is None:
            конец = len(экземпляр._deque)
        for i, x in enumerate(экземпляр._deque):
            if начало <= i < конец and x == элемент:
                return i
        raise ValueError(f"{элемент} не найден в диапазоне")

    def Вставить(экземпляр, индекс, значение):
        экземпляр._deque.rotate(-индекс)
        экземпляр._deque.appendleft(значение)
        экземпляр._deque.rotate(индекс)

    def __getitem__(экземпляр, индекс):
        return экземпляр._deque[индекс]

    def __setitem__(экземпляр, индекс, значение):
        экземпляр._deque[индекс] = значение

    def __delitem__(экземпляр, индекс):
        del экземпляр._deque[индекс]

    def __len__(экземпляр):
        return len(экземпляр._deque)

    def __iter__(экземпляр):
        return iter(экземпляр._deque)

    def __contains__(экземпляр, элемент):
        return элемент in экземпляр._deque

    def __reversed__(экземпляр):
        return iter(reversed(экземпляр._deque))

    def __str__(экземпляр):
        элементы = ', '.join(str(x) for x in экземпляр._deque)
        return f"Двусторонняя_очередь([{элементы}])"

class Счётчик(_Отображение):
    def __init__(экземпляр, перебираемый = None):
        экземпляр._counter = collections.Counter(перебираемый or [])

    def Обновить(экземпляр, перебираемый):
        экземпляр._counter.update(перебираемый)

    def Вычесть(экземпляр, перебираемый):
        экземпляр._counter.subtract(перебираемый)

    def Наиболее_частые(экземпляр, количество = None):
        return экземпляр._counter.most_common(количество)

    def Элементы(экземпляр):
        return list(экземпляр._counter.elements())

    def Получить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._counter.get(ключ, по_умолчанию)

    def __getitem__(экземпляр, ключ):
        return экземпляр._counter[ключ]

    def __setitem__(экземпляр, ключ, значение):
        экземпляр._counter[ключ] = значение

    def __delitem__(экземпляр, ключ):
        del экземпляр._counter[ключ]

    def __iter__(экземпляр):
        return iter(экземпляр._counter)

    def __len__(экземпляр):
        return len(экземпляр._counter)

    def __contains__(экземпляр, ключ):
        return ключ in экземпляр._counter

    def __add__(экземпляр, другой):
        if isinstance(другой, Счётчик):
            return Счётчик(экземпляр._counter + другой._counter)
        return NotImplemented

    def __sub__(экземпляр, другой):
        if isinstance(другой, Счётчик):
            return Счётчик(экземпляр._counter - другой._counter)
        return NotImplemented

    def __str__(экземпляр):
        элементы = ', '.join(f"{k}: {v}" for k, v in экземпляр._counter.items())
        return f"Счётчик({{{элементы}}})"

    def В_строку(экземпляр):
        if not экземпляр._counter:
            return "Пустой счётчик"
        элементы = []
        for ключ, количество in экземпляр._counter.items():
            слово = __Общие_функции__.Склонение_после_числительного(количество, ['элемент', 'элемента', 'элементов'])
            элементы.append(f"{ключ}: {слово}")
        return ', '.join(элементы)

class Упорядоченный_словарь(_Изменяемое_отображение):
    def __init__(экземпляр, *ПА, **ИА):
        экземпляр._ordered_dict = collections.OrderedDict(*ПА, **ИА)

    def Вставить(экземпляр, ключ, значение):
        экземпляр._ordered_dict[ключ] = значение

    def Удалить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._ordered_dict.pop(ключ, по_умолчанию)

    def Удалить_последний(экземпляр, последний = True):
        return экземпляр._ordered_dict.popitem(last = последний)

    def Получить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._ordered_dict.get(ключ, по_умолчанию)

    def Установить_по_умолчанию(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._ordered_dict.setdefault(ключ, по_умолчанию)

    def Ключи(экземпляр):
        return list(экземпляр._ordered_dict.keys())

    def Значения(экземпляр):
        return list(экземпляр._ordered_dict.values())

    def Элементы(экземпляр):
        return list(экземпляр._ordered_dict.items())

    def Переместить_в_конец(экземпляр, ключ, последний = True):
        экземпляр._ordered_dict.move_to_end(ключ, last = последний)

    def __getitem__(экземпляр, ключ):
        return экземпляр._ordered_dict[ключ]

    def __setitem__(экземпляр, ключ, значение):
        экземпляр._ordered_dict[ключ] = значение

    def __delitem__(экземпляр, ключ):
        del экземпляр._ordered_dict[ключ]

    def __iter__(экземпляр):
        return iter(экземпляр._ordered_dict)

    def __len__(экземпляр):
        return len(экземпляр._ordered_dict)

    def __contains__(экземпляр, ключ):
        return ключ in экземпляр._ordered_dict

    def __str__(экземпляр):
        элементы = ', '.join(f"{k}: {v}" for k, v in экземпляр._ordered_dict.items())
        return f"Упорядоченный_словарь({{{элементы}}})"

class Словарь_по_умолчанию(_Изменяемое_отображение):
    def __init__(экземпляр, функция_по_умолчанию = None, *ПА, **ИА):
        экземпляр._default_dict = collections.defaultdict(функция_по_умолчанию, *ПА, **ИА)

    def Получить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._default_dict.get(ключ, по_умолчанию)

    def Установить_по_умолчанию(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._default_dict.setdefault(ключ, по_умолчанию)

    def Удалить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._default_dict.pop(ключ, по_умолчанию)

    def Удалить_последний(экземпляр, последний = True):
        return экземпляр._default_dict.popitem(last = последний)

    def __getitem__(экземпляр, ключ):
        return экземпляр._default_dict[ключ]

    def __setitem__(экземпляр, ключ, значение):
        экземпляр._default_dict[ключ] = значение

    def __delitem__(экземпляр, ключ):
        del экземпляр._default_dict[ключ]

    def __iter__(экземпляр):
        return iter(экземпляр._default_dict)

    def __len__(экземпляр):
        return len(экземпляр._default_dict)

    def __contains__(экземпляр, ключ):
        return ключ in экземпляр._default_dict

    def Ключи(экземпляр):
        return list(экземпляр._default_dict.keys())

    def Значения(экземпляр):
        return list(экземпляр._default_dict.values())

    def Элементы(экземпляр):
        return list(экземпляр._default_dict.items())

    def __str__(экземпляр):
        элементы = ', '.join(f"{k}: {v}" for k, v in экземпляр._default_dict.items())
        return f"Словарь_по_умолчанию({{{элементы}}})"

class Слоистый_словарь(_Изменяемое_отображение):
    def __init__(экземпляр, *словари):
        экземпляр._chainmap = collections.ChainMap(*словари)

    def Новый_дочерний(экземпляр, словарь = None):
        return Слоистый_словарь(словарь or {}, *экземпляр._chainmap.maps)

    def Родители(экземпляр):
        return Слоистый_словарь(*экземпляр._chainmap.maps[1:])

    def Получить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._chainmap.get(ключ, по_умолчанию)

    def Установить_по_умолчанию(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._chainmap.setdefault(ключ, по_умолчанию)

    def Удалить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._chainmap.pop(ключ, по_умолчанию)

    def __getitem__(экземпляр, ключ):
        return экземпляр._chainmap[ключ]

    def __setitem__(экземпляр, ключ, значение):
        экземпляр._chainmap[ключ] = значение

    def __delitem__(экземпляр, ключ):
        del экземпляр._chainmap[ключ]

    def __iter__(экземпляр):
        return iter(экземпляр._chainmap)

    def __len__(экземпляр):
        return len(экземпляр._chainmap)

    def __contains__(экземпляр, ключ):
        return ключ in экземпляр._chainmap

    def Ключи(экземпляр):
        return list(экземпляр._chainmap.keys())

    def Значения(экземпляр):
        return list(экземпляр._chainmap.values())

    def Элементы(экземпляр):
        return list(экземпляр._chainmap.items())

    def __str__(экземпляр):
        элементы = ', '.join(f"{k}: {v}" for k, v in экземпляр._chainmap.items())
        return f"Слоистый_словарь({{{элементы}}})"

class Собственный_словарь(_Изменяемое_отображение):
    def __init__(экземпляр, *ПА, **ИА):
        экземпляр._user_dict = collections.UserDict(*ПА, **ИА)

    def Получить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._user_dict.get(ключ, по_умолчанию)

    def Установить_по_умолчанию(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._user_dict.setdefault(ключ, по_умолчанию)

    def Удалить(экземпляр, ключ, по_умолчанию = None):
        return экземпляр._user_dict.pop(ключ, по_умолчанию)

    def Удалить_последний(экземпляр, последний = True):
        return экземпляр._user_dict.popitem(last = последний)

    def __getitem__(экземпляр, ключ):
        return экземпляр._user_dict[ключ]

    def __setitem__(экземпляр, ключ, значение):
        экземпляр._user_dict[ключ] = значение

    def __delitem__(экземпляр, ключ):
        del экземпляр._user_dict[ключ]

    def __iter__(экземпляр):
        return iter(экземпляр._user_dict)

    def __len__(экземпляр):
        return len(экземпляр._user_dict)

    def __contains__(экземпляр, ключ):
        return ключ in экземпляр._user_dict

    def Ключи(экземпляр):
        return list(экземпляр._user_dict.keys())

    def Значения(экземпляр):
        return list(экземпляр._user_dict.values())

    def Элементы(экземпляр):
        return list(экземпляр._user_dict.items())

    def __str__(экземпляр):
        элементы = ', '.join(f"{k}: {v}" for k, v in экземпляр._user_dict.items())
        return f"Собственный_словарь({{{элементы}}})"

class Собственный_список(_Изменяемая_последовательность):
    def __init__(экземпляр, перебираемый = None):
        экземпляр._user_list = collections.UserList(перебираемый or [])

    def Добавить(экземпляр, элемент):
        экземпляр._user_list.append(элемент)

    def Вставить(экземпляр, индекс, элемент):
        экземпляр._user_list.insert(индекс, элемент)

    def Удалить(экземпляр, индекс = None):
        if индекс is None:
            return экземпляр._user_list.pop()
        return экземпляр._user_list.pop(индекс)

    def Очистить(экземпляр):
        экземпляр._user_list.clear()

    def Количество(экземпляр, элемент):
        return экземпляр._user_list.count(элемент)

    def Индекс(экземпляр, элемент, начало = 0, конец = None):
        return экземпляр._user_list.index(элемент, начало, конец or len(экземпляр._user_list))

    def Сортировать(экземпляр, ключ = None, по_убыванию = False):
        экземпляр._user_list.sort(key = ключ, reverse = по_убыванию)

    def Перевернуть(экземпляр):
        экземпляр._user_list.reverse()

    def Расширить(экземпляр, перебираемый):
        экземпляр._user_list.extend(перебираемый)

    def __getitem__(экземпляр, индекс):
        return экземпляр._user_list[индекс]

    def __setitem__(экземпляр, индекс, значение):
        экземпляр._user_list[индекс] = значение

    def __delitem__(экземпляр, индекс):
        del экземпляр._user_list[индекс]

    def __len__(экземпляр):
        return len(экземпляр._user_list)

    def __iter__(экземпляр):
        return iter(экземпляр._user_list)

    def __contains__(экземпляр, элемент):
        return элемент in экземпляр._user_list

    def __reversed__(экземпляр):
        return reversed(экземпляр._user_list)

    def __str__(экземпляр):
        return f"Собственный_список({list(экземпляр._user_list)})"

class Собственная_строка(_Последовательность):
    def __init__(экземпляр, строка = ""):
        экземпляр._user_string = collections.UserString(строка)

    def Разделить(экземпляр, разделитель = None):
        return экземпляр._user_string.split(разделитель)

    def Соединить(экземпляр, перебираемый):
        return экземпляр._user_string.join(перебираемый)

    def В_верхний_регистр(экземпляр):
        return Собственная_строка(экземпляр._user_string.upper())

    def В_нижний_регистр(экземпляр):
        return Собственная_строка(экземпляр._user_string.lower())

    def Начинается_с(экземпляр, префикс):
        return экземпляр._user_string.startswith(префикс)

    def Заканчивается_на(экземпляр, суффикс):
        return экземпляр._user_string.endswith(суффикс)

    def __getitem__(экземпляр, индекс):
        return экземпляр._user_string[индекс]

    def __len__(экземпляр):
        return len(экземпляр._user_string)

    def __iter__(экземпляр):
        return iter(экземпляр._user_string)

    def __contains__(экземпляр, элемент):
        return элемент in экземпляр._user_string

    def __reversed__(экземпляр):
        return reversed(экземпляр._user_string)

    def __str__(экземпляр):
        return str(экземпляр._user_string)

class Собственное_множество(_Изменяемое_множество):
    def __init__(экземпляр, перебираемый = None):
        экземпляр._set = set(перебираемый or [])

    def Добавить(экземпляр, элемент):
        экземпляр._set.add(элемент)

    def Удалить(экземпляр, элемент):
        try:
            экземпляр._set.remove(элемент)
        except KeyError:
            raise KeyError(f"Элемент {элемент} не найден")

    def Отбросить(экземпляр, элемент):
        экземпляр._set.discard(элемент)

    def Очистить(экземпляр):
        экземпляр._set.clear()

    def Объединить(экземпляр, другой):
        if isinstance(другой, Собственное_множество):
            return Собственное_множество(экземпляр._set | другой._set)
        return NotImplemented

    def Пересечь(экземпляр, другой):
        if isinstance(другой, Собственное_множество):
            return Собственное_множество(экземпляр._set & другой._set)
        return NotImplemented

    def Разность(экземпляр, другой):
        if isinstance(другой, Собственное_множество):
            return Собственное_множество(экземпляр._set - другой._set)
        return NotImplemented

    def Симметрическая_разность(экземпляр, другой):
        if isinstance(другой, Собственное_множество):
            return Собственное_множество(экземпляр._set ^ другой._set)
        return NotImplemented

    def __contains__(экземпляр, элемент):
        return элемент in экземпляр._set

    def __iter__(экземпляр):
        return iter(экземпляр._set)

    def __len__(экземпляр):
        return len(экземпляр._set)

    def __or__(экземпляр, другой):
        return экземпляр.Объединить(другой)

    def __and__(экземпляр, другой):
        return экземпляр.Пересечь(другой)

    def __sub__(экземпляр, другой):
        return экземпляр.Разность(другой)

    def __xor__(экземпляр, другой):
        return экземпляр.Симметрическая_разность(другой)

    def __str__(экземпляр):
        элементы = ', '.join(str(x) for x in экземпляр._set)
        return f"Собственное_множество({{{элементы}}})"

    def В_строку(экземпляр):
        длина = len(экземпляр._set)
        if длина == 0:
            return "Пустое множество"
        return f"Множество с {__Общие_функции__.Склонение_после_числительного(длина, ['элементом', 'элементами', 'элементами'])}: {{{', '.join(str(x) for x in экземпляр._set)}}}"
