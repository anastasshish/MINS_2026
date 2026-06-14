from typing import Optional

from sos.errors import ОшибкаСинтаксиса
from sos.tokens import Token, TokenType
from sos import ast_nodes as ast


class Парсер:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def _текущий(self) -> Token:
        return self.tokens[self.pos]

    def _ошибка(self, сообщение: str):
        t = self._текущий()
        raise ОшибкаСинтаксиса(сообщение, t.line, t.column)

    def _совпадает(self, *types: TokenType) -> bool:
        return self._текущий().type in types

    def _съесть(self, type_: TokenType, сообщение: str = "") -> Token:
        if self._текущий().type != type_:
            self._ошибка(сообщение or f"ожидался {type_.name}, получен {self._текущий().type.name}")
        tok = self._текущий()
        self.pos += 1
        return tok

    def _опционально(self, type_: TokenType) -> Optional[Token]:
        if self._текущий().type == type_:
            tok = self._текущий()
            self.pos += 1
            return tok
        return None

    def разобрать(self) -> ast.Программа:
        объявления = []
        while not self._совпадает(TokenType.КОНЕЦ_ФАЙЛА):
            if self._совпадает(TokenType.ПОДКЛЮЧИТЬ):
                объявления.append(self._разобрать_подключение())
            elif self._совпадает(TokenType.КЛАСС):
                объявления.append(self._разобрать_класс())
            elif self._совпадает(TokenType.ИНТЕРФЕЙС):
                объявления.append(self._разобрать_интерфейс())
            elif self._совпадает(TokenType.ФУНКЦИЯ, TokenType.НАЧАЛО_НАЧАЛ):
                объявления.append(self._разобрать_функцию())
            elif self._это_объявление_переменной():
                объявления.append(self._разобрать_объявление_переменной())
            else:
                self._ошибка("ожидалось объявление на верхнем уровне")
        return ast.Программа(объявления=объявления)

    def _разобрать_подключение(self) -> ast.Подключение:
        self._съесть(TokenType.ПОДКЛЮЧИТЬ)
        путь = self._съесть(TokenType.СТРОКА).value
        self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
        return ast.Подключение(путь=путь)

    def _это_тип(self) -> bool:
        return self._текущий().type in {
            TokenType.ЦЕЛОЕ_ТИП, TokenType.ВЕЩЕСТВЕННОЕ_ТИП, TokenType.СТРОКА_ТИП,
            TokenType.СИМВОЛ_ТИП, TokenType.ЛОГИЧЕСКОЕ_ТИП, TokenType.ПУСТОЕ_ТИП,
            TokenType.СЛОВАРЬ_ТИП, TokenType.ИДЕНТИФИКАТОР,
        }

    def _разобрать_имя_типа(self) -> tuple:
        if self._совпадает(TokenType.СЛОВАРЬ_ТИП):
            self._съесть(TokenType.СЛОВАРЬ_ТИП)
            self._съесть(TokenType.МЕНЬШЕ_УГОЛ)
            ключ = self._имя_типа_простой()
            self._съесть(TokenType.ЗАПЯТАЯ)
            знач = self._имя_типа_простой()
            self._съесть(TokenType.БОЛЬШЕ_УГОЛ)
            return f"словарь<{ключ},{знач}>", ключ, знач

        base = self._имя_типа_простой()
        размерность = 0
        while self._совпадает(TokenType.ЛЕВАЯ_КВАДРАТНАЯ):
            if self.pos + 1 >= len(self.tokens) or self.tokens[self.pos + 1].type != TokenType.ПРАВАЯ_КВАДРАТНАЯ:
                break
            self._съесть(TokenType.ЛЕВАЯ_КВАДРАТНАЯ)
            self._съесть(TokenType.ПРАВАЯ_КВАДРАТНАЯ)
            размерность += 1
        if размерность:
            return base + "[]" * размерность, None, None
        return base, None, None

    def _имя_типа_простой(self) -> str:
        t = self._текущий()
        mapping = {
            TokenType.ЦЕЛОЕ_ТИП: "целое",
            TokenType.ВЕЩЕСТВЕННОЕ_ТИП: "вещественное",
            TokenType.СТРОКА_ТИП: "строка",
            TokenType.СИМВОЛ_ТИП: "символ",
            TokenType.ЛОГИЧЕСКОЕ_ТИП: "логическое",
            TokenType.ПУСТОЕ_ТИП: "пустое",
        }
        if t.type in mapping:
            self.pos += 1
            return mapping[t.type]
        if t.type == TokenType.ИДЕНТИФИКАТОР:
            self.pos += 1
            return t.value
        self._ошибка("ожидалось имя типа")

    def _это_объявление_переменной(self) -> bool:
        if not self._это_тип():
            return False
        saved = self.pos
        try:
            self._разобрать_имя_типа()
            return self._текущий().type == TokenType.ИДЕНТИФИКАТОР
        finally:
            self.pos = saved

    def _разобрать_объявление_переменной(self) -> ast.ОбъявлениеПеременной:
        тип, ключ, знач = self._разобрать_имя_типа()
        имя = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        инициализатор = None
        if self._опционально(TokenType.ПРИСВОИТЬ):
            инициализатор = self._разобрать_выражение()
        self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
        return ast.ОбъявлениеПеременной(
            тип=тип, имя=имя,
            размерность=тип.count("[]"),
            ключевой_тип=ключ, значение_тип=знач,
            инициализатор=инициализатор,
        )

    def _разобрать_блок(self) -> ast.Блок:
        self._съесть(TokenType.ЛЕВАЯ_ФИГУРНАЯ)
        ops = []
        while not self._совпадает(TokenType.ПРАВАЯ_ФИГУРНАЯ):
            ops.append(self._разобрать_оператор())
        self._съесть(TokenType.ПРАВАЯ_ФИГУРНАЯ)
        return ast.Блок(операторы=ops)

    def _разобрать_оператор(self) -> ast.Оператор:
        if self._совпадает(TokenType.ЛЕВАЯ_ФИГУРНАЯ):
            return self._разобрать_блок()
        if self._это_объявление_переменной():
            return self._разобрать_объявление_переменной()
        if self._совпадает(TokenType.ЕСЛИ):
            return self._разобрать_если()
        if self._совпадает(TokenType.ПОКА):
            return self._разобрать_пока()
        if self._совпадает(TokenType.ДЛЯ):
            return self._разобрать_для()
        if self._совпадает(TokenType.ВЫБРАТЬ):
            return self._разобрать_выбрать()
        if self._совпадает(TokenType.ПРЕРВАТЬ):
            self._съесть(TokenType.ПРЕРВАТЬ)
            self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
            return ast.Прервать()
        if self._совпадает(TokenType.ПРОДОЛЖИТЬ):
            self._съесть(TokenType.ПРОДОЛЖИТЬ)
            self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
            return ast.Продолжить()
        if self._совпадает(TokenType.ВЫЙТИ, TokenType.ВЕРНУТЬ):
            return self._разобрать_возврат()
        if self._совпадает(TokenType.ПОПРОБОВАТЬ):
            return self._разобрать_попробовать()
        if self._совпадает(TokenType.БРОСИТЬ):
            return self._разобрать_бросить()
        return self._разобрать_присваивание_или_выражение()

    def _последний_если_в_цепочке(self, node: ast.Если) -> ast.Если:
        current = node
        while isinstance(current.иначе, ast.Если):
            current = current.иначе
        return current

    def _разобрать_если(self) -> ast.Если:
        self._съесть(TokenType.ЕСЛИ)
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        условие = self._разобрать_выражение()
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        тогда = self._разобрать_блок()
        иначе = None
        while self._совпадает(TokenType.ИНАЧЕ_ЕСЛИ) or (
            self._совпадает(TokenType.ИНАЧЕ) and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == TokenType.ЕСЛИ
        ):
            if self._совпадает(TokenType.ИНАЧЕ_ЕСЛИ):
                self._съесть(TokenType.ИНАЧЕ_ЕСЛИ)
            else:
                self._съесть(TokenType.ИНАЧЕ)
                self._съесть(TokenType.ЕСЛИ)
            self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
            cond2 = self._разобрать_выражение()
            self._съесть(TokenType.ПРАВАЯ_СКОБКА)
            body2 = self._разобрать_блок()
            иначе = ast.Если(условие=cond2, тогда=body2, иначе=иначе)
        if self._совпадает(TokenType.ИНАЧЕ):
            self._съесть(TokenType.ИНАЧЕ)
            final = self._разобрать_блок()
            if иначе is None:
                иначе = final
            else:
                self._последний_если_в_цепочке(иначе).иначе = final
        return ast.Если(условие=условие, тогда=тогда, иначе=иначе)

    def _разобрать_пока(self) -> ast.Пока:
        self._съесть(TokenType.ПОКА)
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        условие = self._разобрать_выражение()
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        self._съесть(TokenType.ВЫПОЛНЯТЬ)
        тело = self._разобрать_блок()
        return ast.Пока(условие=условие, тело=тело)

    def _разобрать_для(self) -> ast.Для:
        self._съесть(TokenType.ДЛЯ)
        var = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        self._съесть(TokenType.В)
        итер = self._разобрать_выражение()
        self._съесть(TokenType.ДЕЛАТЬ)
        тело = self._разобрать_блок()
        return ast.Для(переменная=var, итерируемое=итер, тело=тело)

    def _разобрать_выбрать(self) -> ast.Выбрать:
        self._съесть(TokenType.ВЫБРАТЬ)
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        expr = self._разобрать_выражение()
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        self._съесть(TokenType.ЛЕВАЯ_ФИГУРНАЯ)
        варианты = []
        while self._совпадает(TokenType.ВАРИАНТ):
            self._съесть(TokenType.ВАРИАНТ)
            val = self._разобрать_выражение()
            self._съесть(TokenType.ДВОЕТОЧИЕ)
            if self._совпадает(TokenType.ЛЕВАЯ_ФИГУРНАЯ):
                block = self._разобрать_блок()
            else:
                self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
                block = ast.Блок(операторы=[self._разобрать_выражение()])
                self._съесть(TokenType.ПРАВАЯ_СКОБКА)
            self._опционально(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
            варианты.append((val, block))
        default = None
        if self._совпадает(TokenType.ИНАЧЕ):
            self._съесть(TokenType.ИНАЧЕ)
            default = self._разобрать_блок()
        self._съесть(TokenType.ПРАВАЯ_ФИГУРНАЯ)
        return ast.Выбрать(выражение=expr, варианты=варианты, по_умолчанию=default)

    def _разобрать_возврат(self) -> ast.Вернуть:
        if not self._совпадает(TokenType.ВЫЙТИ, TokenType.ВЕРНУТЬ):
            self._ошибка("ожидался выйти или вернуть")
        self.pos += 1
        val = None
        if not self._совпадает(TokenType.ТОЧКА_С_ЗАПЯТОЙ):
            val = self._разобрать_выражение()
        self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
        return ast.Вернуть(значение=val)

    def _разобрать_попробовать(self) -> ast.Попробовать:
        self._съесть(TokenType.ПОПРОБОВАТЬ)
        тело = self._разобрать_блок()
        handlers = []
        while self._совпадает(TokenType.СЛОВИТЬ):
            self._съесть(TokenType.СЛОВИТЬ)
            type_name = None
            var_name = None
            if not self._совпадает(TokenType.ЛЕВАЯ_ФИГУРНАЯ):
                type_name = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
                if self._совпадает(TokenType.КАК):
                    self._съесть(TokenType.КАК)
                    var_name = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
            block = self._разобрать_блок()
            handlers.append((type_name, var_name, block))
        finally_block = None
        if self._совпадает(TokenType.НАКОНЕЦ):
            self._съесть(TokenType.НАКОНЕЦ)
            finally_block = self._разобрать_блок()
        return ast.Попробовать(тело=тело, обработчики=handlers, наконец=finally_block)

    def _разобрать_бросить(self) -> ast.Бросить:
        self._съесть(TokenType.БРОСИТЬ)
        exc = self._разобрать_выражение()
        self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
        return ast.Бросить(исключение=exc)

    def _разобрать_присваивание_или_выражение(self) -> ast.Оператор:
        expr = self._разобрать_выражение()
        assign_ops = {
            TokenType.ПРИСВОИТЬ: "=",
            TokenType.ПЛЮС_ПРИСВОИТЬ: "+=",
            TokenType.МИНУС_ПРИСВОИТЬ: "-=",
            TokenType.ПЛЮС_ПЛЮС_ПРИСВОИТЬ: "++=",
            TokenType.МИНУС_МИНУС_ПРИСВОИТЬ: "--=",
        }
        if self._текущий().type in assign_ops:
            op = assign_ops[self._текущий().type]
            self.pos += 1
            val = self._разобрать_выражение()
            self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
            return ast.Присваивание(цель=expr, оператор=op, значение=val)
        self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
        return ast.ВыражениеКакОператор(выражение=expr)

    # --- Выражения ---

    def _разобрать_выражение(self) -> ast.Выражение:
        return self._разобрать_или()

    def _разобрать_или(self) -> ast.Выражение:
        left = self._разобрать_и()
        while self._совпадает(TokenType.ИЛИ):
            self._съесть(TokenType.ИЛИ)
            right = self._разобрать_и()
            left = ast.БинарнаяОперация(лево=left, оператор="или", право=right)
        return left

    def _разобрать_и(self) -> ast.Выражение:
        left = self._разобрать_равенство()
        while self._совпадает(TokenType.И):
            self._съесть(TokenType.И)
            right = self._разобрать_равенство()
            left = ast.БинарнаяОперация(лево=left, оператор="и", право=right)
        return left

    def _разобрать_равенство(self) -> ast.Выражение:
        left = self._разобрать_сравнение()
        while self._совпадает(TokenType.РАВНО, TokenType.НЕ_РАВНО):
            op = "==" if self._текущий().type == TokenType.РАВНО else "!="
            self.pos += 1
            right = self._разобрать_сравнение()
            left = ast.БинарнаяОперация(лево=left, оператор=op, право=right)
        return left

    def _разобрать_сравнение(self) -> ast.Выражение:
        left = self._разобрать_сложение()
        while self._совпадает(TokenType.МЕНЬШЕ, TokenType.БОЛЬШЕ, TokenType.МЕНЬШЕ_РАВНО, TokenType.БОЛЬШЕ_РАВНО):
            op_map = {
                TokenType.МЕНЬШЕ: "<",
                TokenType.БОЛЬШЕ: ">",
                TokenType.МЕНЬШЕ_РАВНО: "<=",
                TokenType.БОЛЬШЕ_РАВНО: ">=",
            }
            op = op_map[self._текущий().type]
            self.pos += 1
            right = self._разобрать_сложение()
            left = ast.БинарнаяОперация(лево=left, оператор=op, право=right)
        return left

    def _разобрать_сложение(self) -> ast.Выражение:
        left = self._разобрать_умножение()
        while self._совпадает(TokenType.ПЛЮС, TokenType.МИНУС):
            op = "+" if self._текущий().type == TokenType.ПЛЮС else "-"
            self.pos += 1
            right = self._разобрать_умножение()
            left = ast.БинарнаяОперация(лево=left, оператор=op, право=right)
        return left

    def _разобрать_умножение(self) -> ast.Выражение:
        left = self._разобрать_степень()
        while self._совпадает(TokenType.УМНОЖИТЬ, TokenType.РАЗДЕЛИТЬ, TokenType.ОСТАТОК):
            op_map = {TokenType.УМНОЖИТЬ: "*", TokenType.РАЗДЕЛИТЬ: "/", TokenType.ОСТАТОК: "%"}
            op = op_map[self._текущий().type]
            self.pos += 1
            right = self._разобрать_степень()
            left = ast.БинарнаяОперация(лево=left, оператор=op, право=right)
        return left

    def _разобрать_степень(self) -> ast.Выражение:
        left = self._разобрать_унарное()
        if self._совпадает(TokenType.СТЕПЕНЬ):
            self._съесть(TokenType.СТЕПЕНЬ)
            right = self._разобрать_степень()
            return ast.БинарнаяОперация(лево=left, оператор="^", право=right)
        return left

    def _разобрать_унарное(self) -> ast.Выражение:
        if self._совпадает(TokenType.МИНУС, TokenType.НЕ):
            op = "не" if self._текущий().type == TokenType.НЕ else "-"
            self.pos += 1
            return ast.УнарнаяОперация(оператор=op, операнд=self._разобрать_унарное())
        return self._разобрать_первичное()

    def _попытка_приведение_через_вызов(self) -> ast.Выражение | None:
        type_tokens = {
            TokenType.ЦЕЛОЕ_ТИП: "целое",
            TokenType.ВЕЩЕСТВЕННОЕ_ТИП: "вещественное",
            TokenType.СТРОКА_ТИП: "строка",
            TokenType.СИМВОЛ_ТИП: "символ",
            TokenType.ЛОГИЧЕСКОЕ_ТИП: "логическое",
            TokenType.ПУСТОЕ_ТИП: "пустое",
        }
        if self._текущий().type not in type_tokens:
            return None
        if self.pos + 1 >= len(self.tokens) or self.tokens[self.pos + 1].type != TokenType.ЛЕВАЯ_СКОБКА:
            return None
        tname = type_tokens[self._текущий().type]
        self.pos += 1
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        inner = self._разобрать_выражение()
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        return ast.ПриведениеТипа(целевой_тип=tname, выражение=inner)

    def _разобрать_первичное(self) -> ast.Выражение:
        if self._совпадает(TokenType.НОВЫЙ):
            return self._разобрать_новый()
        cast = self._попытка_приведение_через_вызов()
        if cast:
            return self._разобрать_хвост_вызова(cast)
        if self._совпадает(TokenType.ЭТОТ):
            self._съесть(TokenType.ЭТОТ)
            return self._разобрать_хвост_вызова(ast.Это())
        if self._совпадает(TokenType.ЦЕЛОЕ):
            v = self._съесть(TokenType.ЦЕЛОЕ).value
            return ast.Литерал(значение=v)
        if self._совпадает(TokenType.ВЕЩЕСТВЕННОЕ):
            v = self._съесть(TokenType.ВЕЩЕСТВЕННОЕ).value
            return ast.Литерал(значение=v)
        if self._совпадает(TokenType.СТРОКА):
            v = self._съесть(TokenType.СТРОКА).value
            return ast.Литерал(значение=v, имя_типа="строка")
        if self._совпадает(TokenType.СИМВОЛ):
            v = self._съесть(TokenType.СИМВОЛ).value
            return ast.Литерал(значение=v, имя_типа="символ")
        if self._совпадает(TokenType.ДА):
            self._съесть(TokenType.ДА)
            return ast.Литерал(значение=True)
        if self._совпадает(TokenType.НЕТ):
            self._съесть(TokenType.НЕТ)
            return ast.Литерал(значение=False)
        if self._совпадает(TokenType.НУЛЬ):
            self._съесть(TokenType.НУЛЬ)
            return ast.Литерал(значение=None)

        # приведение типа (целое) x
        if self._совпадает(TokenType.ЛЕВАЯ_СКОБКА):
            saved = self.pos
            self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
            if self._это_тип():
                t, _, _ = self._разобрать_имя_типа()
                if self._совпадает(TokenType.ПРАВАЯ_СКОБКА):
                    self._съесть(TokenType.ПРАВАЯ_СКОБКА)
                    expr = self._разобрать_унарное()
                    return ast.ПриведениеТипа(целевой_тип=t, выражение=expr)
            self.pos = saved

        if self._совпадает(TokenType.ИДЕНТИФИКАТОР, TokenType.РОДИТЕЛЬ):
            name_tok = self._текущий()
            self.pos += 1
            expr = ast.Переменная(имя=name_tok.value)
        elif self._совпадает(TokenType.ЛЕВАЯ_СКОБКА):
            if self._это_кортеж_литерал():
                expr = self._разобрать_кортеж_литерал()
            else:
                self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
                expr = self._разобрать_выражение()
                self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        elif self._совпадает(TokenType.ЛЕВАЯ_КВАДРАТНАЯ):
            expr = self._разобрать_массив_литерал()
        elif self._совпадает(TokenType.ЛЕВАЯ_ФИГУРНАЯ):
            expr = self._разобрать_словарь_литерал()
        else:
            self._ошибка("ожидалось выражение")

        return self._разобрать_хвост_вызова(expr)

    def _разобрать_массив_литерал(self) -> ast.НовыйМассив:
        self._съесть(TokenType.ЛЕВАЯ_КВАДРАТНАЯ)
        elems = []
        if not self._совпадает(TokenType.ПРАВАЯ_КВАДРАТНАЯ):
            elems.append(self._разобрать_выражение())
            while self._опционально(TokenType.ЗАПЯТАЯ):
                elems.append(self._разобрать_выражение())
        self._съесть(TokenType.ПРАВАЯ_КВАДРАТНАЯ)
        return ast.НовыйМассив(тип_элемента="", элементы=elems)

    def _это_кортеж_литерал(self) -> bool:
        saved = self.pos
        try:
            self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
            if self._совпадает(TokenType.ПРАВАЯ_СКОБКА):
                return False
            self._разобрать_выражение()
            return self._совпадает(TokenType.ЗАПЯТАЯ)
        finally:
            self.pos = saved

    def _разобрать_кортеж_литерал(self) -> ast.НовыйМассив:
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        elems = []
        if not self._совпадает(TokenType.ПРАВАЯ_СКОБКА):
            elems.append(self._разобрать_выражение())
            while self._опционально(TokenType.ЗАПЯТАЯ):
                elems.append(self._разобрать_выражение())
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        return ast.НовыйМассив(тип_элемента="", элементы=elems)

    def _разобрать_словарь_литерал(self) -> ast.НовыйСловарь:
        self._съесть(TokenType.ЛЕВАЯ_ФИГУРНАЯ)
        пары = []
        if not self._совпадает(TokenType.ПРАВАЯ_ФИГУРНАЯ):
            k = self._разобрать_выражение()
            self._съесть(TokenType.ДВОЕТОЧИЕ)
            v = self._разобрать_выражение()
            пары.append((k, v))
            while self._опционально(TokenType.ЗАПЯТАЯ):
                k = self._разобрать_выражение()
                self._съесть(TokenType.ДВОЕТОЧИЕ)
                v = self._разобрать_выражение()
                пары.append((k, v))
        self._съесть(TokenType.ПРАВАЯ_ФИГУРНАЯ)
        return ast.НовыйСловарь(пары=пары)

    def _разобрать_новый(self) -> ast.Выражение:
        self._съесть(TokenType.НОВЫЙ)
        if self._это_тип():
            if (
                self.pos + 1 < len(self.tokens)
                and self.tokens[self.pos + 1].type == TokenType.ЛЕВАЯ_КВАДРАТНАЯ
            ):
                elem = self._имя_типа_простой()
                self._съесть(TokenType.ЛЕВАЯ_КВАДРАТНАЯ)
                size = self._разобрать_выражение()
                self._съесть(TokenType.ПРАВАЯ_КВАДРАТНАЯ)
                return ast.НовыйМассив(тип_элемента=elem, размер=size)
            t, _, _ = self._разобрать_имя_типа()
            self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
            args = self._разобрать_аргументы()
            self._съесть(TokenType.ПРАВАЯ_СКОБКА)
            return ast.НовыйОбъект(тип_имя=t, аргументы=args)
        имя = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        args = self._разобрать_аргументы()
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        return ast.НовыйОбъект(тип_имя=имя, аргументы=args)

    def _разобрать_аргументы(self) -> list:
        args = []
        if not self._совпадает(TokenType.ПРАВАЯ_СКОБКА):
            args.append(self._разобрать_выражение())
            while self._опционально(TokenType.ЗАПЯТАЯ):
                args.append(self._разобрать_выражение())
        return args

    def _имя_поля(self) -> str:
        if self._совпадает(TokenType.ИДЕНТИФИКАТОР):
            return self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        if self._совпадает(TokenType.КОНСТРУКТОР):
            return self._съесть(TokenType.КОНСТРУКТОР).value
        self._ошибка("ожидалось имя поля или метода")

    def _разобрать_хвост_вызова(self, expr: ast.Выражение) -> ast.Выражение:
        while True:
            if self._совпадает(TokenType.ЛЕВАЯ_СКОБКА):
                self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
                args = self._разобрать_аргументы()
                self._съесть(TokenType.ПРАВАЯ_СКОБКА)
                expr = ast.Вызов(callee=expr, аргументы=args)
            elif self._совпадает(TokenType.ТОЧКА):
                self._съесть(TokenType.ТОЧКА)
                field = self._имя_поля()
                expr = ast.ДоступКПолю(объект=expr, поле=field)
            elif self._совпадает(TokenType.ЛЕВАЯ_КВАДРАТНАЯ):
                self._съесть(TokenType.ЛЕВАЯ_КВАДРАТНАЯ)
                idx = self._разобрать_выражение()
                self._съесть(TokenType.ПРАВАЯ_КВАДРАТНАЯ)
                expr = ast.Индекс(массив=expr, индекс=idx)
            else:
                break
        return expr

    # --- Классы и функции ---

    def _разобрать_модификатор(self) -> str:
        if self._совпадает(TokenType.ПУБЛИЧНЫЙ):
            self._съесть(TokenType.ПУБЛИЧНЫЙ)
            return "публичный"
        if self._совпадает(TokenType.ПРИВАТНЫЙ):
            self._съесть(TokenType.ПРИВАТНЫЙ)
            return "приватный"
        if self._совпадает(TokenType.ЗАЩИЩЁННЫЙ):
            self._съесть(TokenType.ЗАЩИЩЁННЫЙ)
            return "защищённый"
        return "публичный"

    def _разобрать_функцию(self) -> ast.ОбъявлениеФункции:
        if self._совпадает(TokenType.НАЧАЛО_НАЧАЛ):
            self._съесть(TokenType.НАЧАЛО_НАЧАЛ)
            имя = "начало_начал"
        else:
            self._съесть(TokenType.ФУНКЦИЯ)
            if self._совпадает(TokenType.НАЧАЛО_НАЧАЛ):
                имя = self._съесть(TokenType.НАЧАЛО_НАЧАЛ).value
            else:
                имя = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        params = self._разобрать_параметры()
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        ret_type = None
        if self._это_тип():
            ret_type, _, _ = self._разобрать_имя_типа()
        body = self._разобрать_блок()
        return ast.ОбъявлениеФункции(имя=имя, параметры=params, возвращаемый_тип=ret_type, тело=body)

    def _разобрать_параметры(self) -> list:
        params = []
        if not self._совпадает(TokenType.ПРАВАЯ_СКОБКА):
            params.append(self._разобрать_параметр())
            while self._опционально(TokenType.ЗАПЯТАЯ):
                params.append(self._разобрать_параметр())
        return params

    def _разобрать_параметр(self) -> ast.Параметр:
        t, _, _ = self._разобрать_имя_типа()
        name = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        default = None
        if self._опционально(TokenType.ПРИСВОИТЬ):
            default = self._разобрать_выражение()
        return ast.Параметр(тип=t, имя=name, значение_по_умолчанию=default)

    def _разобрать_класс(self) -> ast.ОбъявлениеКласса:
        self._съесть(TokenType.КЛАСС)
        имя = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        parent = None
        interfaces = []
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        if not self._совпадает(TokenType.ПРАВАЯ_СКОБКА):
            parent = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        if self._совпадает(TokenType.РЕАЛИЗУЕТ):
            self._съесть(TokenType.РЕАЛИЗУЕТ)
            interfaces.append(self._съесть(TokenType.ИДЕНТИФИКАТОР).value)
            while self._опционально(TokenType.ЗАПЯТАЯ):
                interfaces.append(self._съесть(TokenType.ИДЕНТИФИКАТОР).value)
        self._съесть(TokenType.ЛЕВАЯ_ФИГУРНАЯ)
        поля, методы, ctor = [], [], None
        while not self._совпадает(TokenType.ПРАВАЯ_ФИГУРНАЯ):
            override = False
            if self._совпадает(TokenType.ПЕРЕОПРЕДЕЛИТЬ):
                self._съесть(TokenType.ПЕРЕОПРЕДЕЛИТЬ)
                override = True
            mod = self._разобрать_модификатор()
            if self._совпадает(TokenType.КОНСТРУКТОР):
                ctor = self._разобрать_метод(конструктор=True, mod=mod, переопределить=override)
            elif self._совпадает(TokenType.ФУНКЦИЯ):
                методы.append(self._разобрать_метод(mod=mod, переопределить=override))
            elif self._это_тип():
                t, _, _ = self._разобрать_имя_типа()
                fname = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
                init = None
                if self._опционально(TokenType.ПРИСВОИТЬ):
                    init = self._разобрать_выражение()
                self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
                поля.append(ast.ОбъявлениеПоля(тип=t, имя=fname, модификатор=mod, инициализатор=init))
            else:
                self._ошибка("ожидалось поле, метод или конструктор")
        self._съесть(TokenType.ПРАВАЯ_ФИГУРНАЯ)
        return ast.ОбъявлениеКласса(имя=имя, родитель=parent, интерфейсы=interfaces, поля=поля, методы=методы, конструктор=ctor)

    def _разобрать_метод(self, конструктор=False, mod="публичный", переопределить=False) -> ast.ОбъявлениеМетода:
        if конструктор:
            self._съесть(TokenType.КОНСТРУКТОР)
            имя = "конструктор"
        else:
            self._съесть(TokenType.ФУНКЦИЯ)
            имя = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        params = self._разобрать_параметры()
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        ret = None
        if not конструктор and self._это_тип():
            ret, _, _ = self._разобрать_имя_типа()
        body = self._разобрать_блок() if self._совпадает(TokenType.ЛЕВАЯ_ФИГУРНАЯ) else ast.Блок()
        return ast.ОбъявлениеМетода(имя=имя, параметры=params, возвращаемый_тип=ret, тело=body, модификатор=mod, переопределить=переопределить)

    def _разобрать_интерфейс(self) -> ast.ОбъявлениеИнтерфейса:
        self._съесть(TokenType.ИНТЕРФЕЙС)
        имя = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
        self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
        self._съесть(TokenType.ПРАВАЯ_СКОБКА)
        self._съесть(TokenType.ЛЕВАЯ_ФИГУРНАЯ)
        методы = []
        while not self._совпадает(TokenType.ПРАВАЯ_ФИГУРНАЯ):
            mod = self._разобрать_модификатор()
            self._съесть(TokenType.ФУНКЦИЯ)
            mname = self._съесть(TokenType.ИДЕНТИФИКАТОР).value
            self._съесть(TokenType.ЛЕВАЯ_СКОБКА)
            params = self._разобрать_параметры()
            self._съесть(TokenType.ПРАВАЯ_СКОБКА)
            ret = None
            if self._это_тип():
                ret, _, _ = self._разобрать_имя_типа()
            self._съесть(TokenType.ТОЧКА_С_ЗАПЯТОЙ)
            методы.append(ast.ОбъявлениеМетода(имя=mname, параметры=params, возвращаемый_тип=ret, тело=ast.Блок(), модификатор=mod))
        self._съесть(TokenType.ПРАВАЯ_ФИГУРНАЯ)
        return ast.ОбъявлениеИнтерфейса(имя=имя, методы=методы)


def разобрать(tokens: list) -> ast.Программа:
    return Парсер(tokens).разобрать()
