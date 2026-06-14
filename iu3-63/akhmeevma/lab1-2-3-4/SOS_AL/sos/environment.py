from typing import Dict, Optional

from sos.values import Значение


class Окружение:
    def __init__(self, родитель: Optional["Окружение"] = None):
        self.родитель = родитель
        self.переменные: Dict[str, Значение] = {}
        self.типы: Dict[str, str] = {}

    def определить(self, имя: str, значение: Значение, тип: str):
        self.переменные[имя] = значение
        self.типы[имя] = тип

    def получить(self, имя: str) -> Значение:
        if имя in self.переменные:
            return self.переменные[имя]
        if self.родитель:
            return self.родитель.получить(имя)
        raise KeyError(имя)

    def получить_тип(self, имя: str) -> str:
        if имя in self.типы:
            return self.типы[имя]
        if self.родитель:
            return self.родитель.получить_тип(имя)
        raise KeyError(имя)

    def присвоить(self, имя: str, значение: Значение):
        if имя in self.переменные:
            self.переменные[имя] = значение
            return
        if self.родитель:
            self.родитель.присвоить(имя, значение)
            return
        raise KeyError(имя)

    def существует_локально(self, имя: str) -> bool:
        return имя in self.переменные
