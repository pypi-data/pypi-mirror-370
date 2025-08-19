from __future__ import annotations
from typing import TYPE_CHECKING

from pyAliceKit.utils.errors.errors import SettingsErrors
if TYPE_CHECKING:
    from pyAliceKit.py_alice.py_alice import PyAlice


def processing_service_storage(self: PyAlice) -> None:
        if self.new:
            self.previous_dialogue = "/"
        else:
            try:
                self.previous_dialogue = self.session_storage.get_service_storage().get("previous_dialogue", "/")
            except Exception as e:
                raise SettingsErrors("previous_dialogue_error", context=str(e), language=self.settings.DEBUG_LANGUAGE)