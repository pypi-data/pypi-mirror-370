from types import ModuleType
from typing import Any, Self, Optional

from pyAliceKit.utils.errors.errors import IntentsErrors


class Intents:
    def __init__(self: Self, params_alice: dict[Any, Any], settings: ModuleType) -> None:
        self.params_alice: dict[Any, Any] = params_alice
        self.__settings: ModuleType = settings
        self.intents: dict[str, dict[str, Any]] = {}
        
        self.__parse_intents()

    def __parse_intents(self: Self) -> None:
        request = self.params_alice.get("request", {})
        intents = request.get("nlu", {}).get("intents")
        if not intents:
            intents = request.get("intents", {})

        self.intents = intents if intents else {}

    def get_intent_names(self: Self) -> list[str]:
        return list(self.intents.keys())

    def has_intent(self: Self, intent_name: str) -> bool:
        return intent_name in self.intents

    def get_slots(self: Self, intent_name: str) -> Optional[dict[str, Any]]:
        if intent_name not in self.intents:
            raise IntentsErrors("intent_not_found", context=intent_name, language=self.__settings.LANGUAGE)
        return self.intents[intent_name].get("slots")

    def get_slot_value(self: Self, intent_name: str, slot_name: str) -> Optional[Any]:
        slots = self.get_slots(intent_name)
        if not slots:
            raise IntentsErrors("slots_not_found", context=intent_name, language=self.__settings.LANGUAGE)

        slot = slots.get(slot_name)
        if not slot:
            raise IntentsErrors("slot_not_found", context=f"{intent_name}.{slot_name}", language=self.__settings.LANGUAGE)

        value = slot.get("value")
        if value is None:
            raise IntentsErrors("slot_value_not_found", context=f"{intent_name}.{slot_name}", language=self.__settings.LANGUAGE)

        return value

    def get_first_intent_name(self: Self) -> Optional[str]:
        names = self.get_intent_names()
        return names[0] if names else None
