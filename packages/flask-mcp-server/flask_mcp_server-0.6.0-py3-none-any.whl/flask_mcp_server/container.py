from __future__ import annotations
from typing import Callable, Dict, Any

class Container:
    def __init__(self):
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}

    def set(self, name: str, value: Any) -> None:
        self._singletons[name] = value

    def factory(self, name: str, fn: Callable[[], Any]) -> None:
        self._factories[name] = fn

    def get(self, name: str) -> Any:
        if name in self._singletons:
            return self._singletons[name]
        if name in self._factories:
            v = self._factories[name]()
            self._singletons[name] = v
            return v
        raise KeyError(name)

default_container = Container()
