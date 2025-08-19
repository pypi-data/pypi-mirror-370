import json
from typing import TYPE_CHECKING, Optional, Any
import traceback

from pyAliceKit.utils.dialogs import flatten_dialogs, get_with_sources

if TYPE_CHECKING:
    from pyAliceKit.GUI.localserver import RequestHandler


def get_dialog_nodes(http: "RequestHandler") -> Optional[dict[Any, Any]]:
    try:
        nodes = getattr(http.settings, "DIALOG_NODES", None)
        if nodes is None:
            raise ValueError("DIALOG_NODES not found in settings")

        raw = get_with_sources(nodes)
        dialogs_only = raw.get("value")
        if not isinstance(dialogs_only, dict):
            raise ValueError("get_with_sources(nodes)['value'] должен быть словарём")

        flat = flatten_dialogs(dialogs_only)

        full_data = {
            "flat": flat,             # результат flatten_dialogs
            "value": dialogs_only,    # оригинальное дерево
            "sources": raw.get("sources"),
            "depth_map": raw.get("depth_map"),
            "max_depth": raw.get("max_depth"),
        }

        json_bytes = json.dumps(full_data, ensure_ascii=False, indent=2, default=str).encode("utf-8")

        http.send_response(200)
        http.send_header("Content-Type", "application/json; charset=utf-8")
        http.send_header("Content-Length", str(len(json_bytes)))
        http.end_headers()
        http.wfile.write(json_bytes)

        return full_data

    except Exception as e:
        traceback.print_exc()
        error = {"error": str(e)}
        error_bytes = json.dumps(error, ensure_ascii=False).encode("utf-8")

        http.send_response(500)
        http.send_header("Content-Type", "application/json; charset=utf-8")
        http.send_header("Content-Length", str(len(error_bytes)))
        http.end_headers()
        http.wfile.write(error_bytes)
        return None

