"""
HTTP Integration Module for Flask MCP Server.

This module provides functionality to mount MCP endpoints on existing Flask
applications as a Blueprint. It includes middleware support, authentication,
rate limiting, CORS handling, and both JSON-RPC and Server-Sent Events (SSE)
support.

The integration module is designed for applications that want to add MCP
capabilities to an existing Flask application without creating a new server.
It provides a flexible middleware system and comprehensive protocol support.

Features:
- Blueprint-based integration with existing Flask apps
- Middleware system for custom request processing
- Multiple authentication modes (none, API key, HMAC)
- Rate limiting with configurable scopes
- CORS support for browser-based clients
- Server-Sent Events (SSE) for real-time communication
- JSON-RPC 2.0 protocol compliance
- Backward compatibility routes

Example Usage:
    >>> from flask import Flask
    >>> from flask_mcp_server import MCPRegistry, mount_mcp
    >>>
    >>> app = Flask(__name__)
    >>> registry = MCPRegistry()
    >>>
    >>> # Add some tools to the registry
    >>> @registry.tool("hello", "Say hello")
    >>> def hello(name: str) -> str:
    ...     return f"Hello, {name}!"
    >>>
    >>> # Mount MCP endpoints on the existing app
    >>> blueprint, middleware_manager, registry = mount_mcp(
    ...     app, registry, url_prefix="/api/mcp"
    ... )
    >>>
    >>> app.run()
"""

from __future__ import annotations
from typing import Callable, List, Dict, Any, Optional
import json
import time
import uuid
import os
import logging
from flask import Blueprint, request, jsonify, Response
from .registry import MCPRegistry, default_registry
from .security import auth_mode, check_apikey, check_hmac_signature, parse_rate, api_key_roles
from .ratelimit import make_limiter
from .spec import MCP_SPEC_VERSION

# Set up logging for HTTP integration
logger = logging.getLogger(__name__)

# Type alias for middleware functions
# Middleware functions receive a context dict and a next function, and return a Response
Middleware = Callable[[Dict[str, Any], Callable[[], Response]], Response]


class MiddlewareManager:
    """
    Manages middleware execution for MCP HTTP endpoints.

    This class implements a middleware chain pattern where each middleware
    can process the request, call the next middleware in the chain, and
    process the response. Middleware can modify the request context,
    short-circuit the chain, or modify the response.

    The middleware system is inspired by Express.js middleware and provides
    a flexible way to add cross-cutting concerns like authentication,
    logging, rate limiting, etc.
    """

    def __init__(self, middlewares: Optional[List[Middleware]] = None):
        """
        Initialize the middleware manager.

        Args:
            middlewares: List of middleware functions to execute in order
        """
        # Create a copy of the middleware list to avoid external modifications
        self.middlewares = middlewares[:] if middlewares else []
        logger.debug(f"Initialized middleware manager with {len(self.middlewares)} middlewares")

    def add(self, middleware: Middleware) -> None:
        """
        Add a middleware function to the end of the chain.

        Args:
            middleware: Middleware function to add

        Example:
            >>> def logging_middleware(ctx, next_fn):
            ...     print(f"Request: {ctx}")
            ...     response = next_fn()
            ...     print(f"Response: {response.status_code}")
            ...     return response
            >>>
            >>> manager.add(logging_middleware)
        """
        self.middlewares.append(middleware)
        logger.debug(f"Added middleware, total count: {len(self.middlewares)}")

    def wrap(self, handler: Callable[[Dict[str, Any]], Response]) -> Callable[[Dict[str, Any]], Response]:
        """
        Wrap a handler function with the middleware chain.

        This method creates a new function that executes all middlewares
        in order before calling the final handler. Each middleware can
        choose to call the next function in the chain or short-circuit.

        Args:
            handler: Final handler function to wrap

        Returns:
            Wrapped handler function that executes the middleware chain

        Example:
            >>> def my_handler(ctx):
            ...     return jsonify({"message": "Hello"})
            >>>
            >>> wrapped_handler = manager.wrap(my_handler)
            >>> response = wrapped_handler({"request_id": "123"})
        """
        def wrapped_call(context: Dict[str, Any]) -> Response:
            """Execute the middleware chain and final handler."""
            middleware_index = -1

            def next_function() -> Response:
                """Call the next middleware or final handler in the chain."""
                nonlocal middleware_index
                middleware_index += 1

                # If we've executed all middlewares, call the final handler
                if middleware_index >= len(self.middlewares):
                    logger.debug("Executing final handler")
                    return handler(context)

                # Execute the next middleware in the chain
                current_middleware = self.middlewares[middleware_index]
                logger.debug(f"Executing middleware {middleware_index + 1}/{len(self.middlewares)}")

                try:
                    return current_middleware(context, next_function)
                except Exception as e:
                    logger.error(f"Middleware {middleware_index} failed: {e}")
                    # Re-raise the exception to be handled by Flask's error handlers
                    raise

            return next_function()

        return wrapped_call


