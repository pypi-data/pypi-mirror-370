from pathlib import Path
from typing import Any



def get_html_template(template_name: str, current_file: Path) -> str:
    """
    Returns the content of the HTML template file.

    :param template_name: Name of the HTML template file.
    :param current_file: __file__ from the calling script.
    :return: Content of the HTML template file as a string.
    """
    templates_dir = current_file.parent / "static" / "templates"
    template_path = templates_dir / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found in {templates_dir}")

    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()