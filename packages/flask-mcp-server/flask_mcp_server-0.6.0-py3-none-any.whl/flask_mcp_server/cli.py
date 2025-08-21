from __future__ import annotations
import importlib, json, typer
from typing import Optional
from .server_http import create_app
from .server_stdio import stdio_serve
from .registry import MCPRegistry, default_registry

app = typer.Typer(help="flask-mcp-server CLI")

def _load_registry(module: Optional[str]) -> MCPRegistry:
    if not module:
        return default_registry
    mod, _, attr = module.partition(":")
    m = importlib.import_module(mod)
    reg = getattr(m, attr) if attr else getattr(m, "registry", default_registry)
    if not isinstance(reg, MCPRegistry):
        return default_registry
    return reg

@app.command("serve-http")
def serve_http(module: Optional[str] = typer.Option(None), host: str = typer.Option("127.0.0.1"), port: int = typer.Option(8765)):
    reg = _load_registry(module)
    app_flask = create_app(registry=reg)
    app_flask.run(host=host, port=port)

@app.command("serve-stdio")
def serve_stdio_cmd(module: Optional[str] = typer.Option(None)):
    reg = _load_registry(module)
    stdio_serve(registry=reg)

@app.command("list")
def list_(module: Optional[str] = typer.Option(None)):
    reg = _load_registry(module)
    print(json.dumps(reg.list_all(), ensure_ascii=False, indent=2))
