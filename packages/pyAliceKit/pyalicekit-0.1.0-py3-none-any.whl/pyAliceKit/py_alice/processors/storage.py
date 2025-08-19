from __future__ import annotations
from typing import TYPE_CHECKING

from pyAliceKit.core.event_emitter import event_emitter
from pyAliceKit.core.session_storage import SessionStorage
if TYPE_CHECKING:
    from pyAliceKit.py_alice.py_alice import PyAlice

def processing_storage(self: PyAlice) -> None:
        self.session_storage = SessionStorage(
            params_alice=self.params_alice,
            settings=self.settings
        )
        if self.session_storage.get_all() != {}:
            self.add_log("storage_fill", color="green", start_time=self.start_time)
            event_emitter.emit(event_name="storageFillEvent", event={
                                                                "event": "storageFillEvent",
                                                                "where": "PyAlice.__processing_params",
                                                                "cls": self,
                                                                "storage": self.session_storage
                                                                })
        else:
            self.add_log("storage_not_fill", color="light_red", start_time=self.start_time)
            event_emitter.emit(event_name="storageNotFillEvent", event={
                                                                "event": "storageNotFillEvent",
                                                                "where": "PyAlice.__processing_params",
                                                                "cls": self,
                                                                "storage": self.session_storage
                                                                })