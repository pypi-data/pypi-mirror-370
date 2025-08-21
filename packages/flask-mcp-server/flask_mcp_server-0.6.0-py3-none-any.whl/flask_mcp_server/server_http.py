from __future__ import annotations
import json, time, uuid, os
from typing import Any, Dict
from flask import Flask, request, jsonify, Response
from .registry import MCPRegistry, default_registry
from .events import default_bus
from .spec import MCP_SPEC_VERSION
from .security import auth_mode, check_apikey, check_hmac_signature, parse_rate, api_key_roles
from .ratelimit import make_limiter
from .logging_utils import setup_logging

ACCEPTED_PROTOCOLS = {"2025-06-18", "2025-03-26"}

def _origin_allowed():
    allowed = os.getenv("FLASK_MCP_ALLOWED_ORIGINS")
    if not allowed:
        return True
    origins = [o.strip() for o in allowed.split(",") if o.strip()]
    origin = request.headers.get("Origin")
    return (origin in origins) if origin else True

def create_app(registry: MCPRegistry = None) -> Flask:
    reg = registry or default_registry
    app = Flask(__name__)
    setup_logging(app)
    limiter = make_limiter()
    rate_conf = parse_rate(os.getenv("FLASK_MCP_RATE_LIMIT", ""))
    rate_scope = os.getenv("FLASK_MCP_RATE_SCOPE","ip")

    def _client_key():
        if rate_scope == "key":
            auth = request.headers.get("Authorization","")
            token = auth[7:] if auth.startswith("Bearer ") else None
            return request.headers.get("X-API-Key") or token or request.remote_addr
        return request.remote_addr

    def _caller_roles():
        k = request.headers.get("X-API-Key") or (request.headers.get("Authorization","")[7:] if request.headers.get("Authorization","").startswith("Bearer ") else None)
        return api_key_roles(k)

    def _auth_check():
        mode = auth_mode()
        if mode == "none": return True, None
        if mode == "apikey":
            k = request.headers.get("X-API-Key") or (request.headers.get("Authorization","")[7:] if request.headers.get("Authorization","").startswith("Bearer ") else None)
            return (check_apikey(k), "invalid_api_key" if not check_apikey(k) else None)
        if mode == "hmac":
            secret = os.getenv("FLASK_MCP_HMAC_SECRET","")
            raw = request.get_data() or b""
            ok = check_hmac_signature(secret, raw, request.headers.get("X-Signature"))
            return (ok, "invalid_signature" if not ok else None)
        return False, "auth_mode_not_supported"

    def _rl_check():
        if not rate_conf: return True, None, None
        limit, window = rate_conf
        ok, remaining = limiter.allow(f"rl:{_client_key()}:{window}", limit, window)
        return ok, remaining, window

    def _guard():
        ver = request.headers.get("MCP-Protocol-Version")
        if ver and ver not in ACCEPTED_PROTOCOLS:
            return jsonify({"error":"unsupported_protocol_version","got":ver}), 400
        if not _origin_allowed():
            return jsonify({"error":"origin_not_allowed"}), 403
        ok, err = _auth_check()
        if not ok: return jsonify({"error": err}), 401
        ok, remaining, window = _rl_check()
        if not ok: return jsonify({"error":"rate_limited","retry_after":window}), 429
        return None

    def _call(kind, name, args, roles):
        try:
            if kind == "tool":
                return {"ok": True, "result": reg.call_tool(name, caller_roles=roles, **args)}
            if kind == "resource":
                return {"ok": True, "result": reg.get_resource(name, caller_roles=roles, **args)}
            if kind == "prompt":
                return {"ok": True, "result": reg.get_prompt(name, caller_roles=roles, **args)}
            if kind == "complete":
                return {"ok": True, "result": reg.complete(name, caller_roles=roles, **args)}
            return {"ok": False, "error": "invalid kind"}
        except PermissionError:
            return {"ok": False, "error":"forbidden"}

    # Unified MCP endpoint
    @app.post("/mcp")
    def mcp_post():
        g = _guard()
        if g: return g
        roles = _caller_roles()
        data = request.get_json(force=True) or {}
        headers = {}
        if data.get("method") == "initialize":
            headers["Mcp-Session-Id"] = uuid.uuid4().hex

        accept = (request.headers.get("Accept") or "")
        if "text/event-stream" in accept:
            def gen():
                yield "retry: 1500\n\n"
                eid = int(time.time()*1000)
                if data.get("method") == "mcp.call":
                    p = data.get("params") or {}
                    result = _call(p.get("kind"), p.get("name"), p.get("args") or {}, roles)
                    resp = {"jsonrpc":"2.0","id":data.get("id"),"result":result}
                elif data.get("method") == "mcp.list":
                    resp = {"jsonrpc":"2.0","id":data.get("id"),"result":reg.list_all()}
                else:
                    resp = {"jsonrpc":"2.0","id":data.get("id"),"error":{"code":-32601,"message":"Method not implemented"}}
                yield f"id: {eid}\n"
                yield f"data: {json.dumps(resp)}\n\n"
            r = Response(gen(), mimetype="text/event-stream")
            for k,v in headers.items(): r.headers[k]=v
            return r

        if data.get("method") == "mcp.call":
            p = data.get("params") or {}
            out = _call(p.get("kind"), p.get("name"), p.get("args") or {}, roles)
            resp = {"jsonrpc":"2.0","id":data.get("id"),"result":out}
        elif data.get("method") == "mcp.list":
            resp = {"jsonrpc":"2.0","id":data.get("id"),"result":reg.list_all()}
        else:
            resp = {"jsonrpc":"2.0","id":data.get("id"),"error":{"code":-32601,"message":"Method not implemented"}}
        r = jsonify(resp)
        for k,v in headers.items(): r.headers[k]=v
        return r

    @app.get("/mcp")
    def mcp_get():
        g = _guard()
        if g: return g
        def gen():
            yield "retry: 1500\n\n"
            eid = int(time.time()*1000)
            hello = {"event":"hello","spec":MCP_SPEC_VERSION,"version":"0.6.0"}
            yield f"id: {eid}\n"
            yield f"data: {json.dumps(hello)}\n\n"
        return Response(gen(), mimetype="text/event-stream")

    # Compat endpoints
    @app.get("/mcp/list")
    def mcp_list(): return jsonify(reg.list_all())

    @app.post("/mcp/call")
    def mcp_call():
        data = request.get_json(force=True) or {}
        roles = _caller_roles()
        return jsonify(_call(data.get("kind"), data.get("name"), data.get("args") or {}, roles))

    @app.post("/mcp/batch")
    def mcp_batch():
        payload = request.get_json(force=True) or []
        roles = _caller_roles()
        return jsonify([_call(x.get("kind"), x.get("name"), x.get("args") or {}, roles) for x in payload])

    # Minimal docs
    @app.get("/docs.json")
    def docs():
        return jsonify({"openapi":"3.1.0","info":{"title":"flask-mcp-server","version":"0.6.0"},
            "paths":{"\/mcp":{"post":{},"get":{}},"\/mcp/list":{"get":{}},"\/mcp/call":{"post":{}},"\/mcp/batch":{"post":{}}}})

    @app.get("/swagger")
    def swagger_ui():
        html = '<!doctype html><html><head><meta charset="utf-8"/><title>Swagger</title><link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"></head><body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script><script>window.ui=SwaggerUIBundle({url:"/docs.json",dom_id:"#swagger-ui"});</script></body></html>'
        return Response(html, mimetype="text/html")


    @app.get("/healthz")
    def healthz():
        return jsonify({"status":"ok","spec":MCP_SPEC_VERSION,"version":"0.6.0"})

    @app.get("/metrics")
    def metrics():
        # Minimal Prometheus text exposition
        body = "mcp_up 1\n"
        return Response(body, mimetype="text/plain; version=0.0.4")
    return app
