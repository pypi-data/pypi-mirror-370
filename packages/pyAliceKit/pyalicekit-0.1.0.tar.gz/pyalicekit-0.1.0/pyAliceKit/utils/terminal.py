import os
import sys
from typing import Optional

def print_start_welcome() -> None:
    print(r"""
    ____        ___    ___           __ __ _ __ 
   / __ \__  __/   |  / (_)_______  / //_/(_) /_
  / /_/ / / / / /| | / / / ___/ _ \/ ,<  / / __/
 / ____/ /_/ / ___ |/ / / /__/  __/ /| |/ / /_  
/_/    \__, /_/  |_/_/_/\___/\___/_/ |_/_/\__/  
      /____/  
                        Welcome to PyAliceKit!
        """)


def clear_terminal() -> None:
    platforms: dict[str, str] = {
        "linux": "clear",
        "linux2": "clear",
        "darwin": "clear",
        "win32": "cls"
    }
    command: str | None = platforms.get(sys.platform)
    if command:
        os.system(command)


def print_log(
    log_text: str,
    time: str,
    text_color: Optional[str] = None,
    bg_color: Optional[str] = None
) -> None:
    colors: dict[str, int] = {
        "black": 0,           # HEX: #000000, RGB: rgb(0, 0, 0)
        "red": 1,             # HEX: #800000, RGB: rgb(128, 0, 0)
        "green": 2,           # HEX: #008000, RGB: rgb(0, 128, 0)
        "yellow": 3,          # HEX: #808000, RGB: rgb(128, 128, 0)
        "blue": 4,            # HEX: #000080, RGB: rgb(0, 0, 128)
        "purple": 5,          # HEX: #800080, RGB: rgb(128, 0, 128)
        "magenta": 5,         # alias of purple — HEX: #800080, RGB: rgb(128, 0, 128)
        "cyan": 6,            # HEX: #008080, RGB: rgb(0, 128, 128)
        "turquoise": 6,       # alias of cyan — HEX: #008080, RGB: rgb(0, 128, 128)
        "white": 7,           # HEX: #C0C0C0, RGB: rgb(192, 192, 192)
        "gray": 8,            # HEX: #808080, RGB: rgb(128, 128, 128)
        "light_red": 9,       # HEX: #FF0000, RGB: rgb(255, 0, 0)
        "light_green": 10,    # HEX: #00FF00, RGB: rgb(0, 255, 0)
        "light_yellow": 11,   # HEX: #FFFF00, RGB: rgb(255, 255, 0)
        "light_blue": 12,     # HEX: #0000FF, RGB: rgb(0, 0, 255)
        "light_purple": 13,   # HEX: #FF00FF, RGB: rgb(255, 0, 255)
        "light_cyan": 14,     # HEX: #00FFFF, RGB: rgb(0, 255, 255)
        "light_white": 15,    # HEX: #FFFFFF, RGB: rgb(255, 255, 255)
        "brown": 16,          # HEX: #A52A2A, RGB: rgb(165, 42, 42)
        "orange": 17,         # HEX: #FFA500, RGB: rgb(255, 165, 0)
        "pink": 18,           # HEX: #FFC0CB, RGB: rgb(255, 192, 203)
        "gold": 19            # HEX: #FFD700, RGB: rgb(255, 215, 0)
    }

    def color_code(name: Optional[str], is_bg: bool = False) -> str:
        if name is None:
            return ""
        name = name.lower()
        if name not in colors:
            return ""
        base = 48 if is_bg else 38
        return f"\033[{base};5;{colors[name]}m"

    color_start: str = f"{color_code(text_color)}{color_code(bg_color, is_bg=True)}"
    color_end: str = "\033[0m" if color_start else ""

    print(f"{color_start}{time}  -->  {log_text}{color_end}")