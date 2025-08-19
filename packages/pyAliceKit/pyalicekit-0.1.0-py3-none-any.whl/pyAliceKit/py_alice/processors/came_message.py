from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyAliceKit.py_alice.py_alice import PyAlice

def processing_came_message(self: PyAlice) -> None:
        if self.settings.SOURCE_TEXT in self.params_alice["request"].keys():
            self.came_message = self.params_alice["request"][self.settings.SOURCE_TEXT]
        elif "nlu" in self.params_alice["request"].keys():
            self.came_message = " ".join(self.params_alice["request"]["nlu"]["tokens"])
        else:
            self.came_message = ""