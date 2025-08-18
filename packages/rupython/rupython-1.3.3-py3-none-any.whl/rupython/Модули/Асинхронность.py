import asyncio

Задача_отменена = asyncio.CancelledError
Время_ожидания_истекло = asyncio.TimeoutError
Недопустимое_состояние = asyncio.InvalidStateError
Чтение_неполное = asyncio.IncompleteReadError
Буфер_переполнен = asyncio.LimitOverrunError
Ошибка_протокола_потока = asyncio.StreamReaderProtocol
Очередь_пуста = asyncio.QueueEmpty
Очередь_переполнена = asyncio.QueueFull

class Процедура:
	def __init__(экземпляр, функция, *аргументы, **параметры):
		экземпляр.функция = функция
		экземпляр.аргументы = аргументы
		экземпляр.параметры = параметры
		экземпляр.задача = None

	def Запустить(экземпляр):
		экземпляр.задача = asyncio.create_task(
			экземпляр.функция(*экземпляр.аргументы, **экземпляр.параметры)
		)
		return экземпляр.задача

	async def Ждать(экземпляр):
		if экземпляр.задача is None:
			экземпляр.задача = экземпляр.запустить()
		return await экземпляр.задача

class Задачи:
	def __init__(экземпляр):
		экземпляр.список = []

	def Добавить(экземпляр, процедура):
		задача = процедура.Запустить()
		экземпляр.список.append(задача)

	async def Ждать_все(экземпляр):
		return await asyncio.gather(*экземпляр.список)

class Процесс:
	def __init__(экземпляр, команда):
		экземпляр.команда = команда
		экземпляр.процесс = None

	async def Запустить(экземпляр):
		экземпляр.процесс = await asyncio.create_subprocess_shell(
			экземпляр.команда,
			stdout = asyncio.subprocess.PIPE,
			stderr = asyncio.subprocess.PIPE
		)
		stdout, stderr = await экземпляр.процесс.communicate()
		return {
			"код": экземпляр.процесс.returncode,
			"вывод": stdout.decode(),
			"ошибка": stderr.decode()
		}

class Поток:
	def __init__(экземпляр, поток_чтения):
		экземпляр.поток = поток_чтения

	async def читать_всё(экземпляр):
		строки = []
		while True:
			строка = await экземпляр.поток.readline()
			if not строка:
				break
			строки.append(строка.decode())
		return строки

class Блокование:
	def __init__(экземпляр):
		экземпляр.блокировка = asyncio.Lock()

	async def Выполнить(экземпляр, функция, *аргументы, **параметры):
		async with экземпляр.блокировка:
			return await функция(*аргументы, **параметры)

async def Спать(секунд):
	await asyncio.sleep(секунд)

def Запустить(процедура):
	return asyncio.run(процедура)

def Создать_задачу(процедура):
	return asyncio.create_task(процедура)

def Собрать(*процедуры):
	return asyncio.gather(*процедуры)

def Ожидать(объект, таймаут = None):
	return asyncio.wait_for(объект, timeout = таймаут)

def Все_задачи():
	return asyncio.all_tasks()

def Текущая_задача():
	return asyncio.current_task()