def _origin_ok() -> bool:
    """
    Check if the request origin is allowed based on CORS configuration.

    This function validates the Origin header against a list of allowed
    origins configured via environment variables. If no origins are
    configured, all origins are allowed.

    Returns:
        True if the origin is allowed, False otherwise

    Environment Variables:
        FLASK_MCP_ALLOWED_ORIGINS: Comma-separated list of allowed origins

    Example:
        >>> os.environ['FLASK_MCP_ALLOWED_ORIGINS'] = 'https://example.com,https://app.example.com'
        >>> # Request with Origin: https://example.com -> True
        >>> # Request with Origin: https://evil.com -> False
        >>> # Request with no Origin header -> True (for non-browser clients)
    """
    # Get allowed origins from environment
    allowed_origins_env = os.getenv("FLASK_MCP_ALLOWED_ORIGINS")

    # If no origins configured, allow all
    if not allowed_origins_env:
        return True

    # Parse comma-separated list of allowed origins
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

    # Get the Origin header from the request
    request_origin = request.headers.get("Origin")

    # If no Origin header (non-browser clients), allow the request
    if not request_origin:
        return True

    # Check if the request origin is in the allowed list
    is_allowed = request_origin in allowed_origins

    if not is_allowed:
        logger.warning(f"Origin not allowed: {request_origin}, allowed: {allowed_origins}")

    return is_allowed


def mw_auth(ctx: Dict[str, Any], next_fn: Callable[[], Response]) -> Response:
    """
    Authentication middleware for MCP endpoints.

    This middleware enforces authentication based on the configured auth mode.
    It supports multiple authentication methods and validates credentials
    before allowing requests to proceed.

    Args:
        ctx: Request context dictionary
        next_fn: Function to call next middleware or handler

    Returns:
        Response object (either error response or result from next_fn)

    Authentication Modes:
        - none: No authentication required
        - apikey: API key authentication via X-API-Key header or Authorization Bearer
        - hmac: HMAC signature authentication via X-Signature header

    Environment Variables:
        FLASK_MCP_AUTH_MODE: Authentication mode (none, apikey, hmac)
        FLASK_MCP_HMAC_SECRET: Secret key for HMAC authentication
    """
    # Get the configured authentication mode
    mode = auth_mode()
    logger.debug(f"Authentication mode: {mode}")

    # No authentication required
    if mode == "none":
        return next_fn()

    # API key authentication
    elif mode == "apikey":
        # Try to get API key from X-API-Key header or Authorization Bearer token
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            # Try Authorization header with Bearer token
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                api_key = auth_header[7:]  # Remove "Bearer " prefix

        # Validate the API key
        if not check_apikey(api_key):
            logger.warning(f"Invalid API key authentication attempt from {request.remote_addr}")
            return jsonify({"error": "invalid_api_key"}), 401

        logger.debug("API key authentication successful")
        return next_fn()

    # HMAC signature authentication
    elif mode == "hmac":
        # Get HMAC secret from environment
        secret = os.getenv("FLASK_MCP_HMAC_SECRET", "")

        # Get request body for signature verification
        request_body = request.get_data() or b""

        # Get signature from header
        signature = request.headers.get("X-Signature")

        # Validate HMAC signature
        if not check_hmac_signature(secret, request_body, signature):
            logger.warning(f"Invalid HMAC signature authentication attempt from {request.remote_addr}")
            return jsonify({"error": "invalid_signature"}), 401

        logger.debug("HMAC signature authentication successful")
        return next_fn()

    # Unsupported authentication mode
    else:
        logger.error(f"Unsupported authentication mode: {mode}")
        return jsonify({"error": "auth_mode_not_supported"}), 401


