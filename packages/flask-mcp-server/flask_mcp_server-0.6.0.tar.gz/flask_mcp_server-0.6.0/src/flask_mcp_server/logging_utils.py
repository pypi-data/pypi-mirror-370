from __future__ import annotations
import logging, json, time, uuid
from flask import request

def request_id() -> str:
    return request.headers.get("X-Request-Id") or uuid.uuid4().hex

class JsonFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "ts": int(time.time()*1000),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "extra"):
            base.update(record.extra)
        return json.dumps(base, ensure_ascii=False)

def setup_logging(app):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    return logger
