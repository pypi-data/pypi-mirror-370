from __future__ import annotations
import os
from blinker import Signal

class EventBus:
    def __init__(self) -> None:
        self.registry_changed = Signal("registry_changed")
        self._redis = None
        if os.getenv("FLASK_MCP_SSE_BACKEND") == "redis":
            try:
                import redis
                self._redis = redis.from_url(os.getenv("FLASK_MCP_REDIS_URL", "redis://localhost:6379/0"))
            except Exception:
                self._redis = None

    def publish_registry_changed(self, payload: dict) -> None:
        self.registry_changed.send(payload)
        if self._redis:
            try:
                self._redis.publish("flask_mcp_events", {"type":"registry.changed","payload":payload}.__repr__())
            except Exception:
                pass

default_bus = EventBus()
