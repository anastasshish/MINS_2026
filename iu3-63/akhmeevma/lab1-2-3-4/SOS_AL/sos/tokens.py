from enum import Enum, auto


class TokenType(Enum):
    # Литералы
    ЦЕЛОЕ = auto()
    ВЕЩЕСТВЕННОЕ = auto()
    СТРОКА = auto()
    СИМВОЛ = auto()
    ДА = auto()
    НЕТ = auto()
    НУЛЬ = auto()

    # Идентификатор
    ИДЕНТИФИКАТОР = auto()

    # Ключевые слова
    НАЧАЛО_НАЧАЛ = auto()
    ЕСЛИ = auto()
    ИНАЧЕ = auto()
    ИНАЧЕ_ЕСЛИ = auto()
    ПОКА = auto()
    ВЫПОЛНЯТЬ = auto()
    ДЛЯ = auto()
    В = auto()
    ДЕЛАТЬ = auto()
    ПРЕРВАТЬ = auto()
    ПРОДОЛЖИТЬ = auto()
    ВЫЙТИ = auto()
    ВЕРНУТЬ = auto()
    ФУНКЦИЯ = auto()
    КЛАСС = auto()
    КОНСТРУКТОР = auto()
    ИНТЕРФЕЙС = auto()
    РЕАЛИЗУЕТ = auto()
    НОВЫЙ = auto()
    ЭТОТ = auto()
    РОДИТЕЛЬ = auto()
    ПУБЛИЧНЫЙ = auto()
    ПРИВАТНЫЙ = auto()
    ЗАЩИЩЁННЫЙ = auto()
    ПЕРЕОПРЕДЕЛИТЬ = auto()
    ПОПРОБОВАТЬ = auto()
    СЛОВИТЬ = auto()
    НАКОНЕЦ = auto()
    БРОСИТЬ = auto()
    ВЫБРАТЬ = auto()
    ВАРИАНТ = auto()
    КАК = auto()
    ПОДКЛЮЧИТЬ = auto()
    И = auto()
    ИЛИ = auto()
    НЕ = auto()

    # Типы
    ЦЕЛОЕ_ТИП = auto()
    ВЕЩЕСТВЕННОЕ_ТИП = auto()
    СТРОКА_ТИП = auto()
    СИМВОЛ_ТИП = auto()
    ЛОГИЧЕСКОЕ_ТИП = auto()
    ПУСТОЕ_ТИП = auto()
    СЛОВАРЬ_ТИП = auto()

    # Операторы
    ПЛЮС = auto()
    МИНУС = auto()
    УМНОЖИТЬ = auto()
    РАЗДЕЛИТЬ = auto()
    ОСТАТОК = auto()
    СТЕПЕНЬ = auto()
    ПРИСВОИТЬ = auto()
    ПЛЮС_ПРИСВОИТЬ = auto()
    МИНУС_ПРИСВОИТЬ = auto()
    ПЛЮС_ПЛЮС_ПРИСВОИТЬ = auto()
    МИНУС_МИНУС_ПРИСВОИТЬ = auto()
    РАВНО = auto()
    НЕ_РАВНО = auto()
    МЕНЬШЕ = auto()
    БОЛЬШЕ = auto()
    МЕНЬШЕ_РАВНО = auto()
    БОЛЬШЕ_РАВНО = auto()

    # Разделители
    ТОЧКА_С_ЗАПЯТОЙ = auto()
    ЗАПЯТАЯ = auto()
    ЛЕВАЯ_СКОБКА = auto()
    ПРАВАЯ_СКОБКА = auto()
    ЛЕВАЯ_ФИГУРНАЯ = auto()
    ПРАВАЯ_ФИГУРНАЯ = auto()
    ЛЕВАЯ_КВАДРАТНАЯ = auto()
    ПРАВАЯ_КВАДРАТНАЯ = auto()
    ТОЧКА = auto()
    ДВОЕТОЧИЕ = auto()
    МЕНЬШЕ_УГОЛ = auto()
    БОЛЬШЕ_УГОЛ = auto()

    КОНЕЦ_ФАЙЛА = auto()


KEYWORDS = {
    "начало_начал": TokenType.НАЧАЛО_НАЧАЛ,
    "если": TokenType.ЕСЛИ,
    "иначе": TokenType.ИНАЧЕ,
    "иначе_если": TokenType.ИНАЧЕ_ЕСЛИ,
    "пока": TokenType.ПОКА,
    "выполнять": TokenType.ВЫПОЛНЯТЬ,
    "для": TokenType.ДЛЯ,
    "в": TokenType.В,
    "делать": TokenType.ДЕЛАТЬ,
    "прервать": TokenType.ПРЕРВАТЬ,
    "продолжить": TokenType.ПРОДОЛЖИТЬ,
    "выйти": TokenType.ВЫЙТИ,
    "вернуть": TokenType.ВЕРНУТЬ,
    "функция": TokenType.ФУНКЦИЯ,
    "класс": TokenType.КЛАСС,
    "конструктор": TokenType.КОНСТРУКТОР,
    "интерфейс": TokenType.ИНТЕРФЕЙС,
    "реализует": TokenType.РЕАЛИЗУЕТ,
    "новый": TokenType.НОВЫЙ,
    "этот": TokenType.ЭТОТ,
    "родитель": TokenType.РОДИТЕЛЬ,
    "публичный": TokenType.ПУБЛИЧНЫЙ,
    "приватный": TokenType.ПРИВАТНЫЙ,
    "защищённый": TokenType.ЗАЩИЩЁННЫЙ,
    "переопределить": TokenType.ПЕРЕОПРЕДЕЛИТЬ,
    "попробовать": TokenType.ПОПРОБОВАТЬ,
    "словить": TokenType.СЛОВИТЬ,
    "наконец": TokenType.НАКОНЕЦ,
    "бросить": TokenType.БРОСИТЬ,
    "выбрать": TokenType.ВЫБРАТЬ,
    "вариант": TokenType.ВАРИАНТ,
    "как": TokenType.КАК,
    "подключить": TokenType.ПОДКЛЮЧИТЬ,
    "и": TokenType.И,
    "или": TokenType.ИЛИ,
    "не": TokenType.НЕ,
    "да": TokenType.ДА,
    "нет": TokenType.НЕТ,
    "Нуль": TokenType.НУЛЬ,
    "целое": TokenType.ЦЕЛОЕ_ТИП,
    "вещественное": TokenType.ВЕЩЕСТВЕННОЕ_ТИП,
    "строка": TokenType.СТРОКА_ТИП,
    "символ": TokenType.СИМВОЛ_ТИП,
    "логическое": TokenType.ЛОГИЧЕСКОЕ_ТИП,
    "пустое": TokenType.ПУСТОЕ_ТИП,
    "словарь": TokenType.СЛОВАРЬ_ТИП,
}


class Token:
    __slots__ = ("type", "value", "line", "column")

    def __init__(self, type_: TokenType, value, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"
