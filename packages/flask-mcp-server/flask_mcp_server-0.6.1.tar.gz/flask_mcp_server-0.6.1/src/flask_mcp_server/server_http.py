"""
HTTP Server Implementation for Flask MCP Server.

This module provides the main HTTP server implementation for the Model Context
Protocol (MCP) using Flask. It includes comprehensive request handling, validation,
authentication, rate limiting, error handling, and protocol compliance.

The HTTP server supports:
- JSON-RPC 2.0 protocol compliance
- Server-Sent Events (SSE) for real-time communication
- Multiple authentication modes (none, API key, HMAC)
- Rate limiting with automatic cleanup
- Comprehensive input validation
- Role-based access control
- Health checks and metrics endpoints
- OpenAPI documentation generation
- Graceful error handling with proper HTTP status codes

Key Features:
- Thread-safe operations with proper error handling
- Automatic configuration validation on startup
- Comprehensive logging with structured output
- Memory management with automatic cleanup
- Security-first design with input validation
- Production-ready with monitoring endpoints

Example Usage:
    >>> from flask_mcp_server import MCPRegistry, create_app
    >>>
    >>> # Create registry and add tools
    >>> registry = MCPRegistry()
    >>>
    >>> @registry.tool("hello", "Say hello to someone")
    >>> def hello(name: str) -> str:
    ...     return f"Hello, {name}!"
    >>>
    >>> # Create and run the server
    >>> app = create_app(registry)
    >>> app.run(host='0.0.0.0', port=8080)

Environment Configuration:
    FLASK_MCP_AUTH_MODE: Authentication mode (none, apikey, hmac)
    FLASK_MCP_API_KEYS: API keys for authentication
    FLASK_MCP_HMAC_SECRET: Secret for HMAC authentication
    FLASK_MCP_RATE_LIMIT: Rate limiting rule (e.g., "100/hour")
    FLASK_MCP_RATE_SCOPE: Rate limiting scope (ip, key)
    FLASK_MCP_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
    FLASK_MCP_CORS_ORIGIN: CORS allowed origin
"""

from __future__ import annotations
import json
import time
import uuid
import os
import logging
from typing import Dict, Any, Optional, Tuple, List
from flask import Flask, request, jsonify, Response
from .registry import MCPRegistry, default_registry
from .security import (
    auth_mode, check_apikey, check_hmac_signature, parse_rate,
    api_key_roles, validate_environment_config
)
from .ratelimit import make_limiter
from .logging_utils import setup_logging
from .validation import (
    validate_json_request, validate_jsonrpc_request, validate_mcp_call_params,
    create_error_response
)
from .exceptions import (
    handle_exceptions, safe_execute, AuthenticationError, AuthorizationError,
    RateLimitError, ToolNotFoundError, ResourceNotFoundError,
    PromptNotFoundError, CompletionProviderNotFoundError, ToolExecutionError,
    create_jsonrpc_error_response
)
from .__version__ import get_version_info

logger = logging.getLogger(__name__)

ACCEPTED_PROTOCOLS = {"2025-06-18", "2025-03-26"}


def validate_startup_config():
    """
    Validate configuration on startup and log any issues.

    Raises:
        ValueError: If critical configuration errors are found
    """
    errors = validate_environment_config()
    if errors:
        logger.warning("Configuration validation errors found:")
        for var, error in errors.items():
            logger.warning(f"  {var}: {error}")

        # Check for critical errors that should prevent startup
        critical_errors = []
        auth_mode_val = auth_mode()

        if auth_mode_val == "apikey" and "FLASK_MCP_API_KEYS" in errors:
            critical_errors.append("API key authentication enabled but no keys configured")

        if auth_mode_val == "hmac" and "FLASK_MCP_HMAC_SECRET" in errors:
            critical_errors.append("HMAC authentication enabled but no secret configured")

        if critical_errors:
            raise ValueError(f"Critical configuration errors: {'; '.join(critical_errors)}")
    else:
        logger.info("Configuration validation passed")