def mw_ratelimit(ctx: Dict[str, Any], next_fn: Callable[[], Response]) -> Response:
    """
    Rate limiting middleware for MCP endpoints.

    This middleware enforces rate limits based on configured rules and scopes.
    It can limit requests per IP address or per API key, with configurable
    time windows and request counts.

    Args:
        ctx: Request context dictionary
        next_fn: Function to call next middleware or handler

    Returns:
        Response object (either rate limit error or result from next_fn)

    Environment Variables:
        FLASK_MCP_RATE_LIMIT: Rate limit rule (e.g., "100/hour", "10/minute")
        FLASK_MCP_RATE_SCOPE: Rate limiting scope ("ip" or "key")

    Rate Limit Scopes:
        - ip: Limit by client IP address
        - key: Limit by API key (falls back to IP if no key)

    Example:
        >>> os.environ['FLASK_MCP_RATE_LIMIT'] = '100/hour'
        >>> os.environ['FLASK_MCP_RATE_SCOPE'] = 'key'
        >>> # Allows 100 requests per hour per API key
    """
    # Get rate limit configuration from environment
    rate_rule = os.getenv("FLASK_MCP_RATE_LIMIT", "")
    rate_config = parse_rate(rate_rule)

    # If no rate limit configured, skip rate limiting
    if not rate_config:
        return next_fn()

    limit, window = rate_config
    logger.debug(f"Rate limiting: {limit} requests per {window} seconds")

    # Determine rate limiting scope
    scope = os.getenv("FLASK_MCP_RATE_SCOPE", "ip")

    # Default to client IP address
    client_identifier = request.remote_addr

    # If scope is "key", try to use API key as identifier
    if scope == "key":
        # Try to get API key from headers
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            # Try Authorization header with Bearer token
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                api_key = auth_header[7:]  # Remove "Bearer " prefix

        # Use API key if available, otherwise fall back to IP
        client_identifier = api_key or request.remote_addr
        logger.debug(f"Rate limiting by key: {client_identifier[:8]}..." if api_key else f"Rate limiting by IP: {client_identifier}")
    else:
        logger.debug(f"Rate limiting by IP: {client_identifier}")

    # Create rate limiter and check if request is allowed
    limiter = make_limiter()
    rate_key = f"rl:{client_identifier}:{window}"

    is_allowed, remaining_requests = limiter.allow(rate_key, limit, window)

    if not is_allowed:
        logger.warning(f"Rate limit exceeded for {client_identifier}: {limit} requests per {window}s")
        return jsonify({
            "error": "rate_limited",
            "message": f"Rate limit exceeded: {limit} requests per {window} seconds",
            "retry_after": window,
            "remaining": 0
        }), 429

    logger.debug(f"Rate limit check passed for {client_identifier}: {remaining_requests} remaining")

    # Add rate limit info to response headers (will be set by next middleware/handler)
    ctx["rate_limit_remaining"] = remaining_requests
    ctx["rate_limit_limit"] = limit
    ctx["rate_limit_window"] = window

    return next_fn()


