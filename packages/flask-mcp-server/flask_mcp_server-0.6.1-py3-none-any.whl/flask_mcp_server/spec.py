"""
MCP specification version management.

This module provides access to the MCP specification version
from the centralized version management system.
"""

from .__version__ import get_mcp_spec_version

# Import the MCP spec version from centralized version management
MCP_SPEC_VERSION = get_mcp_spec_version()
