"""
Exception handling utilities for flask-mcp-server.

This module provides comprehensive exception handling to prevent
information leakage and ensure graceful error responses.
"""

from __future__ import annotations
import logging
import traceback
from typing import Any, Optional, Union
from flask import jsonify, Response
from functools import wraps

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """Base exception class for MCP-related errors."""

    def __init__(self, message: str, code: str = "mcp_error", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(MCPError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "authentication_failed", 401)


class AuthorizationError(MCPError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, "access_forbidden", 403)


class RateLimitError(MCPError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message, "rate_limit_exceeded", 429)
        self.retry_after = retry_after


class ValidationError(MCPError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, "validation_error", 400)
        self.field = field


class ToolNotFoundError(MCPError):
    """Raised when a requested tool is not found."""

    def __init__(self, tool_name: str):
        super().__init__(f"Tool '{tool_name}' not found", "tool_not_found", 404)
        self.tool_name = tool_name


class ResourceNotFoundError(MCPError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_name: str):
        super().__init__(f"Resource '{resource_name}' not found", "resource_not_found", 404)
        self.resource_name = resource_name


class PromptNotFoundError(MCPError):
    """Raised when a requested prompt is not found."""

    def __init__(self, prompt_name: str):
        super().__init__(f"Prompt '{prompt_name}' not found", "prompt_not_found", 404)
        self.prompt_name = prompt_name


class CompletionProviderNotFoundError(MCPError):
    """Raised when a requested completion provider is not found."""

    def __init__(self, provider_name: str):
        super().__init__(f"Completion provider '{provider_name}' not found", "completion_provider_not_found", 404)
        self.provider_name = provider_name


class ToolExecutionError(MCPError):
    """Raised when tool execution fails."""

    def __init__(self, tool_name: str, original_error: Optional[Exception] = None):
        message = f"Tool '{tool_name}' execution failed"
        if original_error:
            # Don't expose internal error details in production
            logger.error(f"Tool execution error for {tool_name}: {original_error}")
            logger.error(traceback.format_exc())
        super().__init__(message, "tool_execution_error", 500)
        self.tool_name = tool_name
        self.original_error = original_error


def safe_execute(func, *args, **kwargs) -> Any:
    """
    Safely execute a function with comprehensive error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Function result
        
    Raises:
        MCPError: Appropriate MCP error based on the exception type
    """
    try:
        return func(*args, **kwargs)
    except PermissionError as e:
        logger.warning(f"Permission error in {func.__name__}: {e}")
        raise AuthorizationError("Access forbidden")
    except KeyError as e:
        logger.warning(f"Key error in {func.__name__}: {e}")
        if "tool" in str(e).lower():
            raise ToolNotFoundError(str(e).strip("'\""))
        elif "resource" in str(e).lower():
            raise ResourceNotFoundError(str(e).strip("'\""))
        elif "prompt" in str(e).lower():
            raise PromptNotFoundError(str(e).strip("'\""))
        else:
            raise ValidationError(f"Missing required field: {e}")
    except ValueError as e:
        logger.warning(f"Value error in {func.__name__}: {e}")
        raise ValidationError(str(e))
    except TypeError as e:
        logger.warning(f"Type error in {func.__name__}: {e}")
        raise ValidationError(f"Invalid argument type: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in {func.__name__}: {e}")
        logger.error(traceback.format_exc())
        # Don't expose internal error details
        raise MCPError("Internal server error", "internal_error", 500)


def handle_exceptions(func):
    """
    Decorator to handle exceptions in Flask route handlers.
    
    This decorator catches all exceptions and converts them to appropriate
    HTTP responses without exposing sensitive information.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MCPError as e:
            logger.warning(f"MCP error in {func.__name__}: {e.message}")
            response_data = {
                "error": e.code,
                "message": e.message
            }

            # Add additional fields for specific error types
            if isinstance(e, RateLimitError) and e.retry_after:
                response_data["retry_after"] = e.retry_after
            elif isinstance(e, ValidationError) and e.field:
                response_data["field"] = e.field

            response = jsonify(response_data)
            response.status_code = e.status_code

            # Add retry-after header for rate limit errors
            if isinstance(e, RateLimitError) and e.retry_after:
                response.headers["Retry-After"] = str(e.retry_after)

            return response
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())

            # Return generic error without exposing details
            return jsonify({
                "error": "internal_error",
                "message": "An internal server error occurred"
            }), 500

    return wrapper


def create_jsonrpc_error_response(
        error: MCPError,
        request_id: Optional[Union[str, int]] = None
) -> Response:
    """
    Create a JSON-RPC error response.
    
    Args:
        error: MCPError instance
        request_id: Request ID from the original JSON-RPC request
        
    Returns:
        Flask Response object with JSON-RPC error format
    """
    # Map MCP error codes to JSON-RPC error codes
    jsonrpc_code_map = {
        "validation_error": -32602,  # Invalid params
        "tool_not_found": -32601,  # Method not found
        "resource_not_found": -32601,
        "prompt_not_found": -32601,
        "completion_provider_not_found": -32601,
        "authentication_failed": -32600,  # Invalid request
        "access_forbidden": -32600,
        "rate_limit_exceeded": -32600,
        "tool_execution_error": -32603,  # Internal error
        "internal_error": -32603,
    }

    jsonrpc_code = jsonrpc_code_map.get(error.code, -32603)

    response_data = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": jsonrpc_code,
            "message": error.message,
            "data": {"mcp_code": error.code}
        }
    }

    # Add additional error data
    if isinstance(error, ValidationError) and error.field:
        response_data["error"]["data"]["field"] = error.field
    elif isinstance(error, RateLimitError) and error.retry_after:
        response_data["error"]["data"]["retry_after"] = error.retry_after

    response = jsonify(response_data)
    response.status_code = error.status_code

    return response