def _origin_allowed():
    allowed = os.getenv("FLASK_MCP_ALLOWED_ORIGINS")
    if not allowed:
        return True
    origins = [o.strip() for o in allowed.split(",") if o.strip()]
    origin = request.headers.get("Origin")
    return (origin in origins) if origin else True


def create_app(registry: MCPRegistry = None) -> Flask:
    """
    Create a Flask application with MCP server functionality.

    Args:
        registry: Optional MCPRegistry instance. If None, uses default_registry.

    Returns:
        Configured Flask application

    Raises:
        ValueError: If critical configuration errors are found
    """
    # Validate configuration before starting
    validate_startup_config()

    reg = registry or default_registry
    app = Flask(__name__)
    setup_logging(app)

    # Initialize components with error handling
    try:
        limiter = make_limiter()
        rate_conf = parse_rate(os.getenv("FLASK_MCP_RATE_LIMIT", ""))
        rate_scope = os.getenv("FLASK_MCP_RATE_SCOPE", "ip")
    except Exception as e:
        logger.error(f"Failed to initialize server components: {e}")
        raise ValueError(f"Server initialization failed: {e}")

    logger.info(f"Starting MCP server with auth_mode={auth_mode()}, rate_limit={rate_conf}")

    # Get version info for responses
    version_info = get_version_info()

    def _client_key():
        if rate_scope == "key":
            auth = request.headers.get("Authorization", "")
            token = auth[7:] if auth.startswith("Bearer ") else None
            return request.headers.get("X-API-Key") or token or request.remote_addr
        return request.remote_addr

    def _caller_roles():
        k = request.headers.get("X-API-Key") or (
            request.headers.get("Authorization", "")[7:] if request.headers.get("Authorization", "").startswith(
                "Bearer ") else None)
        return api_key_roles(k)

    def _auth_check():
        """
        Check authentication based on configured auth mode.

        Returns:
            Tuple of (is_authenticated, error_message)

        Raises:
            AuthenticationError: If authentication fails
        """
        mode = auth_mode()
        if mode == "none":
            return True, None

        if mode == "apikey":
            # Extract API key from X-API-Key header or Authorization Bearer token
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                auth_header = request.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    api_key = auth_header[7:]

            if not api_key:
                logger.warning("API key authentication required but no key provided")
                raise AuthenticationError("API key required")

            if not check_apikey(api_key):
                logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
                raise AuthenticationError("Invalid API key")

            return True, None

        if mode == "hmac":
            secret = os.getenv("FLASK_MCP_HMAC_SECRET", "")
            if not secret:
                logger.error("HMAC authentication enabled but no secret configured")
                raise AuthenticationError("HMAC authentication misconfigured")

            raw_data = request.get_data() or b""
            signature = request.headers.get("X-Signature")

            if not signature:
                logger.warning("HMAC authentication required but no signature provided")
                raise AuthenticationError("HMAC signature required")

            if not check_hmac_signature(secret, raw_data, signature):
                logger.warning("Invalid HMAC signature attempted")
                raise AuthenticationError("Invalid HMAC signature")

            return True, None

        logger.error(f"Unsupported authentication mode: {mode}")
        raise AuthenticationError("Unsupported authentication mode")

    def _rl_check():
        """
        Check rate limiting for the current request.

        Returns:
            Tuple of (is_allowed, remaining_requests, window_seconds)

        Raises:
            RateLimitError: If rate limit is exceeded
        """
        if not rate_conf:
            return True, None, None

        limit, window = rate_conf
        client_key = _client_key()
        rate_key = f"rl:{client_key}:{window}"

        try:
            allowed, remaining = limiter.allow(rate_key, limit, window)
            if not allowed:
                logger.warning(f"Rate limit exceeded for {client_key}: {limit}/{window}s")
                raise RateLimitError(
                    f"Rate limit exceeded: {limit} requests per {window} seconds",
                    retry_after=window
                )

            if remaining < 5:  # Log when getting close to limit
                logger.info(f"Rate limit warning for {client_key}: {remaining} requests remaining")

            return True, remaining, window

        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Don't fail the request due to rate limiting errors
            return True, None, None

    def _guard():
        """
        Perform security checks for incoming requests.

        Returns:
            None if all checks pass, or Flask Response if any check fails
        """
        try:
            # Check protocol version
            protocol_version = request.headers.get("MCP-Protocol-Version")
            if protocol_version and protocol_version not in ACCEPTED_PROTOCOLS:
                logger.warning(f"Unsupported protocol version: {protocol_version}")
                return jsonify({
                    "error": "unsupported_protocol_version",
                    "message": f"Unsupported protocol version: {protocol_version}",
                    "supported_versions": list(ACCEPTED_PROTOCOLS)
                }), 400

            # Check origin if configured
            if not _origin_allowed():
                origin = request.headers.get("Origin", "unknown")
                logger.warning(f"Origin not allowed: {origin}")
                return jsonify({
                    "error": "origin_not_allowed",
                    "message": "Request origin is not allowed"
                }), 403

            # Check authentication
            _auth_check()  # Will raise exception if auth fails

            # Check rate limiting
            _rl_check()  # Will raise exception if rate limited

            return None

        except (AuthenticationError, AuthorizationError, RateLimitError) as e:
            # These are expected errors that should be returned to client
            return create_jsonrpc_error_response(e), e.status_code
        except Exception as e:
            # Unexpected errors should be logged but not expose details
            logger.error(f"Unexpected error in request guard: {e}")
            return jsonify({
                "error": "internal_error",
                "message": "An internal server error occurred"
            }), 500

    def _call(kind: str, name: str, args: dict, roles: list):
        """
        Execute a call to a registered tool, resource, prompt, or completion provider.

        Args:
            kind: Type of call ('tool', 'resource', 'prompt', 'complete')
            name: Name of the item to call
            args: Arguments to pass to the call
            roles: Caller roles for authorization

        Returns:
            Dictionary with call result or error information
        """
        try:
            if kind == "tool":
                result = safe_execute(reg.call_tool, name, caller_roles=roles, **args)
                return {"ok": True, "result": result}
            elif kind == "resource":
                result = safe_execute(reg.get_resource, name, caller_roles=roles, **args)
                return {"ok": True, "result": result}
            elif kind == "prompt":
                result = safe_execute(reg.get_prompt, name, caller_roles=roles, **args)
                return {"ok": True, "result": result}
            elif kind == "complete":
                result = safe_execute(reg.complete, name, caller_roles=roles, **args)
                return {"ok": True, "result": result}
            else:
                logger.warning(f"Invalid call kind: {kind}")
                return {"ok": False, "error": "invalid_kind", "message": f"Invalid kind: {kind}"}

        except (ToolNotFoundError, ResourceNotFoundError, PromptNotFoundError,
                CompletionProviderNotFoundError) as e:
            logger.warning(f"Item not found: {e.message}")
            return {"ok": False, "error": e.code, "message": e.message}
        except AuthorizationError as e:
            logger.warning(f"Authorization failed for {kind} '{name}': {e.message}")
            return {"ok": False, "error": "forbidden", "message": "Access forbidden"}
        except ToolExecutionError as e:
            logger.error(f"Tool execution failed for '{name}': {e.message}")
            return {"ok": False, "error": "execution_error", "message": "Tool execution failed"}
        except Exception as e:
            logger.error(f"Unexpected error calling {kind} '{name}': {e}")
            return {"ok": False, "error": "internal_error", "message": "Internal server error"}

    # Unified MCP endpoint
    @app.post("/mcp")
    @handle_exceptions
    def mcp_post():
        """
        Unified MCP endpoint for JSON-RPC requests.

        Supports both regular JSON responses and Server-Sent Events (SSE)
        based on the Accept header.
        """
        # Security checks
        guard_result = _guard()
        if guard_result:
            return guard_result

        # Get caller roles for authorization
        roles = _caller_roles()

        # Validate and parse JSON request
        try:
            data = validate_json_request()
            jsonrpc_request = validate_jsonrpc_request(data)
        except Exception as e:
            logger.warning(f"Request validation failed: {e}")
            return create_error_response(e)

        # Prepare response headers
        headers = {}
        if jsonrpc_request.method == "initialize":
            session_id = uuid.uuid4().hex
            headers["Mcp-Session-Id"] = session_id
            logger.info(f"New session initialized: {session_id}")

        # Check if client wants Server-Sent Events
        accept_header = request.headers.get("Accept", "")
        wants_sse = "text/event-stream" in accept_header

        if wants_sse:
            def generate_sse():
                """Generate Server-Sent Events response."""
                yield "retry: 1500\n\n"
                event_id = int(time.time() * 1000)

                try:
                    if jsonrpc_request.method == "mcp.call":
                        # Validate MCP call parameters
                        call_params = validate_mcp_call_params(jsonrpc_request.params)
                        result = _call(call_params.kind, call_params.name, call_params.args, roles)
                        response_data = {"jsonrpc": "2.0", "id": jsonrpc_request.id, "result": result}

                    elif jsonrpc_request.method == "mcp.list":
                        registry_data = reg.list_all()
                        response_data = {"jsonrpc": "2.0", "id": jsonrpc_request.id, "result": registry_data}

                    else:
                        logger.warning(f"Unsupported method in SSE: {jsonrpc_request.method}")
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": jsonrpc_request.id,
                            "error": {
                                "code": -32601,
                                "message": f"Method '{jsonrpc_request.method}' not implemented"
                            }
                        }

                except Exception as e:
                    logger.error(f"Error processing SSE request: {e}")
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": jsonrpc_request.id,
                        "error": {"code": -32603, "message": "Internal error"}
                    }

                yield f"id: {event_id}\n"
                yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"

            response = Response(generate_sse(), mimetype="text/event-stream")
            response.headers.update(headers)
            return response

        # Handle regular JSON response
        try:
            if jsonrpc_request.method == "mcp.call":
                # Validate MCP call parameters
                call_params = validate_mcp_call_params(jsonrpc_request.params)
                result = _call(call_params.kind, call_params.name, call_params.args, roles)
                response_data = {"jsonrpc": "2.0", "id": jsonrpc_request.id, "result": result}

            elif jsonrpc_request.method == "mcp.list":
                registry_data = reg.list_all()
                response_data = {"jsonrpc": "2.0", "id": jsonrpc_request.id, "result": registry_data}

            elif jsonrpc_request.method == "initialize":
                # Return server capabilities and version info
                capabilities = {
                    "capabilities": {
                        "tools": True,
                        "resources": True,
                        "prompts": True,
                        "completions": True
                    },
                    "serverInfo": {
                        "name": "flask-mcp-server",
                        "version": version_info["package_version"]
                    },
                    "protocolVersion": version_info["mcp_spec_version"]
                }
                response_data = {"jsonrpc": "2.0", "id": jsonrpc_request.id, "result": capabilities}

            else:
                logger.warning(f"Unsupported method: {jsonrpc_request.method}")
                response_data = {
                    "jsonrpc": "2.0",
                    "id": jsonrpc_request.id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{jsonrpc_request.method}' not implemented"
                    }
                }

        except Exception as e:
            logger.error(f"Error processing JSON-RPC request: {e}")
            response_data = {
                "jsonrpc": "2.0",
                "id": jsonrpc_request.id,
                "error": {"code": -32603, "message": "Internal error"}
            }

        response = jsonify(response_data)
        response.headers.update(headers)
        return response

    @app.get("/mcp")
    @handle_exceptions
    def mcp_get():
        """
        MCP endpoint for Server-Sent Events.

        Opens an SSE stream and sends a hello event with server information.
        """
        # Security checks
        guard_result = _guard()
        if guard_result:
            return guard_result

        def generate_hello_sse():
            """Generate SSE hello event."""
            yield "retry: 1500\n\n"
            event_id = int(time.time() * 1000)

            hello_data = {
                "event": "hello",
                "serverInfo": {
                    "name": "flask-mcp-server",
                    "version": version_info["package_version"]
                },
                "protocolVersion": version_info["mcp_spec_version"],
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": True,
                    "completions": True
                }
            }

            yield f"id: {event_id}\n"
            yield f"data: {json.dumps(hello_data, ensure_ascii=False)}\n\n"

        return Response(generate_hello_sse(), mimetype="text/event-stream")

    # Legacy compatibility endpoints
    @app.get("/mcp/list")
    @handle_exceptions
    def mcp_list():
        """Legacy endpoint for listing registry contents."""
        # Apply same security checks as main endpoint
        guard_result = _guard()
        if guard_result:
            return guard_result

        return jsonify(reg.list_all())

    @app.post("/mcp/call")
    @handle_exceptions
    def mcp_call():
        """Legacy endpoint for calling tools/resources."""
        # Apply same security checks as main endpoint
        guard_result = _guard()
        if guard_result:
            return guard_result

        # Validate JSON input
        try:
            data = validate_json_request()
        except Exception as e:
            return create_error_response(e)

        roles = _caller_roles()
        kind = data.get("kind")
        name = data.get("name")
        args = data.get("args", {})

        if not kind or not name:
            return jsonify({
                "ok": False,
                "error": "missing_parameters",
                "message": "Both 'kind' and 'name' parameters are required"
            }), 400

        result = _call(kind, name, args, roles)
        return jsonify(result)

    @app.post("/mcp/batch")
    @handle_exceptions
    def mcp_batch():
        """Legacy endpoint for batch calls."""
        # Apply same security checks as main endpoint
        guard_result = _guard()
        if guard_result:
            return guard_result

        # Validate JSON input
        try:
            data = validate_json_request()
        except Exception as e:
            return create_error_response(e)

        if not isinstance(data, list):
            return jsonify({
                "error": "invalid_format",
                "message": "Batch request must be an array"
            }), 400

        roles = _caller_roles()
        results = []

        for i, item in enumerate(data):
            if not isinstance(item, dict):
                results.append({
                    "ok": False,
                    "error": "invalid_item",
                    "message": f"Item {i} is not an object"
                })
                continue

            kind = item.get("kind")
            name = item.get("name")
            args = item.get("args", {})

            if not kind or not name:
                results.append({
                    "ok": False,
                    "error": "missing_parameters",
                    "message": f"Item {i} missing 'kind' or 'name'"
                })
                continue

            result = _call(kind, name, args, roles)
            results.append(result)

        return jsonify(results)

    # OpenAPI documentation
    @app.get("/docs.json")
    def docs():
        """Generate OpenAPI 3.1 specification from registered tools and resources."""
        try:
            openapi_spec = _generate_openapi_spec(reg, version_info)
            return jsonify(openapi_spec)
        except Exception as e:
            logger.error(f"Error generating OpenAPI spec: {e}")
            # Return minimal spec as fallback
            return jsonify({
                "openapi": "3.1.0",
                "info": {
                    "title": "flask-mcp-server",
                    "version": version_info["package_version"],
                    "description": "Model Context Protocol (MCP) server"
                },
                "paths": {
                    "/mcp": {"post": {"summary": "Unified MCP endpoint"}, "get": {"summary": "SSE endpoint"}},
                    "/mcp/list": {"get": {"summary": "List registry (legacy)"}},
                    "/mcp/call": {"post": {"summary": "Call tool/resource (legacy)"}},
                    "/mcp/batch": {"post": {"summary": "Batch calls (legacy)"}}
                }
            })

    @app.get("/swagger")
    def swagger_ui():
        """Serve Swagger UI for API documentation."""
        html = '''<!doctype html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Flask MCP Server API Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <script>
        window.ui = SwaggerUIBundle({
            url: "/docs.json",
            dom_id: "#swagger-ui",
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ]
        });
    </script>
</body>
</html>'''
        return Response(html, mimetype="text/html")

    @app.get("/healthz")
    def healthz():
        """Health check endpoint."""
        try:
            # Basic health checks
            registry_size = len(reg.tools) + len(reg.resources) + len(reg.prompts) + len(reg.completions)

            health_data = {
                "status": "ok",
                "timestamp": int(time.time()),
                "version": version_info["package_version"],
                "mcp_spec_version": version_info["mcp_spec_version"],
                "registry": {
                    "total_items": registry_size,
                    "tools": len(reg.tools),
                    "resources": len(reg.resources),
                    "prompts": len(reg.prompts),
                    "completions": len(reg.completions)
                }
            }

            return jsonify(health_data)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "status": "error",
                "timestamp": int(time.time()),
                "error": "Health check failed"
            }), 500

    @app.get("/metrics")
    def metrics():
        """Prometheus metrics endpoint."""
        try:
            # Collect basic metrics
            registry_size = len(reg.tools) + len(reg.resources) + len(reg.prompts) + len(reg.completions)

            metrics_text = f"""# HELP mcp_up Server is up and running
# TYPE mcp_up gauge
mcp_up 1

# HELP mcp_registry_items_total Total number of items in registry
# TYPE mcp_registry_items_total gauge
mcp_registry_items_total {registry_size}

# HELP mcp_tools_total Number of registered tools
# TYPE mcp_tools_total gauge
mcp_tools_total {len(reg.tools)}

# HELP mcp_resources_total Number of registered resources
# TYPE mcp_resources_total gauge
mcp_resources_total {len(reg.resources)}

# HELP mcp_prompts_total Number of registered prompts
# TYPE mcp_prompts_total gauge
mcp_prompts_total {len(reg.prompts)}

# HELP mcp_completions_total Number of registered completion providers
# TYPE mcp_completions_total gauge
mcp_completions_total {len(reg.completions)}
"""

            return Response(metrics_text, mimetype="text/plain; version=0.0.4")
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return Response("# Error collecting metrics\n", mimetype="text/plain"), 500

    return app


