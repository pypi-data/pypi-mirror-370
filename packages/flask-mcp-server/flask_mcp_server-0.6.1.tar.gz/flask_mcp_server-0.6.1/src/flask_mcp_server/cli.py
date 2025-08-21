"""
Command Line Interface (CLI) for Flask MCP Server.

This module provides a command-line interface for running and managing
Flask MCP servers. It supports both HTTP and STDIO modes, as well as
utilities for listing registered MCP items.

The CLI supports loading custom registries from Python modules, making it
easy to deploy MCP servers with different configurations and tool sets.

Usage Examples:
    # Start HTTP server with default registry
    flask-mcp serve-http

    # Start HTTP server with custom registry
    flask-mcp serve-http --module mypackage.registry:my_registry

    # Start STDIO server
    flask-mcp serve-stdio

    # List all registered items
    flask-mcp list
"""

from __future__ import annotations
import importlib
import json
import typer
from typing import Optional

# Import server components
from .server_http import create_app      # HTTP server factory
from .server_stdio import stdio_serve    # STDIO server function
from .registry import MCPRegistry, default_registry  # Registry management

# Create the main CLI application
app = typer.Typer(
    help="Flask MCP Server CLI - Command line interface for running MCP servers",
    add_completion=False,  # Disable shell completion for simplicity
    rich_markup_mode="rich"  # Enable rich text formatting in help
)


def _load_registry(module: Optional[str]) -> MCPRegistry:
    """
    Load an MCP registry from a Python module.

    This function supports loading registries from modules using the format:
    - "module_name" - loads the 'registry' attribute from the module
    - "module_name:attribute" - loads the specified attribute from the module

    Args:
        module: Module specification string, or None to use default registry

    Returns:
        MCPRegistry instance, either loaded from module or default registry

    Examples:
        >>> _load_registry("myapp.tools")  # loads myapp.tools.registry
        >>> _load_registry("myapp.tools:custom_registry")  # loads myapp.tools.custom_registry
        >>> _load_registry(None)  # returns default_registry
    """
    # Use default registry if no module specified
    if not module:
        return default_registry

    # Parse module specification (module:attribute format)
    module_name, _, attribute_name = module.partition(":")

    try:
        # Import the specified module
        imported_module = importlib.import_module(module_name)

        # Get the registry attribute (specified or default 'registry')
        if attribute_name:
            registry = getattr(imported_module, attribute_name)
        else:
            # Try to get 'registry' attribute, fallback to default if not found
            registry = getattr(imported_module, "registry", default_registry)

        # Validate that the loaded object is actually an MCPRegistry
        if not isinstance(registry, MCPRegistry):
            typer.echo(f"Warning: {module} does not contain a valid MCPRegistry, using default", err=True)
            return default_registry

        return registry

    except ImportError as e:
        typer.echo(f"Error: Could not import module '{module_name}': {e}", err=True)
        return default_registry
    except AttributeError as e:
        typer.echo(f"Error: Could not find attribute in module '{module}': {e}", err=True)
        return default_registry


@app.command("serve-http")
def serve_http(
    module: Optional[str] = typer.Option(
        None,
        "--module", "-m",
        help="Python module containing MCP registry (format: module or module:attribute)"
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host", "-h",
        help="Host address to bind the server to"
    ),
    port: int = typer.Option(
        8765,
        "--port", "-p",
        help="Port number to bind the server to"
    )
):
    """
    Start an HTTP MCP server.

    This command starts a Flask-based HTTP server that implements the Model Context
    Protocol (MCP). The server provides JSON-RPC endpoints for tools, resources,
    prompts, and completion providers.

    The server supports:
    - JSON-RPC 2.0 protocol
    - Server-Sent Events (SSE) for streaming responses
    - Authentication (API key, HMAC)
    - Rate limiting and caching
    - Health checks and metrics
    - OpenAPI documentation

    Examples:
        flask-mcp serve-http
        flask-mcp serve-http --host 0.0.0.0 --port 8080
        flask-mcp serve-http --module myapp.tools:registry
    """
    # Load the specified registry or use default
    registry = _load_registry(module)

    # Display startup information
    typer.echo(f"Starting HTTP MCP server...")
    typer.echo(f"Host: {host}")
    typer.echo(f"Port: {port}")
    typer.echo(f"Registry: {len(registry.tools)} tools, {len(registry.resources)} resources, "
               f"{len(registry.prompts)} prompts, {len(registry.completions)} completions")

    # Create and run the Flask application
    flask_app = create_app(registry=registry)
    flask_app.run(host=host, port=port, debug=False)


@app.command("serve-stdio")
def serve_stdio_cmd(
    module: Optional[str] = typer.Option(
        None,
        "--module", "-m",
        help="Python module containing MCP registry (format: module or module:attribute)"
    )
):
    """
    Start a STDIO MCP server.

    This command starts a STDIO-based MCP server that communicates over standard
    input/output streams. This mode is typically used when the MCP server is
    launched as a subprocess by an MCP client.

    The STDIO server:
    - Reads JSON-RPC requests from stdin
    - Writes JSON-RPC responses to stdout
    - Supports the same MCP protocol as the HTTP server
    - Is suitable for process-based communication

    Examples:
        flask-mcp serve-stdio
        flask-mcp serve-stdio --module myapp.tools:registry
    """
    # Load the specified registry or use default
    registry = _load_registry(module)

    # Display startup information to stderr (stdout is used for protocol communication)
    typer.echo(f"Starting STDIO MCP server...", err=True)
    typer.echo(f"Registry: {len(registry.tools)} tools, {len(registry.resources)} resources, "
               f"{len(registry.prompts)} prompts, {len(registry.completions)} completions", err=True)

    # Start the STDIO server (this will block until the process is terminated)
    stdio_serve(registry=registry)


@app.command("list")
def list_items(
    module: Optional[str] = typer.Option(
        None,
        "--module", "-m",
        help="Python module containing MCP registry (format: module or module:attribute)"
    ),
    format_output: bool = typer.Option(
        True,
        "--format/--no-format",
        help="Format JSON output with indentation"
    )
):
    """
    List all registered MCP items.

    This command displays all tools, resources, prompts, and completion providers
    registered in the specified MCP registry. The output is in JSON format and
    includes metadata about each registered item.

    The output includes:
    - Tools: Available tool functions with their schemas
    - Resources: Available resource providers with their schemas
    - Prompts: Available prompt templates with their schemas
    - Completions: Available completion providers with their schemas

    Examples:
        flask-mcp list
        flask-mcp list --module myapp.tools:registry
        flask-mcp list --no-format  # Compact JSON output
    """
    # Load the specified registry or use default
    registry = _load_registry(module)

    # Get all registered items
    all_items = registry.list_all()

    # Format and display the output
    if format_output:
        # Pretty-printed JSON with indentation
        output = json.dumps(all_items, ensure_ascii=False, indent=2)
    else:
        # Compact JSON output
        output = json.dumps(all_items, ensure_ascii=False)

    # Print to stdout
    print(output)
