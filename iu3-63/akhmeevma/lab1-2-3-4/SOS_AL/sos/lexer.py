import re

from sos.errors import ОшибкаЛексера
from sos.tokens import KEYWORDS, Token, TokenType

# Кириллица + цифры + ? ! - _
IDENT_PATTERN = re.compile(
    r"[а-яА-ЯёЁ][а-яА-ЯёЁ0-9?!_-]*|[а-яА-ЯёЁ0-9?!_-]+"
)
NUMBER_PATTERN = re.compile(r"-?\d+(\.\d+)?")
CHAR_PATTERN = re.compile(r"'(\\.|.)'")


class Лексер:
    def __init__(self, исходный_код: str, имя_файла: str = "<программа>"):
        self.исходный_код = исходный_код
        self.имя_файла = имя_файла
        self.позиция = 0
        self.строка = 1
        self.столбец = 1
        self.длина = len(исходный_код)

    def _ошибка(self, сообщение: str):
        raise ОшибкаЛексера(сообщение, self.строка, self.столбец)

    def _текущий(self) -> str:
        if self.позиция >= self.длина:
            return "\0"
        return self.исходный_код[self.позиция]

    def _следующий(self) -> str:
        ch = self._текущий()
        self.позиция += 1
        if ch == "\n":
            self.строка += 1
            self.столбец = 1
        else:
            self.столбец += 1
        return ch

    def _пропустить_пробелы(self):
        while self._текущий() in " \t\r\n":
            self._следующий()

    def _пропустить_комментарий(self):
        if self._текущий() != "/" or self.позиция + 1 >= self.длина or self.исходный_код[self.позиция + 1] != "/":
            return
        self._следующий()
        self._следующий()

        # многострочный: //<пусто> ... //
        rest_of_line = ""
        scan = self.позиция
        while scan < self.длина and self.исходный_код[scan] != "\n":
            rest_of_line += self.исходный_код[scan]
            scan += 1
        if rest_of_line.strip() == "":
            while self.позиция < self.длина:
                if self._текущий() == "/" and self.позиция + 1 < self.длина and self.исходный_код[self.позиция + 1] == "/":
                    self._следующий()
                    self._следующий()
                    return
                self._следующий()
            return

        # однострочный: до конца строки
        while self.позиция < self.длина and self._текущий() != "\n":
            self._следующий()

    def _читать_строку(self) -> str:
        self._следующий()
        result = []
        while self._текущий() != '"':
            if self._текущий() == "\0":
                self._ошибка("незакрытая строковая константа")
            if self._текущий() == "\\":
                self._следующий()
                esc = self._текущий()
                mapping = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                result.append(mapping.get(esc, esc))
                self._следующий()
            else:
                result.append(self._следующий())
        self._следующий()
        return "".join(result)

    def _читать_число(self) -> Token:
        start_col = self.столбец
        match = NUMBER_PATTERN.match(self.исходный_код, self.позиция)
        if not match:
            self._ошибка("некорректное числовое литерало")
        text = match.group()
        self.позиция += len(text)
        self.столбец += len(text)
        if "." in text:
            return Token(TokenType.ВЕЩЕСТВЕННОЕ, float(text), self.строка, start_col)
        return Token(TokenType.ЦЕЛОЕ, int(text), self.строка, start_col)

    def _читать_идентификатор(self) -> Token:
        start_col = self.столбец
        match = IDENT_PATTERN.match(self.исходный_код, self.позиция)
        if not match:
            self._ошибка(f"недопустимый символ '{self._текущий()}'")
        text = match.group()
        self.позиция += len(text)
        self.столбец += len(text)
        kw = KEYWORDS.get(text)
        if kw:
            return Token(kw, text, self.строка, start_col)
        return Token(TokenType.ИДЕНТИФИКАТОР, text, self.строка, start_col)

    def следующий_токен(self) -> Token:
        while True:
            self._пропустить_пробелы()
            if self.позиция >= self.длина:
                return Token(TokenType.КОНЕЦ_ФАЙЛА, None, self.строка, self.столбец)

            if self._текущий() == "/" and self.позиция + 1 < self.длина and self.исходный_код[self.позиция + 1] == "/":
                self._пропустить_комментарий()
                continue

            start_line = self.строка
            start_col = self.столбец
            ch = self._текущий()

            двусимвольные = {
                "++=": TokenType.ПЛЮС_ПЛЮС_ПРИСВОИТЬ,
                "--=": TokenType.МИНУС_МИНУС_ПРИСВОИТЬ,
                "+=": TokenType.ПЛЮС_ПРИСВОИТЬ,
                "-=": TokenType.МИНУС_ПРИСВОИТЬ,
                "==": TokenType.РАВНО,
                "!=": TokenType.НЕ_РАВНО,
                "<=": TokenType.МЕНЬШЕ_РАВНО,
                ">=": TokenType.БОЛЬШЕ_РАВНО,
            }
            for lexeme, tt in двусимвольные.items():
                if self.исходный_код.startswith(lexeme, self.позиция):
                    for _ in lexeme:
                        self._следующий()
                    return Token(tt, lexeme, start_line, start_col)

            одиночные = {
                "+": TokenType.ПЛЮС,
                "-": TokenType.МИНУС,
                "*": TokenType.УМНОЖИТЬ,
                "/": TokenType.РАЗДЕЛИТЬ,
                "%": TokenType.ОСТАТОК,
                "^": TokenType.СТЕПЕНЬ,
                "=": TokenType.ПРИСВОИТЬ,
                ";": TokenType.ТОЧКА_С_ЗАПЯТОЙ,
                ",": TokenType.ЗАПЯТАЯ,
                "(": TokenType.ЛЕВАЯ_СКОБКА,
                ")": TokenType.ПРАВАЯ_СКОБКА,
                "{": TokenType.ЛЕВАЯ_ФИГУРНАЯ,
                "}": TokenType.ПРАВАЯ_ФИГУРНАЯ,
                "[": TokenType.ЛЕВАЯ_КВАДРАТНАЯ,
                "]": TokenType.ПРАВАЯ_КВАДРАТНАЯ,
                ".": TokenType.ТОЧКА,
                ":": TokenType.ДВОЕТОЧИЕ,
                "<": TokenType.МЕНЬШЕ,
                ">": TokenType.БОЛЬШЕ,
            }
            if ch in одиночные:
                self._следующий()
                return Token(одиночные[ch], ch, start_line, start_col)

            if ch == '"':
                value = self._читать_строку()
                return Token(TokenType.СТРОКА, value, start_line, start_col)

            if ch == "'":
                m = CHAR_PATTERN.match(self.исходный_код, self.позиция)
                if not m:
                    self._ошибка("некорректный символьный литерал")
                raw = m.group()[1:-1]
                if raw.startswith("\\"):
                    raw = {"n": "\n", "t": "\t", "'": "'", "\\": "\\"}.get(raw[1], raw[1])
                self.позиция += len(m.group())
                self.столбец += len(m.group())
                return Token(TokenType.СИМВОЛ, raw, start_line, start_col)

            if ch.isdigit() or (ch == "-" and self.позиция + 1 < self.длина and self.исходный_код[self.позиция + 1].isdigit()):
                return self._читать_число()

            if re.match(r"[а-яА-ЯёЁ]", ch):
                return self._читать_идентификатор()

            self._ошибка(f"недопустимый символ '{ch}'")

    def токенизировать(self) -> list:
        tokens = []
        while True:
            tok = self.следующий_токен()
            tokens.append(tok)
            if tok.type == TokenType.КОНЕЦ_ФАЙЛА:
                break
        return tokens
