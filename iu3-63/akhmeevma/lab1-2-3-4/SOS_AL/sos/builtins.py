import os

from sos.values import Значение, Массив, Словарь, ЭкземплярКласса
from sos.types_check import проверить_элемент, привести_значение


def _разрешить_путь_файла(interp, raw_path: str) -> str:
    from sos.loader import разрешить_путь
    return разрешить_путь(raw_path, interp.корневая_директория)


def встроенные_функции():
    def печать(interp, args):
        parts = []
        for a in args:
            parts.append(_формат(a))
        print(" ".join(parts))
        return Значение("пустое", None)

    def ввод(interp, args):
        prompt = _формат(args[0]) if args else ""
        text = input(prompt).strip()
        return Значение("строка", text)

    def длина(interp, args):
        if len(args) != 1:
            raise ValueError("длина принимает 1 аргумент")
        a = args[0]
        if isinstance(a, (Массив, Словарь)):
            return Значение("целое", len(a.элементы if isinstance(a, Массив) else a.пары))
        if isinstance(a, Значение) and a.имя_типа == "строка":
            return Значение("целое", len(a.значение))
        raise ValueError("длина неприменима к данному типу")

    def тип_(interp, args):
        a = args[0]
        if isinstance(a, ЭкземплярКласса):
            return Значение("строка", a.класс.имя)
        return Значение("строка", getattr(a, "имя_типа", type(a).__name__))

    def целое_(interp, args):
        v = args[0]
        if isinstance(v, Значение):
            return Значение("целое", int(v.значение))
        return Значение("целое", int(v))

    def вещественное_(interp, args):
        v = args[0]
        if isinstance(v, Значение):
            return Значение("вещественное", float(v.значение))
        return Значение("вещественное", float(v))

    def строка_(interp, args):
        return Значение("строка", _формат(args[0]))

    def добавить(interp, args):
        if len(args) != 2:
            raise ValueError("добавить принимает 2 аргумента")
        coll, item = args[0], args[1]
        if isinstance(coll, Массив):
            if not проверить_элемент(coll.тип_элемента, item):
                item = привести_значение(coll.тип_элемента, item)
            coll.элементы.append(item)
            return Значение("пустое", None)
        raise ValueError("добавить применимо только к массиву")

    def это_экземпляр(interp, args):
        if len(args) != 2:
            raise ValueError("это_экземпляр принимает 2 аргумента")
        obj, cls = args[0], args[1]
        cls_name = cls.значение if isinstance(cls, Значение) else str(cls)
        from sos.values import Класс as КлассТип
        if isinstance(cls, КлассТип):
            cls_name = cls.имя
        if isinstance(obj, ЭкземплярКласса):
            return Значение("логическое", obj.класс.наследует(str(cls_name)))
        return Значение("логическое", False)

    def прочитать_файл(interp, args):
        if len(args) != 1:
            raise ValueError("прочитать_файл принимает 1 аргумент")
        path = _разрешить_путь_файла(interp, str(args[0].значение))
        if not os.path.isfile(path):
            raise interp._runtime_exc("ошибка_имени", f"файл не найден: {args[0].значение}")
        with open(path, encoding="utf-8") as f:
            return Значение("строка", f.read())

    def записать_файл(interp, args):
        if len(args) != 2:
            raise ValueError("записать_файл принимает 2 аргумента")
        path = _разрешить_путь_файла(interp, str(args[0].значение))
        content = _формат(args[1])
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return Значение("пустое", None)

    def добавить_в_файл(interp, args):
        if len(args) != 2:
            raise ValueError("добавить_в_файл принимает 2 аргумента")
        path = _разрешить_путь_файла(interp, str(args[0].значение))
        content = _формат(args[1])
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return Значение("пустое", None)

    return {
        "печать": печать,
        "ввод": ввод,
        "длина": длина,
        "тип": тип_,
        "целое": целое_,
        "вещественное": вещественное_,
        "строка": строка_,
        "добавить": добавить,
        "это_экземпляр": это_экземпляр,
        "прочитать_файл": прочитать_файл,
        "записать_файл": записать_файл,
        "добавить_в_файл": добавить_в_файл,
    }


def _формат(value) -> str:
    if isinstance(value, Значение):
        if value.имя_типа == "логическое":
            return "да" if value.значение else "нет"
        if value.имя_типа == "пустое" and value.значение is None:
            return "Нуль"
        return str(value.значение)
    if isinstance(value, ЭкземплярКласса):
        return f"<{value.класс.имя}>"
    if isinstance(value, Массив):
        return "[" + ", ".join(_формат(e) for e in value.элементы) + "]"
    if isinstance(value, Словарь):
        parts = [f"{k}: {_формат(v)}" for k, v in value.пары.items()]
        return "{" + ", ".join(parts) + "}"
    return str(value)
