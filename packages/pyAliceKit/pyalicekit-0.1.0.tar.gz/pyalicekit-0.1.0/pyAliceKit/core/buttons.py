from types import ModuleType
from typing import Any, Self

from pyAliceKit.utils.errors.errors import SettingsErrors


class Buttons:
    def __init__(self: Self, settings: ModuleType) -> None:
        self.__settings: ModuleType = settings
        self.current_buttons: list[str] = []
        self.alice_buttons: list[dict[Any, Any]] = []
        self.add_buttons(self.__settings.CONSTANT_BUTTONS)

    def add_group_buttons(self: Self, group: str) -> None:
        group_buttons: str | None = self.__settings.BUTTONS_GROUPS.get(group)
        if group_buttons is None:
            raise SettingsErrors("group_buttons_not_found_error", context=group, language=self.__settings.DEBUG_LANGUAGE)
        for item in group_buttons:
            if item not in self.current_buttons:
                self.current_buttons.append(item)

    def add_button(self: Self, button: str) -> None:
        if "$" in button and button[0] == "$":
            self.add_group_buttons(button)
        elif button not in self.current_buttons:
            self.current_buttons.append(button)

    def add_buttons(self: Self, buttons: list[str]) -> None:
        for item in buttons:
            self.add_button(item)
    
    def conversion_buttons(self: Self) -> None:
        self.alice_buttons = []
        for item in self.current_buttons:
            btn = self.__settings.BUTTONS.get(item)
            if btn is None:
                raise SettingsErrors("button_not_found_error", context=item, language=self.__settings.DEBUG_LANGUAGE)
            self.alice_buttons.append(btn)

    def get_buttons(self: Self) -> list[dict[str, str]]:
        if not self.alice_buttons:
            self.conversion_buttons()
        return self.alice_buttons
    
    def get_current_buttons(self: Self) -> list[str]:
        return self.current_buttons
    
    def clear_buttons(self: Self) -> None:
        self.current_buttons = []
        self.alice_buttons = []
    
    def get_button_by_name(self: Self, name: str) -> dict[str, str]:
        if not self.alice_buttons:
            self.conversion_buttons()
        for item in self.alice_buttons:
            if item.get("title") == name:
                return item
        raise SettingsErrors("button_not_found_error", context=name, language=self.__settings.DEBUG_LANGUAGE)