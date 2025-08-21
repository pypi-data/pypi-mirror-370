from __future__ import annotations
import os, hmac, hashlib

def auth_mode() -> str:
    return os.getenv("FLASK_MCP_AUTH_MODE", "none").lower()

def _apikeys_map():
    raw = os.getenv("FLASK_MCP_API_KEYS_MAP", "")
    entries = [e.strip() for e in raw.split(";") if e.strip()]
    mapping = {}
    for e in entries:
        key, _, roles = e.partition(":")
        mapping[key.strip()] = [r.strip() for r in roles.split("|") if r.strip()] if roles else []
    return mapping

def _apikeys_list():
    keys = os.getenv("FLASK_MCP_API_KEYS", "").strip()
    return [k.strip() for k in keys.split(",") if k.strip()]

def api_key_roles(value: str | None):
    if not value: return []
    return _apikeys_map().get(value, [])

def check_apikey(value: str | None) -> bool:
    if not value: return False
    if value in _apikeys_list(): return True
    return value in _apikeys_map()

def check_hmac_signature(secret: str, body: bytes, signature: str | None) -> bool:
    if not signature or not signature.startswith("sha256="):
        return False
    sig = signature.split("=",1)[1]
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, sig)

def parse_rate(rule: str):
    if not rule: return None
    n, sep, per = rule.partition("/")
    try:
        n = int(n)
    except Exception:
        return None
    if per == "s": window = 1
    elif per == "m": window = 60
    elif per == "h": window = 3600
    elif per == "d": window = 86400
    else: return None
    return (n, window)
