from __future__ import annotations
import time

class MemoryLimiter:
    def __init__(self):
        self.store = {}

    def allow(self, key: str, limit: int, window: int) -> tuple[bool,int]:
        now = int(time.time())
        bucket = now // window
        rec = self.store.get(key)
        if not rec or rec[0] != bucket:
            self.store[key] = (bucket, 1)
            return True, limit-1
        cnt = rec[1] + 1
        self.store[key] = (bucket, cnt)
        return (cnt <= limit, max(0, limit - cnt))

def make_limiter():
    return MemoryLimiter()
