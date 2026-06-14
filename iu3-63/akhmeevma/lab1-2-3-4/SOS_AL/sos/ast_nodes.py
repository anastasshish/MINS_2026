from dataclasses import dataclass, field
from typing import Any, List, Optional


# --- Выражения ---

@dataclass
class Узел:
    строка: int = 0
    столбец: int = 0


@dataclass
class Выражение(Узел):
    pass


@dataclass
class Литерал(Выражение):
    значение: Any = None
    имя_типа: str = ""


@dataclass
class Переменная(Выражение):
    имя: str = ""


@dataclass
class БинарнаяОперация(Выражение):
    лево: Выражение = None
    оператор: str = ""
    право: Выражение = None


@dataclass
class УнарнаяОперация(Выражение):
    оператор: str = ""
    операнд: Выражение = None


@dataclass
class Вызов(Выражение):
    callee: Выражение = None
    аргументы: List[Выражение] = field(default_factory=list)


@dataclass
class ДоступКПолю(Выражение):
    объект: Выражение = None
    поле: str = ""


@dataclass
class Индекс(Выражение):
    массив: Выражение = None
    индекс: Выражение = None


@dataclass
class НовыйОбъект(Выражение):
    тип_имя: str = ""
    аргументы: List[Выражение] = field(default_factory=list)


@dataclass
class НовыйМассив(Выражение):
    тип_элемента: str = ""
    размер: Optional[Выражение] = None
    элементы: Optional[List[Выражение]] = None


@dataclass
class НовыйСловарь(Выражение):
    пары: List[tuple] = field(default_factory=list)


@dataclass
class ПриведениеТипа(Выражение):
    целевой_тип: str = ""
    выражение: Выражение = None


@dataclass
class Это(Выражение):
    """этот — ссылка на текущий объект в методе."""
    pass


# --- Операторы ---

@dataclass
class Оператор(Узел):
    pass


@dataclass
class Блок(Оператор):
    операторы: List[Оператор] = field(default_factory=list)


@dataclass
class ОбъявлениеПеременной(Оператор):
    тип: str = ""
    имя: str = ""
    размерность: int = 0
    ключевой_тип: Optional[str] = None
    значение_тип: Optional[str] = None
    инициализатор: Optional[Выражение] = None


@dataclass
class Присваивание(Оператор):
    цель: Выражение = None
    оператор: str = "="
    значение: Выражение = None


@dataclass
class Если(Оператор):
    условие: Выражение = None
    тогда: Блок = None
    иначе: Optional[Оператор] = None


@dataclass
class Пока(Оператор):
    условие: Выражение = None
    тело: Блок = None


@dataclass
class Для(Оператор):
    переменная: str = ""
    итерируемое: Выражение = None
    тело: Блок = None


@dataclass
class Выбрать(Оператор):
    выражение: Выражение = None
    варианты: List[tuple] = field(default_factory=list)
    по_умолчанию: Optional[Блок] = None


@dataclass
class Вернуть(Оператор):
    значение: Optional[Выражение] = None


@dataclass
class Прервать(Оператор):
    pass


@dataclass
class Продолжить(Оператор):
    pass


@dataclass
class Бросить(Оператор):
    исключение: Выражение = None


@dataclass
class Попробовать(Оператор):
    тело: Блок = None
    обработчики: List[tuple] = field(default_factory=list)
    наконец: Optional[Блок] = None


@dataclass
class ВыражениеКакОператор(Оператор):
    выражение: Выражение = None


# --- Объявления верхнего уровня ---

@dataclass
class Параметр:
    тип: str = ""
    имя: str = ""
    значение_по_умолчанию: Optional[Выражение] = None


@dataclass
class ОбъявлениеФункции(Узел):
    имя: str = ""
    параметры: List[Параметр] = field(default_factory=list)
    возвращаемый_тип: Optional[str] = None
    тело: Блок = None
    модификатор: str = "публичный"


@dataclass
class ОбъявлениеМетода(ОбъявлениеФункции):
    переопределить: bool = False


@dataclass
class ОбъявлениеПоля(Узел):
    тип: str = ""
    имя: str = ""
    модификатор: str = "публичный"
    инициализатор: Optional[Выражение] = None


@dataclass
class ОбъявлениеКласса(Узел):
    имя: str = ""
    родитель: Optional[str] = None
    интерфейсы: List[str] = field(default_factory=list)
    поля: List[ОбъявлениеПоля] = field(default_factory=list)
    методы: List[ОбъявлениеМетода] = field(default_factory=list)
    конструктор: Optional[ОбъявлениеМетода] = None


@dataclass
class ОбъявлениеИнтерфейса(Узел):
    имя: str = ""
    методы: List[ОбъявлениеМетода] = field(default_factory=list)


@dataclass
class Подключение(Узел):
    путь: str = ""


@dataclass
class Программа(Узел):
    объявления: List[Узел] = field(default_factory=list)
