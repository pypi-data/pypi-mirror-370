import random
from rupython import __Общие_функции__

# Управление
def НачЗнач(a = None): return random.seed(a, version = 2)
def Состояние(): return random.getstate()
def ЗадатьСостояние(состояние): return random.setstate(состояние)

# Байты
def СлучБайты(n): return random.randbytes(n)

# Целые числа
def ИзДиапазона(*ПА, **ИА):
    ИА = __Общие_функции__.Заменить_ключи_в_словаре(ИА, \
        { 'нач': 'start', 'кон': 'stop', 'шаг': 'step' })
    return random.randrange(*ПА, **ИА)
def СлучЦелое(a, b): return random.randint(a, b)
def СлучБиты(k): return random.getrandbits(k)

# Последовательности
def ВыбратьИзПосл(посл): return random.choice(посл)
def ВыбратьПосл(*ПА, **ИА):
    ИА = __Общие_функции__.Заменить_ключи_в_словаре(ИА, \
        { 'посл': 'population', 'веса': 'weights', 'накоплВеса': 'cum_weights' })
    return random.choices(*ПА, **ИА)
def Перемешать(x): return random.shuffle(x)
def СлучПосл(*ПА, **ИА):
    ИА = __Общие_функции__.Заменить_ключи_в_словаре(ИА, \
        { 'посл': 'population', 'колич': 'counts' })
    return random.sample(*ПА, **ИА)

# Дискретное распределение
def БиномРаспр(n, p): return random.binomialvariate(n, p)

# Вещественные числа
def От0До1(): return random.random()
def РавномернРаспр(a, b): return random.uniform(a, b)
def ТреугРаспр(нижнГр, верхГр, мода): return random.triangular(нижнГр, верхГр, мода)
def БетаРаспр(альфа, бета): return random.betavariate(альфа, бета)
def ЭкспРаспр(лямбда = 1.0): return random.expovariate(лямбда)
def ГаммаРаспр(альфа, бета): return random.gammavariate(альфа, бета)
def РаспрГаусса(мю = 0.0, сигма = 1.0): return random.gauss(мю, сигма)
def ЛогНормРаспр(мю, сигма): return random.lognormvariate(мю, сигма)
def НормРаспр(мю = 0.0, сигма = 1.0): return random.normalvariate(мю, сигма)
def РаспрМизеса(мю, каппа): return random.vonmisesvariate(мю, каппа)
def РаспрПарето(альфа): return random.paretovariate(альфа)
def РаспрВейбулла(альфа, бета): return random.weibullvariate(альфа, бета)
