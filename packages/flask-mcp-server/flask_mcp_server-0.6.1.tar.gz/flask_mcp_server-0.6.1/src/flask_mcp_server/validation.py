"""
Input validation and error handling utilities for flask-mcp-server.

This module provides comprehensive validation for JSON-RPC requests,
environment variables, and other inputs to prevent security vulnerabilities
and improve error handling.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Optional, Union
from flask import request, jsonify, Response
from pydantic import BaseModel, ValidationError, Field
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error with structured error information."""
    
    def __init__(self, message: str, field: Optional[str] = None, code: str = "validation_error"):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)

class JSONRPCRequest(BaseModel):
    """Pydantic model for validating JSON-RPC requests."""
    
    jsonrpc: str = Field(..., pattern=r"^2\.0$", description="JSON-RPC version must be 2.0")
    id: Optional[Union[str, int]] = Field(None, description="Request ID")
    method: str = Field(..., min_length=1, max_length=100, description="Method name")
    params: Optional[Dict[str, Any]] = Field(None, description="Method parameters")

class MCPCallParams(BaseModel):
    """Pydantic model for validating MCP call parameters."""
    
    kind: str = Field(..., pattern=r"^(tool|resource|prompt|complete)$", description="Call type")
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    args: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Call arguments")

def validate_json_request() -> Dict[str, Any]:
    """
    Validate and parse JSON request body with comprehensive error handling.
    
    Returns:
        Parsed and validated JSON data
        
    Raises:
        ValidationError: If JSON is invalid or malformed
    """
    try:
        # Check content type
        content_type = request.headers.get('Content-Type', '')
        if not content_type.startswith('application/json'):
            logger.warning(f"Invalid content type: {content_type}")
            raise ValidationError(
                "Content-Type must be application/json",
                code="invalid_content_type"
            )
        
        # Get raw data for size validation
        raw_data = request.get_data()
        if len(raw_data) > 1024 * 1024:  # 1MB limit
            raise ValidationError(
                "Request body too large (max 1MB)",
                code="request_too_large"
            )
        
        # Parse JSON with error handling
        try:
            data = json.loads(raw_data.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e}")
            raise ValidationError(
                f"Invalid JSON: {str(e)}",
                code="invalid_json"
            )
        except UnicodeDecodeError as e:
            logger.warning(f"Unicode decode error: {e}")
            raise ValidationError(
                "Invalid UTF-8 encoding",
                code="invalid_encoding"
            )
        
        # Validate data is a dictionary
        if not isinstance(data, dict):
            raise ValidationError(
                "Request body must be a JSON object",
                code="invalid_json_type"
            )
        
        return data
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during JSON validation: {e}")
        raise ValidationError(
            "Internal validation error",
            code="internal_error"
        )

def validate_jsonrpc_request(data: Dict[str, Any]) -> JSONRPCRequest:
    """
    Validate JSON-RPC request structure.
    
    Args:
        data: Parsed JSON data
        
    Returns:
        Validated JSONRPCRequest object
        
    Raises:
        ValidationError: If request structure is invalid
    """
    try:
        return JSONRPCRequest(**data)
    except ValidationError as e:
        logger.warning(f"Pydantic validation error: {e}")
        # Convert Pydantic errors to our custom format
        error_details = []
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            error_details.append(f"{field}: {error['msg']}")
        
        raise ValidationError(
            f"Invalid JSON-RPC request: {'; '.join(error_details)}",
            code="invalid_jsonrpc"
        )

def validate_mcp_call_params(params: Optional[Dict[str, Any]]) -> MCPCallParams:
    """
    Validate MCP call parameters.
    
    Args:
        params: Call parameters from JSON-RPC request
        
    Returns:
        Validated MCPCallParams object
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if params is None:
        raise ValidationError(
            "Missing required parameters for mcp.call",
            code="missing_params"
        )
    
    try:
        return MCPCallParams(**params)
    except ValidationError as e:
        logger.warning(f"MCP call params validation error: {e}")
        error_details = []
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            error_details.append(f"{field}: {error['msg']}")
        
        raise ValidationError(
            f"Invalid MCP call parameters: {'; '.join(error_details)}",
            code="invalid_mcp_params"
        )

def validate_environment_variable(name: str, value: Optional[str], pattern: Optional[str] = None) -> bool:
    """
    Validate environment variable format.
    
    Args:
        name: Environment variable name
        value: Environment variable value
        pattern: Optional regex pattern to validate against
        
    Returns:
        True if valid, False otherwise
    """
    if value is None:
        return True  # Optional variables are valid when None
    
    if not isinstance(value, str):
        logger.warning(f"Environment variable {name} is not a string: {type(value)}")
        return False
    
    if pattern and not re.match(pattern, value):
        logger.warning(f"Environment variable {name} doesn't match pattern {pattern}: {value}")
        return False
    
    return True

def create_error_response(error: ValidationError, request_id: Optional[Union[str, int]] = None) -> Response:
    """
    Create a standardized error response.
    
    Args:
        error: ValidationError instance
        request_id: Optional request ID for JSON-RPC response
        
    Returns:
        Flask Response object with error details
    """
    # Determine appropriate HTTP status code
    status_code = 400  # Default to Bad Request
    if error.code == "request_too_large":
        status_code = 413
    elif error.code == "internal_error":
        status_code = 500
    
    # Create error response
    if request_id is not None:
        # JSON-RPC error response
        response_data = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32600 if error.code == "invalid_jsonrpc" else -32602,
                "message": error.message,
                "data": {"code": error.code, "field": error.field}
            }
        }
    else:
        # Standard error response
        response_data = {
            "error": error.code,
            "message": error.message,
            "field": error.field
        }
    
    return jsonify(response_data), status_code
