"""
Event System for Flask MCP Server.

This module provides an event bus system for inter-component communication
within the MCP server. It supports both local (in-process) events using
the Blinker library and distributed events using Redis pub/sub.

The event system is used for:
- Notifying components when the registry changes
- Coordinating between different parts of the application
- Supporting distributed deployments with multiple server instances
- Real-time updates for Server-Sent Events (SSE) clients

Events Supported:
- registry_changed: Fired when tools, resources, prompts, or completions are added/removed

Example Usage:
    >>> from flask_mcp_server.events import default_bus
    >>>
    >>> # Subscribe to registry changes
    >>> @default_bus.registry_changed.connect
    >>> def on_registry_changed(sender, **kwargs):
    ...     print(f"Registry changed: {kwargs}")
    >>>
    >>> # Publish a registry change event
    >>> default_bus.publish_registry_changed({"action": "tool_added", "name": "my_tool"})
"""

from __future__ import annotations
import os
import json
import logging
from typing import Optional, Dict, Any
from blinker import Signal

# Set up logging for event operations
logger = logging.getLogger(__name__)


class EventBus:
    """
    Event bus for inter-component communication.

    This class provides both local and distributed event publishing capabilities.
    Local events use the Blinker library for in-process communication, while
    distributed events use Redis pub/sub for multi-instance deployments.

    The event bus automatically configures Redis support based on environment
    variables, falling back to local-only events if Redis is not available.
    """

    def __init__(self) -> None:
        """
        Initialize the event bus.

        Sets up local event signals and optionally configures Redis for
        distributed events based on environment variables.

        Environment Variables:
            FLASK_MCP_SSE_BACKEND: Set to "redis" to enable Redis pub/sub
            FLASK_MCP_REDIS_URL: Redis connection URL (default: redis://localhost:6379/0)
        """
        # Initialize local event signals using Blinker
        self.registry_changed = Signal("registry_changed")
        logger.debug("Initialized local event signals")

        # Initialize Redis connection for distributed events (optional)
        self._redis: Optional[Any] = None
        self._setup_redis()

    def _setup_redis(self) -> None:
        """
        Set up Redis connection for distributed events.

        This method checks environment variables and attempts to establish
        a Redis connection if distributed events are enabled.
        """
        if os.getenv("FLASK_MCP_SSE_BACKEND") == "redis":
            try:
                import redis
                redis_url = os.getenv("FLASK_MCP_REDIS_URL", "redis://localhost:6379/0")
                self._redis = redis.from_url(redis_url)

                # Test the connection
                self._redis.ping()
                logger.info(f"Redis event backend initialized: {redis_url}")

            except ImportError:
                logger.warning("Redis backend requested but redis package not installed")
                self._redis = None
            except Exception as e:
                logger.warning(f"Failed to initialize Redis event backend: {e}")
                self._redis = None
        else:
            logger.debug("Redis event backend not configured, using local events only")

    def publish_registry_changed(self, payload: Dict[str, Any]) -> None:
        """
        Publish a registry changed event.

        This method publishes the event both locally (using Blinker signals)
        and to Redis (if configured) for distributed event handling.

        Args:
            payload: Event payload containing details about the registry change
                    Expected keys: action, name, type, etc.

        Example:
            >>> bus.publish_registry_changed({
            ...     "action": "tool_added",
            ...     "name": "my_tool",
            ...     "type": "tool"
            ... })
        """
        # Publish local event using Blinker
        try:
            self.registry_changed.send(self, payload=payload)
            logger.debug(f"Published local registry_changed event: {payload}")
        except Exception as e:
            logger.error(f"Failed to publish local registry_changed event: {e}")

        # Publish distributed event using Redis (if available)
        if self._redis:
            try:
                event_data = {
                    "type": "registry.changed",
                    "payload": payload,
                    "timestamp": int(time.time())
                }

                # Serialize to JSON for Redis pub/sub
                event_json = json.dumps(event_data, ensure_ascii=False)

                # Publish to Redis channel
                self._redis.publish("flask_mcp_events", event_json)
                logger.debug(f"Published Redis registry_changed event: {payload}")

            except Exception as e:
                logger.warning(f"Failed to publish Redis registry_changed event: {e}")
                # Don't fail the operation if Redis publishing fails

    def subscribe_registry_changed(self, callback) -> None:
        """
        Subscribe to registry changed events.

        Args:
            callback: Function to call when registry changes occur
                     Signature: callback(sender, payload=dict)

        Example:
            >>> def on_change(sender, payload=None):
            ...     print(f"Registry changed: {payload}")
            >>>
            >>> bus.subscribe_registry_changed(on_change)
        """
        self.registry_changed.connect(callback)
        logger.debug(f"Subscribed callback to registry_changed events: {callback}")

    def is_redis_available(self) -> bool:
        """
        Check if Redis backend is available and working.

        Returns:
            True if Redis is configured and responsive, False otherwise
        """
        if not self._redis:
            return False

        try:
            self._redis.ping()
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get event bus statistics and status.

        Returns:
            Dictionary containing event bus status information
        """
        return {
            "redis_available": self.is_redis_available(),
            "redis_url": os.getenv("FLASK_MCP_REDIS_URL", "redis://localhost:6379/0") if self._redis else None,
            "local_signals": {
                "registry_changed_receivers": len(self.registry_changed.receivers)
            }
        }


# Import time for timestamp generation
import time

# Global default event bus instance
# This is used throughout the MCP server for event communication
default_bus = EventBus()
