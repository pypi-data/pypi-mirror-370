from setuptools import setup as Установить
from pathlib import Path as Путь

Установить(
    name = 'rupython',
    version = '1.3.3',
    description = "Исполнитель кода Русского Питона",
    packages = [ 'rupython', 'rupython.Модули' ],
    long_description = (Путь(__file__).parent / 'README.md').read_text('UTF-8'),
    long_description_content_type = 'text/markdown',

    author='Сообщество русских программистов',
    license='ОДРН',
    keywords='Россия, русский язык'
)