def mw_cors(ctx: Dict[str, Any], next_fn: Callable[[], Response]) -> Response:
    """
    CORS (Cross-Origin Resource Sharing) middleware for MCP endpoints.

    This middleware adds CORS headers to responses to enable browser-based
    clients to access the MCP server from different origins. It configures
    the necessary headers for preflight requests and actual requests.

    Args:
        ctx: Request context dictionary
        next_fn: Function to call next middleware or handler

    Returns:
        Response object with CORS headers added

    Environment Variables:
        FLASK_MCP_CORS_ORIGIN: Allowed origin for CORS (default: "*")

    CORS Headers Added:
        - Access-Control-Allow-Origin: Specifies allowed origins
        - Access-Control-Allow-Headers: Specifies allowed request headers
        - Access-Control-Allow-Methods: Specifies allowed HTTP methods

    Example:
        >>> os.environ['FLASK_MCP_CORS_ORIGIN'] = 'https://myapp.example.com'
        >>> # Only allows requests from https://myapp.example.com
    """
    # Execute the next middleware/handler first
    response = next_fn()

    try:
        # Set CORS headers on the response

        # Allow origin (configurable via environment variable)
        allowed_origin = os.getenv("FLASK_MCP_CORS_ORIGIN", "*")
        response.headers["Access-Control-Allow-Origin"] = allowed_origin

        # Allow specific headers that MCP clients might send
        allowed_headers = [
            "Content-Type",           # For JSON requests
            "Authorization",          # For Bearer token authentication
            "X-API-Key",             # For API key authentication
            "X-Signature",           # For HMAC authentication
            "MCP-Protocol-Version",  # MCP protocol version header
            "Mcp-Session-Id"         # MCP session identifier
        ]
        response.headers["Access-Control-Allow-Headers"] = ", ".join(allowed_headers)

        # Allow specific HTTP methods used by MCP
        allowed_methods = ["GET", "POST", "OPTIONS"]
        response.headers["Access-Control-Allow-Methods"] = ", ".join(allowed_methods)

        # Optionally expose custom headers to the client
        exposed_headers = [
            "Mcp-Session-Id",        # Session ID for client tracking
            "X-RateLimit-Remaining", # Rate limit information
            "X-RateLimit-Limit",     # Rate limit information
            "X-RateLimit-Reset"      # Rate limit information
        ]
        response.headers["Access-Control-Expose-Headers"] = ", ".join(exposed_headers)

        # Set max age for preflight cache (24 hours)
        response.headers["Access-Control-Max-Age"] = "86400"

        logger.debug(f"Added CORS headers with origin: {allowed_origin}")

    except Exception as e:
        # Don't fail the request if CORS header setting fails
        logger.warning(f"Failed to set CORS headers: {e}")

    return response


