from types import FunctionType
from typing import Any

from pyAliceKit.utils.errors.errors import DialogEngineErrors


def from_str_bool_to_py_bool(boolean: str | bool) -> bool | int:
    if type(boolean) is str:
        if boolean == "true":
            return True
        elif boolean == "false":
            return False
    elif type(boolean) is bool:
        return boolean
    return -1



def load_user_function(code: str, func_name: str, language: str) -> FunctionType:
    local_ns: dict[Any, Any] = {}
    exec(code, {}, local_ns)  # Выполняем в изолированном пространстве
    func = local_ns.get(func_name)
    if not callable(func):
        raise DialogEngineErrors("chooser_function_execution_failed", context=func_name, language=language)
    return func
