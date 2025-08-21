from __future__ import annotations
from typing import Callable, List
import json, time, uuid, os
from flask import Blueprint, request, jsonify, Response
from .registry import MCPRegistry, default_registry
from .security import auth_mode, check_apikey, check_hmac_signature, parse_rate, api_key_roles
from .ratelimit import make_limiter
from .spec import MCP_SPEC_VERSION

Middleware = Callable[[dict, Callable[[], Response]], Response]

class MiddlewareManager:
    def __init__(self, middlewares: List[Middleware] | None = None):
        self.middlewares = middlewares[:] if middlewares else []
    def add(self, mw: Middleware): self.middlewares.append(mw)
    def wrap(self, handler: Callable[[dict], Response]) -> Callable[[dict], Response]:
        def call(ctx: dict) -> Response:
            idx = -1
            def next_fn():
                nonlocal idx
                idx += 1
                if idx < len(self.middlewares):
                    return self.middlewares[idx](ctx, next_fn)
                return handler(ctx)
            return next_fn()
        return call

def _origin_ok():
    allowed = os.getenv("FLASK_MCP_ALLOWED_ORIGINS")
    if not allowed: return True
    origins = [o.strip() for o in allowed.split(",") if o.strip()]
    origin = request.headers.get("Origin")
    return (origin in origins) if origin else True

def mw_auth(ctx, next_fn):
    mode = auth_mode()
    if mode == "none": return next_fn()
    if mode == "apikey":
        k = request.headers.get("X-API-Key") or (request.headers.get("Authorization","")[7:] if request.headers.get("Authorization","").startswith("Bearer ") else None)
        if not check_apikey(k): return jsonify({"error":"invalid_api_key"}), 401
        return next_fn()
    if mode == "hmac":
        secret = os.getenv("FLASK_MCP_HMAC_SECRET",""); raw = request.get_data() or b""
        if not check_hmac_signature(secret, raw, request.headers.get("X-Signature")): return jsonify({"error":"invalid_signature"}), 401
        return next_fn()
    return jsonify({"error":"auth_mode_not_supported"}), 401

def mw_ratelimit(ctx, next_fn):
    rule = os.getenv("FLASK_MCP_RATE_LIMIT","")
    conf = parse_rate(rule)
    if not conf: return next_fn()
    limit, window = conf
    scope = os.getenv("FLASK_MCP_RATE_SCOPE","ip")
    client = request.remote_addr
    if scope == "key":
        auth = request.headers.get("Authorization","")
        token = auth[7:] if auth.startswith("Bearer ") else None
        client = request.headers.get("X-API-Key") or token or request.remote_addr
    limiter = make_limiter()
    ok, remaining = limiter.allow(f"rl:{client}:{window}", limit, window)
    if not ok: return jsonify({"error":"rate_limited","retry_after":window}), 429
    return next_fn()

def mw_cors(ctx, next_fn):
    resp = next_fn()
    try:
        resp.headers["Access-Control-Allow-Origin"] = os.getenv("FLASK_MCP_CORS_ORIGIN","*")
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Key, X-Signature, MCP-Protocol-Version, Mcp-Session-Id"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    except Exception:
        pass
    return resp

def mount_mcp(app, registry: MCPRegistry = None, url_prefix: str = "/mcp", middlewares: List[Middleware] | None = None):
    reg = registry or default_registry
    bp = Blueprint("mcp", __name__)
    mm = MiddlewareManager(middlewares)

    def _roles():
        k = request.headers.get("X-API-Key") or (request.headers.get("Authorization","")[7:] if request.headers.get("Authorization","").startswith("Bearer ") else None)
        return api_key_roles(k)

    def _call(kind, name, args):
        roles = _roles()
        try:
            if kind == "tool": return {"ok": True, "result": reg.call_tool(name, caller_roles=roles, **(args or {}))}
            if kind == "resource": return {"ok": True, "result": reg.get_resource(name, caller_roles=roles, **(args or {}))}
            if kind == "prompt": return {"ok": True, "result": reg.get_prompt(name, caller_roles=roles, **(args or {}))}
            if kind == "complete": return {"ok": True, "result": reg.complete(name, caller_roles=roles, **(args or {}))}
            return {"ok": False, "error": "invalid kind"}
        except PermissionError:
            return {"ok": False, "error":"forbidden"}

    @bp.post("")
    def mcp_root_post():
        if not _origin_ok(): return jsonify({"error":"origin_not_allowed"}), 403
        data = request.get_json(force=True) or {}
        accept = (request.headers.get("Accept") or "")

        headers = {}
        if data.get("method") == "initialize":
            headers["Mcp-Session-Id"] = uuid.uuid4().hex

        if "text/event-stream" in accept:
            def gen():
                yield "retry: 1500\n\n"
                eid = int(time.time()*1000)
                if data.get("method") == "mcp.call":
                    p = data.get("params") or {}
                    res = _call(p.get("kind"), p.get("name"), p.get("args"))
                    payload = {"jsonrpc":"2.0","id":data.get("id"),"result":res}
                elif data.get("method") == "mcp.list":
                    payload = {"jsonrpc":"2.0","id":data.get("id"),"result":reg.list_all()}
                else:
                    payload = {"jsonrpc":"2.0","id":data.get("id"),"error":{"code":-32601,"message":"Method not implemented"}}
                yield f"id: {eid}\n"
                yield f"data: {json.dumps(payload)}\n\n"
            resp = Response(gen(), mimetype="text/event-stream")
            for k,v in headers.items(): resp.headers[k]=v
            return resp

        if data.get("method") == "mcp.call":
            p = data.get("params") or {}
            out = _call(p.get("kind"), p.get("name"), p.get("args"))
            resp = {"jsonrpc":"2.0","id":data.get("id"),"result":out}
        elif data.get("method") == "mcp.list":
            resp = {"jsonrpc":"2.0","id":data.get("id"),"result":reg.list_all()}
        else:
            resp = {"jsonrpc":"2.0","id":data.get("id"),"error":{"code":-32601,"message":"Method not implemented"}}
        r = jsonify(resp); [r.headers.__setitem__(k,v) for k,v in headers.items()]
        return r

    @bp.get("")
    def mcp_root_get():
        if not _origin_ok(): return jsonify({"error":"origin_not_allowed"}), 403
        def gen():
            yield "retry: 1500\n\n"
            eid = int(time.time()*1000)
            hello = {"event":"hello","spec":MCP_SPEC_VERSION,"version":"0.6.0"}
            yield f"id: {eid}\n"
            yield f"data: {json.dumps(hello)}\n\n"
        return Response(gen(), mimetype="text/event-stream")

    # Compat routes
    @bp.get("/list")
    def list_():
        handler = mm.wrap(lambda ctx: jsonify(reg.list_all()))
        return handler({})

    @bp.post("/call")
    def call_():
        payload = request.get_json(force=True) or {}
        handler = mm.wrap(lambda ctx: jsonify(_call(payload.get("kind"), payload.get("name"), payload.get("args"))))
        return handler({})

    @bp.post("/batch")
    def batch_():
        calls = request.get_json(force=True) or []
        def _h(ctx):
            results = []
            for item in calls:
                results.append(_call(item.get("kind"), item.get("name"), item.get("args")))
            return jsonify(results)
        handler = mm.wrap(_h)
        return handler({})

    app.register_blueprint(bp, url_prefix=url_prefix)
    return bp, mm, reg
