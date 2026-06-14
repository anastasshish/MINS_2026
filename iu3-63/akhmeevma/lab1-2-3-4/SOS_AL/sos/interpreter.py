import os

from sos import ast_nodes as ast
from sos.environment import Окружение
from sos.errors import ОшибкаСос, ОшибкаТипов
from sos.types_check import проверить_элемент, проверить_совместимость, привести_значение
from sos.values import (
    Значение,
    Класс,
    Массив,
    Метод,
    Словарь,
    ФункцияПользователя,
    ЭкземплярКласса,
    ИсключениеВыполнения,
    Интерфейс,
)


class КонтрольЦикла(Exception):
    def __init__(self, kind: str, value=None):
        self.kind = kind
        self.value = value


class Интерпретатор:
    def __init__(self):
        self.глобальное = Окружение()
        self.классы: dict[str, Класс] = {}
        self.интерфейсы: dict[str, Интерфейс] = {}
        self.функции: dict[str, ФункцияПользователя] = {}
        self.текущий_объект: ЭкземплярКласса | None = None
        self.текущий_класс: Класс | None = None
        self.корневая_директория = "."
        self.загруженные_файлы: set[str] = set()
        self._зарегистрировать_встроенные()
        self._создать_исключения_по_умолчанию()

    def выполнить_файл(self, путь: str):
        from sos.loader import разрешить_путь

        abs_path = разрешить_путь(путь, os.getcwd())
        self.корневая_директория = os.path.dirname(abs_path)
        self._загрузить_модуль(abs_path, главный=True)

    def _загрузить_модуль(self, abs_path: str, главный: bool = False):
        from sos.loader import загрузить_программу, разрешить_путь

        if abs_path in self.загруженные_файлы:
            return
        self.загруженные_файлы.add(abs_path)
        program = загрузить_программу(abs_path)
        self._обработать_объявления(program.объявления, os.path.dirname(abs_path))
        if главный:
            if "начало_начал" not in self.функции:
                raise ОшибкаСос("не найдена точка входа начало_начал()")
            self.вызвать_функцию(self.функции["начало_начал"], [])

    def _обработать_объявления(self, объявления: list, базовая_директория: str):
        from sos.loader import разрешить_путь

        for decl in объявления:
            if isinstance(decl, ast.Подключение):
                path = разрешить_путь(decl.путь, базовая_директория)
                if not os.path.isfile(path):
                    raise ОшибкаСос(f"файл не найден: {decl.путь}")
                self._загрузить_модуль(path)
            elif isinstance(decl, ast.ОбъявлениеИнтерфейса):
                self._регистрировать_интерфейс(decl)
            elif isinstance(decl, ast.ОбъявлениеКласса):
                self._регистрировать_класс(decl)
            elif isinstance(decl, ast.ОбъявлениеФункции):
                if decl.имя == "начало_начал" and decl.имя in self.функции:
                    raise ОшибкаСос("точка входа начало_начал() уже определена")
                self._регистрировать_функцию(decl)
            elif isinstance(decl, ast.ОбъявлениеПеременной):
                self._выполнить_объявление(decl, self.глобальное)

    def _зарегистрировать_встроенные(self):
        from sos.builtins import встроенные_функции

        for имя, fn in встроенные_функции().items():
            self.глобальное.определить(имя, fn, "встроенная")

    def выполнить_программу(self, program: ast.Программа):
        self._обработать_объявления(program.объявления, self.корневая_директория)
        if "начало_начал" not in self.функции:
            raise ОшибкаСос("не найдена точка входа начало_начал()")
        self.вызвать_функцию(self.функции["начало_начал"], [])

    def _создать_исключения_по_умолчанию(self):
        if "исключение" in self.классы:
            return
        defs = [
            ("исключение", None),
            ("ошибка_выполнения", "исключение"),
            ("деление_на_ноль", "ошибка_выполнения"),
            ("индекс_вне_диапазона", "ошибка_выполнения"),
            ("ошибка_типа", "ошибка_выполнения"),
            ("ошибка_имени", "исключение"),
            ("ошибка_атрибута", "исключение"),
        ]
        for имя, родитель in defs:
            if имя in self.классы:
                continue
            parent_cls = self.классы.get(родитель) if родитель else None
            cls = Класс(имя=имя, родитель=parent_cls, это_исключение=True)
            cls.поля["сообщение"] = ("строка", "публичный")

            def make_ctor(c):
                def ctor_impl(interp, instance, args):
                    msg = args[0].значение if args else ""
                    instance.поля["сообщение"] = Значение("строка", str(msg))

                return ctor_impl

            cls.конструктор = Метод(
                имя="конструктор", параметры=[ast.Параметр("строка", "сообщение")],
                тело=None, это_конструктор=True, класс_владелец=cls,
            )
            cls.конструктор._impl = make_ctor(cls)
            self.классы[имя] = cls
            self.глобальное.определить(имя, cls, имя)

    def _регистрировать_интерфейс(self, decl: ast.ОбъявлениеИнтерфейса):
        iface = Интерфейс(имя=decl.имя)
        for m in decl.методы:
            iface.методы[m.имя] = Метод(
                имя=m.имя, параметры=m.параметры, тело=m.тело,
                модификатор=m.модификатор, класс_владелец=None,
            )
        self.интерфейсы[decl.имя] = iface

    def _регистрировать_класс(self, decl: ast.ОбъявлениеКласса):
        parent = self.классы.get(decl.родитель) if decl.родитель else None
        if decl.родитель and not parent:
            raise ОшибкаСос(f"неизвестный родительский класс {decl.родитель}")
        interfaces = []
        for iname in decl.интерфейсы:
            if iname not in self.интерфейсы:
                raise ОшибкаСос(f"неизвестный интерфейс {iname}")
            interfaces.append(self.интерфейсы[iname])
        cls = Класс(имя=decl.имя, родитель=parent, интерфейсы=interfaces)
        cls.это_исключение = (
            decl.имя == "исключение"
            or (parent is not None and parent.это_исключение)
        )

        for f in decl.поля:
            cls.поля[f.имя] = (f.тип, f.модификатор)

        for m in decl.методы:
            method = Метод(
                имя=m.имя, параметры=m.параметры, тело=m.тело,
                модификатор=m.модификатор, переопределить=m.переопределить,
                класс_владелец=cls,
            )
            cls.методы[m.имя] = method

        if decl.конструктор:
            cls.конструктор = Метод(
                имя="конструктор", параметры=decl.конструктор.параметры,
                тело=decl.конструктор.тело, модификатор=decl.конструктор.модификатор,
                это_конструктор=True, класс_владелец=cls,
            )
        elif parent and parent.конструктор:
            cls.конструктор = Метод(
                имя="конструктор", параметры=parent.конструктор.параметры,
                тело=parent.конструктор.тело, модификатор=parent.конструктор.модификатор,
                это_конструктор=True, класс_владелец=cls,
            )

        if cls.это_исключение and "сообщение" not in cls.все_поля():
            cls.поля["сообщение"] = ("строка", "публичный")

        for iface in interfaces:
            for mname, sig in iface.методы.items():
                if mname not in cls.методы:
                    raise ОшибкаСос(f"класс {decl.имя} не реализует метод {mname} интерфейса {iface.имя}")

        self.классы[decl.имя] = cls
        self.глобальное.определить(decl.имя, cls, decl.имя)

    def _регистрировать_функцию(self, decl: ast.ОбъявлениеФункции):
        fn = ФункцияПользователя(
            имя=decl.имя, параметры=decl.параметры,
            тело=decl.тело, возвращаемый_тип=decl.возвращаемый_тип,
        )
        self.функции[decl.имя] = fn
        self.глобальное.определить(decl.имя, fn, "функция")

    def вычислить(self, node: ast.Выражение, env: Окружение) -> Значение | Массив | Словарь | ЭкземплярКласса:
        if isinstance(node, ast.Литерал):
            v = node.значение
            if v is None:
                return Значение("пустое", None)
            if isinstance(v, bool):
                return Значение("логическое", v)
            if isinstance(v, int):
                return Значение("целое", v)
            if isinstance(v, float):
                return Значение("вещественное", v)
            if isinstance(v, str):
                if node.имя_типа == "символ":
                    return Значение("символ", v)
                return Значение("строка", str(v))
            return Значение("строка", str(v))

        if isinstance(node, ast.Переменная):
            try:
                val = env.получить(node.имя)
            except KeyError:
                raise self._runtime_name(node.имя)
            if callable(val) and getattr(val, "__name__", "") == node.имя and node.имя in self.функции:
                return val
            return val

        if isinstance(node, ast.Это):
            if not self.текущий_объект:
                raise ОшибкаСос("этот использован вне метода")
            return self.текущий_объект

        if isinstance(node, ast.БинарнаяОперация):
            return self._биноп(node, env)
        if isinstance(node, ast.УнарнаяОперация):
            return self._унар(node, env)
        if isinstance(node, ast.Вызов):
            return self._вызов(node, env)
        if isinstance(node, ast.ДоступКПолю):
            return self._поле(node, env)
        if isinstance(node, ast.Индекс):
            return self._индекс(node, env)
        if isinstance(node, ast.НовыйОбъект):
            return self._новый_объект(node, env)
        if isinstance(node, ast.НовыйМассив):
            return self._новый_массив(node, env)
        if isinstance(node, ast.НовыйСловарь):
            return self._новый_словарь(node, env)
        if isinstance(node, ast.ПриведениеТипа):
            val = self.вычислить(node.выражение, env)
            return привести_значение(node.целевой_тип, val)

        raise ОшибкаСос(f"неизвестный узел выражения {type(node)}")

    def _биноп(self, node, env):
        if node.оператор == "и":
            l = self.вычислить(node.лево, env)
            return l if not self._в_логическое(l) else self.вычислить(node.право, env)
        if node.оператор == "или":
            l = self.вычислить(node.лево, env)
            return l if self._в_логическое(l) else self.вычислить(node.право, env)

        l = self.вычислить(node.лево, env)
        r = self.вычислить(node.право, env)
        op = node.оператор
        lt, rt = l.значение, r.значение

        if op == "+":
            if l.имя_типа == "строка" or r.имя_типа == "строка":
                return Значение("строка", str(lt) + str(rt))
            if l.имя_типа == "вещественное" or r.имя_типа == "вещественное":
                return Значение("вещественное", float(lt) + float(rt))
            return Значение("целое", int(lt) + int(rt))
        if op == "-":
            if l.имя_типа == "вещественное" or r.имя_типа == "вещественное":
                return Значение("вещественное", float(lt) - float(rt))
            return Значение("целое", int(lt) - int(rt))
        if op == "*":
            if l.имя_типа == "вещественное" or r.имя_типа == "вещественное":
                return Значение("вещественное", float(lt) * float(rt))
            return Значение("целое", int(lt) * int(rt))
        if op == "/":
            if int(rt) == 0:
                raise self._runtime_exc("деление_на_ноль", "деление на ноль")
            return Значение("целое", int(lt) // int(rt))
        if op == "%":
            return Значение("целое", int(lt) % int(rt))
        if op == "^":
            return Значение("целое" if l.имя_типа == "целое" and r.имя_типа == "целое" else "вещественное", lt ** rt)
        if op == "==":
            return Значение("логическое", lt == rt)
        if op == "!=":
            return Значение("логическое", lt != rt)
        if op == "<":
            return Значение("логическое", lt < rt)
        if op == ">":
            return Значение("логическое", lt > rt)
        if op == "<=":
            return Значение("логическое", lt <= rt)
        if op == ">=":
            return Значение("логическое", lt >= rt)
        raise ОшибкаСос(f"неизвестный оператор {op}")

    def _унар(self, node, env):
        v = self.вычислить(node.операнд, env)
        if node.оператор == "-":
            if v.имя_типа == "вещественное":
                return Значение("вещественное", -v.значение)
            return Значение("целое", -int(v.значение))
        if node.оператор == "не":
            return Значение("логическое", not self._в_логическое(v))
        raise ОшибкаСос(f"неизвестный унарный оператор {node.оператор}")

    def _в_логическое(self, v) -> bool:
        if v.имя_типа == "логическое":
            return bool(v.значение)
        if v.имя_типа == "пустое" and v.значение is None:
            return False
        return bool(v.значение)

    def _имя_класса(self, arg) -> str:
        from sos.values import Класс as КлассТип
        if isinstance(arg, КлассТип):
            return arg.имя
        if isinstance(arg, Значение):
            return str(arg.значение)
        return str(arg)

    def _вызов(self, node, env):
        callee = node.callee
        if isinstance(callee, ast.Переменная) and callee.имя == "это_экземпляр":
            args = [self.вычислить(a, env) for a in node.аргументы]
            if len(args) != 2:
                raise ОшибкаСос("это_экземпляр принимает 2 аргумента")
            obj, cls_name = args[0], args[1]
            name = self._имя_класса(cls_name)
            if isinstance(obj, ЭкземплярКласса):
                return Значение("логическое", obj.класс.наследует(name))
            return Значение("логическое", False)

        if isinstance(callee, ast.ДоступКПолю) and isinstance(callee.объект, ast.Это):
            return self._вызов_метода(self.текущий_объект, callee.поле, node.аргументы, env, через_родителя=False)

        if isinstance(callee, ast.ДоступКПолю) and isinstance(callee.объект, ast.Переменная) and callee.объект.имя == "родитель":
            return self._вызов_метода(self.текущий_объект, callee.поле, node.аргументы, env, через_родителя=True)

        args = [self.вычислить(a, env) for a in node.аргументы]

        if isinstance(callee, ast.Переменная):
            if callee.имя in self.функции:
                return self.вызвать_функцию(self.функции[callee.имя], args)
            if callee.имя in self.глобальное.переменные:
                fn_val = self.глобальное.переменные[callee.имя]
                if isinstance(fn_val, ФункцияПользователя):
                    return self.вызвать_функцию(fn_val, args)
                if callable(fn_val):
                    return fn_val(self, args)

        if isinstance(callee, ast.ДоступКПолю):
            obj = self.вычислить(callee.объект, env)
            if isinstance(obj, ЭкземплярКласса):
                return self._вызов_метода(obj, callee.поле, args, env, аргументы_вычислены=True)

        fn_val = self.вычислить(callee, env)
        if isinstance(fn_val, ФункцияПользователя):
            return self.вызвать_функцию(fn_val, args)
        if callable(fn_val):
            return fn_val(self, args)
        raise ОшибкаСос("вызов не callable значения")

    def _вызов_метода(
        self,
        obj: ЭкземплярКласса,
        name: str,
        arg_nodes,
        env,
        через_родителя=False,
        *,
        аргументы_вычислены=False,
    ):
        if not аргументы_вычислены:
            args = [self.вычислить(a, env) for a in arg_nodes]
        else:
            args = arg_nodes
        target_cls = obj.класс.родитель if через_родителя and obj.класс.родитель else obj.класс
        if name == "конструктор":
            method = target_cls.конструктор if через_родителя else (obj.класс.конструктор or (target_cls.конструктор if target_cls else None))
        elif через_родителя and obj.класс.родитель:
            method = obj.класс.родитель.найти_метод(name)
        else:
            method = obj.класс.найти_метод(name)
        if not method:
            raise self._runtime_exc("ошибка_атрибута", f"метод {name} не найден")
        owner = method.класс_владелец or target_cls
        if not self._доступ_разрешён(method.модификатор, owner):
            raise self._runtime_exc("ошибка_атрибута", f"нет доступа к методу {name}")
        return self._вызвать_метод(obj, method, args)

    def _вызвать_метод(self, obj, method: Метод, args):
        if hasattr(method, "_impl"):
            instance = obj
            method._impl(self, instance, args)
            return Значение("пустое", None)
        env = Окружение(self.глобальное)
        old_obj, old_cls = self.текущий_объект, self.текущий_класс
        self.текущий_объект = obj
        self.текущий_класс = method.класс_владелец or obj.класс
        for p, a in zip(method.параметры, args):
            env.определить(p.имя, a, p.тип)
        try:
            result = self._выполнить_блок(method.тело, env)
            return result if result is not None else Значение("пустое", None)
        except КонтрольЦикла as c:
            if c.kind == "return":
                return c.value if c.value is not None else Значение("пустое", None)
            raise
        finally:
            self.текущий_объект = old_obj
            self.текущий_класс = old_cls

    def вызвать_функцию(self, fn: ФункцияПользователя, args):
        env = Окружение(self.глобальное)
        params = fn.параметры
        for i, p in enumerate(params):
            if i < len(args):
                val = args[i]
            elif p.значение_по_умолчанию:
                val = self.вычислить(p.значение_по_умолчанию, env)
            else:
                raise ОшибкаСос(f"не передан аргумент {p.имя}")
            if not проверить_совместимость(p.тип, val):
                raise ОшибкаТипов(f"аргумент {p.имя}: ожидался {p.тип}, получен {getattr(val, 'имя_типа', type(val))}")
            env.определить(p.имя, val, p.тип)
        try:
            result = self._выполнить_блок(fn.тело, env)
            return result if result is not None else Значение("пустое", None)
        except КонтрольЦикла as c:
            if c.kind == "return":
                return c.value if c.value is not None else Значение("пустое", None)
            raise

    def _найти_поле(self, cls: Класс, имя: str):
        if имя in cls.поля:
            return cls, cls.поля[имя]
        if cls.родитель:
            return self._найти_поле(cls.родитель, имя)
        return None, None

    def _поле(self, node, env, for_assign=False):
        if isinstance(node.объект, ast.Переменная) and node.объект.имя == "родитель":
            if not self.текущий_объект or not self.текущий_объект.класс.родитель:
                raise self._runtime_exc("ошибка_атрибута", "родитель недоступен")
            # доступ к полю родителя через текущий объект
            obj = self.текущий_объект
            field = node.поле
            if field in obj.поля:
                return obj.поля[field]
            raise self._runtime_exc("ошибка_атрибута", f"поле {field} не найдено")

        obj = self.вычислить(node.объект, env)
        if isinstance(obj, ЭкземплярКласса):
            if node.поле not in obj.поля:
                owner, meta = self._найти_поле(obj.класс, node.поле)
                if meta:
                    obj.поля[node.поле] = self._значение_по_умолчанию(meta[0])
                else:
                    raise self._runtime_exc("ошибка_атрибута", f"поле {node.поле} не найдено")
            if not for_assign:
                owner, meta = self._найти_поле(obj.класс, node.поле)
                mod = meta[1] if meta else "публичный"
                if owner and not self._доступ_разрешён(mod, owner):
                    raise self._runtime_exc("ошибка_атрибута", f"нет доступа к полю {node.поле}")
            return obj.поля[node.поле]
        if isinstance(obj, Значение) and obj.имя_типа == "строка" and node.поле == "длина":
            return Значение("целое", len(obj.значение))
        raise self._runtime_exc("ошибка_атрибута", f"поле {node.поле} недоступно")

    def _индекс(self, node, env):
        arr = self.вычислить(node.массив, env)
        idx = self.вычислить(node.индекс, env)
        i = int(idx.значение)
        if isinstance(arr, Массив):
            if i < 0 or i >= len(arr):
                raise self._runtime_exc("индекс_вне_диапазона", f"индекс {i} вне массива")
            return arr.элементы[i]
        if isinstance(arr, Словарь):
            key = idx.значение
            if key not in arr.пары:
                raise self._runtime_exc("ошибка_имени", f"ключ {key} не найден")
            return arr.пары[key]
        if isinstance(arr, Значение) and arr.имя_типа == "строка":
            if i < 0 or i >= len(arr.значение):
                raise self._runtime_exc("индекс_вне_диапазона", f"индекс {i} вне строки")
            return Значение("символ", arr.значение[i])
        raise self._runtime_exc("ошибка_типа", "индексация неприменима")

    def _новый_объект(self, node, env):
        if node.тип_имя not in self.классы:
            raise self._runtime_exc("ошибка_имени", f"класс {node.тип_имя} не найден")
        cls = self.классы[node.тип_имя]
        args = [self.вычислить(a, env) for a in node.аргументы]
        instance = ЭкземплярКласса(класс=cls)
        for fname, (ftype, _) in cls.все_поля().items():
            instance.поля[fname] = self._значение_по_умолчанию(ftype)
        if cls.конструктор:
            if hasattr(cls.конструктор, "_impl"):
                cls.конструктор._impl(self, instance, args)
            else:
                self._вызвать_метод(instance, cls.конструктор, args)
        return instance

    def _имя_типа_значения(self, val) -> str:
        if isinstance(val, ЭкземплярКласса):
            return val.класс.имя
        if isinstance(val, Массив):
            return val.имя_типа
        if isinstance(val, Словарь):
            return val.имя_типа
        return val.имя_типа

    def _новый_массив(self, node, env, declared_type: str | None = None):
        if node.размер is not None:
            size = int(self.вычислить(node.размер, env).значение)
            elem_type = node.тип_элемента or (declared_type.replace("[]", "") if declared_type else "целое")
            elems = [self._значение_по_умолчанию(elem_type) for _ in range(size)]
            return Массив(имя_типа=f"{elem_type}[]", тип_элемента=elem_type, элементы=elems)
        elems = [self.вычислить(e, env) for e in (node.элементы or [])]
        if declared_type and declared_type.endswith("[]"):
            elem_type = declared_type[:-2]
        else:
            elem_type = node.тип_элемента or (self._имя_типа_значения(elems[0]) if elems else "целое")
        arr = Массив(имя_типа=f"{elem_type}[]", тип_элемента=elem_type, элементы=[])
        for e in elems:
            if not проверить_элемент(elem_type, e):
                e = привести_значение(elem_type, e)
            arr.элементы.append(e)
        return arr

    def _привести_массив(self, declared: str, val: Массив) -> Массив:
        elem_type = declared[:-2]
        val.имя_типа = declared
        val.тип_элемента = elem_type
        for i, e in enumerate(val.элементы):
            if not проверить_элемент(elem_type, e):
                val.элементы[i] = привести_значение(elem_type, e)
        return val

    def _значение_по_умолчанию(self, тип: str):
        defaults = {
            "целое": 0, "вещественное": 0.0, "строка": "", "символ": "\0",
            "логическое": False, "пустое": None,
        }
        if тип in defaults:
            return Значение(тип, defaults[тип])
        if тип.endswith("[]"):
            inner = тип[:-2]
            return Массив(имя_типа=тип, тип_элемента=inner, элементы=[])
        if тип.startswith("словарь"):
            return Словарь(имя_типа=тип, тип_ключа="строка", тип_значения="пустое", пары={})
        if тип in self.классы:
            return Значение("пустое", None)
        return Значение("пустое", None)

    def _новый_словарь(self, node, env):
        пары = {}
        kt, vt = "строка", "пустое"
        for k_node, v_node in node.пары:
            k = self.вычислить(k_node, env)
            v = self.вычислить(v_node, env)
            kt, vt = k.имя_типа, v.имя_типа
            пары[k.значение] = v
        return Словарь(имя_типа=f"словарь<{kt},{vt}>", тип_ключа=kt, тип_значения=vt, пары=пары)

    def _выполнить_блок(self, block: ast.Блок, env: Окружение):
        result = None
        for stmt in block.операторы:
            result = self._выполнить(stmt, env)
        return result

    def _выполнить(self, stmt: ast.Оператор, env: Окружение):
        if isinstance(stmt, ast.Блок):
            return self._выполнить_блок(stmt, env)
        if isinstance(stmt, ast.ОбъявлениеПеременной):
            return self._выполнить_объявление(stmt, env)
        if isinstance(stmt, ast.Присваивание):
            return self._выполнить_присваивание(stmt, env)
        if isinstance(stmt, ast.Если):
            return self._выполнить_если(stmt, env)
        if isinstance(stmt, ast.Пока):
            return self._выполнить_пока(stmt, env)
        if isinstance(stmt, ast.Для):
            return self._выполнить_для(stmt, env)
        if isinstance(stmt, ast.Выбрать):
            return self._выполнить_выбрать(stmt, env)
        if isinstance(stmt, ast.Вернуть):
            val = self.вычислить(stmt.значение, env) if stmt.значение else Значение("пустое", None)
            raise КонтрольЦикла("return", val)
        if isinstance(stmt, ast.Прервать):
            raise КонтрольЦикла("break")
        if isinstance(stmt, ast.Продолжить):
            raise КонтрольЦикла("continue")
        if isinstance(stmt, ast.Бросить):
            return self._выполнить_бросить(stmt, env)
        if isinstance(stmt, ast.Попробовать):
            return self._выполнить_попробовать(stmt, env)
        if isinstance(stmt, ast.ВыражениеКакОператор):
            return self.вычислить(stmt.выражение, env)
        return None

    def _выполнить_объявление(self, stmt: ast.ОбъявлениеПеременной, env: Окружение):
        if stmt.инициализатор:
            if isinstance(stmt.инициализатор, ast.НовыйМассив):
                val = self._новый_массив(
                    stmt.инициализатор, env,
                    stmt.тип if stmt.тип.endswith("[]") else None,
                )
            else:
                val = self.вычислить(stmt.инициализатор, env)
            if stmt.тип.startswith("словарь"):
                val = self._привести_к_объявленному(stmt, val)
            elif stmt.тип.endswith("[]") and isinstance(val, Массив):
                val = self._привести_массив(stmt.тип, val)
            elif not проверить_совместимость(stmt.тип, val):
                val = привести_значение(stmt.тип, val)
        else:
            val = self._значение_по_умолчанию(stmt.тип)
        env.определить(stmt.имя, val, stmt.тип)
        return val

    def _привести_к_объявленному(self, stmt, val):
        if isinstance(val, Словарь):
            val.имя_типа = stmt.тип
            if stmt.ключевой_тип:
                val.тип_ключа = stmt.ключевой_тип
            if stmt.значение_тип:
                val.тип_значения = stmt.значение_тип
            return val
        return val

    def _выполнить_присваивание(self, stmt: ast.Присваивание, env: Окружение):
        rhs = self.вычислить(stmt.значение, env)
        target = stmt.цель
        op = stmt.оператор

        if isinstance(target, ast.Переменная):
            name = target.имя
            try:
                current = env.получить(name)
                expected = env.получить_тип(name)
            except KeyError:
                raise self._runtime_name(name)
            new_val = self._применить_оп(current, op, rhs)
            if not проверить_совместимость(expected, new_val):
                new_val = привести_значение(expected, new_val)
            env.присвоить(name, new_val)
            return new_val

        if isinstance(target, ast.ДоступКПолю):
            obj = self.вычислить(target.объект, env)
            if isinstance(obj, ЭкземплярКласса):
                cur = obj.поля.get(target.поле, self._значение_по_умолчанию("пустое"))
                obj.поля[target.поле] = self._применить_оп(cur, op, rhs)
                return obj.поля[target.поле]

        if isinstance(target, ast.Индекс):
            arr = self.вычислить(target.массив, env)
            idx = int(self.вычислить(target.индекс, env).значение)
            if isinstance(arr, Массив):
                cur = arr.элементы[idx]
                new_val = self._применить_оп(cur, op, rhs)
                if not проверить_элемент(arr.тип_элемента, new_val):
                    new_val = привести_значение(arr.тип_элемента, new_val)
                arr.элементы[idx] = new_val
                return arr.элементы[idx]
            if isinstance(arr, Словарь):
                key = self.вычислить(target.индекс, env).значение
                cur = arr.пары.get(key, Значение("пустое", None))
                arr.пары[key] = self._применить_оп(cur, op, rhs)
                return arr.пары[key]

        raise ОшибкаСос("недопустимая цель присваивания")

    def _применить_оп(self, current, op, rhs):
        if op == "=":
            return rhs
        if op == "+=":
            return self._биноп(
                ast.БинарнаяОперация(
                    лево=ast.Литерал(значение=current.значение),
                    оператор="+",
                    право=ast.Литерал(значение=rhs.значение),
                ),
                self.глобальное,
            )
        if op == "-=":
            return self._биноп(
                ast.БинарнаяОперация(
                    лево=ast.Литерал(значение=current.значение),
                    оператор="-",
                    право=ast.Литерал(значение=rhs.значение),
                ),
                self.глобальное,
            )
        if op == "++=":
            return Значение(current.имя_типа, current.значение + 2)
        if op == "--=":
            return Значение(current.имя_типа, current.значение - 2)
        raise ОшибкаСос(f"неизвестный оператор присваивания {op}")

    def _выполнить_если(self, stmt, env):
        if self._в_логическое(self.вычислить(stmt.условие, env)):
            return self._выполнить(stmt.тогда, env)
        if stmt.иначе:
            return self._выполнить(stmt.иначе, env)
        return None

    def _выполнить_пока(self, stmt, env):
        result = None
        while self._в_логическое(self.вычислить(stmt.условие, env)):
            try:
                result = self._выполнить(stmt.тело, env)
            except КонтрольЦикла as c:
                if c.kind == "break":
                    break
                if c.kind == "continue":
                    continue
                raise
        return result

    def _выполнить_для(self, stmt, env):
        iterable = self.вычислить(stmt.итерируемое, env)
        items = []
        if isinstance(iterable, Массив):
            items = iterable.элементы
        elif isinstance(iterable, Значение) and iterable.имя_типа == "строка":
            items = [Значение("символ", c) for c in iterable.значение]
        else:
            raise self._runtime_exc("ошибка_типа", "итерируемый объект не поддерживается")
        result = None
        for item in items:
            env.определить(stmt.переменная, item, item.имя_типа)
            try:
                result = self._выполнить(stmt.тело, env)
            except КонтрольЦикла as c:
                if c.kind == "break":
                    break
                if c.kind == "continue":
                    continue
                raise
        return result

    def _выполнить_выбрать(self, stmt, env):
        val = self.вычислить(stmt.выражение, env)
        for case_val, block in stmt.варианты:
            cv = self.вычислить(case_val, env)
            if cv.значение == val.значение:
                return self._выполнить(block, env)
        if stmt.по_умолчанию:
            return self._выполнить(stmt.по_умолчанию, env)
        return None

    def _выполнить_бросить(self, stmt, env):
        exc_val = self.вычислить(stmt.исключение, env)
        if isinstance(exc_val, ЭкземплярКласса) and exc_val.класс.это_исключение:
            msg = exc_val.поля.get("сообщение", Значение("строка", "")).значение
            raise ИсключениеВыполнения(exc_val.класс, str(msg), exc_val)
        if isinstance(exc_val, ЭкземплярКласса):
            raise ИсключениеВыполнения(exc_val.класс, "", exc_val)
        raise ИсключениеВыполнения(self.классы.get("исключение", Класс("исключение")), str(exc_val))

    def _выполнить_попробовать(self, stmt, env):
        exc_instance = None
        try:
            return self._выполнить(stmt.тело, env)
        except ИсключениеВыполнения as e:
            exc_instance = e
            handled = False
            for type_name, var_name, block in stmt.обработчики:
                if type_name is None or e.это_или_наследник(type_name):
                    handler_env = Окружение(env)
                    if var_name:
                        inst = e.экземпляр or self._создать_экземпляр_исключения(e)
                        handler_env.определить(var_name, inst, e.класс.имя)
                    self._выполнить(block, handler_env)
                    handled = True
                    break
            if not handled:
                raise
        finally:
            if stmt.наконец:
                self._выполнить(stmt.наконец, env)
        return None

    def _создать_экземпляр_исключения(self, e: ИсключениеВыполнения):
        inst = ЭкземплярКласса(класс=e.класс)
        inst.поля["сообщение"] = Значение("строка", e.сообщение)
        return inst

    def _доступ_разрешён(self, mod: str, owner_cls: Класс) -> bool:
        if mod == "публичный":
            return True
        if not self.текущий_класс:
            return mod == "публичный"
        if mod == "приватный":
            return self.текущий_класс.имя == owner_cls.имя
        if mod == "защищённый":
            return (
                self.текущий_класс.имя == owner_cls.имя
                or self.текущий_класс.наследует(owner_cls.имя)
                or owner_cls.наследует(self.текущий_класс.имя)
            )
        return True

    def _runtime_exc(self, name: str, msg: str):
        if name not in self.классы:
            self._создать_исключения_по_умолчанию()
        return ИсключениеВыполнения(self.классы[name], msg)

    def _runtime_name(self, name: str):
        return self._runtime_exc("ошибка_имени", f"переменная {name} не определена")
