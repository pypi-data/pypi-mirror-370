from __future__ import annotations
import time, json

class MemoryTTLCache:
    def __init__(self):
        self.store = {}

    def get(self, key: str):
        rec = self.store.get(key)
        if not rec: return None
        val, exp = rec
        if exp and exp < time.time():
            del self.store[key]
            return None
        return val

    def set(self, key: str, value, ttl: int):
        exp = time.time() + ttl if ttl else None
        self.store[key] = (value, exp)

def make_cache():
    return MemoryTTLCache()
