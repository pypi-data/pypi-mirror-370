from typing import Any, Self
from pyAliceKit.messages import embedded_errors_message


class BaseErrors(Exception):
    def __init__(self: Self, text: str, context: str | None = None, language: str = "en", *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.msg = text
        self.context = context
        self.language = language

    def get_dialog(self: Self, key: str) -> str:
        return embedded_errors_message.embedded_errors_message.get(f"{key}-{self.language}", "")

    def __str__(self: Self):
        return f"Base Error: {self.get_dialog(self.msg)}"


class SettingsErrors(BaseErrors):
    def __str__(self: Self) -> str:
        return f"Settings Error: {self.get_dialog(self.msg).format(self.context)}"
    
class KeyWordsErrors(BaseErrors):
    def __str__(self: Self) -> str:
        return f"Key words Error: {self.get_dialog(self.msg).format(self.context)}"
    
class IntentsErrors(BaseErrors):
    def __str__(self: Self) -> str:
        return f"Intent Error: {self.get_dialog(self.msg).format(self.context)}"
    
class MessageErrors(BaseErrors):
    def __str__(self: Self) -> str:
        return f"Message Error: {self.get_dialog(self.msg).format(self.context)}"
    
class StorageErrors(BaseErrors):
    def __str__(self: Self) -> str:
        return f"Storage Error: {self.get_dialog(self.msg).format(self.context)}"
    
class AliceRequestErrors(BaseErrors):
    def __str__(self: Self) -> str:
        return f"Alice Request Error: {self.get_dialog(self.msg).format(self.context)}"
    
class DialogEngineErrors(BaseErrors):
    def __str__(self: Self) -> str:
        return f"Dialog Engine Error: {self.get_dialog(self.msg).format(self.context)}"