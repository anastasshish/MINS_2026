import os
import unittest

from sos import выполнить_код, выполнить_файл, Интерпретатор
from io import StringIO
import sys


class TestВозможности(unittest.TestCase):
    def test_массивы_всех_типов(self):
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            root = os.path.dirname(os.path.dirname(__file__))
            выполнить_файл(os.path.join(root, "examples", "массивы.сос"))
        finally:
            sys.stdout = old
        out = buf.getvalue()
        self.assertIn("динамический список", out)

    def test_наследование_и_модули(self):
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            root = os.path.dirname(os.path.dirname(__file__))
            выполнить_файл(os.path.join(root, "examples", "наследование.сос"))
        finally:
            sys.stdout = old
        out = buf.getvalue()
        self.assertIn("гав", out)
        self.assertIn("неверный формат", out)

    def test_файлы(self):
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        root = os.path.dirname(os.path.dirname(__file__))
        cwd = os.getcwd()
        try:
            os.chdir(root)
            выполнить_файл(os.path.join("examples", "файлы.сос"))
        finally:
            os.chdir(cwd)
            sys.stdout = old
        out = buf.getvalue()
        self.assertIn("Первая строка", out)
        self.assertIn("Вторая строка", out)

    def test_свои_исключения(self):
        with self.assertRaises(SystemExit):
            выполнить_код("""
                класс моя_ошибка(исключение) {
                    конструктор(строка сообщение) {
                        этот.сообщение = сообщение;
                    }
                }
                функция начало_начал() {
                    бросить новый моя_ошибка("тест");
                }
            """)


if __name__ == "__main__":
    unittest.main()
