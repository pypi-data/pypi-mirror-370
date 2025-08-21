from __future__ import annotations
import importlib, os
from typing import List
from .container import Container
from .registry import MCPRegistry

class ServiceProvider:
    def register(self, container: Container, registry: MCPRegistry) -> None: pass
    def boot(self, app, registry: MCPRegistry) -> None: pass

def load_providers(container: Container, registry: MCPRegistry, app=None, providers: List[str] | None = None) -> None:
    spec = providers or [p.strip() for p in os.getenv("FLASK_MCP_PROVIDERS","").split(",") if p.strip()]
    for path in spec:
        mod_path, _, cls_name = path.partition(":")
        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name or "Provider")
        inst: ServiceProvider = cls() if isinstance(cls, type) else cls
        inst.register(container, registry)
        if app is not None and hasattr(inst, "boot"):
            inst.boot(app, registry)
