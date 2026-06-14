from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Значение:
    имя_типа: str
    значение: Any

    def __repr__(self):
        return f"{self.имя_типа}({self.значение!r})"


@dataclass
class Массив:
    имя_типа: str
    тип_элемента: str
    элементы: List[Значение] = field(default_factory=list)

    def __len__(self):
        return len(self.элементы)


@dataclass
class Словарь:
    имя_типа: str
    тип_ключа: str
    тип_значения: str
    пары: Dict[Any, Значение] = field(default_factory=dict)


@dataclass
class Метод:
    имя: str
    параметры: list
    тело: Any
    модификатор: str = "публичный"
    переопределить: bool = False
    это_конструктор: bool = False
    класс_владелец: Any = None


@dataclass
class Класс:
    имя: str
    родитель: Optional["Класс"] = None
    интерфейсы: List["Интерфейс"] = field(default_factory=list)
    поля: Dict[str, tuple] = field(default_factory=dict)  # имя -> (тип, модификатор)
    методы: Dict[str, Метод] = field(default_factory=dict)
    конструктор: Optional[Метод] = None
    это_исключение: bool = False

    def наследует(self, имя: str) -> bool:
        if self.имя == имя:
            return True
        if self.родитель and self.родитель.наследует(имя):
            return True
        return False

    def найти_метод(self, имя: str) -> Optional[Метод]:
        if имя in self.методы:
            return self.методы[имя]
        if self.родитель:
            return self.родитель.найти_метод(имя)
        return None

    def все_поля(self) -> Dict[str, tuple]:
        result = {}
        if self.родитель:
            result.update(self.родитель.все_поля())
        result.update(self.поля)
        return result


@dataclass
class Интерфейс:
    имя: str
    методы: Dict[str, Метод] = field(default_factory=dict)


@dataclass
class ЭкземплярКласса:
    класс: Класс
    поля: Dict[str, Значение] = field(default_factory=dict)

    @property
    def имя_типа(self):
        return self.класс.имя


class ИсключениеВыполнения(Exception):
    """Пользовательское исключение языка Сос."""

    def __init__(self, класс: Класс, сообщение: str = "", экземпляр: Optional[ЭкземплярКласса] = None):
        self.класс = класс
        self.сообщение = сообщение
        self.экземпляр = экземпляр
        super().__init__(сообщение)

    def это_или_наследник(self, имя_класса: str) -> bool:
        return self.класс.наследует(имя_класса)


@dataclass
class ФункцияПользователя:
    имя: str
    параметры: list
    тело: Any
    окружение_замыкания: Any = None
    возвращаемый_тип: Optional[str] = None


ВстроеннаяФункция = Callable[..., Значение]
