from __future__ import annotations
from typing import TYPE_CHECKING

from pyAliceKit.utils.errors.errors import SettingsErrors
from pyAliceKit.utils.tools import from_str_bool_to_py_bool
if TYPE_CHECKING:
    from pyAliceKit.py_alice.py_alice import PyAlice

def processing_new(self: PyAlice) -> None:
        temp_new: bool | int = from_str_bool_to_py_bool(self.params_alice["session"]["new"])
        if temp_new != -1:
            self.new = temp_new # type: ignore
        else:
            raise SettingsErrors("new_boolean_setting_error", language=self.settings.DEBUG_LANGUAGE)