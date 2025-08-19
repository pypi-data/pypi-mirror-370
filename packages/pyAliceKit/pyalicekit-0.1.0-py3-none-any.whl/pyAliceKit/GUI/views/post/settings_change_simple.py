from __future__ import annotations
import json
from pathlib import Path
import traceback
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyAliceKit.GUI.localserver import RequestHandler


def cast_value(value: Any, expected_type: type) -> Any:
    try:
        if expected_type == bool:
            if isinstance(value, str):
                return value.lower() == "true"
            return bool(value)
        elif expected_type == int:
            return int(value)
        elif expected_type == float:
            return float(value)
        elif expected_type in (list, dict) and isinstance(value, str):
            return json.loads(value)
        return expected_type(value) # type: ignore
    except Exception:
        return value

def update_settings_file(http: RequestHandler, key: str, value: Any):
    file_path = Path(http.settings.__file__).resolve() # type: ignore

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines: list[Any] = []
    updated = False
    for line in lines:
        if line.strip().startswith(f"{key} ="):
            python_value = python_repr(value)
            new_lines.append(f"{key} = {python_value}\n")
            updated = True
        else:
            new_lines.append(line)

    if updated:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

def python_repr(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "True" if value else "False"
    else:
        return json.dumps(value, ensure_ascii=False)


def post_settings_change_simple(http: RequestHandler) -> None:
    try:
        content_length = int(http.headers.get("Content-Length", 0))
        body = http.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))

        key = data.get("key")
        value = data.get("value")

        if not hasattr(http.settings, key):
            http.send_response(400)
            http.end_headers()
            http.wfile.write(json.dumps({"error": f"Ключ '{key}' не найден в settings"}).encode("utf-8"))
            return

        current_value = getattr(http.settings, key)
        new_value = cast_value(value, type(current_value)) # type: ignore
        setattr(http.settings, key, new_value)

        print(f"KEY: {key} | RAW VALUE: {value} | CASTED VALUE: {new_value}")
        print("SETTINGS_PATH:", Path(http.settings.__file__).resolve()) # type: ignore

        update_settings_file(http, key, new_value)

        http.send_response(200)
        http.send_header("Content-Type", "application/json; charset=utf-8")
        http.end_headers()
        http.wfile.write(json.dumps({
            "status": "ok",
            "key": key,
            "value": new_value
        }, ensure_ascii=False).encode("utf-8"))

    except Exception as e:
        traceback.print_exc()
        http.send_response(500)
        http.end_headers()
        http.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))