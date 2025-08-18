import heapq
from rupython import __Общие_функции__

# Словарь для перевода параметров
Словарь_параметров = {
    'перебираемое': 'iterable',
    'ключ': 'key',
    'количество': 'n',
    'элемент': 'item'
}

Словарь_склонений = {
    'элемент': ['элемент', 'элемента', 'элементов']
}

def Склонение_после_числительного(число, слова):
    return str(число) + ' ' + (
        слова[2] if число % 100 >= 5 and число % 100 <= 20 else (
            слова[0] if число % 10 == 1 else (
                слова[1] if число % 10 >= 2 and число % 10 <= 4 else слова[2]
            )
        )
    )

class Куча:
    def __init__(экземпляр, перебираемое=None):
        экземпляр._heap = list(перебираемое or [])
        heapq.heapify(экземпляр._heap)

    def Добавить(экземпляр, элемент):
        heapq.heappush(экземпляр._heap, элемент)

    def Извлечь(экземпляр):
        if not экземпляр._heap:
            raise IndexError("Куча пуста")
        return heapq.heappop(экземпляр._heap)

    def Добавить_и_извлечь(экземпляр, элемент):
        return heapq.heappushpop(экземпляр._heap, элемент)

    def Заменить(экземпляр, элемент):
        if not экземпляр._heap:
            raise IndexError("Куча пуста")
        return heapq.heapreplace(экземпляр._heap, элемент)

    def Наибольшие(экземпляр, количество, ключ=None):
        kwargs = {'n': количество}
        if ключ is not None:
            kwargs['key'] = ключ
        return heapq.nlargest(**kwargs, iterable=экземпляр._heap)

    def Наименьшие(экземпляр, количество, ключ=None):
        kwargs = {'n': количество}
        if ключ is not None:
            kwargs['key'] = ключ
        return heapq.nsmallest(**kwargs, iterable=экземпляр._heap)

    def Размер(экземпляр):
        return len(экземпляр._heap)

    def Пустая(экземпляр):
        return len(экземпляр._heap) == 0

    def Получить_список(экземпляр):
        return list(экземпляр._heap)

    def __len__(экземпляр):
        return len(экземпляр._heap)

    def __iter__(экземпляр):
        return iter(экземпляр._heap)

    def __contains__(экземпляр, элемент):
        return элемент in экземпляр._heap

    def __str__(экземпляр):
        размер = экземпляр.Размер()
        return f"Куча с {Склонение_после_числительного(размер, Словарь_склонений['элемент'])}: {экземпляр._heap}"

def Слить_кучи(*перебираемые, ключ=None):
    kwargs = {}
    if ключ is not None:
        kwargs['key'] = ключ
    return heapq.merge(*перебираемые, **kwargs)

def Создать_кучу(перебираемое):
    return Куча(перебираемое)
