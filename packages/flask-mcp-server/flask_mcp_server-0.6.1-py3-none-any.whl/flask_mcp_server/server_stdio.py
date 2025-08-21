"""
STDIO-based MCP Server for Flask MCP Server.

This module provides a STDIO (standard input/output) based implementation of
the Model Context Protocol (MCP) server. This mode is typically used when the
MCP server is launched as a subprocess by an MCP client, with communication
happening over stdin/stdout pipes.

The STDIO server:
- Reads JSON-RPC requests from stdin (one per line)
- Processes requests using the MCP registry
- Writes JSON-RPC responses to stdout (one per line)
- Supports the same MCP protocol as the HTTP server
- Is suitable for process-based communication patterns

This implementation is useful for:
- Integration with MCP clients that prefer subprocess communication
- Command-line tools and scripts
- Environments where HTTP servers are not suitable
- Testing and development workflows

Example Usage:
    >>> from flask_mcp_server import MCPRegistry, stdio_serve
    >>>
    >>> # Create and populate registry
    >>> registry = MCPRegistry()
    >>>
    >>> @registry.tool("echo", "Echo the input")
    >>> def echo_tool(message: str) -> str:
    ...     return message
    >>>
    >>> # Start STDIO server (blocks until stdin is closed)
    >>> stdio_serve(registry)

Protocol Format:
    Input (stdin):  {"jsonrpc": "2.0", "id": 1, "method": "mcp.call", "params": {...}}
    Output (stdout): {"jsonrpc": "2.0", "id": 1, "result": {...}}
    Error (stdout):  {"jsonrpc": "2.0", "id": 1, "error": {"code": -32603, "message": "..."}}
"""

from __future__ import annotations
import sys
import json
import logging
from typing import Dict, Any, Optional, Union
from .registry import MCPRegistry, default_registry
from .exceptions import (
    safe_execute, ToolNotFoundError, ResourceNotFoundError,
    PromptNotFoundError, CompletionProviderNotFoundError
)

# Set up logging for STDIO server (log to stderr to avoid interfering with protocol)
logger = logging.getLogger(__name__)


def _handle_request(registry: MCPRegistry, request: Dict[str, Any]) -> Any:
    """
    Handle a JSON-RPC request and return the result.

    This function processes MCP protocol requests and delegates to the
    appropriate registry methods based on the request method.

    Args:
        registry: MCP registry containing tools, resources, prompts, and completions
        request: JSON-RPC request dictionary

    Returns:
        Result data to be included in the JSON-RPC response

    Raises:
        ValueError: If the method is unknown or invalid

    Supported Methods:
        - mcp.list: List all registered items
        - mcp.call: Call a specific tool, resource, prompt, or completion
        - mcp.batch: Execute multiple calls in a single request
    """
    method = request.get("method")
    params = request.get("params") or {}

    logger.debug(f"Handling request: method={method}")

    if method == "mcp.list":
        # Return all registered items
        result = registry.list_all()
        logger.debug(f"Listed {sum(len(v) for v in result.values())} total items")
        return result

    elif method == "mcp.call":
        # Execute a single call
        kind = params.get("kind")
        name = params.get("name")
        args = params.get("args") or {}

        if not kind or not name:
            raise ValueError("mcp.call requires 'kind' and 'name' parameters")

        logger.debug(f"Executing call: kind={kind}, name={name}")
        return _execute_call(registry, kind, name, args)

    elif method == "mcp.batch":
        # Execute multiple calls
        calls = params.get("calls", [])
        if not isinstance(calls, list):
            raise ValueError("mcp.batch requires 'calls' parameter as a list")

        logger.debug(f"Executing batch with {len(calls)} calls")
        results = []

        for i, call_item in enumerate(calls):
            try:
                kind = call_item.get("kind")
                name = call_item.get("name")
                args = call_item.get("args") or {}

                if not kind or not name:
                    results.append({
                        "ok": False,
                        "error": f"Batch item {i}: missing 'kind' or 'name'"
                    })
                    continue

                result = _execute_call(registry, kind, name, args)
                results.append({"ok": True, "result": result})

            except Exception as e:
                logger.warning(f"Batch item {i} failed: {e}")
                results.append({
                    "ok": False,
                    "error": str(e)
                })

        return results

    else:
        raise ValueError(f"Unknown method: {method}")


