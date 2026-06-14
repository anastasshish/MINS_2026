class ОшибкаСос(Exception):
    """Базовая ошибка интерпретатора (не пользовательское исключение языка)."""

    def __init__(self, сообщение: str, строка: int = 0, столбец: int = 0):
        self.сообщение = сообщение
        self.строка = строка
        self.столбец = столбец
        super().__init__(self.format())

    def format(self) -> str:
        if self.строка:
            return f"[строка {self.строка}, столбец {self.столбец}] {self.сообщение}"
        return self.сообщение


class ОшибкаЛексера(ОшибкаСос):
    pass


class ОшибкаСинтаксиса(ОшибкаСос):
    pass


class ОшибкаТипов(ОшибкаСос):
    pass
