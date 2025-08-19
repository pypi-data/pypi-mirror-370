from types import ModuleType


def new_settings_is_valid(new_settings: ModuleType) -> str:
    # Проверка на наличие всех обязательных атрибутов
    required_settings = [
        "DEBUG",
        "LOG_OUTPUT_IMMEDIATELY",
        "TIME_ZONE",
        "EVENTS",
        "TEXT_FOR_KEY_WORDS",
        "VERSION",
        "ALL_MESSAGES",
        "STARTING_MESSAGE",
        "ERROR_MESSAGE",
        "HELP_MESSAGE",
        "DEBUG_LANGUAGE",
        "LANGUAGE",
        "SOURCE_TEXT"
    ]

    for key in required_settings:
        if not hasattr(new_settings, key):
            return f"{key.lower()}_not_set"

    # Проверка типов и допустимых значений
    if not isinstance(new_settings.DEBUG, bool):
        return "debug_setting_error"

    if not isinstance(new_settings.LOG_OUTPUT_IMMEDIATELY, bool):
        return "log_output_immediately_setting_error"

    if new_settings.TIME_ZONE is not None and not isinstance(new_settings.TIME_ZONE, str):
        return "timezone_setting_error"

    if not isinstance(new_settings.EVENTS, bool):
        return "events_setting_error"

    if new_settings.TEXT_FOR_KEY_WORDS not in ["command", "original_utterance"]:
        return "text_for_key_word_setting_error"

    if not isinstance(new_settings.VERSION, str):
        return "version_setting_error"

    if not isinstance(new_settings.ALL_MESSAGES, dict):
        return "all_messages_setting_error"

    if not new_settings.STARTING_MESSAGE or new_settings.STARTING_MESSAGE not in new_settings.ALL_MESSAGES: # type: ignore
        return "starting_message_setting_error"

    if not new_settings.ERROR_MESSAGE or new_settings.ERROR_MESSAGE not in new_settings.ALL_MESSAGES: # type: ignore
        return "error_message_setting_error"

    if not new_settings.HELP_MESSAGE or new_settings.HELP_MESSAGE not in new_settings.ALL_MESSAGES: # type: ignore
        return "help_message_setting_error"

    if not isinstance(new_settings.DEBUG_LANGUAGE, str):
        return "debug_language_setting_error"

    if not isinstance(new_settings.LANGUAGE, str):
        return "language_setting_error"

    if new_settings.SOURCE_TEXT not in ["command", "original_utterance"]:
        return "source_text_setting_error"
    
    return "settings_is_valid"