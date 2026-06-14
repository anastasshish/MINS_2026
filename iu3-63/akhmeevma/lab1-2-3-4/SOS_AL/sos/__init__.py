"""Интерпретатор языка программирования Сос."""

from sos.lexer import Лексер
from sos.parser import разобрать
from sos.interpreter import Интерпретатор
from sos.values import ИсключениеВыполнения
from sos.errors import ОшибкаСос

__all__ = ["Лексер", "разобрать", "Интерпретатор", "ИсключениеВыполнения", "ОшибкаСос", "выполнить_файл", "выполнить_код"]


def выполнить_код(исходный_код: str, имя_файла: str = "<программа>"):
    tokens = Лексер(исходный_код, имя_файла).токенизировать()
    tree = разобрать(tokens)
    interp = Интерпретатор()
    try:
        interp.выполнить_программу(tree)
    except ИсключениеВыполнения as e:
        msg = e.сообщение or "необработанное исключение"
        print(f"Исключение {e.класс.имя}: {msg}")
        raise SystemExit(1)


def выполнить_файл(путь: str):
    interp = Интерпретатор()
    try:
        interp.выполнить_файл(путь)
    except ИсключениеВыполнения as e:
        msg = e.сообщение or "необработанное исключение"
        print(f"Исключение {e.класс.имя}: {msg}")
        raise SystemExit(1)
    except ОшибкаСос as e:
        print(f"Ошибка: {e.format()}")
        raise SystemExit(1)
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        raise SystemExit(1)
