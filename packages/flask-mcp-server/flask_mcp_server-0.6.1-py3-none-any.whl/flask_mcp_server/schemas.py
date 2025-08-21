"""
JSON Schema Generation for Flask MCP Server.

This module provides utilities for automatically generating JSON schemas from
Python function signatures and type annotations. These schemas are used for
input validation, output validation, and API documentation generation.

The schema generation leverages Python's type hints and the Pydantic library
to create JSON Schema specifications that are compatible with the MCP protocol
and OpenAPI documentation.

Features:
- Automatic input schema generation from function parameters
- Output schema generation from return type annotations
- Support for complex types via Pydantic TypeAdapter
- Graceful fallback for unsupported types
- Integration with MCP registry for tool/resource documentation

Example Usage:
    >>> def add_numbers(a: int, b: int = 10) -> int:
    ...     '''Add two numbers together'''
    ...     return a + b
    >>>
    >>> input_schema = build_input_schema(add_numbers)
    >>> print(input_schema)
    >>> # {
    >>> #   "type": "object",
    >>> #   "properties": {
    >>> #     "a": {"type": "integer"},
    >>> #     "b": {"type": "integer"}
    >>> #   },
    >>> #   "required": ["a"]
    >>> # }
    >>>
    >>> output_schema = build_output_schema(add_numbers)
    >>> print(output_schema)
    >>> # {"type": "integer"}
"""

from __future__ import annotations
import inspect
import logging
from typing import Any, Dict, Callable, get_type_hints, Union, Optional
from pydantic import TypeAdapter

# Set up logging for schema operations
logger = logging.getLogger(__name__)


def _py_to_json_schema(py_type: Any) -> Dict[str, Any]:
    """
    Convert a Python type to a JSON Schema representation.

    This function uses Pydantic's TypeAdapter to convert Python type annotations
    into JSON Schema format. It provides a fallback for types that cannot be
    converted, ensuring that schema generation never fails completely.

    Args:
        py_type: Python type annotation to convert

    Returns:
        JSON Schema dictionary representing the type

    Examples:
        >>> _py_to_json_schema(int)
        {'type': 'integer'}

        >>> _py_to_json_schema(str)
        {'type': 'string'}

        >>> _py_to_json_schema(list[str])
        {'type': 'array', 'items': {'type': 'string'}}

        >>> _py_to_json_schema(dict[str, int])
        {'type': 'object', 'additionalProperties': {'type': 'integer'}}
    """
    try:
        # Use Pydantic's TypeAdapter for robust type conversion
        adapter = TypeAdapter(py_type)
        schema = adapter.json_schema()

        logger.debug(f"Generated schema for type {py_type}: {schema}")
        return schema

    except Exception as e:
        # Log the error but don't fail - provide a generic fallback
        logger.warning(f"Failed to generate schema for type {py_type}: {e}")

        # Return a generic object schema as fallback
        return {"type": "object", "description": f"Schema generation failed for {py_type}"}


def build_input_schema(fn: Callable[..., Any]) -> Dict[str, Any]:
    """
    Build a JSON Schema for function input parameters.

    This function analyzes a function's signature and type hints to generate
    a JSON Schema that describes the expected input parameters. The schema
    includes property definitions, required fields, and type information.

    Args:
        fn: Function to analyze

    Returns:
        JSON Schema dictionary describing the function's input parameters

    Schema Structure:
        {
            "type": "object",
            "properties": {
                "param_name": {"type": "param_type", ...},
                ...
            },
            "required": ["required_param1", "required_param2", ...]
        }

    Example:
        >>> def greet(name: str, age: int = 25, greeting: str = "Hello") -> str:
        ...     return f"{greeting}, {name}! You are {age} years old."
        >>>
        >>> schema = build_input_schema(greet)
        >>> print(schema)
        >>> # {
        >>> #   "type": "object",
        >>> #   "properties": {
        >>> #     "name": {"type": "string"},
        >>> #     "age": {"type": "integer"},
        >>> #     "greeting": {"type": "string"}
        >>> #   },
        >>> #   "required": ["name"]
        >>> # }
    """
    try:
        # Get function signature and type hints
        signature = inspect.signature(fn)
        type_hints = get_type_hints(fn)

        properties = {}
        required_params = []

        logger.debug(f"Building input schema for function: {fn.__name__}")

        # Analyze each parameter
        for param_name, param in signature.parameters.items():
            # Skip 'self' parameter for methods
            if param_name == "self":
                continue

            # Get type annotation (default to Any if not specified)
            param_type = type_hints.get(param_name, Any)

            # Generate JSON schema for this parameter type
            param_schema = _py_to_json_schema(param_type)

            # Add parameter description if available from docstring
            # TODO: Extract parameter descriptions from docstring

            properties[param_name] = param_schema

            # Check if parameter is required (no default value)
            if param.default is inspect.Parameter.empty:
                required_params.append(param_name)
                logger.debug(f"Parameter '{param_name}' is required")
            else:
                logger.debug(f"Parameter '{param_name}' has default value: {param.default}")

        # Build the complete input schema
        input_schema = {
            "type": "object",
            "properties": properties,
            "required": required_params
        }

        logger.debug(f"Generated input schema for {fn.__name__}: {len(properties)} properties, {len(required_params)} required")
        return input_schema

    except Exception as e:
        logger.error(f"Failed to build input schema for {fn.__name__}: {e}")

        # Return a minimal schema as fallback
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "description": f"Schema generation failed: {e}"
        }


