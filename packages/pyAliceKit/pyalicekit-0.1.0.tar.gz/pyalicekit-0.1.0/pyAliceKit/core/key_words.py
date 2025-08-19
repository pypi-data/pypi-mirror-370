import re
from types import ModuleType
from typing import Any, Self

from pyAliceKit.utils.errors.errors import KeyWordsErrors


class KeyWords():
    def __init__(self: Self, text: str, settings: ModuleType) -> None:
        self.text: str = text.lower()
        self.settings: ModuleType = settings
        self.key_words_map: dict[str, list[str]] = self.settings.KEY_WORDS
        self.key_words: list[str] = []

        if self.settings.DEBUG:
            self._validate_key_words()

    def _validate_key_words(self: Self) -> None:
        all_words: dict[str, Any] = {}
        for intent, words in self.key_words_map.items():
            for word in words:
                word_lc = word.lower()
                if word_lc in all_words:
                    raise KeyWordsErrors("duplicate_keyword", context=f"'{word_lc}' используется в '{intent}' и '{all_words[word_lc]}'", language=self.settings.DEBUG_LANGUAGE)
                all_words[word_lc] = intent

    def key_word(self: Self) -> None:
        found_intents: set[Any] = set()

        for intent, words in self.key_words_map.items():
            for word in words:
                if re.search(rf"\b{re.escape(word)}\b", self.text):
                    found_intents.add(intent)

        if found_intents:
            self.key_words = list(found_intents)
