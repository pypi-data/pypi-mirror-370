import inspect
from types import ModuleType
from typing import Any, Callable, TypeVar, Union, cast


# Тип значения узла в диалоге
DialogNode = dict[str, Any]
# Тип функции выбора: принимает строку, возвращает строку
ChooserFunc = Callable[[str], str]
# Обобщённый тип, чтобы не терялась сигнатура оборачиваемой функции
F = TypeVar("F", bound=ChooserFunc)

def chooser(base_url: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        def wrapper(user_input: str) -> str:
            leaf = func(user_input)
            return f"{base_url}/{leaf}" if leaf else ""
        return cast(F, wrapper)
    return decorator


def flatten_dialogs(dialogs: dict[str, Any], base_path: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}

    def walk(node: dict[str, Any], path: str):
        flat_node = {k: v for k, v in node.items() if k != "childs"}

        # Сохраняем исходный код функции chooser, если она есть
        if "chooser" in flat_node and callable(flat_node["chooser"]):
            function_name: str = flat_node["chooser"].__name__
            flat_node["chooser"] = inspect.getsource(flat_node["chooser"]).strip()
            flat_node["chooser_name"] = function_name

        full_path = f"/{path}"
        child_paths = []

        if "childs" in node and isinstance(node["childs"], dict):
            for child_key, child_node in node["childs"].items(): # type: ignore
                child_path = f"{path}/{child_key}"
                child_paths.append(f"/{child_path}") # type: ignore
                walk(child_node, child_path) # type: ignore

        if child_paths:
            flat_node["childs"] = child_paths

        result[full_path] = flat_node

    for key, node in dialogs.items():
        walk(node, key)

    return result


def prev_path(path: str) -> str:
    parts = path.strip('/').split('/')

    if len(parts) <= 1:
        return '/'

    return '/' + '/'.join(parts[:-1])





def include_nodes(obj: dict[str, Any], DEBUG: bool) -> dict[str, Any]:
    if not DEBUG:
        return obj

    frame_info = inspect.stack()[1]
    frame = frame_info.frame

    import_name = None
    for name, val in frame.f_globals.items():
        if val is obj:
            import_name = name
            break

    source_file = frame.f_globals.get("__file__", None)

    def get_depth(o: Any, level=1) -> int:
        if isinstance(o, dict):
            for v in o.values():
                if isinstance(v, dict) and "__source__" in v:
                    return get_depth(v["__value__"], level + 1)
        return level

    depth = get_depth(obj)

    return {
        "__value__": obj,
        "__source__": {
            "parent": source_file,
            "depth": depth,
            "dependencies": {
                source_file: {
                    "import_name": import_name,
                    "value": obj,
                    "depth": depth
                }
            }
        }
    }




def get_with_sources(element: Union[dict[Any, Any], list[Any]]) -> dict[str, Any]:
    def unwrap(obj: Any) -> Any:
        if isinstance(obj, dict) and '__value__' in obj and '__source__' in obj:
            sources.append(obj['__source__'])
            return unwrap(obj['__value__'])
        elif isinstance(obj, dict):
            return {k: unwrap(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [unwrap(i) for i in obj]
        return obj

    def clean(obj):
        if isinstance(obj, dict):
            if "__value__" in obj and "__source__" in obj:
                return clean(obj["__value__"])
            return {k: clean(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj

    sources = []
    unwrapped = unwrap(element)

    merged_sources = {
        "called_from": None,
        "defined_in": None,
        "dependencies": {}
    }

    max_depth = 1
    depth_map: dict[int, list[dict[str, Any]]] = {}

    for src in sources:
        called_from = src.get("called_from")
        defined_in = src.get("defined_in")
        if not merged_sources["called_from"]:
            merged_sources["called_from"] = called_from
        if not merged_sources["defined_in"]:
            merged_sources["defined_in"] = defined_in

        for path, dep in src.get("dependencies", {}).items():
            cleaned_value = clean(dep["value"])
            depth = dep.get("depth", 1)
            max_depth = max(max_depth, depth)

            merged_sources["dependencies"][path] = {
                "import_name": dep["import_name"],
                "value": cleaned_value,
                "depth": depth
            }

            depth_map.setdefault(depth, []).append({
                "path": path,
                "import_name": dep["import_name"],
                "value": cleaned_value
            })

    return {
        "value": unwrapped,
        "sources": merged_sources,
        "max_depth": max_depth,
        "depth_map": depth_map
    }


def strip_meta(data: Any) -> Any:
    if not isinstance(data, (dict, list)):
        return data

    # Для верхнего уровня, если есть __value__, заменяем сразу
    if isinstance(data, dict) and "__value__" in data:
        data = data["__value__"]

    stack = [(data, None, None)]  # (текущий_объект, родитель, ключ_или_индекс)
    root = data if isinstance(data, dict) else list(data)

    while stack:
        current, parent, parent_key = stack.pop()

        if isinstance(current, dict):
            # Если есть __value__ внутри — разворачиваем
            if "__value__" in current:
                new_val = current["__value__"]

                # Заменяем в родителе
                if parent is not None:
                    if isinstance(parent, dict):
                        parent[parent_key] = new_val
                    elif isinstance(parent, list):
                        parent[parent_key] = new_val

                # Теперь новый объект обрабатываем
                current = new_val

            # Удаляем все ключи вида __xxx__
            keys_to_delete = [k for k in current.keys() if k.startswith("__") and k.endswith("__")]
            for k in keys_to_delete:
                if k != "__value__":
                    del current[k]

            # Продолжаем обход
            for k, v in list(current.items()):
                if isinstance(v, (dict, list)):
                    stack.append((v, current, k))

        elif isinstance(current, list):
            for i, v in enumerate(current):
                if isinstance(v, (dict, list)):
                    stack.append((v, current, i))

    return root


def putting_dialog_constants_places(settings: ModuleType) -> None:
    settings.DIALOG_NODES_WITH_META = settings.DIALOG_NODES # type: ignore
    settings.DIALOG_NODES = strip_meta(settings.DIALOG_NODES_WITH_META) # type: ignore

