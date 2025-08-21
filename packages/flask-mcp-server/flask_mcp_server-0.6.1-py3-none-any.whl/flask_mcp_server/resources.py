"""
Resource Management for Flask MCP Server.

This module provides classes for managing MCP resources, which are data sources
that can be accessed by MCP clients. Resources can be static data, dynamic
content, or parameterized templates that generate content based on input.

Resources in the MCP protocol represent any kind of data that can be retrieved,
such as:
- File contents
- Database records
- API responses
- Generated content
- Configuration data

Example Usage:
    >>> from flask_mcp_server.resources import Resource, ResourceTemplate
    >>>
    >>> # Simple resource with a getter function
    >>> def get_user_data(user_id: str) -> dict:
    ...     return {"id": user_id, "name": f"User {user_id}"}
    >>>
    >>> user_resource = Resource(get_user_data)
    >>>
    >>> # Template-based resource
    >>> template = ResourceTemplate("Hello, {name}! Welcome to {app_name}.")
    >>> greeting = template.expand(name="Alice", app_name="MyApp")
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Union
import logging

# Set up logging for resource operations
logger = logging.getLogger(__name__)


class Resource:
    """
    Wrapper for MCP resource functions.

    A Resource encapsulates a function that retrieves or generates data.
    The function can accept parameters and should return the resource content.
    Resources are typically registered with the MCP registry and can be
    accessed by clients via the MCP protocol.

    The resource function should be designed to:
    - Accept named parameters for customization
    - Return serializable data (dict, list, str, etc.)
    - Handle errors gracefully
    - Be stateless when possible
    """

    def __init__(self, get: Callable[..., Any], description: Optional[str] = None):
        """
        Initialize a resource with a getter function.

        Args:
            get: Function that retrieves or generates the resource content
            description: Optional human-readable description of the resource

        Example:
            >>> def get_config() -> dict:
            ...     return {"debug": True, "version": "1.0"}
            >>>
            >>> config_resource = Resource(get_config, "Application configuration")
        """
        self.get = get
        self.description = description or getattr(get, '__doc__', None) or "No description available"

        # Store function metadata for introspection
        self.name = getattr(get, '__name__', 'unknown')
        self.module = getattr(get, '__module__', None)

        logger.debug(f"Created resource: {self.name}")

    def __call__(self, *args, **kwargs) -> Any:
        """
        Call the resource getter function.

        Args:
            *args: Positional arguments to pass to the getter
            **kwargs: Keyword arguments to pass to the getter

        Returns:
            Resource content returned by the getter function

        Raises:
            Any exception raised by the getter function
        """
        try:
            logger.debug(f"Calling resource getter: {self.name}")
            result = self.get(*args, **kwargs)
            logger.debug(f"Resource getter completed: {self.name}")
            return result
        except Exception as e:
            logger.error(f"Resource getter failed: {self.name} - {e}")
            raise

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this resource.

        Returns:
            Dictionary containing resource metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "module": self.module,
            "callable": True
        }


class ResourceTemplate:
    """
    Template-based resource for generating parameterized content.

    ResourceTemplate allows you to define content templates that can be
    expanded with parameters. This is useful for generating dynamic content
    like messages, configurations, or formatted data based on input parameters.

    The template uses Python's str.format() syntax for parameter substitution.
    """

    def __init__(self, template: str, description: Optional[str] = None):
        """
        Initialize a resource template.

        Args:
            template: Template string with format placeholders (e.g., "Hello, {name}!")
            description: Optional human-readable description of the template

        Example:
            >>> template = ResourceTemplate(
            ...     "User {user_id} has {count} items in {category}",
            ...     "User item count message"
            ... )
        """
        self.template = template
        self.description = description or "Template-based resource"

        # Validate template by attempting to format with empty dict
        try:
            self.template.format()
        except KeyError:
            # This is expected if template has required parameters
            pass
        except Exception as e:
            logger.warning(f"Template validation warning: {e}")

        logger.debug(f"Created resource template with {len(template)} characters")

    def expand(self, **params) -> str:
        """
        Expand the template with the provided parameters.

        Args:
            **params: Parameters to substitute in the template

        Returns:
            Expanded template string

        Raises:
            KeyError: If required template parameters are missing
            ValueError: If parameter values cannot be formatted

        Example:
            >>> template = ResourceTemplate("Hello, {name}! You have {count} messages.")
            >>> result = template.expand(name="Alice", count=5)
            >>> print(result)  # "Hello, Alice! You have 5 messages."
        """
        try:
            logger.debug(f"Expanding template with parameters: {list(params.keys())}")
            result = self.template.format(**params)
            logger.debug(f"Template expansion completed, result length: {len(result)}")
            return result
        except KeyError as e:
            logger.error(f"Template expansion failed - missing parameter: {e}")
            raise KeyError(f"Missing required template parameter: {e}")
        except ValueError as e:
            logger.error(f"Template expansion failed - formatting error: {e}")
            raise ValueError(f"Template formatting error: {e}")

    def get_required_params(self) -> list:
        """
        Extract required parameter names from the template.

        Returns:
            List of parameter names required by the template

        Note:
            This is a simple implementation that may not catch all edge cases
            in complex format strings.
        """
        import re

        # Find all format placeholders in the template
        # This regex matches {param_name} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, self.template)

        # Extract parameter names (before any format specifiers)
        params = []
        for match in matches:
            # Split on ':' to handle format specifiers like {name:>10}
            param_name = match.split(':')[0]
            if param_name not in params:
                params.append(param_name)

        return params

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this template.

        Returns:
            Dictionary containing template metadata
        """
        return {
            "description": self.description,
            "template": self.template,
            "required_params": self.get_required_params(),
            "template_length": len(self.template)
        }

    def __str__(self) -> str:
        """String representation of the template."""
        return f"ResourceTemplate('{self.template[:50]}{'...' if len(self.template) > 50 else ''}')"

    def __repr__(self) -> str:
        """Detailed string representation of the template."""
        return f"ResourceTemplate(template='{self.template}', description='{self.description}')"


def create_static_resource(content: Any, description: Optional[str] = None) -> Resource:
    """
    Create a resource that returns static content.

    This is a convenience function for creating resources that always return
    the same content without requiring parameters.

    Args:
        content: Static content to return
        description: Optional description of the resource

    Returns:
        Resource instance that returns the static content

    Example:
        >>> config = {"debug": True, "version": "1.0"}
        >>> config_resource = create_static_resource(config, "Application configuration")
    """
    def getter() -> Any:
        return content

    return Resource(getter, description)


def create_file_resource(file_path: str, encoding: str = 'utf-8') -> Resource:
    """
    Create a resource that reads content from a file.

    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)

    Returns:
        Resource instance that reads and returns file content

    Example:
        >>> readme_resource = create_file_resource("README.md")
    """
    def getter() -> str:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except IOError as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise

    return Resource(getter, f"File content from {file_path}")
