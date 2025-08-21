"""
Package Discovery System for Flask MCP Server.

This module provides functionality to automatically discover and import MCP-related
modules from Python packages. It includes caching mechanisms to improve performance
and avoid redundant imports during development.

The discovery system is useful for:
- Automatically loading all MCP tools from a package
- Development workflows where modules are frequently added/modified
- Plugin systems where MCP items are distributed across multiple modules
- Large codebases with many MCP-related modules

Example Usage:
    >>> from flask_mcp_server.discovery import discover_package, DiscoveryCache
    >>>
    >>> # Discover all modules in a package
    >>> discover_package("myapp.tools")
    >>>
    >>> # Use caching for better performance
    >>> cache = DiscoveryCache("my_discovery_cache.json")
    >>> discover_package("myapp.tools", cache=cache)
"""

from __future__ import annotations
import importlib
import pkgutil
import json
import os
import time
import logging
from typing import Optional, List, Dict, Any

# Set up logging for discovery operations
logger = logging.getLogger(__name__)


class DiscoveryCache:
    """
    File-based cache for package discovery results.

    This cache stores information about discovered packages and their modules
    to avoid redundant imports and improve performance during development.
    The cache includes timestamps to track when packages were last discovered.
    """

    def __init__(self, path: str = ".flask_mcp_discovery.json"):
        """
        Initialize the discovery cache.

        Args:
            path: File path for the cache file (default: .flask_mcp_discovery.json)
        """
        self.path = path

    def load(self) -> Dict[str, Any]:
        """
        Load cached discovery data from file.

        Returns:
            Dictionary containing cached discovery data, or empty dict if file
            doesn't exist or cannot be read

        The returned dictionary has the format:
        {
            "package_name": {
                "modules": ["module1", "module2", ...],
                "timestamp": 1234567890
            }
        }
        """
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.debug(f"Loaded discovery cache from {self.path}")
                    return data
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load discovery cache from {self.path}: {e}")
                return {}
        return {}

    def save(self, data: Dict[str, Any]) -> None:
        """
        Save discovery data to cache file.

        Args:
            data: Dictionary containing discovery data to cache

        Raises:
            IOError: If the cache file cannot be written
        """
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                logger.debug(f"Saved discovery cache to {self.path}")
        except IOError as e:
            logger.error(f"Failed to save discovery cache to {self.path}: {e}")
            raise

    def is_fresh(self, package: str, max_age_seconds: int = 3600) -> bool:
        """
        Check if cached data for a package is still fresh.

        Args:
            package: Package name to check
            max_age_seconds: Maximum age in seconds before cache is considered stale

        Returns:
            True if cached data exists and is fresh, False otherwise
        """
        data = self.load()
        if package not in data:
            return False

        package_data = data[package]
        if "timestamp" not in package_data:
            return False

        age = time.time() - package_data["timestamp"]
        return age < max_age_seconds

    def get_modules(self, package: str) -> List[str]:
        """
        Get cached module list for a package.

        Args:
            package: Package name

        Returns:
            List of module names, or empty list if not cached
        """
        data = self.load()
        if package in data and "modules" in data[package]:
            return data[package]["modules"]
        return []


def discover_package(
    pkg: str,
    cache: Optional[DiscoveryCache] = None,
    force_refresh: bool = False
) -> List[str]:
    """
    Discover and import all modules in a Python package.

    This function recursively walks through a package and imports all its modules.
    This is useful for ensuring that all MCP decorators (@tool, @resource, etc.)
    are executed and their items are registered in the global registry.

    Args:
        pkg: Package name to discover (e.g., "myapp.tools")
        cache: Optional cache instance for storing discovery results
        force_refresh: If True, ignore cache and force fresh discovery

    Returns:
        List of discovered module names

    Raises:
        ImportError: If the package cannot be imported

    Example:
        >>> # Discover all modules in a package
        >>> modules = discover_package("myapp.tools")
        >>> print(f"Discovered {len(modules)} modules")

        >>> # Use caching for better performance
        >>> cache = DiscoveryCache()
        >>> modules = discover_package("myapp.tools", cache=cache)
    """
    logger.info(f"Starting discovery for package: {pkg}")

    # Check cache first (unless force refresh is requested)
    if cache and not force_refresh and cache.is_fresh(pkg):
        cached_modules = cache.get_modules(pkg)
        logger.info(f"Using cached discovery for {pkg}: {len(cached_modules)} modules")
        return cached_modules

    discovered_modules = []

    try:
        # Import the main package
        main_module = importlib.import_module(pkg)
        logger.debug(f"Successfully imported main package: {pkg}")

        # Check if this is a package (has __path__) or a single module
        if hasattr(main_module, '__path__'):
            # This is a package - walk through all submodules
            logger.debug(f"Package {pkg} has __path__, walking submodules...")

            for module_info in pkgutil.walk_packages(
                main_module.__path__,
                main_module.__name__ + "."
            ):
                try:
                    # Import each discovered module
                    importlib.import_module(module_info.name)
                    discovered_modules.append(module_info.name)
                    logger.debug(f"Successfully imported module: {module_info.name}")

                except ImportError as e:
                    logger.warning(f"Failed to import module {module_info.name}: {e}")
                    # Continue with other modules even if one fails
                    continue

        else:
            # This is a single module, not a package
            discovered_modules.append(pkg)
            logger.debug(f"Package {pkg} is a single module")

    except ImportError as e:
        logger.error(f"Failed to import package {pkg}: {e}")
        raise ImportError(f"Cannot discover package '{pkg}': {e}")

    logger.info(f"Discovery completed for {pkg}: {len(discovered_modules)} modules")

    # Update cache if provided
    if cache:
        try:
            cache_data = cache.load()
            cache_data[pkg] = {
                "modules": discovered_modules,
                "timestamp": int(time.time())
            }
            cache.save(cache_data)
            logger.debug(f"Updated cache for package {pkg}")
        except Exception as e:
            logger.warning(f"Failed to update cache for {pkg}: {e}")
            # Don't fail the discovery if cache update fails

    return discovered_modules


def discover_multiple_packages(
    packages: List[str],
    cache: Optional[DiscoveryCache] = None,
    force_refresh: bool = False
) -> Dict[str, List[str]]:
    """
    Discover multiple packages in a single operation.

    Args:
        packages: List of package names to discover
        cache: Optional cache instance for storing discovery results
        force_refresh: If True, ignore cache and force fresh discovery

    Returns:
        Dictionary mapping package names to their discovered modules

    Example:
        >>> packages = ["myapp.tools", "myapp.resources", "myapp.prompts"]
        >>> results = discover_multiple_packages(packages)
        >>> for pkg, modules in results.items():
        ...     print(f"{pkg}: {len(modules)} modules")
    """
    results = {}

    for package in packages:
        try:
            modules = discover_package(package, cache=cache, force_refresh=force_refresh)
            results[package] = modules
        except ImportError as e:
            logger.error(f"Failed to discover package {package}: {e}")
            results[package] = []

    return results
