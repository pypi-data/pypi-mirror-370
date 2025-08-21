"""
Dependency Injection Container for Flask MCP Server.

This module provides a simple dependency injection container that supports
both singleton instances and factory functions. It's used throughout the
MCP server to manage dependencies and provide a clean separation of concerns.

The container supports:
- Singleton instances: Objects that are created once and reused
- Factory functions: Functions that create new instances on demand
- Lazy initialization: Factory functions are called only when needed

Example Usage:
    >>> container = Container()
    >>>
    >>> # Register a singleton value
    >>> container.set("config", {"debug": True})
    >>>
    >>> # Register a factory function
    >>> container.factory("database", lambda: create_database_connection())
    >>>
    >>> # Retrieve values (factory is called once and cached)
    >>> config = container.get("config")
    >>> db = container.get("database")  # Factory called here
    >>> db2 = container.get("database")  # Cached value returned
"""

from __future__ import annotations
from typing import Callable, Dict, Any


class Container:
    """
    Simple dependency injection container with singleton and factory support.

    This container manages dependencies using two strategies:
    1. Singletons: Pre-created or explicitly set values
    2. Factories: Functions that create values on first access

    All factory-created values are automatically cached as singletons
    after their first creation to ensure consistent behavior.
    """

    def __init__(self):
        """
        Initialize a new container.

        Creates empty storage for both singleton instances and factory functions.
        """
        # Storage for singleton instances (including factory-created ones)
        self._singletons: Dict[str, Any] = {}

        # Storage for factory functions that create instances on demand
        self._factories: Dict[str, Callable[[], Any]] = {}

    def set(self, name: str, value: Any) -> None:
        """
        Register a singleton value in the container.

        The value will be returned as-is whenever requested via get().
        This overwrites any existing singleton or factory with the same name.

        Args:
            name: Unique identifier for the dependency
            value: The singleton instance to store

        Example:
            >>> container.set("config", {"debug": True, "port": 8080})
            >>> container.set("logger", logging.getLogger(__name__))
        """
        self._singletons[name] = value

    def factory(self, name: str, fn: Callable[[], Any]) -> None:
        """
        Register a factory function in the container.

        The factory function will be called once when the dependency is first
        requested, and the result will be cached as a singleton for future requests.

        Args:
            name: Unique identifier for the dependency
            fn: Factory function that creates the dependency (takes no arguments)

        Example:
            >>> container.factory("database", lambda: create_db_connection())
            >>> container.factory("cache", lambda: MemoryTTLCache(max_size=1000))
        """
        self._factories[name] = fn

    def get(self, name: str) -> Any:
        """
        Retrieve a dependency from the container.

        This method follows a specific resolution order:
        1. Check if a singleton instance exists and return it
        2. Check if a factory function exists, call it, cache the result, and return it
        3. Raise KeyError if neither exists

        Args:
            name: Unique identifier for the dependency

        Returns:
            The dependency instance

        Raises:
            KeyError: If no singleton or factory is registered with the given name

        Example:
            >>> config = container.get("config")  # Returns singleton
            >>> db = container.get("database")    # Calls factory, caches result
            >>> db2 = container.get("database")   # Returns cached result
        """
        # First, check if we have a singleton instance
        if name in self._singletons:
            return self._singletons[name]

        # Next, check if we have a factory function
        if name in self._factories:
            # Call the factory function to create the instance
            instance = self._factories[name]()

            # Cache the created instance as a singleton for future requests
            self._singletons[name] = instance

            return instance

        # Neither singleton nor factory found
        raise KeyError(f"No dependency registered with name '{name}'")

    def has(self, name: str) -> bool:
        """
        Check if a dependency is registered in the container.

        Args:
            name: Unique identifier for the dependency

        Returns:
            True if the dependency is registered (as singleton or factory), False otherwise
        """
        return name in self._singletons or name in self._factories

    def clear(self) -> None:
        """
        Clear all registered dependencies.

        This removes both singleton instances and factory functions.
        Useful for testing or resetting the container state.
        """
        self._singletons.clear()
        self._factories.clear()


# Global default container instance
# This is used throughout the MCP server for dependency management
default_container = Container()
