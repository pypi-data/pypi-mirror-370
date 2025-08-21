"""
Tests for exception handling module.

This module tests custom exceptions, error handling decorators,
and safe execution functionality.
"""

import pytest
from flask import Flask
from flask_mcp_server.exceptions import (
    MCPError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ValidationError,
    ToolNotFoundError,
    ResourceNotFoundError,
    PromptNotFoundError,
    CompletionProviderNotFoundError,
    ToolExecutionError,
    safe_execute,
    handle_exceptions,
    create_jsonrpc_error_response
)


class TestMCPError:
    """Test MCPError base class."""
    
    def test_mcp_error_creation(self):
        """Test MCPError creation."""
        error = MCPError("Test message")
        assert error.message == "Test message"
        assert error.code == "mcp_error"
        assert error.status_code == 500
        
        error = MCPError("Custom message", "custom_code", 400)
        assert error.message == "Custom message"
        assert error.code == "custom_code"
        assert error.status_code == 400


class TestSpecificErrors:
    """Test specific error classes."""
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError()
        assert error.code == "authentication_failed"
        assert error.status_code == 401
        
        error = AuthenticationError("Custom auth message")
        assert error.message == "Custom auth message"
    
    def test_authorization_error(self):
        """Test AuthorizationError."""
        error = AuthorizationError()
        assert error.code == "access_forbidden"
        assert error.status_code == 403
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError()
        assert error.code == "rate_limit_exceeded"
        assert error.status_code == 429
        assert error.retry_after is None
        
        error = RateLimitError("Rate limited", retry_after=60)
        assert error.retry_after == 60
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid input")
        assert error.code == "validation_error"
        assert error.status_code == 400
        assert error.field is None
        
        error = ValidationError("Invalid field", field="test_field")
        assert error.field == "test_field"
    
    def test_tool_not_found_error(self):
        """Test ToolNotFoundError."""
        error = ToolNotFoundError("test_tool")
        assert error.code == "tool_not_found"
        assert error.status_code == 404
        assert error.tool_name == "test_tool"
        assert "test_tool" in error.message
    
    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        error = ResourceNotFoundError("test_resource")
        assert error.code == "resource_not_found"
        assert error.status_code == 404
        assert error.resource_name == "test_resource"
    
    def test_prompt_not_found_error(self):
        """Test PromptNotFoundError."""
        error = PromptNotFoundError("test_prompt")
        assert error.code == "prompt_not_found"
        assert error.status_code == 404
        assert error.prompt_name == "test_prompt"
    
    def test_completion_provider_not_found_error(self):
        """Test CompletionProviderNotFoundError."""
        error = CompletionProviderNotFoundError("test_provider")
        assert error.code == "completion_provider_not_found"
        assert error.status_code == 404
        assert error.provider_name == "test_provider"
    
    def test_tool_execution_error(self):
        """Test ToolExecutionError."""
        original_error = ValueError("Original error")
        error = ToolExecutionError("test_tool", original_error)
        assert error.code == "tool_execution_error"
        assert error.status_code == 500
        assert error.tool_name == "test_tool"
        assert error.original_error == original_error


class TestSafeExecute:
    """Test safe_execute function."""
    
    def test_successful_execution(self):
        """Test successful function execution."""
        def test_func(a, b):
            return a + b
        
        result = safe_execute(test_func, 1, 2)
        assert result == 3
    
    def test_permission_error_handling(self):
        """Test PermissionError handling."""
        def test_func():
            raise PermissionError("Access denied")
        
        with pytest.raises(AuthorizationError):
            safe_execute(test_func)
    
    def test_key_error_handling(self):
        """Test KeyError handling."""
        def test_func():
            raise KeyError("tool_name")
        
        with pytest.raises(ToolNotFoundError):
            safe_execute(test_func)
        
        def test_func2():
            raise KeyError("resource_name")
        
        with pytest.raises(ResourceNotFoundError):
            safe_execute(test_func2)
    
    def test_value_error_handling(self):
        """Test ValueError handling."""
        def test_func():
            raise ValueError("Invalid value")
        
        with pytest.raises(ValidationError):
            safe_execute(test_func)
    
    def test_type_error_handling(self):
        """Test TypeError handling."""
        def test_func():
            raise TypeError("Invalid type")
        
        with pytest.raises(ValidationError):
            safe_execute(test_func)
    
    def test_generic_exception_handling(self):
        """Test generic exception handling."""
        def test_func():
            raise RuntimeError("Unexpected error")
        
        with pytest.raises(MCPError) as exc_info:
            safe_execute(test_func)
        assert exc_info.value.code == "internal_error"


