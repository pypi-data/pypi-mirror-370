from typing import Any, Callable, Self


class EventEmitter:
    def __init__(self: Self) -> None:
        self.__listeners: dict[str, list[Callable[..., Any]]] = {}
        self.__events: list[str] = []


    def on(self: Self, event_name: str, handler: Callable[..., Any]) -> None:
        self.__listeners.setdefault(event_name, []).append(handler)


    def emit(self: Self, event_name: str, event: dict[str, Any], *args: Any, **kwargs: Any) -> None:
        self.__events.append(event_name)
        for handler in self.__listeners.get(event_name, []):
            handler(event, *args, **kwargs)  # type: ignore


    def get_events(self: Self) -> list[str]:
        return self.__events


event_emitter = EventEmitter()

def on_event(event_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        event_emitter.on(event_name, func)
        return func
    return decorator