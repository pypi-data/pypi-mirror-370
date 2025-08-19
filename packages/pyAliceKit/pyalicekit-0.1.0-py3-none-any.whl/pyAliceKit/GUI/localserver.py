# pyAliceKit/GUI/localserver.py
import http.server
import json
import socketserver
import os
import threading
import time
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any
import uuid

from pyAliceKit.GUI.utils.html import get_html_template
from pyAliceKit.GUI.views.get.get_settings_const import get_settings_const
from pyAliceKit.GUI.views.get.get_dialog_nodes import get_dialog_nodes
from pyAliceKit.GUI.views.get.settings import get_all_settings
from pyAliceKit.GUI.views.post.settings_change_simple import post_settings_change_simple

PORT = 8081
SERVER_ID = str(uuid.uuid4())

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    sse_clients = []

    def __init__(self, *args: Any, settings: ModuleType, **kwargs: Any) -> None:
        self.settings = settings
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/api/updates/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            # Отправляем сразу серверный ID клиенту
            self.wfile.write(f"data: server_id:{SERVER_ID}\n\n".encode("utf-8"))
            self.wfile.flush()

            # Регистрируем клиента для уведомлений
            self.sse_clients.append(self.wfile)

            try:
                while True:
                    # Пинг с server_id
                    self.wfile.write(f"data: ping server_id:{SERVER_ID}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    time.sleep(5)
            except (ConnectionAbortedError, BrokenPipeError):
                print("SSE client disconnected")
            except Exception as e:
                print("SSE error:", e)
            finally:
                if self.wfile in self.sse_clients:
                    self.sse_clients.remove(self.wfile)
            return

        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(get_html_template("index.html", Path(__file__)).encode('utf-8'))

        elif self.path.endswith(".html"):
            html_file = self.path.lstrip("/")
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(get_html_template(html_file, Path(__file__)).encode("utf-8"))
            except FileNotFoundError:
                self.send_error(404, f"{html_file} not found")

        elif self.path == "/api/settings/get_all":
            try:
                data = get_all_settings(self.settings)
                json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(json_bytes)))
                self.end_headers()
                self.wfile.write(json_bytes)

            except Exception as e:
                traceback.print_exc()
                error_message = {"error": str(e)}
                error_bytes = json.dumps(error_message, ensure_ascii=False).encode("utf-8")

                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(error_bytes)))
                self.end_headers()
                self.wfile.write(error_bytes)

        elif self.path == "/api/settings/get_dialog_nodes":
            get_dialog_nodes(self)

        elif self.path.startswith("/api/settings/get_const"):
            get_settings_const(self)

        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/settings/change_simple":
            post_settings_change_simple(self)


def monitor_files_and_notify(root_dir: Path):
    files = list(root_dir.rglob("*.py"))
    mtimes = {str(f): f.stat().st_mtime for f in files}

    while True:
        time.sleep(1)
        files = list(root_dir.rglob("*.py"))
        new_mtimes = {str(f): f.stat().st_mtime for f in files}

        changed = any(mtimes.get(str(f), 0) != new_mtimes.get(str(f), 0) for f in new_mtimes)

        if changed:
            print("Изменение файлов, уведомляем клиентов SSE...")
            for client in list(RequestHandler.sse_clients):
                try:
                    client.write(b"data: reload\n\n")
                    client.flush()
                except Exception:
                    RequestHandler.sse_clients.remove(client)
            mtimes = new_mtimes


# ✅ Многопоточный сервер
class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def run(settings: ModuleType):
    static_dir = Path(__file__).parent / "static"
    os.chdir(static_dir)

    def handler_with_settings(*args, **kwargs):
        return RequestHandler(*args, settings=settings, **kwargs)

    try:
        with ThreadingTCPServer(("", PORT), handler_with_settings) as httpd:
            print(f"🚀 Local server running at http://localhost:{PORT}")

            monitor_thread = threading.Thread(
                target=monitor_files_and_notify,
                args=(Path(__file__).parent.parent,),
                daemon=True
            )
            monitor_thread.start()

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("🛑 Server interrupted and stopped gracefully")
    except OSError as e:
        if e.errno == 98:
            print(f"❌ Порт {PORT} уже занят. Возможно, сервер уже запущен.")
            print("   Завершите старый процесс или выберите другой порт.")
        else:
            print("🔥 Ошибка при запуске сервера:")
            traceback.print_exc()



if __name__ == "__main__":
    # run()
    pass