class TestHandleExceptionsDecorator:
    """Test handle_exceptions decorator."""
    
    def test_successful_route(self):
        """Test successful route execution."""
        app = Flask(__name__)
        
        @handle_exceptions
        def test_route():
            return {"success": True}
        
        with app.app_context():
            result = test_route()
            assert result == {"success": True}
    
    def test_mcp_error_handling(self):
        """Test MCP error handling in routes."""
        app = Flask(__name__)

        @handle_exceptions
        def test_route():
            raise ValidationError("Test validation error", field="test_field")

        with app.app_context():
            response = test_route()
            assert response.status_code == 400  # Status code
            data = response.get_json()
            assert data["error"] == "validation_error"
            assert data["message"] == "Test validation error"
            assert data["field"] == "test_field"
    
    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry-after header."""
        app = Flask(__name__)

        @handle_exceptions
        def test_route():
            raise RateLimitError("Rate limited", retry_after=60)

        with app.app_context():
            response = test_route()
            assert response.status_code == 429
            assert response.headers.get("Retry-After") == "60"
    
    def test_generic_exception_handling(self):
        """Test generic exception handling in routes."""
        app = Flask(__name__)

        @handle_exceptions
        def test_route():
            raise RuntimeError("Unexpected error")

        with app.app_context():
            response, status_code = test_route()
            assert status_code == 500
            data = response.get_json()
            assert data["error"] == "internal_error"
            assert "internal server error" in data["message"].lower()


class TestCreateJsonrpcErrorResponse:
    """Test create_jsonrpc_error_response function."""

    def test_validation_error_response(self):
        """Test validation error JSON-RPC response."""
        app = Flask(__name__)
        with app.app_context():
            error = ValidationError("Test error", field="test_field")
            response = create_jsonrpc_error_response(error, request_id=123)

            assert response.status_code == 400
            data = response.get_json()
            assert data["jsonrpc"] == "2.0"
            assert data["id"] == 123
            assert data["error"]["code"] == -32602  # Invalid params
            assert data["error"]["message"] == "Test error"
            assert data["error"]["data"]["mcp_code"] == "validation_error"
            assert data["error"]["data"]["field"] == "test_field"

    def test_tool_not_found_response(self):
        """Test tool not found JSON-RPC response."""
        app = Flask(__name__)
        with app.app_context():
            error = ToolNotFoundError("test_tool")
            response = create_jsonrpc_error_response(error, request_id="test_id")

            data = response.get_json()
            assert data["error"]["code"] == -32601  # Method not found
            assert data["error"]["data"]["mcp_code"] == "tool_not_found"

    def test_rate_limit_response(self):
        """Test rate limit JSON-RPC response."""
        app = Flask(__name__)
        with app.app_context():
            error = RateLimitError("Rate limited", retry_after=60)
            response = create_jsonrpc_error_response(error)

            data = response.get_json()
            assert data["error"]["data"]["retry_after"] == 60

    def test_internal_error_response(self):
        """Test internal error JSON-RPC response."""
        app = Flask(__name__)
        with app.app_context():
            error = MCPError("Internal error", "internal_error", 500)
            response = create_jsonrpc_error_response(error)

            data = response.get_json()
            assert data["error"]["code"] == -32603  # Internal error
