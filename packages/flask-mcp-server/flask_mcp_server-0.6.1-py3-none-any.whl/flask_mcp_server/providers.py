"""
Service Provider System for Flask MCP Server.

This module implements a service provider pattern that allows for modular
registration of services, tools, resources, and other components. Service
providers offer a clean way to organize and bootstrap complex applications
with multiple components.

The service provider system supports:
- Dependency injection via the container
- Registry registration for MCP items
- Application bootstrapping with Flask integration
- Environment-based configuration
- Modular architecture for large applications

Example Usage:
    >>> from flask_mcp_server.providers import ServiceProvider, load_providers
    >>> from flask_mcp_server import Container, MCPRegistry
    >>>
    >>> class MyServiceProvider(ServiceProvider):
    ...     def register(self, container, registry):
    ...         # Register dependencies
    ...         container.set("my_service", MyService())
    ...
    ...         # Register MCP tools
    ...         @registry.tool("my_tool", "My custom tool")
    ...         def my_tool():
    ...             return "Hello from my tool!"
    ...
    ...     def boot(self, app, registry):
    ...         # Perform application-level initialization
    ...         app.config['MY_SETTING'] = 'configured'
    >>>
    >>> # Load providers
    >>> container = Container()
    >>> registry = MCPRegistry()
    >>> load_providers(container, registry, providers=["myapp.providers:MyServiceProvider"])
"""

from __future__ import annotations
import importlib
import os
import logging
from typing import List, Optional, Any, Union
from .container import Container
from .registry import MCPRegistry

# Set up logging for provider operations
logger = logging.getLogger(__name__)


class ServiceProvider:
    """
    Base class for service providers.

    Service providers are responsible for registering services and dependencies
    with the container and registry. They follow a two-phase initialization:

    1. register(): Register dependencies and services
    2. boot(): Perform application-level initialization (optional)

    This pattern allows for proper dependency resolution and initialization order.
    """

    def register(self, container: Container, registry: MCPRegistry) -> None:
        """
        Register services and dependencies.

        This method is called during the registration phase and should:
        - Register services with the dependency injection container
        - Register MCP tools, resources, prompts, and completions
        - Set up any required dependencies

        Args:
            container: Dependency injection container
            registry: MCP registry for tools, resources, etc.

        Example:
            >>> def register(self, container, registry):
            ...     # Register a service
            ...     container.set("database", DatabaseService())
            ...
            ...     # Register a tool
            ...     @registry.tool("query_db", "Query the database")
            ...     def query_db(sql: str) -> list:
            ...         db = container.get("database")
            ...         return db.execute(sql)
        """
        pass  # Default implementation does nothing

    def boot(self, app: Any, registry: MCPRegistry) -> None:
        """
        Perform application-level initialization.

        This method is called after all providers have been registered and
        should perform any application-level setup that requires the full
        application context.

        Args:
            app: Flask application instance (or None if not available)
            registry: MCP registry for tools, resources, etc.

        Example:
            >>> def boot(self, app, registry):
            ...     if app:
            ...         # Configure Flask app
            ...         app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
            ...
            ...         # Set up request hooks
            ...         @app.before_request
            ...         def setup_request():
            ...             # Initialize request-specific services
            ...             pass
        """
        pass  # Default implementation does nothing

    def get_name(self) -> str:
        """
        Get the provider name for logging and debugging.

        Returns:
            Provider name (defaults to class name)
        """
        return self.__class__.__name__


def load_providers(
    container: Container,
    registry: MCPRegistry,
    app: Optional[Any] = None,
    providers: Optional[List[str]] = None
) -> List[ServiceProvider]:
    """
    Load and initialize service providers.

    This function loads service providers from module paths and initializes
    them in two phases: registration and booting. Providers can be specified
    explicitly or loaded from environment variables.

    Args:
        container: Dependency injection container
        registry: MCP registry for tools, resources, etc.
        app: Optional Flask application instance
        providers: List of provider module paths, or None to use environment

    Returns:
        List of loaded and initialized service provider instances

    Environment Variables:
        FLASK_MCP_PROVIDERS: Comma-separated list of provider module paths

    Provider Path Format:
        - "module.path" - loads the "Provider" class from the module
        - "module.path:ClassName" - loads the specified class from the module

    Example:
        >>> # Load providers from environment
        >>> os.environ['FLASK_MCP_PROVIDERS'] = 'myapp.providers:DatabaseProvider,myapp.tools:ToolProvider'
        >>> providers = load_providers(container, registry, app)
        >>>
        >>> # Load providers explicitly
        >>> providers = load_providers(
        ...     container, registry, app,
        ...     providers=['myapp.providers:DatabaseProvider']
        ... )
    """
    # Get provider specifications from parameters or environment
    provider_specs = providers or _get_provider_specs_from_env()

    if not provider_specs:
        logger.info("No service providers configured")
        return []

    logger.info(f"Loading {len(provider_specs)} service providers")
    loaded_providers = []

    # Phase 1: Load and register all providers
    for spec in provider_specs:
        try:
            provider = _load_provider_from_spec(spec)
            logger.debug(f"Registering provider: {provider.get_name()}")

            # Call register method
            provider.register(container, registry)
            loaded_providers.append(provider)

            logger.info(f"Successfully registered provider: {provider.get_name()}")

        except Exception as e:
            logger.error(f"Failed to load/register provider '{spec}': {e}")
            # Continue with other providers even if one fails
            continue

    # Phase 2: Boot all successfully loaded providers
    if app is not None:
        for provider in loaded_providers:
            try:
                if hasattr(provider, "boot"):
                    logger.debug(f"Booting provider: {provider.get_name()}")
                    provider.boot(app, registry)
                    logger.debug(f"Successfully booted provider: {provider.get_name()}")
            except Exception as e:
                logger.error(f"Failed to boot provider '{provider.get_name()}': {e}")
                # Continue with other providers even if one fails
                continue

    logger.info(f"Successfully loaded {len(loaded_providers)} service providers")
    return loaded_providers


def _get_provider_specs_from_env() -> List[str]:
    """
    Get provider specifications from environment variables.

    Returns:
        List of provider specification strings
    """
    env_value = os.getenv("FLASK_MCP_PROVIDERS", "").strip()
    if not env_value:
        return []

    # Split by comma and clean up whitespace
    specs = [spec.strip() for spec in env_value.split(",") if spec.strip()]
    return specs


def _load_provider_from_spec(spec: str) -> ServiceProvider:
    """
    Load a service provider from a module specification.

    Args:
        spec: Provider specification in format "module" or "module:class"

    Returns:
        ServiceProvider instance

    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the class cannot be found
        TypeError: If the loaded object is not a ServiceProvider
    """
    # Parse the specification
    module_path, _, class_name = spec.partition(":")
    if not class_name:
        class_name = "Provider"  # Default class name

    # Import the module
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Cannot import provider module '{module_path}': {e}")

    # Get the provider class
    try:
        provider_class = getattr(module, class_name)
    except AttributeError as e:
        raise AttributeError(f"Cannot find provider class '{class_name}' in module '{module_path}': {e}")

    # Create provider instance
    if isinstance(provider_class, type):
        # It's a class, instantiate it
        provider_instance = provider_class()
    else:
        # It's already an instance or callable
        provider_instance = provider_class

    # Validate that it's a ServiceProvider
    if not isinstance(provider_instance, ServiceProvider):
        raise TypeError(f"Provider '{spec}' is not a ServiceProvider instance")

    return provider_instance