def build_output_schema(fn: Callable[..., Any]) -> Dict[str, Any]:
    """
    Build a JSON Schema for function return type.

    This function analyzes a function's return type annotation to generate
    a JSON Schema that describes the expected output format.

    Args:
        fn: Function to analyze

    Returns:
        JSON Schema dictionary describing the function's return type

    Example:
        >>> def get_user(user_id: str) -> dict[str, Union[str, int]]:
        ...     return {"id": user_id, "name": "John", "age": 30}
        >>>
        >>> schema = build_output_schema(get_user)
        >>> print(schema)
        >>> # {
        >>> #   "type": "object",
        >>> #   "additionalProperties": {
        >>> #     "anyOf": [
        >>> #       {"type": "string"},
        >>> #       {"type": "integer"}
        >>> #     ]
        >>> #   }
        >>> # }
    """
    try:
        # Get type hints for the function
        type_hints = get_type_hints(fn)

        # Get return type annotation (default to Any if not specified)
        return_type = type_hints.get("return", Any)

        logger.debug(f"Building output schema for function: {fn.__name__}, return type: {return_type}")

        # Generate JSON schema for the return type
        output_schema = _py_to_json_schema(return_type)

        logger.debug(f"Generated output schema for {fn.__name__}: {output_schema}")
        return output_schema

    except Exception as e:
        logger.error(f"Failed to build output schema for {fn.__name__}: {e}")

        # Return a generic schema as fallback
        return {
            "type": "object",
            "description": f"Schema generation failed: {e}"
        }


def validate_function_signature(fn: Callable[..., Any]) -> Dict[str, Any]:
    """
    Validate and analyze a function signature for MCP compatibility.

    This function checks if a function signature is suitable for use as an MCP
    tool, resource, or prompt provider. It returns information about potential
    issues and recommendations.

    Args:
        fn: Function to validate

    Returns:
        Dictionary containing validation results and recommendations

    Example:
        >>> def good_function(name: str, count: int = 1) -> str:
        ...     return f"Hello {name} " * count
        >>>
        >>> result = validate_function_signature(good_function)
        >>> print(result['valid'])  # True
    """
    issues = []
    warnings = []

    try:
        signature = inspect.signature(fn)
        type_hints = get_type_hints(fn)

        # Check for type annotations
        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            if param_name not in type_hints:
                warnings.append(f"Parameter '{param_name}' lacks type annotation")

        # Check return type annotation
        if "return" not in type_hints:
            warnings.append("Function lacks return type annotation")

        # Check for unsupported parameter types
        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                issues.append(f"*args parameter '{param_name}' not supported in MCP")
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                warnings.append(f"**kwargs parameter '{param_name}' may cause issues")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "parameter_count": len([p for p in signature.parameters.values() if p.name != "self"]),
            "has_return_annotation": "return" in type_hints
        }

    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Signature analysis failed: {e}"],
            "warnings": [],
            "parameter_count": 0,
            "has_return_annotation": False
        }
