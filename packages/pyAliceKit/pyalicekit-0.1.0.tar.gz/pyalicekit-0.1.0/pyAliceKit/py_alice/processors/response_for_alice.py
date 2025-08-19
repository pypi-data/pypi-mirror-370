from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from pyAliceKit.py_alice.py_alice import PyAlice

def processing_response_for_alice(self: PyAlice) -> dict[str, Any]:
    self.buttons.conversion_buttons()
    storage: dict[Any, Any] = self.session_storage.get_all() if self.session_storage else {}
    response_for_alice: dict[str, Any] = {
        "state": {
            "session": storage
        },
        "session_state": storage,
        'version': self.params_alice['version'],
        'session': self.params_alice['session'],
        'response': {
            "buttons": self.buttons.alice_buttons,
            'text': self.result_message if self.result_message else self.dialogs.get_message(self.settings.HELP_MESSAGE),
            'end_session': self.end_session
        },
    }
    if self.image != {}:
        response_for_alice['response']['card'] = self.image
    return response_for_alice