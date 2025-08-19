from types import ModuleType
from typing import Any, Self

from pyAliceKit.utils.errors.errors import StorageErrors


class SessionStorage:
    def __init__(self: Self, params_alice: dict[Any, Any], settings: ModuleType) -> None:
        self.__params_alice = params_alice
        self.__settings = settings
        self.__session_data: dict[Any, Any] = self.__params_alice.get("state", {}).get("session", {})
        self.__service_storage: dict[str, Any] = self.get("pyAliceKit", default={})

    def get_all(self: Self) -> dict[str, Any]:
        self.__session_data["pyAliceKit"] = self.__service_storage
        return self.__session_data

    def get(self: Self, key: str, default: Any = None) -> Any:
        return self.__session_data.get(key, default)

    def set(self: Self, key: str, value: Any, overwrite: bool = True) -> None:
        if key in self.__session_data and not overwrite:
            raise StorageErrors("overwrite_session_error", context=key, language=self.__settings.DEBUG_LANGUAGE)
        self.__session_data[key] = value

    def has(self: Self, key: str) -> bool:
        return key in self.__session_data

    def delete(self: Self, key: str) -> None:
        if key in self.__session_data:
            del self.__session_data[key]

    def to_dict(self: Self) -> dict[str, Any]:
        return self.__session_data.copy()

    def get_service_storage(self: Self) -> dict[str, Any]:
        return self.__service_storage
    
    def set_service_storage(self: Self, key: str, value: Any) -> None:
        self.__service_storage[key] = value