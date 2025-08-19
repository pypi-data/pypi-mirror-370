import json
import types

from types import ModuleType
from typing import Any



def is_serializable(value: Any) -> bool:
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False


def clean_dict(obj: dict[Any, Any]) -> dict[Any, Any]:
    """Рекурсивно удаляет функции и модули из словаря"""
    result: dict[Any, Any] = {}
    for k, v in obj.items():
        if isinstance(v, types.FunctionType):
            result[k] = f"<function {v.__name__}>"
        elif isinstance(v, types.ModuleType):
            continue
        elif isinstance(v, dict):
            result[k] = clean_dict(v) # type: ignore
        else:
            result[k] = v
    return result


def get_all_settings(settings: ModuleType) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for key in dir(settings):
        if not key.isupper():
            continue

        value = getattr(settings, key)

        if isinstance(value, (types.FunctionType, types.ModuleType)):
            continue

        if isinstance(value, dict):
            cleaned = clean_dict(value) # type: ignore
            if is_serializable(cleaned):
                result[key] = cleaned
            else:
                result[key] = str(cleaned)
            continue

        if is_serializable(value):
            result[key] = value
        else:
            result[key] = str(value)

    return result
