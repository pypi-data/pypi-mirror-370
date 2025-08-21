"""
Simplified Facade API for Flask MCP Server.

This module provides a simplified, static interface for registering MCP items
without needing to import or manage registry instances directly. It's designed
to make the most common operations as simple as possible.

The facade provides static methods that delegate to the underlying registry
decorators, making it easy to register tools, resources, prompts, and
completion providers with minimal boilerplate.

Example Usage:
    >>> from flask_mcp_server import Mcp
    >>>
    >>> @Mcp.tool("add_numbers", "Add two numbers together")
    >>> def add_numbers(a: int, b: int) -> int:
    ...     return a + b
    >>>
    >>> @Mcp.resource("user_data", "Get user information")
    >>> def get_user_data(user_id: str) -> dict:
    ...     return {"id": user_id, "name": f"User {user_id}"}
    >>>
    >>> @Mcp.prompt("greeting", "Generate a greeting message")
    >>> def greeting_prompt(name: str) -> str:
    ...     return f"Write a friendly greeting for {name}"
    >>>
    >>> @Mcp.completion("cities")
    >>> def city_completion(prefix: str = "") -> list:
    ...     cities = ["New York", "London", "Tokyo", "Paris"]
    ...     return [city for city in cities if city.lower().startswith(prefix.lower())]

This facade is particularly useful for:
- Quick prototyping and simple applications
- Educational examples and tutorials
- Cases where you don't need multiple registries
- Reducing import complexity in simple use cases
"""

from __future__ import annotations
from typing import Optional, List, Callable, Any


class Mcp:
    """
    Simplified facade for MCP item registration.

    This class provides static methods that wrap the underlying registry
    decorators, offering a clean and simple API for the most common
    MCP operations. All methods delegate to the default registry.
    """

    @staticmethod
    def tool(
        name: Optional[str] = None,
        description: Optional[str] = None,
        roles: Optional[List[str]] = None,
        ttl: Optional[int] = None
    ) -> Callable:
        """
        Register a tool function with the default registry.

        This is a convenience method that delegates to the registry.tool decorator.
        Tools are functions that can be called by MCP clients to perform actions.

        Args:
            name: Tool name (defaults to function name if not provided)
            description: Human-readable description of what the tool does
            roles: List of roles required to access this tool (optional)
            ttl: Cache TTL in seconds for tool results (optional)

        Returns:
            Decorator function for registering the tool

        Example:
            >>> @Mcp.tool("calculate_sum", "Add two numbers together")
            >>> def add_numbers(a: int, b: int) -> int:
            ...     return a + b
        """
        from .registry import tool as _tool
        return _tool(name=name, description=description, roles=roles, ttl=ttl)

    @staticmethod
    def resource(
        name: Optional[str] = None,
        description: Optional[str] = None,
        roles: Optional[List[str]] = None,
        ttl: Optional[int] = None
    ) -> Callable:
        """
        Register a resource function with the default registry.

        This is a convenience method that delegates to the registry.resource decorator.
        Resources provide data or content that can be retrieved by MCP clients.

        Args:
            name: Resource name (defaults to function name if not provided)
            description: Human-readable description of what the resource provides
            roles: List of roles required to access this resource (optional)
            ttl: Cache TTL in seconds for resource results (optional)

        Returns:
            Decorator function for registering the resource

        Example:
            >>> @Mcp.resource("user_profile", "Get user profile information")
            >>> def get_user_profile(user_id: str) -> dict:
            ...     return {"id": user_id, "name": f"User {user_id}"}
        """
        from .registry import resource as _resource
        return _resource(name=name, description=description, roles=roles, ttl=ttl)

    @staticmethod
    def prompt(
        name: Optional[str] = None,
        description: Optional[str] = None,
        roles: Optional[List[str]] = None
    ) -> Callable:
        """
        Register a prompt function with the default registry.

        This is a convenience method that delegates to the registry.prompt decorator.
        Prompts are templates or generators for creating prompts for language models.

        Args:
            name: Prompt name (defaults to function name if not provided)
            description: Human-readable description of what the prompt generates
            roles: List of roles required to access this prompt (optional)

        Returns:
            Decorator function for registering the prompt

        Example:
            >>> @Mcp.prompt("code_review", "Generate a code review prompt")
            >>> def code_review_prompt(code: str, language: str) -> str:
            ...     return f"Please review this {language} code:\\n\\n{code}"
        """
        from .registry import prompt as _prompt
        return _prompt(name=name, description=description, roles=roles)

    @staticmethod
    def completion(
        name: Optional[str] = None,
        roles: Optional[List[str]] = None
    ) -> Callable:
        """
        Register a completion provider with the default registry.

        This is a convenience method that delegates to the registry.completion_provider decorator.
        Completion providers offer autocomplete suggestions for various contexts.

        Args:
            name: Completion provider name (defaults to function name if not provided)
            roles: List of roles required to access this completion provider (optional)

        Returns:
            Decorator function for registering the completion provider

        Example:
            >>> @Mcp.completion("file_paths")
            >>> def file_path_completion(prefix: str = "") -> list:
            ...     import os
            ...     return [f for f in os.listdir('.') if f.startswith(prefix)]
        """
        from .registry import completion_provider as _completion_provider
        return _completion_provider(name=name, roles=roles)

    @staticmethod
    def create_app(**kwargs) -> Any:
        """
        Create a Flask app with the default registry.

        This is a convenience method for creating an MCP server app
        using the default registry that contains all items registered
        via the facade methods.

        Args:
            **kwargs: Additional arguments passed to create_app()

        Returns:
            Flask application instance

        Example:
            >>> app = Mcp.create_app()
            >>> app.run(host='0.0.0.0', port=8080)
        """
        from .server_http import create_app
        from .registry import default_registry
        return create_app(registry=default_registry, **kwargs)

    @staticmethod
    def list_all() -> dict:
        """
        List all items registered via the facade.

        Returns:
            Dictionary containing all registered tools, resources, prompts, and completions

        Example:
            >>> items = Mcp.list_all()
            >>> print(f"Registered {len(items['tools'])} tools")
        """
        from .registry import default_registry
        return default_registry.list_all()
