from __future__ import annotations
from typing import Any, Callable

class Resource:
    def __init__(self, get: Callable[..., Any]):
        self.get = get

class ResourceTemplate:
    def __init__(self, template: str):
        self.template = template
    def expand(self, **params) -> str:
        return self.template.format(**params)
