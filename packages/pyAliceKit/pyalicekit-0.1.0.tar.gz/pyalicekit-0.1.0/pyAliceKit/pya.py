# pya.py
import os
import sys

TEMPLATE_SETTINGS = """# Настройки проекта
from typing import Any

EVENTS = True
DEBUG = True
LOG_OUTPUT_IMMEDIATELY = True
TIME_ZONE = None


TEXT_FOR_KEY_WORDS = "command"
VERSION = "1.0"


DIALOG_NODES: dict[str, Any] = {}

DIALOG_NODES_WITH_META = ""

DIALOGS_MAP_FILE = "dialogs_map.json"


ALL_MESSAGES = messages

STARTING_MESSAGE = "start_message"
ERROR_MESSAGE = "help"
HELP_MESSAGE = "help"
MORE_DATA_MESSAGES = {}


BUTTONS: dict[str, Any] = {}

CONSTANT_BUTTONS = []
BUTTONS_GROUPS = {}
STARTING_BUTTONS = []

KEY_WORDS = {}

IMAGES = {}

DEBUG_LANGUAGE = "ru"
LANGUAGE = "ru"
SOURCE_TEXT = "command"
"""

TEMPLATE_APP = """# Основной файл приложения
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def alice_handler():
    print(request)
    if not request.is_json:
        return jsonify({"error": "Unsupported Media Type. Expected application/json."}), 415
    

    event = request.get_json()
    pyAlice = PyAlice(params_alice=event, settings=settings)
    
    response = pyAlice.get_response_for_alice(type="dict")
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=5000)

"""

def create_project(project_name: str):
    if os.path.exists(project_name):
        print(f"Проект {project_name} уже существует!")
        return

    os.makedirs(os.path.join(project_name, "dialogs"))
    with open(os.path.join(project_name, "settings.py"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_SETTINGS)
    with open(os.path.join(project_name, "app.py"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_APP)

    print(f"Проект {project_name} успешно создан!")

def main():
    if len(sys.argv) != 3 or sys.argv[1] != "create-project":
        print("Использование: pya create-project <имя_проекта>")
        return
    create_project(sys.argv[2])

if __name__ == "__main__":
    main()
