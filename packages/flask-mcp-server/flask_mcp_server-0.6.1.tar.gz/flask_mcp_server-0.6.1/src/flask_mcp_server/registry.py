"""
MCP Registry - Core component for managing MCP tools, resources, prompts, and completions.

This module provides the central registry system for the Flask MCP Server. The registry
manages all MCP items (tools, resources, prompts, completion providers) and provides
thread-safe access to them. It also handles caching, role-based access control,
and event publishing for registry changes.

The registry is the heart of the MCP server, responsible for:
- Registering and storing MCP items with their metadata
- Providing thread-safe access to registered items
- Enforcing role-based access control
- Caching results with configurable TTL
- Publishing events when the registry changes
- Generating JSON schemas for input/output validation

Example Usage:
    >>> from flask_mcp_server import MCPRegistry
    >>>
    >>> registry = MCPRegistry()
    >>>
    >>> # Register a tool
    >>> @registry.tool("add_numbers", "Add two numbers together")
    >>> def add_numbers(a: int, b: int) -> int:
    ...     return a + b
    >>>
    >>> # Register a resource
    >>> @registry.resource("user_data", "Get user information")
    >>> def get_user_data(user_id: str) -> dict:
    ...     return {"id": user_id, "name": f"User {user_id}"}
    >>>
    >>> # Call registered items
    >>> result = registry.call_tool("add_numbers", a=5, b=3)
    >>> user = registry.get_resource("user_data", user_id="123")
"""

from __future__ import annotations
import inspect
import threading
import hashlib
import json
import logging
from typing import Any, Callable, Dict, Optional, List, Union
from .schemas import build_input_schema, build_output_schema
from .events import default_bus
from .caching import make_cache

# Set up logging for registry operations
logger = logging.getLogger(__name__)


