"""
Tests for validation module.

This module tests input validation, JSON-RPC validation,
and error handling functionality.
"""

import pytest
import json
from flask import Flask
from flask_mcp_server.validation import (
    ValidationError,
    JSONRPCRequest,
    MCPCallParams,
    validate_json_request,
    validate_jsonrpc_request,
    validate_mcp_call_params,
    validate_environment_variable,
    create_error_response
)


class TestValidationError:
    """Test ValidationError class."""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation with different parameters."""
        error = ValidationError("Test message")
        assert error.message == "Test message"
        assert error.field is None
        assert error.code == "validation_error"
        
        error = ValidationError("Test message", field="test_field", code="custom_code")
        assert error.message == "Test message"
        assert error.field == "test_field"
        assert error.code == "custom_code"


class TestJSONRPCRequest:
    """Test JSONRPCRequest validation."""
    
    def test_valid_jsonrpc_request(self):
        """Test valid JSON-RPC request validation."""
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method",
            "params": {"arg1": "value1"}
        }
        request = JSONRPCRequest(**data)
        assert request.jsonrpc == "2.0"
        assert request.id == 1
        assert request.method == "test_method"
        assert request.params == {"arg1": "value1"}
    
    def test_invalid_jsonrpc_version(self):
        """Test invalid JSON-RPC version."""
        data = {
            "jsonrpc": "1.0",
            "method": "test_method"
        }
        with pytest.raises(ValueError):
            JSONRPCRequest(**data)
    
    def test_missing_method(self):
        """Test missing method field."""
        data = {
            "jsonrpc": "2.0",
            "id": 1
        }
        with pytest.raises(ValueError):
            JSONRPCRequest(**data)
    
    def test_method_too_long(self):
        """Test method name too long."""
        data = {
            "jsonrpc": "2.0",
            "method": "a" * 101  # Too long
        }
        with pytest.raises(ValueError):
            JSONRPCRequest(**data)


class TestMCPCallParams:
    """Test MCPCallParams validation."""
    
    def test_valid_mcp_call_params(self):
        """Test valid MCP call parameters."""
        data = {
            "kind": "tool",
            "name": "test_tool",
            "args": {"arg1": "value1"}
        }
        params = MCPCallParams(**data)
        assert params.kind == "tool"
        assert params.name == "test_tool"
        assert params.args == {"arg1": "value1"}
    
    def test_invalid_kind(self):
        """Test invalid kind parameter."""
        data = {
            "kind": "invalid_kind",
            "name": "test_tool"
        }
        with pytest.raises(ValueError):
            MCPCallParams(**data)
    
    def test_missing_name(self):
        """Test missing name parameter."""
        data = {
            "kind": "tool"
        }
        with pytest.raises(ValueError):
            MCPCallParams(**data)
    
    def test_default_args(self):
        """Test default args parameter."""
        data = {
            "kind": "tool",
            "name": "test_tool"
        }
        params = MCPCallParams(**data)
        assert params.args == {}


class TestValidateJsonRequest:
    """Test validate_json_request function."""
    
    def test_valid_json_request(self):
        """Test valid JSON request validation."""
        app = Flask(__name__)
        with app.test_request_context(
            '/',
            method='POST',
            data=json.dumps({"test": "data"}),
            content_type='application/json'
        ):
            data = validate_json_request()
            assert data == {"test": "data"}
    
    def test_invalid_content_type(self):
        """Test invalid content type."""
        app = Flask(__name__)
        with app.test_request_context(
            '/',
            method='POST',
            data='{"test": "data"}',
            content_type='text/plain'
        ):
            with pytest.raises(ValidationError) as exc_info:
                validate_json_request()
            assert exc_info.value.code == "invalid_content_type"
    
    def test_request_too_large(self):
        """Test request body too large."""
        app = Flask(__name__)
        large_data = "a" * (1024 * 1024 + 1)  # > 1MB
        with app.test_request_context(
            '/',
            method='POST',
            data=large_data,
            content_type='application/json'
        ):
            with pytest.raises(ValidationError) as exc_info:
                validate_json_request()
            assert exc_info.value.code == "request_too_large"
    
    def test_invalid_json(self):
        """Test invalid JSON."""
        app = Flask(__name__)
        with app.test_request_context(
            '/',
            method='POST',
            data='{"invalid": json}',
            content_type='application/json'
        ):
            with pytest.raises(ValidationError) as exc_info:
                validate_json_request()
            assert exc_info.value.code == "invalid_json"
    
    def test_non_object_json(self):
        """Test non-object JSON."""
        app = Flask(__name__)
        with app.test_request_context(
            '/',
            method='POST',
            data='"string"',
            content_type='application/json'
        ):
            with pytest.raises(ValidationError) as exc_info:
                validate_json_request()
            assert exc_info.value.code == "invalid_json_type"


class TestValidateEnvironmentVariable:
    """Test validate_environment_variable function."""
    
    def test_valid_environment_variable(self):
        """Test valid environment variable."""
        assert validate_environment_variable("TEST_VAR", "valid_value") is True
        assert validate_environment_variable("TEST_VAR", None) is True
    
    def test_invalid_type(self):
        """Test invalid variable type."""
        assert validate_environment_variable("TEST_VAR", 123) is False
    
    def test_pattern_validation(self):
        """Test pattern validation."""
        pattern = r'^[a-zA-Z0-9_]+$'
        assert validate_environment_variable("TEST_VAR", "valid_123", pattern) is True
        assert validate_environment_variable("TEST_VAR", "invalid-value", pattern) is False


class TestCreateErrorResponse:
    """Test create_error_response function."""

    def test_validation_error_response(self):
        """Test validation error response."""
        app = Flask(__name__)
        with app.app_context():
            error = ValidationError("Test error", field="test_field")
            response, status_code = create_error_response(error)

            assert status_code == 400
            data = response.get_json()
            assert data["error"] == "validation_error"
            assert data["message"] == "Test error"
            assert data["field"] == "test_field"

    def test_jsonrpc_error_response(self):
        """Test JSON-RPC error response."""
        app = Flask(__name__)
        with app.app_context():
            error = ValidationError("Test error")
            response, status_code = create_error_response(error, request_id=123)

            assert status_code == 400
            data = response.get_json()
            assert data["jsonrpc"] == "2.0"
            assert data["id"] == 123
            assert "error" in data
            assert data["error"]["message"] == "Test error"

    def test_request_too_large_status(self):
        """Test request too large status code."""
        app = Flask(__name__)
        with app.app_context():
            error = ValidationError("Too large", code="request_too_large")
            response, status_code = create_error_response(error)
            assert status_code == 413

    def test_internal_error_status(self):
        """Test internal error status code."""
        app = Flask(__name__)
        with app.app_context():
            error = ValidationError("Internal error", code="internal_error")
            response, status_code = create_error_response(error)
            assert status_code == 500
