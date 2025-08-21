"""
Logging Utilities for Flask MCP Server.

This module provides structured logging capabilities for the MCP server,
including JSON formatting, request ID tracking, and proper log configuration.
The logging system is designed to be production-ready with structured output
that's easy to parse and analyze.

Features:
- JSON-formatted log output for easy parsing
- Request ID tracking for request correlation
- Configurable log levels and handlers
- Integration with Flask request context
- Support for additional log fields via extras

Example Usage:
    >>> import logging
    >>> from flask_mcp_server.logging_utils import setup_logging, request_id
    >>>
    >>> # Set up logging for a Flask app
    >>> app = Flask(__name__)
    >>> logger = setup_logging(app)
    >>>
    >>> # Log with request context
    >>> @app.route('/test')
    >>> def test():
    ...     logger.info("Processing request", extra={"request_id": request_id()})
    ...     return "OK"
"""

from __future__ import annotations
import logging
import json
import time
import uuid
import os
from typing import Dict, Any, Optional
from flask import Flask, request, has_request_context


def request_id() -> str:
    """
    Get or generate a request ID for the current request.

    This function first checks for an existing X-Request-Id header,
    which is commonly used for request tracing in microservices.
    If no header is present, it generates a new UUID.

    Returns:
        Request ID string (either from header or newly generated)

    Example:
        >>> # In a Flask route
        >>> @app.route('/api/test')
        >>> def test():
        ...     req_id = request_id()
        ...     logger.info("Processing request", extra={"request_id": req_id})
        ...     return {"request_id": req_id}
    """
    if has_request_context():
        # Try to get request ID from header first
        header_id = request.headers.get("X-Request-Id")
        if header_id:
            return header_id

    # Generate a new UUID if no header present or outside request context
    return uuid.uuid4().hex


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    This formatter converts log records into JSON format with consistent
    field names and structure. It includes timestamp, level, message,
    logger name, and any additional fields provided via the 'extra' parameter.

    The JSON output is designed to be easily parsed by log aggregation
    systems like ELK stack, Fluentd, or cloud logging services.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON-formatted log string

        The output JSON structure:
        {
            "ts": 1234567890123,           # Timestamp in milliseconds
            "level": "INFO",               # Log level
            "msg": "Log message",          # Formatted message
            "logger": "module.name",       # Logger name
            "request_id": "abc123",        # Request ID (if available)
            ...                            # Additional fields from 'extra'
        }
        """
        # Base log structure with standard fields
        log_data = {
            "ts": int(time.time() * 1000),  # Timestamp in milliseconds for precision
            "level": record.levelname,       # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            "msg": record.getMessage(),      # Formatted log message
            "logger": record.name,           # Logger name (usually module name)
        }

        # Add request ID if we're in a request context
        if has_request_context():
            try:
                log_data["request_id"] = request_id()
            except Exception:
                # Don't fail logging if request_id() fails
                pass

        # Add any extra fields provided via logging calls
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_data.update(record.extra)

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add stack trace if present
        if record.stack_info:
            log_data["stack"] = record.stack_info

        # Convert to JSON with UTF-8 support
        return json.dumps(log_data, ensure_ascii=False, default=str)


def setup_logging(app: Flask, level: Optional[str] = None) -> logging.Logger:
    """
    Set up structured logging for the Flask application.

    This function configures the root logger with JSON formatting and
    appropriate log levels. It's designed to be called once during
    application initialization.

    Args:
        app: Flask application instance
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, uses FLASK_MCP_LOG_LEVEL environment variable or INFO

    Returns:
        Configured root logger instance

    Environment Variables:
        FLASK_MCP_LOG_LEVEL: Default log level (default: INFO)
        FLASK_MCP_LOG_FORMAT: Log format (json or text, default: json)

    Example:
        >>> app = Flask(__name__)
        >>> logger = setup_logging(app, level="DEBUG")
        >>> logger.info("Application started")
    """
    # Determine log level
    if level is None:
        level = os.getenv("FLASK_MCP_LOG_LEVEL", "INFO").upper()

    # Validate log level
    numeric_level = getattr(logging, level, None)
    if not isinstance(numeric_level, int):
        # Fall back to INFO if invalid level provided
        numeric_level = logging.INFO
        level = "INFO"

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler()

    # Choose formatter based on configuration
    log_format = os.getenv("FLASK_MCP_LOG_FORMAT", "json").lower()
    if log_format == "json":
        formatter = JsonFormatter()
    else:
        # Use standard text formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Log the logging configuration
    logger.info(f"Logging configured", extra={
        "level": level,
        "format": log_format,
        "handler_count": len(logger.handlers)
    })

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    This is a convenience function that returns a logger with the given name.
    The logger will inherit the configuration set up by setup_logging().

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    return logging.getLogger(name)


def log_request_info(logger: logging.Logger, extra_fields: Optional[Dict[str, Any]] = None) -> None:
    """
    Log information about the current request.

    This function logs details about the current Flask request including
    method, path, remote address, and user agent. It's useful for request
    tracking and debugging.

    Args:
        logger: Logger instance to use
        extra_fields: Additional fields to include in the log

    Example:
        >>> @app.before_request
        >>> def log_request():
        ...     log_request_info(logger, {"user_id": get_current_user_id()})
    """
    if not has_request_context():
        return

    log_data = {
        "request_id": request_id(),
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", ""),
        "content_length": request.content_length or 0,
    }

    if extra_fields:
        log_data.update(extra_fields)

    logger.info("Request received", extra=log_data)