class MCPRegistry:
    """
    Thread-safe registry for MCP tools, resources, prompts, and completion providers.

    The registry maintains separate collections for each type of MCP item and provides
    methods for registration, retrieval, and execution. All operations are thread-safe
    and support role-based access control and caching.

    Features:
    - Thread-safe operations with RLock
    - Automatic schema generation from function signatures
    - Role-based access control
    - Result caching with configurable TTL
    - Event publishing for registry changes
    - Comprehensive error handling
    """
    def __init__(self) -> None:
        """
        Initialize a new MCP registry.

        Creates empty collections for all MCP item types and sets up
        thread-safe access control and caching.
        """
        # Thread-safe lock for all registry operations
        self._lock = threading.RLock()

        # Storage for different types of MCP items
        self.tools: Dict[str, Dict[str, Any]] = {}          # Tool functions with metadata
        self.resources: Dict[str, Dict[str, Any]] = {}      # Resource providers with metadata
        self.prompts: Dict[str, Dict[str, Any]] = {}        # Prompt generators with metadata
        self.completions: Dict[str, Callable[..., Any]] = {} # Completion providers (simpler storage)

        # Shared cache for all registry operations
        self.cache = make_cache()

        logger.debug("Initialized new MCP registry")

    def register_tool(
        self,
        name: str,
        fn: Callable[..., Any],
        desc: Optional[str] = None,
        roles: Optional[List[str]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Register a tool function in the registry.

        Tools are functions that can be called by MCP clients to perform actions.
        They are automatically introspected to generate input/output schemas.

        Args:
            name: Unique name for the tool
            fn: Function to register as a tool
            desc: Human-readable description (defaults to function docstring)
            roles: List of roles required to access this tool (empty = public)
            ttl: Cache TTL in seconds for tool results (None = no caching)

        Example:
            >>> def add_numbers(a: int, b: int) -> int:
            ...     '''Add two numbers together'''
            ...     return a + b
            >>>
            >>> registry.register_tool("add", add_numbers, roles=["user"], ttl=60)
        """
        with self._lock:
            # Store tool metadata and function
            self.tools[name] = {
                "name": name,
                "description": desc or (inspect.getdoc(fn) or "No description available"),
                "callable": fn,
                "input_schema": build_input_schema(fn),   # Auto-generate from function signature
                "output_schema": build_output_schema(fn), # Auto-generate from return annotation
                "roles": roles or [],                     # Empty list means public access
                "ttl": ttl,                              # Cache TTL in seconds
            }

            logger.info(f"Registered tool: {name}")

        # Publish registry change event
        default_bus.publish_registry_changed({
            "event": "registry.changed",
            "reason": "tool.register",
            "name": name,
            "type": "tool"
        })

    def register_resource(
        self,
        name: str,
        getter: Callable[..., Any],
        desc: Optional[str] = None,
        roles: Optional[List[str]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Register a resource provider in the registry.

        Resources provide data or content that can be retrieved by MCP clients.
        They are functions that return data based on input parameters.

        Args:
            name: Unique name for the resource
            getter: Function that provides the resource data
            desc: Human-readable description (defaults to function docstring)
            roles: List of roles required to access this resource (empty = public)
            ttl: Cache TTL in seconds for resource results (None = no caching)

        Example:
            >>> def get_user_profile(user_id: str) -> dict:
            ...     '''Get user profile information'''
            ...     return {"id": user_id, "name": f"User {user_id}"}
            >>>
            >>> registry.register_resource("user_profile", get_user_profile, ttl=300)
        """
        with self._lock:
            # Store resource metadata and getter function
            self.resources[name] = {
                "name": name,
                "description": desc or (inspect.getdoc(getter) or "No description available"),
                "getter": getter,
                "output_schema": build_output_schema(getter), # Auto-generate from return annotation
                "roles": roles or [],                         # Empty list means public access
                "ttl": ttl,                                  # Cache TTL in seconds
            }

            logger.info(f"Registered resource: {name}")

        # Publish registry change event
        default_bus.publish_registry_changed({
            "event": "registry.changed",
            "reason": "resource.register",
            "name": name,
            "type": "resource"
        })

    def register_prompt(
        self,
        name: str,
        provider: Callable[..., Any],
        desc: Optional[str] = None,
        roles: Optional[List[str]] = None
    ) -> None:
        """
        Register a prompt provider in the registry.

        Prompts are templates or generators for creating prompts for language models.
        They can be parameterized to generate different prompts based on input.

        Args:
            name: Unique name for the prompt
            provider: Function that generates prompt content
            desc: Human-readable description (defaults to function docstring)
            roles: List of roles required to access this prompt (empty = public)

        Example:
            >>> def code_review_prompt(code: str, language: str) -> str:
            ...     '''Generate a code review prompt'''
            ...     return f"Please review this {language} code:\\n\\n{code}"
            >>>
            >>> registry.register_prompt("code_review", code_review_prompt)
        """
        with self._lock:
            # Store prompt metadata and provider function
            self.prompts[name] = {
                "name": name,
                "description": desc or (inspect.getdoc(provider) or "No description available"),
                "provider": provider,
                "output_schema": build_output_schema(provider), # Auto-generate from return annotation
                "roles": roles or [],                           # Empty list means public access
            }

            logger.info(f"Registered prompt: {name}")

        # Publish registry change event
        default_bus.publish_registry_changed({
            "event": "registry.changed",
            "reason": "prompt.register",
            "name": name,
            "type": "prompt"
        })

    def register_completion(
        self,
        name: str,
        provider: Callable[..., Any],
        roles: Optional[List[str]] = None
    ) -> None:
        """
        Register a completion provider in the registry.

        Completion providers offer autocomplete suggestions for various contexts.
        They typically take a prefix string and return a list of possible completions.

        Args:
            name: Unique name for the completion provider
            provider: Function that provides completion suggestions
            roles: List of roles required to access this provider (empty = public)

        Note:
            Completion providers use simplified storage compared to other MCP items.
            Role-based access control is not currently implemented for completions.

        Example:
            >>> def file_completion(prefix: str = "") -> list:
            ...     '''Complete file names'''
            ...     import os
            ...     return [f for f in os.listdir('.') if f.startswith(prefix)]
            >>>
            >>> registry.register_completion("files", file_completion)
        """
        with self._lock:
            # Store completion provider (simplified storage for now)
            # TODO: Implement full metadata storage with role support
            self.completions[name] = provider

            logger.info(f"Registered completion provider: {name}")
            if roles:
                logger.warning(f"Role-based access control not yet implemented for completion provider: {name}")

        # Publish registry change event
        default_bus.publish_registry_changed({
            "event": "registry.changed",
            "reason": "completion.register",
            "name": name,
            "type": "completion"
        })

    def list_all(self) -> Dict[str, Any]:
        """
        List all registered MCP items with their metadata.

        Returns a dictionary containing all tools, resources, prompts, and
        completion providers registered in this registry. Function objects
        are excluded from the output to ensure JSON serializability.

        Returns:
            Dictionary with keys: tools, resources, prompts, completions, version
            Each section contains metadata about registered items

        Example:
            >>> items = registry.list_all()
            >>> print(f"Found {len(items['tools'])} tools")
            >>> for tool_name, tool_info in items['tools'].items():
            ...     print(f"  {tool_name}: {tool_info['description']}")
        """
        with self._lock:
            return {
                # Tools: Include all metadata except the callable function
                "tools": {
                    name: {key: value for key, value in metadata.items() if key != 'callable'}
                    for name, metadata in self.tools.items()
                },
                # Resources: Include all metadata except the getter function
                "resources": {
                    name: {key: value for key, value in metadata.items() if key != 'getter'}
                    for name, metadata in self.resources.items()
                },
                # Prompts: Include all metadata except the provider function
                "prompts": {
                    name: {key: value for key, value in metadata.items() if key != 'provider'}
                    for name, metadata in self.prompts.items()
                },
                # Completions: Simple list of names (no metadata stored currently)
                "completions": list(self.completions.keys()),
                # Version information
                "version": "0.6.1",  # TODO: Use centralized version from __version__.py
            }

    def _permits(self, item_roles: List[str], caller_roles: List[str]) -> bool:
        """
        Check if caller roles permit access to an item.

        This method implements role-based access control by checking if the caller
        has any of the roles required by the item. Items with no required roles
        are considered public and accessible to everyone.

        Args:
            item_roles: List of roles required to access the item
            caller_roles: List of roles possessed by the caller

        Returns:
            True if access is permitted, False otherwise

        Access Rules:
            - If item has no required roles (empty list), access is always permitted
            - If caller has any role that matches item's required roles, access is permitted
            - Otherwise, access is denied
        """
        # Public items (no required roles) are accessible to everyone
        if not item_roles:
            return True

        # Check if caller has any of the required roles
        return any(role in caller_roles for role in item_roles)

    def _cache_key(self, name: str, args: Dict[str, Any]) -> str:
        """
        Generate a cache key for the given item name and arguments.

        Creates a deterministic cache key by combining the item name with
        a hash of the arguments. This ensures that calls with the same
        arguments will hit the cache, while different arguments get
        separate cache entries.

        Args:
            name: Name of the item being cached
            args: Arguments passed to the item

        Returns:
            Cache key string in format "mcp:{name}:{args_hash}"

        Note:
            The arguments are JSON-serialized with sorted keys to ensure
            deterministic hashing regardless of argument order.
        """
        # Create deterministic JSON representation of arguments
        args_json = json.dumps(args, sort_keys=True, ensure_ascii=False)

        # Generate SHA256 hash of the arguments
        args_hash = hashlib.sha256(args_json.encode("utf-8")).hexdigest()

        # Combine into cache key
        return f"mcp:{name}:{args_hash}"

    def call_tool(self, name: str, caller_roles: Optional[List[str]] = None, **kwargs) -> Any:
        """
        Call a registered tool function.

        This method executes a tool function with the provided arguments,
        enforcing role-based access control and caching results if configured.

        Args:
            name: Name of the tool to call
            caller_roles: Roles of the caller for access control
            **kwargs: Arguments to pass to the tool function

        Returns:
            Result returned by the tool function

        Raises:
            KeyError: If the tool is not found
            PermissionError: If the caller lacks required roles
            Any exception raised by the tool function

        Example:
            >>> result = registry.call_tool("add_numbers", a=5, b=3)
            >>> print(result)  # 8
        """
        # Check if tool exists
        if name not in self.tools:
            logger.warning(f"Tool not found: {name}")
            raise KeyError(f"Tool '{name}' not found")

        item = self.tools[name]

        # Check role-based access control
        if not self._permits(item.get("roles", []), caller_roles or []):
            logger.warning(f"Access denied to tool '{name}' for roles: {caller_roles}")
            raise PermissionError("Access forbidden: insufficient roles")

        # Check if caching is enabled for this tool
        ttl = item.get("ttl")
        if ttl:
            # Generate cache key and check for cached result
            cache_key = self._cache_key("tool:" + name, kwargs)
            cached_result = self.cache.get(cache_key)

            if cached_result is not None:
                logger.debug(f"Cache hit for tool: {name}")
                return cached_result

            # Execute tool and cache the result
            logger.debug(f"Executing and caching tool: {name}")
            result = item["callable"](**kwargs)
            self.cache.set(cache_key, result, ttl)
            return result

        # Execute tool without caching
        logger.debug(f"Executing tool: {name}")
        return item["callable"](**kwargs)

    def get_resource(self, name: str, caller_roles: Optional[List[str]] = None, **kwargs) -> Any:
        """
        Get data from a registered resource provider.

        This method executes a resource getter function with the provided arguments,
        enforcing role-based access control and caching results if configured.

        Args:
            name: Name of the resource to get
            caller_roles: Roles of the caller for access control
            **kwargs: Arguments to pass to the resource getter function

        Returns:
            Data returned by the resource getter function

        Raises:
            KeyError: If the resource is not found
            PermissionError: If the caller lacks required roles
            Any exception raised by the resource getter function

        Example:
            >>> user_data = registry.get_resource("user_profile", user_id="123")
            >>> print(user_data)  # {"id": "123", "name": "User 123"}
        """
        # Check if resource exists
        if name not in self.resources:
            logger.warning(f"Resource not found: {name}")
            raise KeyError(f"Resource '{name}' not found")

        item = self.resources[name]

        # Check role-based access control
        if not self._permits(item.get("roles", []), caller_roles or []):
            logger.warning(f"Access denied to resource '{name}' for roles: {caller_roles}")
            raise PermissionError("Access forbidden: insufficient roles")

        # Check if caching is enabled for this resource
        ttl = item.get("ttl")
        if ttl:
            # Generate cache key and check for cached result
            cache_key = self._cache_key("resource:" + name, kwargs)
            cached_result = self.cache.get(cache_key)

            if cached_result is not None:
                logger.debug(f"Cache hit for resource: {name}")
                return cached_result

            # Execute resource getter and cache the result
            logger.debug(f"Executing and caching resource: {name}")
            result = item["getter"](**kwargs)
            self.cache.set(cache_key, result, ttl)
            return result

        # Execute resource getter without caching
        logger.debug(f"Executing resource: {name}")
        return item["getter"](**kwargs)

    def get_prompt(self, name: str, caller_roles: Optional[List[str]] = None, **kwargs) -> Any:
        """
        Get content from a registered prompt provider.

        This method executes a prompt provider function with the provided arguments,
        enforcing role-based access control. Prompts are not cached by default
        since they often generate dynamic content.

        Args:
            name: Name of the prompt to get
            caller_roles: Roles of the caller for access control
            **kwargs: Arguments to pass to the prompt provider function

        Returns:
            Prompt content returned by the provider function

        Raises:
            KeyError: If the prompt is not found
            PermissionError: If the caller lacks required roles
            Any exception raised by the prompt provider function

        Example:
            >>> prompt = registry.get_prompt("code_review", code="def hello(): pass", language="python")
            >>> print(prompt)  # "Please review this python code:\n\ndef hello(): pass"
        """
        # Check if prompt exists
        if name not in self.prompts:
            logger.warning(f"Prompt not found: {name}")
            raise KeyError(f"Prompt '{name}' not found")

        item = self.prompts[name]

        # Check role-based access control
        if not self._permits(item.get("roles", []), caller_roles or []):
            logger.warning(f"Access denied to prompt '{name}' for roles: {caller_roles}")
            raise PermissionError("Access forbidden: insufficient roles")

        # Execute prompt provider (no caching for prompts by default)
        logger.debug(f"Executing prompt: {name}")
        return item["provider"](**kwargs)

    def complete(self, name: str, caller_roles: Optional[List[str]] = None, **kwargs) -> Any:
        """
        Call a completion provider to get autocomplete suggestions.

        Args:
            name: Name of the completion provider to call
            caller_roles: Roles of the caller (for future role-based access control)
            **kwargs: Arguments to pass to the completion provider

        Returns:
            List of completion suggestions from the provider

        Raises:
            KeyError: If the completion provider is not found

        Note:
            Role-based access control is not currently implemented for completions.
            The caller_roles parameter is accepted for future compatibility.

        Example:
            >>> suggestions = registry.complete("files", prefix="test")
            >>> print(suggestions)  # ['test.py', 'test.txt', 'test_data.json']
        """
        if name not in self.completions:
            logger.warning(f"Completion provider not found: {name}")
            raise KeyError(f"Completion provider '{name}' not found")

        # TODO: Implement role-based access control for completions
        if caller_roles:
            logger.debug(f"Caller roles provided but not yet enforced for completion: {name}")

        try:
            logger.debug(f"Calling completion provider: {name}")
            result = self.completions[name](**kwargs)
            logger.debug(f"Completion provider returned {len(result) if isinstance(result, list) else 'non-list'} results")
            return result
        except Exception as e:
            logger.error(f"Completion provider failed: {name} - {e}")
            raise


# Global default registry instance
# This is used by the decorator functions and can be used directly for simple applications
default_registry = MCPRegistry()


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    roles: Optional[List[str]] = None,
    ttl: Optional[int] = None
):
    """
    Decorator to register a function as a tool in the default registry.

    This decorator provides a convenient way to register tool functions
    without needing to manage registry instances directly.

    Args:
        name: Tool name (defaults to function name)
        description: Human-readable description (defaults to function docstring)
        roles: List of roles required to access this tool
        ttl: Cache TTL in seconds for tool results

    Returns:
        Decorator function that registers the tool and returns the original function

    Example:
        >>> @tool("add_numbers", "Add two numbers together", ttl=60)
        >>> def add_numbers(a: int, b: int) -> int:
        ...     return a + b
    """
    def decorator(fn: Callable[..., Any]):
        # Use provided name or default to function name
        tool_name = name or fn.__name__

        # Register the tool with the default registry
        default_registry.register_tool(tool_name, fn, description, roles=roles, ttl=ttl)

        # Return the original function unchanged
        return fn

    return decorator


def resource(
    name: Optional[str] = None,
    description: Optional[str] = None,
    roles: Optional[List[str]] = None,
    ttl: Optional[int] = None
):
    """
    Decorator to register a function as a resource in the default registry.

    This decorator provides a convenient way to register resource functions
    without needing to manage registry instances directly.

    Args:
        name: Resource name (defaults to function name)
        description: Human-readable description (defaults to function docstring)
        roles: List of roles required to access this resource
        ttl: Cache TTL in seconds for resource results

    Returns:
        Decorator function that registers the resource and returns the original function

    Example:
        >>> @resource("user_profile", "Get user profile data", ttl=300)
        >>> def get_user_profile(user_id: str) -> dict:
        ...     return {"id": user_id, "name": f"User {user_id}"}
    """
    def decorator(fn: Callable[..., Any]):
        # Use provided name or default to function name
        resource_name = name or fn.__name__

        # Register the resource with the default registry
        default_registry.register_resource(resource_name, fn, description, roles=roles, ttl=ttl)

        # Return the original function unchanged
        return fn

    return decorator


def prompt(
    name: Optional[str] = None,
    description: Optional[str] = None,
    roles: Optional[List[str]] = None
):
    """
    Decorator to register a function as a prompt in the default registry.

    This decorator provides a convenient way to register prompt functions
    without needing to manage registry instances directly.

    Args:
        name: Prompt name (defaults to function name)
        description: Human-readable description (defaults to function docstring)
        roles: List of roles required to access this prompt

    Returns:
        Decorator function that registers the prompt and returns the original function

    Example:
        >>> @prompt("code_review", "Generate a code review prompt")
        >>> def code_review_prompt(code: str, language: str) -> str:
        ...     return f"Please review this {language} code:\\n\\n{code}"
    """
    def decorator(fn: Callable[..., Any]):
        # Use provided name or default to function name
        prompt_name = name or fn.__name__

        # Register the prompt with the default registry
        default_registry.register_prompt(prompt_name, fn, description, roles=roles)

        # Return the original function unchanged
        return fn

    return decorator


def completion_provider(
    name: Optional[str] = None,
    roles: Optional[List[str]] = None
):
    """
    Decorator to register a function as a completion provider in the default registry.

    This decorator provides a convenient way to register completion provider functions
    without needing to manage registry instances directly.

    Args:
        name: Completion provider name (defaults to function name)
        roles: List of roles required to access this completion provider

    Returns:
        Decorator function that registers the completion provider and returns the original function

    Example:
        >>> @completion_provider("file_names")
        >>> def complete_file_names(prefix: str = "") -> list:
        ...     import os
        ...     return [f for f in os.listdir('.') if f.startswith(prefix)]
    """
    def decorator(fn: Callable[..., Any]):
        # Use provided name or default to function name
        provider_name = name or fn.__name__

        # Register the completion provider with the default registry
        default_registry.register_completion(provider_name, fn, roles=roles)

        # Return the original function unchanged
        return fn

    return decorator
