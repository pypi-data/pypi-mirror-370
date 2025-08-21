"""
Flask MCP Server - Model Context Protocol (MCP) server implementation for Flask.

This package provides a comprehensive implementation of the Model Context Protocol (MCP)
server using Flask as the web framework. It includes tools, resources, prompts, and
completion providers with robust security, caching, and error handling.

Key Features:
- JSON-RPC 2.0 compliant MCP server
- Tool, resource, prompt, and completion provider registry
- Multiple authentication modes (none, API key, HMAC)
- Rate limiting and caching with automatic cleanup
- Comprehensive input validation and error handling
- Thread-safe operations with memory management
- OpenAPI documentation generation
- Health checks and metrics endpoints

Example Usage:
    >>> from flask_mcp_server import MCPRegistry, create_app, tool
    >>>
    >>> registry = MCPRegistry()
    >>>
    >>> @registry.tool("add_numbers", "Add two numbers together")
    >>> def add_numbers(a: int, b: int) -> int:
    ...     return a + b
    >>>
    >>> app = create_app(registry)
    >>> app.run()
"""

# Core registry and decorators - Main components for registering MCP items
from .registry import (
    MCPRegistry,        # Main registry for tools, resources, prompts, completions
    default_registry,   # Global default registry instance
    tool,              # Decorator for registering tools
    resource,          # Decorator for registering resources
    prompt,            # Decorator for registering prompts
    completion_provider # Decorator for registering completion providers
)

# Server components - HTTP and STDIO server implementations
from .server_http import create_app      # Create Flask app with MCP endpoints
from .server_stdio import stdio_serve    # STDIO-based MCP server
from .sessions import make_session_store # Session management factory
from .http_integrated import mount_mcp   # Mount MCP on existing Flask app

# Discovery and resources - Dynamic discovery and resource management
from .discovery import discover_package, DiscoveryCache  # Package discovery utilities
from .resources import Resource, ResourceTemplate        # Resource management classes

# Events and containers - Event system and dependency injection
from .events import EventBus, default_bus              # Event bus for inter-component communication
from .container import Container, default_container    # Dependency injection container

# Service providers and facade - Service management and simplified API
from .providers import ServiceProvider, load_providers  # Service provider pattern
from .facade import Mcp                                # Simplified facade API

# Version and spec - Version management and MCP specification
from .__version__ import __version__, get_version, get_version_info  # Version utilities
from .spec import MCP_SPEC_VERSION                                   # MCP specification version

# Exceptions and validation - Error handling and input validation
from .validation import ValidationError as MCPValidationError  # Input validation errors
from .exceptions import (
    MCPError,                           # Base MCP error class
    AuthenticationError,                # Authentication failures
    AuthorizationError,                 # Authorization failures
    RateLimitError,                     # Rate limiting errors
    ToolNotFoundError,                  # Tool not found errors
    ResourceNotFoundError,              # Resource not found errors
    PromptNotFoundError,                # Prompt not found errors
    CompletionProviderNotFoundError,    # Completion provider not found errors
    ToolExecutionError                  # Tool execution errors
)

# Public API exports - All components available for import
__all__ = [
    # Core registry and decorators - Main components for MCP item registration
    "MCPRegistry",           # Main registry class for managing MCP items
    "default_registry",      # Global default registry instance
    "tool",                  # Decorator for registering tool functions
    "resource",              # Decorator for registering resource functions
    "prompt",                # Decorator for registering prompt functions
    "completion_provider",   # Decorator for registering completion providers

    # Server components - HTTP and STDIO server implementations
    "create_app",            # Factory function to create Flask app with MCP endpoints
    "stdio_serve",           # Function to start STDIO-based MCP server
    "make_session_store",    # Factory function for session storage
    "mount_mcp",             # Function to mount MCP endpoints on existing Flask app

    # Discovery and resources - Dynamic discovery and resource management
    "discover_package",      # Function to discover MCP items in Python packages
    "DiscoveryCache",        # Cache for discovered packages
    "Resource",              # Base class for MCP resources
    "ResourceTemplate",      # Template class for parameterized resources

    # Events and containers - Event system and dependency injection
    "EventBus",              # Event bus for inter-component communication
    "default_bus",           # Global default event bus instance
    "Container",             # Dependency injection container
    "default_container",     # Global default container instance

    # Service providers and facade - Service management and simplified API
    "ServiceProvider",       # Base class for service providers
    "load_providers",        # Function to load service providers
    "Mcp",                   # Simplified facade API for common operations

    # Version and spec - Version management and MCP specification
    "__version__",           # Package version string
    "get_version",           # Function to get package version
    "get_version_info",      # Function to get comprehensive version information
    "MCP_SPEC_VERSION",      # MCP specification version this package implements

    # Exceptions and validation - Error handling and input validation
    "MCPError",                           # Base exception class for MCP errors
    "AuthenticationError",                # Raised when authentication fails
    "AuthorizationError",                 # Raised when authorization fails
    "RateLimitError",                     # Raised when rate limits are exceeded
    "ToolNotFoundError",                  # Raised when requested tool is not found
    "ResourceNotFoundError",              # Raised when requested resource is not found
    "PromptNotFoundError",                # Raised when requested prompt is not found
    "CompletionProviderNotFoundError",    # Raised when completion provider is not found
    "ToolExecutionError",                 # Raised when tool execution fails
    "MCPValidationError"                  # Raised when input validation fails
]
