import os as ОС
import sys as Система

def Заменить_ключи_в_словаре(словарь, замены):
    новый = {}
    for н, з in словарь.items():
        новый.setdefault(замены[н] if н in замены.keys() else н, з)
    return новый

def Ожидать_нажатие_клавиши(сообщение):
    if ОС.name == 'nt':
        import msvcrt
        print('\n' + сообщение)
        msvcrt.getch()
    else:
        import tty
        import termios
        print('\n' + сообщение)
        fd = Система.stdin.fileno()
        старые_настройки = termios.tcgetattr(fd)
        try: tty.setraw(fd); Система.stdin.read(1)
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, старые_настройки)

def Склонение_после_числительного(число, слова):
    return str(число) + ' ' + (
        слова[2] if число % 100 >= 5 and число % 100 <= 20 else (
            слова[0] if число % 10 == 1 else (
                слова[1] if число % 10 >= 2 and число % 10 <= 4 else слова[2]
            )
        )
    )
