import os

from sos.lexer import Лексер
from sos.parser import разобрать
from sos import ast_nodes as ast


def разрешить_путь(путь: str, базовая_директория: str) -> str:
    if not os.path.isabs(путь):
        путь = os.path.join(базовая_директория, путь)
    return os.path.normpath(os.path.abspath(путь))


def загрузить_программу(путь: str) -> ast.Программа:
    with open(путь, encoding="utf-8") as f:
        код = f.read()
    tokens = Лексер(код, путь).токенизировать()
    return разобрать(tokens)
