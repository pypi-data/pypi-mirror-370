"""
Version management for flask-mcp-server.

This module provides a single source of truth for version information
across the entire package, preventing hardcoded version numbers.
"""

__version__ = "0.6.1"
__mcp_spec_version__ = "2025-06-18"

# Version information for API responses and documentation
VERSION_INFO = {
    "package_version": __version__,
    "mcp_spec_version": __mcp_spec_version__,
    "api_version": "1.0",  # Internal API version for compatibility tracking
}


def get_version() -> str:
    """Get the package version string."""
    return __version__


def get_mcp_spec_version() -> str:
    """Get the MCP specification version this package implements."""
    return __mcp_spec_version__


def get_version_info() -> dict:
    """Get comprehensive version information."""
    return VERSION_INFO.copy()
