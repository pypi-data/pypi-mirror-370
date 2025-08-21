from __future__ import annotations
import os
import hmac
import hashlib
import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def auth_mode() -> str:
    """
    Get the authentication mode from environment variables.

    Returns:
        Authentication mode: 'none', 'apikey', or 'hmac'
    """
    mode = os.getenv("FLASK_MCP_AUTH_MODE", "none").lower()
    valid_modes = {"none", "apikey", "hmac"}

    if mode not in valid_modes:
        logger.warning(f"Invalid auth mode '{mode}', defaulting to 'none'")
        return "none"

    return mode


def _apikeys_map() -> Dict[str, List[str]]:
    """
    Parse API keys mapping from environment variable.

    Format: "key1:role1|role2;key2:role3"

    Returns:
        Dictionary mapping API keys to their roles
    """
    raw = os.getenv("FLASK_MCP_API_KEYS_MAP", "")
    if not raw:
        return {}

    mapping = {}
    entries = [e.strip() for e in raw.split(";") if e.strip()]

    for entry in entries:
        if ":" not in entry:
            logger.warning(f"Invalid API key mapping format: {entry}")
            continue

        key, _, roles_str = entry.partition(":")
        key = key.strip()

        # Validate API key format (alphanumeric + some special chars)
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', key):
            logger.warning(f"Invalid API key format: {key}")
            continue

        roles = [r.strip() for r in roles_str.split("|") if r.strip()] if roles_str else []

        # Validate role names
        valid_roles = []
        for role in roles:
            if re.match(r'^[a-zA-Z0-9_\-]+$', role):
                valid_roles.append(role)
            else:
                logger.warning(f"Invalid role name: {role}")

        mapping[key] = valid_roles

    return mapping


def _apikeys_list() -> List[str]:
    """
    Parse API keys list from environment variable.

    Format: "key1,key2,key3"

    Returns:
        List of valid API keys
    """
    keys_str = os.getenv("FLASK_MCP_API_KEYS", "").strip()
    if not keys_str:
        return []

    keys = []
    for key in keys_str.split(","):
        key = key.strip()
        if key and re.match(r'^[a-zA-Z0-9_\-\.]+$', key):
            keys.append(key)
        elif key:
            logger.warning(f"Invalid API key format: {key}")

    return keys


def api_key_roles(value: Optional[str]) -> List[str]:
    """
    Get roles associated with an API key.

    Args:
        value: API key to look up

    Returns:
        List of roles for the API key, empty if key not found
    """
    if not value:
        return []
    return _apikeys_map().get(value, [])


def check_apikey(value: Optional[str]) -> bool:
    """
    Validate an API key.

    Args:
        value: API key to validate

    Returns:
        True if the API key is valid, False otherwise
    """
    if not value:
        return False

    # Check against both simple list and mapped keys
    return value in _apikeys_list() or value in _apikeys_map()


def check_hmac_signature(secret: str, body: bytes, signature: Optional[str]) -> bool:
    """
    Validate HMAC signature with support for multiple hash algorithms.

    Args:
        secret: HMAC secret key
        body: Request body bytes
        signature: Signature header value (format: "algorithm=signature")

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not secret:
        return False

    # Parse signature format: "algorithm=signature"
    if "=" not in signature:
        logger.warning("Invalid signature format: missing algorithm")
        return False

    algorithm, sig_value = signature.split("=", 1)

    # Supported hash algorithms
    hash_algorithms = {
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
        "sha1": hashlib.sha1,  # Less secure, but sometimes needed for compatibility
    }

    if algorithm not in hash_algorithms:
        logger.warning(f"Unsupported hash algorithm: {algorithm}")
        return False

    try:
        # Generate expected signature
        hash_func = hash_algorithms[algorithm]
        expected_mac = hmac.new(
            secret.encode("utf-8"),
            body,
            hash_func
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_mac, sig_value)

    except Exception as e:
        logger.error(f"Error validating HMAC signature: {e}")
        return False


def parse_rate(rule: str) -> Optional[Tuple[int, int]]:
    """
    Parse rate limiting rule string.

    Args:
        rule: Rate limit rule in format "N/period" (e.g., "100/m", "10/s")

    Returns:
        Tuple of (limit, window_seconds) or None if invalid
    """
    if not rule:
        return None

    # Validate format
    if "/" not in rule:
        logger.warning(f"Invalid rate limit format: {rule}")
        return None

    n_str, sep, period = rule.partition("/")

    # Parse limit number
    try:
        limit = int(n_str)
        if limit <= 0:
            logger.warning(f"Invalid rate limit number: {limit}")
            return None
    except ValueError:
        logger.warning(f"Invalid rate limit number: {n_str}")
        return None

    # Parse time period
    period_map = {
        "s": 1,      # second
        "m": 60,     # minute
        "h": 3600,   # hour
        "d": 86400,  # day
    }

    if period not in period_map:
        logger.warning(f"Invalid rate limit period: {period}")
        return None

    window = period_map[period]
    return (limit, window)


def validate_environment_config() -> Dict[str, str]:
    """
    Validate all security-related environment variables.

    Returns:
        Dictionary of validation errors (empty if all valid)
    """
    errors = {}

    # Validate auth mode
    auth_mode_val = os.getenv("FLASK_MCP_AUTH_MODE", "none")
    if auth_mode_val not in {"none", "apikey", "hmac"}:
        errors["FLASK_MCP_AUTH_MODE"] = f"Invalid value: {auth_mode_val}"

    # Validate API keys if auth mode is apikey
    if auth_mode_val == "apikey":
        api_keys = os.getenv("FLASK_MCP_API_KEYS", "")
        if not api_keys:
            errors["FLASK_MCP_API_KEYS"] = "Required when auth mode is 'apikey'"

    # Validate HMAC secret if auth mode is hmac
    if auth_mode_val == "hmac":
        hmac_secret = os.getenv("FLASK_MCP_HMAC_SECRET", "")
        if not hmac_secret:
            errors["FLASK_MCP_HMAC_SECRET"] = "Required when auth mode is 'hmac'"
        elif len(hmac_secret) < 32:
            errors["FLASK_MCP_HMAC_SECRET"] = "Should be at least 32 characters for security"

    # Validate rate limit format
    rate_limit = os.getenv("FLASK_MCP_RATE_LIMIT", "")
    if rate_limit and not parse_rate(rate_limit):
        errors["FLASK_MCP_RATE_LIMIT"] = f"Invalid format: {rate_limit}"

    # Validate rate scope
    rate_scope = os.getenv("FLASK_MCP_RATE_SCOPE", "ip")
    if rate_scope not in {"ip", "key"}:
        errors["FLASK_MCP_RATE_SCOPE"] = f"Invalid value: {rate_scope}"

    return errors
