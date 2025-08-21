from __future__ import annotations
import inspect, threading, hashlib, json
from typing import Any, Callable, Dict, Optional, List
from .schemas import build_input_schema, build_output_schema
from .events import default_bus
from .caching import make_cache

class MCPRegistry:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.completions: Dict[str, Callable[..., Any]] = {}
        self.cache = make_cache()

    def register_tool(self, name: str, fn: Callable[..., Any], desc: Optional[str]=None, roles: Optional[List[str]]=None, ttl: Optional[int]=None):
        with self._lock:
            self.tools[name] = {
                "name": name, "description": desc or (inspect.getdoc(fn) or ""),
                "callable": fn, "input_schema": build_input_schema(fn),
                "output_schema": build_output_schema(fn),
                "roles": roles or [], "ttl": ttl,
            }
        default_bus.publish_registry_changed({"event":"registry.changed","reason":"tool.register","name":name})

    def register_resource(self, name: str, getter: Callable[..., Any], desc: Optional[str]=None, roles: Optional[List[str]]=None, ttl: Optional[int]=None):
        with self._lock:
            self.resources[name] = {
                "name": name, "description": desc or (inspect.getdoc(getter) or ""),
                "getter": getter, "output_schema": build_output_schema(getter),
                "roles": roles or [], "ttl": ttl,
            }
        default_bus.publish_registry_changed({"event":"registry.changed","reason":"resource.register","name":name})

    def register_prompt(self, name: str, provider: Callable[..., Any], desc: Optional[str]=None, roles: Optional[List[str]]=None):
        with self._lock:
            self.prompts[name] = {
                "name": name, "description": desc or (inspect.getdoc(provider) or ""),
                "provider": provider, "output_schema": build_output_schema(provider),
                "roles": roles or [],
            }
        default_bus.publish_registry_changed({"event":"registry.changed","reason":"prompt.register","name":name})

    def register_completion(self, name: str, provider: Callable[..., Any], roles: Optional[List[str]]=None):
        with self._lock:
            self.completions[name] = provider
        default_bus.publish_registry_changed({"event":"registry.changed","reason":"completion.register","name":name})

    def list_all(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "tools": {k: {kk: vv for kk, vv in v.items() if kk not in ('callable',)} for k, v in self.tools.items()},
                "resources": {k: {kk: vv for kk, vv in v.items() if kk not in ('getter',)} for k, v in self.resources.items()},
                "prompts": {k: {kk: vv for kk, vv in v.items() if kk not in ('provider',)} for k, v in self.prompts.items()},
                "completions": list(self.completions.keys()),
                "version": "0.6.0",
            }

    def _permits(self, item_roles: list[str], caller_roles: list[str]) -> bool:
        return (not item_roles) or any(r in caller_roles for r in item_roles)

    def _cache_key(self, name: str, args: dict) -> str:
        return "mcp:" + name + ":" + hashlib.sha256(json.dumps(args, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    def call_tool(self, name: str, caller_roles: list[str] | None = None, **kwargs) -> Any:
        item = self.tools[name]
        if not self._permits(item.get("roles", []), caller_roles or []):
            raise PermissionError("forbidden")
        ttl = item.get("ttl")
        if ttl:
            key = self._cache_key("tool:"+name, kwargs)
            cached = self.cache.get(key)
            if cached is not None: return cached
            result = item["callable"](**kwargs)
            self.cache.set(key, result, ttl)
            return result
        return item["callable"](**kwargs)

    def get_resource(self, name: str, caller_roles: list[str] | None = None, **kwargs) -> Any:
        item = self.resources[name]
        if not self._permits(item.get("roles", []), caller_roles or []):
            raise PermissionError("forbidden")
        ttl = item.get("ttl")
        if ttl:
            key = self._cache_key("resource:"+name, kwargs)
            cached = self.cache.get(key)
            if cached is not None: return cached
            result = item["getter"](**kwargs)
            self.cache.set(key, result, ttl)
            return result
        return item["getter"](**kwargs)

    def get_prompt(self, name: str, caller_roles: list[str] | None = None, **kwargs) -> Any:
        item = self.prompts[name]
        if not self._permits(item.get("roles", []), caller_roles or []):
            raise PermissionError("forbidden")
        return item["provider"](**kwargs)

    def complete(self, name: str, caller_roles: list[str] | None = None, **kwargs) -> Any:
        if name not in self.completions:
            raise KeyError(name)
        return self.completions[name](**kwargs)

default_registry = MCPRegistry()

def tool(name: Optional[str]=None, description: Optional[str]=None, roles: Optional[List[str]]=None, ttl: Optional[int]=None):
    def deco(fn: Callable[..., Any]):
        reg_name = name or fn.__name__
        default_registry.register_tool(reg_name, fn, description, roles=roles, ttl=ttl)
        return fn
    return deco

def resource(name: Optional[str]=None, description: Optional[str]=None, roles: Optional[List[str]]=None, ttl: Optional[int]=None):
    def deco(fn: Callable[..., Any]):
        reg_name = name or fn.__name__
        default_registry.register_resource(reg_name, fn, description, roles=roles, ttl=ttl)
        return fn
    return deco

def prompt(name: Optional[str]=None, description: Optional[str]=None, roles: Optional[List[str]]=None):
    def deco(fn: Callable[..., Any]):
        reg_name = name or fn.__name__
        default_registry.register_prompt(reg_name, fn, description, roles=roles)
        return fn
    return deco

def completion_provider(name: Optional[str]=None, roles: Optional[List[str]]=None):
    def deco(fn: Callable[..., Any]):
        reg_name = name or fn.__name__
        default_registry.register_completion(reg_name, fn, roles=roles)
        return fn
    return deco
