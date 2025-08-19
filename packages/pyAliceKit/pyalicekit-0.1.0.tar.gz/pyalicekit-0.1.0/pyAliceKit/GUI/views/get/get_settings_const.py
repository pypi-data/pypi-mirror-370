import sys
import json
import importlib
import inspect
import types
from urllib.parse import urlparse, parse_qs
from typing import TYPE_CHECKING, Any
import traceback

if TYPE_CHECKING:
    from pyAliceKit.GUI.localserver import RequestHandler


def get_settings_const(http: "RequestHandler") -> Any:
    def deep_serialize(value, _seen=None):
        if _seen is None:
            _seen = set()

        obj_id = id(value)
        if obj_id in _seen:
            return "<circular reference>"
        _seen.add(obj_id)

        try:
            json.dumps(value)
            return value
        except TypeError:
            pass

        if isinstance(value, dict):
            return {
                str(k): deep_serialize(v, _seen)
                for k, v in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [deep_serialize(item, _seen) for item in value]

        if inspect.isfunction(value) or inspect.isclass(value) or inspect.ismethod(value):
            try:
                return inspect.getsource(value)
            except Exception as e:
                return f"<unsourceable: {e}>"

        if isinstance(value, types.ModuleType):
            return f"<module: {value.__name__}>"

        if hasattr(value, "__dict__"):
            try:
                return {
                    "__class__": value.__class__.__name__,
                    "attributes": deep_serialize(value.__dict__, _seen)
                }
            except Exception as e:
                return f"<object: {str(e)}>"

        return str(value)

    try:
        module_name = http.settings.__name__
        if module_name in sys.modules:
            module = sys.modules[module_name]
            importlib.reload(module)
            http.settings = module
        else:
            http.settings = importlib.import_module(module_name)

        query = urlparse(http.path).query
        params = parse_qs(query)
        key = params.get("key", [None])[0]

        if key:
            if hasattr(http.settings, key):
                raw_value = getattr(http.settings, key)
                response: dict[Any, Any] = {key: deep_serialize(raw_value)}
            else:
                http.send_response(404)
                http.send_header("Content-Type", "application/json; charset=utf-8")
                http.end_headers()
                http.wfile.write(json.dumps({
                    "error": f"Ключ '{key}' не найден в settings"
                }).encode("utf-8"))
                return
        else:
            response = {
                k: deep_serialize(v)
                for k, v in http.settings.__dict__.items()
                if not k.startswith("__")
            }

        json_bytes = json.dumps(response, ensure_ascii=False, indent=2).encode("utf-8")

        http.send_response(200)
        http.send_header("Content-Type", "application/json; charset=utf-8")
        http.send_header("Content-Length", str(len(json_bytes)))
        http.end_headers()
        http.wfile.write(json_bytes)

    except Exception as e:
        traceback.print_exc()
        error_message = {"error": str(e)}
        error_bytes = json.dumps(error_message, ensure_ascii=False).encode("utf-8")

        http.send_response(500)
        http.send_header("Content-Type", "application/json; charset=utf-8")
        http.send_header("Content-Length", str(len(error_bytes)))
        http.end_headers()
        http.wfile.write(error_bytes)