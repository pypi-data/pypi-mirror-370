from __future__ import annotations
from .registry import default_registry

class Mcp:
    @staticmethod
    def tool(name=None, description=None, roles=None, ttl=None):
        from .registry import tool as _tool
        return _tool(name=name, description=description, roles=roles, ttl=ttl)
    @staticmethod
    def resource(name=None, description=None, roles=None, ttl=None):
        from .registry import resource as _res
        return _res(name=name, description=description, roles=roles, ttl=ttl)
    @staticmethod
    def prompt(name=None, description=None, roles=None):
        from .registry import prompt as _pr
        return _pr(name=name, description=description, roles=roles)
    @staticmethod
    def completion(name=None, roles=None):
        from .registry import completion_provider as _cp
        return _cp(name=name, roles=roles)
