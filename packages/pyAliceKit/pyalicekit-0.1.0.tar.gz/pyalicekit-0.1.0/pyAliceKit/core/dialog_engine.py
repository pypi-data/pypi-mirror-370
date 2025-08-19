from __future__ import annotations
from typing import TYPE_CHECKING

import json
import os
from types import FunctionType, ModuleType
from typing import Any, Optional, Self

from pyAliceKit.utils.dialogs import flatten_dialogs, prev_path, putting_dialog_constants_places
from pyAliceKit.utils.dialogs_validation import dialogs_is_valid
from pyAliceKit.utils.errors.errors import DialogEngineErrors
from pyAliceKit.utils.tools import load_user_function

if TYPE_CHECKING:
    from pyAliceKit.py_alice.py_alice import PyAlice


class DialogEngine:
    def __init__(self: Self, settings: ModuleType, pyAlice: PyAlice) -> None:
        self.__settings: ModuleType = settings
        self.__pyAlice: "PyAlice" = pyAlice # type: ignore
        self.__dialogs_map_file: str = self.__settings.DIALOGS_MAP_FILE
        self.dialog: Optional[str] = None  # Текущий диалог, если он найден

        putting_dialog_constants_places(self.__settings)

        validation_result: str = dialogs_is_valid(getattr(self.__settings, "DIALOG_NODES", {}))
        if validation_result != "dialog_is_valid":
            raise DialogEngineErrors(
                validation_result,
                context=validation_result,
                language=self.__settings.DEBUG_LANGUAGE
            )



        # Плоская карта диалогов
        self.__dialogs_map: dict[str, dict[str, Any]] = {}

        self.__init_dialogs_map()

    def __init_dialogs_map(self: Self) -> None:
        try:
            if os.path.exists(self.__dialogs_map_file):
                # TODO: path
                with open(self.__dialogs_map_file, "r", encoding="utf-8") as f:
                    self.__dialogs_map = json.load(f)
            if self.__settings.DEBUG:
                dialogs = getattr(self.__settings, "DIALOG_NODES", {})
                self.__dialogs_map = flatten_dialogs(dialogs)
                with open(self.__dialogs_map_file, "w", encoding="utf-8") as f:
                    json.dump(self.__dialogs_map, f, ensure_ascii=False, indent=4)
                self.__pyAlice.add_log( # type: ignore
                    "configuration_options_log",
                    color="cyan",
                    start_time=self.__pyAlice.start_time # type: ignore
                )
            else:
                raise DialogEngineErrors("dialog_map_file_not_found", language=self.__settings.DEBUG_LANGUAGE)
        except Exception as e:
            raise DialogEngineErrors("dialog_map_load_failed", context=str(e), language=self.__settings.DEBUG_LANGUAGE)
        
    def __find_simple_dialog_path(
            self: Self, 
            came_message: str, 
            activated_events: set[Any],
            key_words: set[str],
            intent_names: set[str],
            previous_path: str,
            previous_dialog: dict[str, Any]
            ) -> Optional[str]:
        if "transitions" in previous_dialog and "$prev" in previous_dialog["transitions"] and "prev" in key_words:
            return prev_path(previous_path)

        if "stop" in key_words:
            # TODO: Добавить обработку остановки диалога
            return "/end"
        if "chooser" in previous_dialog:
            chooser_code: str = previous_dialog["chooser"]
            chooser_name: str = previous_dialog.get("chooser_name", "")
            
            if chooser_name == "":
                raise DialogEngineErrors("chooser_name_missing", language=self.__settings.DEBUG_LANGUAGE)
            chooser_func: FunctionType = load_user_function(chooser_code, chooser_name, self.__settings.DEBUG_LANGUAGE)
            
            try:
                result: Optional[str] = chooser_func(self.__pyAlice) # type: ignore
            except Exception as e:
                raise DialogEngineErrors("chooser_function_execution_failed", context=str(e), language=self.__settings.DEBUG_LANGUAGE)
            
            if result != "" and result is not None and result in self.__dialogs_map:
                return result
            else:
                raise DialogEngineErrors("chooser_invalid_result", context=result, language=self.__settings.DEBUG_LANGUAGE)
        
        return None


    def find_best_dialog(self: Self) -> Optional[str]:
        scores: dict[str, int] = {}

        came_message: str = self.__pyAlice.came_message.lower() # type: ignore
        activated_events: set[Any] = set(self.__pyAlice.events.get_events()) # type: ignore
        key_words: set[Any] = set(self.__pyAlice.key_words.key_words) # type: ignore
        intent_names: set[Any] = set(self.__pyAlice.intents.get_intent_names()) # type: ignore
        previous_path: str = self.__pyAlice.previous_dialogue # type: ignore
        previous_dialog = self.__pyAlice.dialogs.get_dialog(previous_path, {}) # type: ignore

        simple_dialog_path: str | None = self.__find_simple_dialog_path(
            came_message=came_message, # type: ignore
            activated_events=activated_events,
            key_words=key_words,
            intent_names=intent_names,
            previous_path=previous_path, # type: ignore
            previous_dialog=previous_dialog # type: ignore
        )

        if simple_dialog_path:
            self.dialog = simple_dialog_path
            return simple_dialog_path

        # Определяем множество кандидатов для сужения поиска
        allowed_dialogs: set[Any] = set()

        # 1) Глобальные (корневые) диалоги — с одним уровнем '/'
        allowed_dialogs.update([
            name for name in self.__dialogs_map
            if name.count("/") == 1
        ])

         # 2) Первые потомки предыдущего диалога
        if previous_path in self.__dialogs_map:
            previous_data = self.__dialogs_map[previous_path]
            allowed_dialogs.update(previous_data.get("childs", []))

            # 3) Диалоги из переходов предыдущего
            # Если transitions — список, просто добавляем элементы
            allowed_dialogs.update(previous_data.get("transitions", []))


        for dialog_name in allowed_dialogs:
            dialog_data: dict[str, Any] = self.__dialogs_map.get(dialog_name, {})
            if not dialog_data:
                continue

            score: int = 0
            reasons: list[str] = []

            # События
            dialog_events = set(dialog_data.get("events", []))
            matched_events = dialog_events & activated_events
            if matched_events:
                score += len(matched_events)
                reasons.append("matched_events")

            # Ключевые слова
            dialog_keywords = set(dialog_data.get("keywords", []))
            matched_keywords = dialog_keywords & key_words
            if matched_keywords:
                score += len(matched_keywords) * 2
                reasons.append("matched_keywords")

            # Интенты
            matched_intents = intent_names & set(dialog_data.get("intents", []))
            if matched_intents:
                score += len(matched_intents) * 2
                reasons.append("matched_intents")

            # TODO: Under a big question
            # Частичное совпадение по сообщению
            message_text = dialog_data.get("message", "").lower()
            if message_text and message_text in came_message:
                score += 1
                reasons.append("matched_message")

            # Приоритет из meta
            priority = dialog_data.get("meta", {}).get("priority", 0)
            if isinstance(priority, int) and priority > 0:
                score += priority
                reasons.append("meta_priority")

            if score > 0:
                scores[dialog_name] = score
                self.__pyAlice.add_log(
                    "dialog_score_log",
                    color="yellow",
                    context=f"{dialog_name}: {score} ({', '.join(reasons)})",
                    start_time=self.__pyAlice.start_time
                )

        result: str | None = max(scores, key=scores.get) if scores else None # type: ignore
        self.dialog = result

        if result:
            self.__pyAlice.add_log(
                "dialog_selected_log",
                color="green",
                context=result, # type: ignore
                start_time=self.__pyAlice.start_time
            )
        else:
            self.__pyAlice.add_log(
                "dialog_not_found_log",
                color="red",
                start_time=self.__pyAlice.start_time
            )

        return result # type: ignore





    def get_dialog(self: Self, name: str, default: Any = None) -> Optional[dict[str, Any]]:
        return self.__dialogs_map.get(name, default)

    def get_all(self: Self) -> dict[str, dict[str, Any]]:
        return self.__dialogs_map
    
    def get_message(self: Self, name: str) -> Optional[str]:
        dialog: Optional[str] = self.__settings.ALL_MESSAGES.get(name, None)
        # TODO: Добавить обработку ошибок
        return dialog
    
    def apply_dialog(self: Self, dialog_path: Optional[str]) -> None:
        if self.__pyAlice.new:
            res: Optional[str] = self.get_message(self.__settings.STARTING_MESSAGE)
            if res is not None:
                self.__pyAlice.result_message = res
                self.__pyAlice.session_storage.set_service_storage("previous_dialogue", "/")
                return
            raise DialogEngineErrors(
                "starting_message_not_found",
                context=self.__settings.STARTING_MESSAGE,
                language=self.__settings.DEBUG_LANGUAGE
            )
        if dialog_path:
            dialog_data: Optional[dict[str, Any]] = self.get_dialog(dialog_path)
            # TODO: Добавить валидатор для dialogs
            if dialog_data and "message" in dialog_data:
                message_key: str = dialog_data["message"]
                self.__pyAlice.result_message = self.get_message(message_key) # type: ignore
                self.__pyAlice.buttons.add_buttons(dialog_data.get("buttons", []))
                image = dialog_data.get("image")
                if image:
                    self.__pyAlice.image = self.__settings.IMAGES.get(image, {})
            self.__pyAlice.session_storage.set_service_storage("previous_dialogue", dialog_path)