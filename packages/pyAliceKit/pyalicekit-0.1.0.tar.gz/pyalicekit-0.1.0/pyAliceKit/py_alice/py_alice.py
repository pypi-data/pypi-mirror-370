import json
from types import ModuleType
from typing import Any, Optional, Self, Union
from pyAliceKit.base import Base
from pyAliceKit.core.dialog_engine import DialogEngine
from pyAliceKit.py_alice.processors.came_message import processing_came_message
from pyAliceKit.py_alice.processors.keyword_and_intents import processing_keyword_and_intents
from pyAliceKit.py_alice.processors.new import processing_new
from pyAliceKit.py_alice.processors.response_for_alice import processing_response_for_alice
from pyAliceKit.py_alice.processors.service_storage import processing_service_storage
from pyAliceKit.py_alice.processors.storage import processing_storage


class PyAlice(Base):
    """
    PyAlice is a class that initializes the Alice API with the provided parameters and settings.
    It sets up various attributes related to the session, such as intents, storage, and buttons.
    """

    def __init__(self: Self, params_alice: dict[Any, Any] | str, settings: ModuleType) -> None:
        super().__init__(params_alice, settings)
        self.add_log("configuration_options_log", color="yellow", start_time=self.start_time)
        self.__processing_params()
        self.dialogs = DialogEngine(
            settings=self.settings,
            pyAlice=self
        )
        path_dialog: Optional[str] = self.dialogs.find_best_dialog()
        self.dialogs.apply_dialog(path_dialog)
    

    def __processing_params(self: Self) -> None:
        processing_came_message(self)

        processing_new(self)
        
        processing_storage(self)
        
        processing_service_storage(self)
        
        processing_keyword_and_intents(self)


    def get_response_for_alice(self: Self, type: str = "json") -> Union[dict[str, Any], str]: # type: ignore
        response_for_alice: dict[str, Any] = processing_response_for_alice(self)
        if type == "json":
            return json.dumps(response_for_alice)
        elif type == "dict":
            return response_for_alice