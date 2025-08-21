from __future__ import annotations
import sys, json
from .registry import MCPRegistry, default_registry

def _handle(reg, req):
    method = req.get("method")
    params = req.get("params") or {}
    if method == "mcp.list":
        return reg.list_all()
    if method == "mcp.batch":
        results = []
        for item in params.get("calls", []):
            results.append(_call(reg, item.get("kind"), item.get("name"), item.get("args") or {}))
        return results
    if method == "mcp.call":
        return _call(reg, params.get("kind"), params.get("name"), params.get("args") or {})
    raise ValueError("Unknown method")

def _call(reg, kind, name, args):
    if kind == "tool": return reg.call_tool(name, **args)
    if kind == "resource": return reg.get_resource(name, **args)
    if kind == "prompt": return reg.get_prompt(name, **args)
    if kind == "complete": return reg.complete(name, **args)
    raise ValueError("invalid kind")

def stdio_serve(registry: MCPRegistry = None):
    reg = registry or default_registry
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            req = json.loads(line)
            result = _handle(reg, req)
            resp = {"jsonrpc":"2.0","id":req.get("id"),"result":result}
        except Exception as e:
            resp = {"jsonrpc":"2.0","id":req.get("id"),"error":{"code":-32603,"message":str(e)}}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()
