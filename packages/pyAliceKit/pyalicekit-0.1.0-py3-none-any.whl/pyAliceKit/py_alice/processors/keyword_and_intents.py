from __future__ import annotations
from typing import TYPE_CHECKING

from pyAliceKit.core.intents import Intents
from pyAliceKit.core.key_words import KeyWords
from pyAliceKit.utils.errors.errors import IntentsErrors, KeyWordsErrors

if TYPE_CHECKING:
    from pyAliceKit.py_alice.py_alice import PyAlice


def processing_keyword_and_intents(self: PyAlice) -> None:
    try:
        if self.settings.TEXT_FOR_KEY_WORDS in self.params_alice["request"]:
            text_for_key_words = self.params_alice["request"][self.settings.TEXT_FOR_KEY_WORDS]
        elif "nlu" in self.params_alice["request"]:
            text_for_key_words = " ".join(self.params_alice["request"]["nlu"]["tokens"])
        else:
            text_for_key_words = ""

        
        self.key_words = KeyWords(
            text=text_for_key_words,
            settings=self.settings
        )
        self.add_log("key_word_init_log", color="purple", start_time=self.start_time)
        self.key_words.key_word()
        if self.key_words.key_words != []:
            self.add_log("key_word_log", color="purple", start_time=self.start_time)
        else:
            self.add_log("key_word_not_found_log", color="purple", start_time=self.start_time)

    except KeyWordsErrors:
        raise

    try:
        self.intents = Intents(
            params_alice=self.params_alice,
            settings=self.settings
        )
        self.add_log("intents_log", color="blue", start_time=self.start_time)
    except IntentsErrors:
        raise