def mount_mcp(
    app,
    registry: Optional[MCPRegistry] = None,
    url_prefix: str = "/mcp",
    middlewares: Optional[List[Middleware]] = None
):
    """
    Mount MCP endpoints on an existing Flask application.

    This function creates a Flask Blueprint with MCP endpoints and registers it
    with the provided Flask application. It supports both JSON-RPC and Server-Sent
    Events (SSE) protocols, along with authentication, rate limiting, and CORS.

    Args:
        app: Flask application instance to mount MCP endpoints on
        registry: MCP registry containing tools, resources, prompts, and completions
                 (defaults to the global default_registry)
        url_prefix: URL prefix for MCP endpoints (default: "/mcp")
        middlewares: List of middleware functions to apply to requests

    Returns:
        Tuple of (blueprint, middleware_manager, registry) for further customization

    Endpoints Created:
        - POST {url_prefix}/: Main MCP endpoint (JSON-RPC and SSE)
        - GET {url_prefix}/: SSE hello endpoint
        - GET {url_prefix}/list: List all registered items (compatibility)
        - POST {url_prefix}/call: Call a single item (compatibility)
        - POST {url_prefix}/batch: Call multiple items (compatibility)

    Protocols Supported:
        - JSON-RPC 2.0: Standard request/response protocol
        - Server-Sent Events (SSE): Real-time streaming protocol

    Features:
        - Authentication (none, API key, HMAC)
        - Rate limiting with configurable scopes
        - CORS support for browser clients
        - Role-based access control
        - Session management
        - Error handling and logging

    Example:
        >>> from flask import Flask
        >>> from flask_mcp_server import MCPRegistry, mount_mcp
        >>>
        >>> app = Flask(__name__)
        >>> registry = MCPRegistry()
        >>>
        >>> @registry.tool("hello", "Say hello")
        >>> def hello(name: str) -> str:
        ...     return f"Hello, {name}!"
        >>>
        >>> blueprint, middleware_manager, registry = mount_mcp(
        ...     app, registry, url_prefix="/api/mcp"
        ... )
        >>>
        >>> # Add custom middleware
        >>> def logging_middleware(ctx, next_fn):
        ...     print(f"Request to {request.path}")
        ...     return next_fn()
        >>>
        >>> middleware_manager.add(logging_middleware)
        >>>
        >>> app.run()
    """
    reg = registry or default_registry
    bp = Blueprint("mcp", __name__)
    mm = MiddlewareManager(middlewares)

    def _roles():
        k = request.headers.get("X-API-Key") or (
            request.headers.get("Authorization", "")[7:] if request.headers.get("Authorization", "").startswith(
                "Bearer ") else None)
        return api_key_roles(k)

    def _call(kind, name, args):
        roles = _roles()
        try:
            if kind == "tool": return {"ok": True, "result": reg.call_tool(name, caller_roles=roles, **(args or {}))}
            if kind == "resource": return {"ok": True,
                                           "result": reg.get_resource(name, caller_roles=roles, **(args or {}))}
            if kind == "prompt": return {"ok": True, "result": reg.get_prompt(name, caller_roles=roles, **(args or {}))}
            if kind == "complete": return {"ok": True, "result": reg.complete(name, caller_roles=roles, **(args or {}))}
            return {"ok": False, "error": "invalid kind"}
        except PermissionError:
            return {"ok": False, "error": "forbidden"}

    @bp.post("")
    def mcp_root_post():
        if not _origin_ok(): return jsonify({"error": "origin_not_allowed"}), 403
        data = request.get_json(force=True) or {}
        accept = (request.headers.get("Accept") or "")

        headers = {}
        if data.get("method") == "initialize":
            headers["Mcp-Session-Id"] = uuid.uuid4().hex

        if "text/event-stream" in accept:
            def gen():
                yield "retry: 1500\n\n"
                eid = int(time.time() * 1000)
                if data.get("method") == "mcp.call":
                    p = data.get("params") or {}
                    res = _call(p.get("kind"), p.get("name"), p.get("args"))
                    payload = {"jsonrpc": "2.0", "id": data.get("id"), "result": res}
                elif data.get("method") == "mcp.list":
                    payload = {"jsonrpc": "2.0", "id": data.get("id"), "result": reg.list_all()}
                else:
                    payload = {"jsonrpc": "2.0", "id": data.get("id"),
                               "error": {"code": -32601, "message": "Method not implemented"}}
                yield f"id: {eid}\n"
                yield f"data: {json.dumps(payload)}\n\n"

            resp = Response(gen(), mimetype="text/event-stream")
            for k, v in headers.items(): resp.headers[k] = v
            return resp

        if data.get("method") == "mcp.call":
            p = data.get("params") or {}
            out = _call(p.get("kind"), p.get("name"), p.get("args"))
            resp = {"jsonrpc": "2.0", "id": data.get("id"), "result": out}
        elif data.get("method") == "mcp.list":
            resp = {"jsonrpc": "2.0", "id": data.get("id"), "result": reg.list_all()}
        else:
            resp = {"jsonrpc": "2.0", "id": data.get("id"),
                    "error": {"code": -32601, "message": "Method not implemented"}}
        r = jsonify(resp);
        [r.headers.__setitem__(k, v) for k, v in headers.items()]
        return r

    @bp.get("")
    def mcp_root_get():
        if not _origin_ok(): return jsonify({"error": "origin_not_allowed"}), 403

        def gen():
            yield "retry: 1500\n\n"
            eid = int(time.time() * 1000)
            hello = {"event": "hello", "spec": MCP_SPEC_VERSION, "version": "0.6.1"}
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
