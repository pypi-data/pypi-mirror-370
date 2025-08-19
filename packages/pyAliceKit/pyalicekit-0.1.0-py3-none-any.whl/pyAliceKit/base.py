import datetime, json
from types import ModuleType
from typing import Any, Optional, Self

from pyAliceKit.core.buttons import Buttons
from pyAliceKit.core.dialog_engine import DialogEngine
from pyAliceKit.core.event_emitter import EventEmitter, event_emitter
from pyAliceKit.core.intents import Intents
from pyAliceKit.core.key_words import KeyWords
from pyAliceKit.core.session_storage import SessionStorage
from pyAliceKit.messages.embedded_message import embedded_message
from pyAliceKit.utils.errors.errors import SettingsErrors
from pyAliceKit.utils.settings_validation import new_settings_is_valid
from pyAliceKit.utils.terminal import clear_terminal, print_log, print_start_welcome


class Base:
    # bool
    new: bool = False
    end_session, inaction = False, True
    # str
    previous_dialogue: str = "/"
    result_message: str = ""
    came_message = ""
    # dict
    logs: dict[str, str] = {}
    more_data_message = {}
    image: dict[str, Any] = {}
   
    # Declarations of attributes with value as instances (to be initialized later)
    buttons: Buttons
    key_words: KeyWords | None = None
    intents: Intents | None = None
    session_storage: SessionStorage
    events: EventEmitter
    dialogs: DialogEngine
    
    EMBEDDED_MESSAGE: dict[str, str] = embedded_message

    def __init__(self, params_alice: dict[Any, Any] | str, settings: ModuleType) -> None:
        self.start_time: datetime.datetime = datetime.datetime.now()

        self.params_alice: dict[Any, Any] = params_alice if isinstance(params_alice, dict) else json.loads(params_alice)

        settings_is_valid: str = new_settings_is_valid(settings)
        if settings_is_valid != "settings_is_valid":
            raise SettingsErrors(settings_is_valid, language=settings.DEBUG_LANGUAGE)
        
        self.settings: ModuleType = settings

        if self.settings.DEBUG:
            clear_terminal()
            print_start_welcome()

        #  Initialize options
        self.buttons = Buttons(self.settings)
        self.events = event_emitter


    def add_log(self: Self, log: str, color: str | None = None, bg_color: Optional[str] = None, context: str = "", start_time: datetime.datetime = datetime.datetime.now()) -> None:
        if not self.settings.DEBUG:
            return
        delta_time: datetime.timedelta = datetime.datetime.now() - start_time
        time: str = f"{delta_time.seconds}s {delta_time.microseconds} micros"
        log_text: str = self.EMBEDDED_MESSAGE.get(f"{log}-{self.settings.DEBUG_LANGUAGE}", "").format(context)
        self.logs[time] = f"{log_text}"
        print_log(
            log_text,
            time,
            text_color=color,
            bg_color=bg_color
        )