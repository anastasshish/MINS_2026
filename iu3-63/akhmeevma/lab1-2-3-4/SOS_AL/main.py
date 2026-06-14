#!/usr/bin/env python3
"""Точка входа интерпретатора языка Сос."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sos import выполнить_файл, выполнить_код, ОшибкаСос
from sos.values import ИсключениеВыполнения


def repl():
    print("Интерпретатор языка Сос (REPL). Выход: Ctrl+C или Ctrl+Z")
    buf = []
    while True:
        try:
            line = input(">>> " if not buf else "... ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        buf.append(line)
        if line.strip().endswith("}"):
            code = "\n".join(buf)
            buf = []
            try:
                выполнить_код(code)
            except (ОшибкаСос, ИсключениеВыполнения) as e:
                if isinstance(e, ИсключениеВыполнения):
                    print(f"Исключение {e.класс.имя}: {e.сообщение}")
                else:
                    print(f"Ошибка: {e.format()}")


def main():
    if len(sys.argv) < 2:
        repl()
        return
    arg = sys.argv[1]
    if arg in ("-h", "--help"):
        print("Использование: python main.py [файл.сос]")
        print("  без аргументов — интерактивный REPL")
        return
    if not os.path.isfile(arg):
        print(f"Файл не найден: {arg}")
        sys.exit(1)
    выполнить_файл(arg)


if __name__ == "__main__":
    main()