def _execute_call(registry: MCPRegistry, kind: str, name: str, args: Dict[str, Any]) -> Any:
    """
    Execute a call to a registry item.

    Args:
        registry: MCP registry
        kind: Type of item to call ('tool', 'resource', 'prompt', 'complete')
        name: Name of the item to call
        args: Arguments to pass to the item

    Returns:
        Result from the registry call

    Raises:
        ValueError: If the kind is invalid
        Various exceptions from the registry calls
    """
    logger.debug(f"Executing {kind} call: {name} with args: {list(args.keys())}")

    try:
        if kind == "tool":
            return safe_execute(registry.call_tool, name, **args)
        elif kind == "resource":
            return safe_execute(registry.get_resource, name, **args)
        elif kind == "prompt":
            return safe_execute(registry.get_prompt, name, **args)
        elif kind == "complete":
            return safe_execute(registry.complete, name, **args)
        else:
            raise ValueError(f"Invalid call kind: {kind}")

    except (ToolNotFoundError, ResourceNotFoundError, PromptNotFoundError,
            CompletionProviderNotFoundError) as e:
        logger.warning(f"Item not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Call execution failed: {e}")
        raise


def stdio_serve(registry: Optional[MCPRegistry] = None) -> None:
    """
    Start a STDIO-based MCP server.

    This function starts a server that reads JSON-RPC requests from stdin
    and writes responses to stdout. The server runs until stdin is closed
    or an unrecoverable error occurs.

    Args:
        registry: MCP registry to use, or None to use the default registry

    Protocol:
        - Each line on stdin should be a complete JSON-RPC request
        - Each line on stdout will be a complete JSON-RPC response
        - Empty lines on stdin are ignored
        - Malformed JSON or other errors result in JSON-RPC error responses

    Example:
        >>> # Start server with default registry
        >>> stdio_serve()
        >>>
        >>> # Start server with custom registry
        >>> my_registry = MCPRegistry()
        >>> stdio_serve(my_registry)

    Note:
        This function blocks until stdin is closed. It's designed to be
        the main entry point for STDIO-based MCP servers.
    """
    # Use provided registry or default
    reg = registry or default_registry

    # Log startup information to stderr (stdout is reserved for protocol)
    logger.info(f"Starting STDIO MCP server", file=sys.stderr)
    logger.info(f"Registry contains: {len(reg.tools)} tools, {len(reg.resources)} resources, "
                f"{len(reg.prompts)} prompts, {len(reg.completions)} completions", file=sys.stderr)

    try:
        # Main server loop - read from stdin, process, write to stdout
        for line_number, line in enumerate(sys.stdin, 1):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Initialize response variables
            request_id = None
            response = None

            try:
                # Parse JSON-RPC request
                request = json.loads(line)
                request_id = request.get("id")

                logger.debug(f"Processing request {line_number}: {request.get('method')}")

                # Handle the request
                result = _handle_request(reg, request)

                # Create success response
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }

                logger.debug(f"Request {line_number} completed successfully")

            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON on line {line_number}: {e}")
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32700,  # Parse error
                        "message": f"Invalid JSON: {str(e)}"
                    }
                }

            except Exception as e:
                logger.error(f"Request {line_number} failed: {e}")
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,  # Internal error
                        "message": str(e)
                    }
                }

            # Write response to stdout
            try:
                response_json = json.dumps(response, ensure_ascii=False)
                sys.stdout.write(response_json + "\n")
                sys.stdout.flush()

            except Exception as e:
                logger.error(f"Failed to write response for request {line_number}: {e}")
                # Try to write a minimal error response
                try:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Failed to serialize response"
                        }
                    }
                    sys.stdout.write(json.dumps(error_response) + "\n")
                    sys.stdout.flush()
                except Exception:
                    # If we can't even write an error response, we're in trouble
                    logger.critical("Failed to write error response, terminating")
                    break

    except KeyboardInterrupt:
        logger.info("STDIO server interrupted by user", file=sys.stderr)
    except Exception as e:
        logger.error(f"STDIO server error: {e}", file=sys.stderr)
    finally:
        logger.info("STDIO MCP server shutting down", file=sys.stderr)
