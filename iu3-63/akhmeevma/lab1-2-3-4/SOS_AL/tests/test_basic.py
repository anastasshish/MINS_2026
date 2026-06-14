import unittest

from sos.lexer import Лексер
from sos.parser import разобрать
from sos import выполнить_код, ОшибкаСос
from sos.values import ИсключениеВыполнения, Значение
from sos.types_check import привести_значение, ОшибкаТипов
from io import StringIO
import sys


class TestСос(unittest.TestCase):
    def test_лексер_комментарии(self):
        tokens = Лексер("// однострочный\nцелое х = 1;").токенизировать()
        types = [t.type.name for t in tokens if t.type.name != "КОНЕЦ_ФАЙЛА"]
        self.assertIn("ЦЕЛОЕ_ТИП", types)

    def test_арифметика(self):
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            выполнить_код("""
                функция начало_начал() {
                    целое а = 7;
                    целое б = 3;
                    печать(а / б, а % б);
                }
            """)
        finally:
            sys.stdout = old
        self.assertIn("2", buf.getvalue())
        self.assertIn("1", buf.getvalue())

    def test_исключение(self):
        with self.assertRaises(SystemExit):
            buf = StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                from sos import выполнить_файл
                import os
                path = os.path.join(os.path.dirname(__file__), "..", "examples", "test_throw.сос")
                with open(path, "w", encoding="utf-8") as f:
                    f.write("""
                        функция начало_начал() {
                            бросить новый деление_на_ноль("тест");
                        }
                    """)
                выполнить_файл(path)
            finally:
                sys.stdout = old

    def test_строка_к_целому(self):
        self.assertEqual(
            привести_значение("целое", Значение("строка", "42")).значение, 42
        )
        self.assertEqual(
            привести_значение("целое", Значение("строка", "-7")).значение, -7
        )
        self.assertEqual(
            привести_значение("целое", Значение("строка", "  13  ")).значение, 13
        )
        with self.assertRaises(ОшибкаТипов):
            привести_значение("целое", Значение("строка", "не число"))

        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            выполнить_код("""
                функция начало_начал() {
                    целое х = (целое)"100";
                    печать(х);
                }
            """)
        finally:
            sys.stdout = old
        self.assertIn("100", buf.getvalue())

    def test_строка_к_вещественному(self):
        self.assertEqual(
            привести_значение("вещественное", Значение("строка", "3.14")).значение, 3.14
        )
        self.assertEqual(
            привести_значение("вещественное", Значение("строка", "  150.0  ")).значение, 150.0
        )
        with self.assertRaises(ОшибкаТипов):
            привести_значение("вещественное", Значение("строка", "не число"))

    def test_иначе_если(self):
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            выполнить_код("""
                функция начало_начал() {
                    строка х = "2";
                    если (х == "1") { печать("one"); }
                    иначе_если (х == "2") { печать("two"); }
                    иначе_если (х == "3") { печать("three"); }
                    иначе { печать("other"); }
                }
            """)
        finally:
            sys.stdout = old
        self.assertIn("two", buf.getvalue())
        self.assertNotIn("other", buf.getvalue())

    def test_аргументы_метода_вычисляются_один_раз(self):
        calls = {"n": 0}

        def fake_input(_prompt=""):
            calls["n"] += 1
            return "ok"

        old_input = __builtins__["input"] if isinstance(__builtins__, dict) else __builtins__.input
        try:
            if isinstance(__builtins__, dict):
                __builtins__["input"] = fake_input
            else:
                import builtins
                builtins.input = fake_input
            выполнить_код("""
                класс Обёртка() {
                    функция принять(строка значение) строка {
                        вернуть значение;
                    }
                }

                функция начало_начал() {
                    Обёртка о = новый Обёртка();
                    строка результат = о.принять(ввод("> "));
                    печать(результат);
                }
            """)
        finally:
            if isinstance(__builtins__, dict):
                __builtins__["input"] = old_input
            else:
                import builtins
                builtins.input = old_input
        self.assertEqual(calls["n"], 1)

    def test_пустой_массив_возвращается_из_метода(self):
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            выполнить_код("""
                класс Хранилище() {
                    функция все() целое[] {
                        целое[] результат = новый целое[0];
                        вернуть результат;
                    }
                }
                функция начало_начал() {
                    Хранилище х = новый Хранилище();
                    целое[] данные = х.все();
                    печать("len:", длина(данные));
                }
            """)
        finally:
            sys.stdout = old
        self.assertIn("len: 0", buf.getvalue())

    def test_односимвольная_строка_остаётся_строкой(self):
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            выполнить_код("""
                функция начало_начал() {
                    строка буква = "я";
                    печать(тип(буква), длина(буква));
                }
            """)
        finally:
            sys.stdout = old
        self.assertIn("строка 1", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
