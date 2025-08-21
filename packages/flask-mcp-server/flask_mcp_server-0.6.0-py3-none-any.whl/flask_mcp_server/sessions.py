from __future__ import annotations
import os, time

class MemorySessionStore:
    def __init__(self):
        self.store = {}
    def get(self, sid: str):
        return self.store.get(sid)
    def set(self, sid: str, data: dict, ttl: int = 3600):
        self.store[sid] = (data, time.time() + ttl)
    def delete(self, sid: str):
        self.store.pop(sid, None)

def make_session_store():
    # Placeholder for future Redis-backed sessions
    return MemorySessionStore()
