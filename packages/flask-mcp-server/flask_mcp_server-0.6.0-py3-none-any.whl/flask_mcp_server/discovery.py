from __future__ import annotations
import importlib, pkgutil, json, os, time
from typing import Optional

class DiscoveryCache:
    def __init__(self, path: str = ".flask_mcp_discovery.json"):
        self.path = path

    def load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save(self, data: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def discover_package(pkg: str, cache: Optional[DiscoveryCache]=None) -> None:
    m = importlib.import_module(pkg)
    discovered = []
    if hasattr(m, '__path__'):
        for modinfo in pkgutil.walk_packages(m.__path__, m.__name__ + "."):
            importlib.import_module(modinfo.name); discovered.append(modinfo.name)
    else:
        discovered.append(pkg)
    if cache:
        data = cache.load()
        data[pkg] = {"modules": discovered, "timestamp": int(time.time())}
        cache.save(data)