def _generate_openapi_spec(registry: MCPRegistry, version_info: dict) -> dict:
    """
    Generate OpenAPI 3.1 specification from registry contents.

    Args:
        registry: MCPRegistry instance
        version_info: Version information dictionary

    Returns:
        OpenAPI specification dictionary
    """
    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "Flask MCP Server",
            "version": version_info["package_version"],
            "description": "Model Context Protocol (MCP) server providing tools, resources, prompts, and completions",
            "contact": {
                "name": "Flask MCP Server",
                "url": "https://github.com/bashar94/flask-mcp-server"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "/",
                "description": "Local server"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {
                "JSONRPCRequest": {
                    "type": "object",
                    "required": ["jsonrpc", "method"],
                    "properties": {
                        "jsonrpc": {"type": "string", "enum": ["2.0"]},
                        "id": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
                        "method": {"type": "string"},
                        "params": {"type": "object"}
                    }
                },
                "JSONRPCResponse": {
                    "type": "object",
                    "required": ["jsonrpc", "id"],
                    "properties": {
                        "jsonrpc": {"type": "string", "enum": ["2.0"]},
                        "id": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
                        "result": {},
                        "error": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "integer"},
                                "message": {"type": "string"},
                                "data": {}
                            }
                        }
                    }
                }
            }
        }
    }

    # Add main MCP endpoints
    spec["paths"]["/mcp"] = {
        "post": {
            "summary": "Unified MCP JSON-RPC endpoint",
            "description": "Main endpoint for JSON-RPC requests. Supports both JSON and SSE responses.",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/JSONRPCRequest"}
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/JSONRPCResponse"}
                        },
                        "text/event-stream": {
                            "schema": {"type": "string"}
                        }
                    }
                }
            }
        },
        "get": {
            "summary": "Server-Sent Events endpoint",
            "description": "Opens SSE stream for server events",
            "responses": {
                "200": {
                    "description": "SSE stream",
                    "content": {
                        "text/event-stream": {
                            "schema": {"type": "string"}
                        }
                    }
                }
            }
        }
    }

    # Add legacy endpoints
    spec["paths"]["/mcp/list"] = {
        "get": {
            "summary": "List registry contents (legacy)",
            "responses": {
                "200": {
                    "description": "Registry contents",
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
            }
        }
    }

    # Add utility endpoints
    spec["paths"]["/healthz"] = {
        "get": {
            "summary": "Health check",
            "responses": {
                "200": {
                    "description": "Server health status",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "version": {"type": "string"},
                                    "timestamp": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return spec
