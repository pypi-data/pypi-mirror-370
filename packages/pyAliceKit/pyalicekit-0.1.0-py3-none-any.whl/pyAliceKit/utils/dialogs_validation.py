from typing import Any, Dict

def dialog_node_is_valid(node: Dict[str, Any]) -> str:
    # Проверка обязательного поля message
    if 'message' not in node or not isinstance(node['message'], str):
        return "message_missing_or_invalid"
    
    # Проверка типов для основных полей
    if 'buttons' in node and not isinstance(node['buttons'], list):
        return "buttons_invalid"
    
    if 'events' in node and not isinstance(node['events'], list):
        return "events_invalid"
    
    if 'keywords' in node and not isinstance(node['keywords'], list):
        return "keywords_invalid"
    
    if 'transitions' in node and not isinstance(node['transitions'], list):
        return "transitions_invalid"
    
    if 'childs' in node:
        if not isinstance(node['childs'], dict):
            return "childs_invalid"
        for child_node in node['childs'].values(): # type: ignore
            result = dialog_node_is_valid(child_node) # type: ignore
            if result != "dialog_is_valid":
                return result
    
    return "dialog_is_valid"


def dialogs_is_valid(dialog: Dict[str, Any]) -> str:
    for node in dialog.values():
        result = dialog_node_is_valid(node)
        if result != "dialog_is_valid":
            return result
    return "dialog_is_valid"