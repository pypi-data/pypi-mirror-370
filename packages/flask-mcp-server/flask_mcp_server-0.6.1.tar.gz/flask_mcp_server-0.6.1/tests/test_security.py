"""
Tests for security module.

This module tests authentication, authorization, HMAC validation,
and security configuration functionality.
"""

import pytest
import os
import hmac
import hashlib
from flask_mcp_server.security import (
    auth_mode,
    api_key_roles,
    check_apikey,
    check_hmac_signature,
    parse_rate,
    validate_environment_config,
    _apikeys_map,
    _apikeys_list
)


class TestAuthMode:
    """Test auth_mode function."""
    
    def test_default_auth_mode(self, clean_env):
        """Test default auth mode."""
        assert auth_mode() == "none"
    
    def test_valid_auth_modes(self, clean_env):
        """Test valid auth modes."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "apikey"
        assert auth_mode() == "apikey"
        
        os.environ["FLASK_MCP_AUTH_MODE"] = "hmac"
        assert auth_mode() == "hmac"
        
        os.environ["FLASK_MCP_AUTH_MODE"] = "none"
        assert auth_mode() == "none"
    
    def test_invalid_auth_mode(self, clean_env):
        """Test invalid auth mode defaults to none."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "invalid"
        assert auth_mode() == "none"
    
    def test_case_insensitive(self, clean_env):
        """Test case insensitive auth mode."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "APIKEY"
        assert auth_mode() == "apikey"


class TestApiKeysMap:
    """Test _apikeys_map function."""
    
    def test_empty_map(self, clean_env):
        """Test empty API keys map."""
        assert _apikeys_map() == {}
    
    def test_valid_map(self, clean_env):
        """Test valid API keys map."""
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "key1:admin|user;key2:user"
        mapping = _apikeys_map()
        assert mapping == {
            "key1": ["admin", "user"],
            "key2": ["user"]
        }
    
    def test_key_without_roles(self, clean_env):
        """Test key without roles."""
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "key1:;key2:user"
        mapping = _apikeys_map()
        assert mapping == {
            "key1": [],
            "key2": ["user"]
        }
    
    def test_invalid_format(self, clean_env):
        """Test invalid format entries are skipped."""
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "invalid_entry;key2:user"
        mapping = _apikeys_map()
        assert mapping == {"key2": ["user"]}
    
    def test_invalid_key_format(self, clean_env):
        """Test invalid key format is skipped."""
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "key@invalid:user;valid_key:admin"
        mapping = _apikeys_map()
        assert mapping == {"valid_key": ["admin"]}
    
    def test_invalid_role_format(self, clean_env):
        """Test invalid role format is filtered out."""
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "key1:valid_role|invalid@role"
        mapping = _apikeys_map()
        assert mapping == {"key1": ["valid_role"]}


class TestApiKeysList:
    """Test _apikeys_list function."""
    
    def test_empty_list(self, clean_env):
        """Test empty API keys list."""
        assert _apikeys_list() == []
    
    def test_valid_list(self, clean_env):
        """Test valid API keys list."""
        os.environ["FLASK_MCP_API_KEYS"] = "key1,key2,key3"
        keys = _apikeys_list()
        assert keys == ["key1", "key2", "key3"]
    
    def test_whitespace_handling(self, clean_env):
        """Test whitespace handling."""
        os.environ["FLASK_MCP_API_KEYS"] = " key1 , key2 , key3 "
        keys = _apikeys_list()
        assert keys == ["key1", "key2", "key3"]
    
    def test_invalid_key_format(self, clean_env):
        """Test invalid key format is filtered out."""
        os.environ["FLASK_MCP_API_KEYS"] = "valid_key,invalid@key,another_valid"
        keys = _apikeys_list()
        assert keys == ["valid_key", "another_valid"]


class TestApiKeyRoles:
    """Test api_key_roles function."""
    
    def test_none_key(self, clean_env):
        """Test None key returns empty list."""
        assert api_key_roles(None) == []
    
    def test_key_with_roles(self, clean_env):
        """Test key with roles."""
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "key1:admin|user"
        roles = api_key_roles("key1")
        assert roles == ["admin", "user"]
    
    def test_key_without_roles(self, clean_env):
        """Test key not in map returns empty list."""
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "key1:admin"
        roles = api_key_roles("key2")
        assert roles == []


class TestCheckApikey:
    """Test check_apikey function."""
    
    def test_none_key(self, clean_env):
        """Test None key is invalid."""
        assert check_apikey(None) is False
    
    def test_valid_key_in_list(self, clean_env):
        """Test valid key in simple list."""
        os.environ["FLASK_MCP_API_KEYS"] = "key1,key2"
        assert check_apikey("key1") is True
        assert check_apikey("key3") is False
    
    def test_valid_key_in_map(self, clean_env):
        """Test valid key in roles map."""
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "key1:admin"
        assert check_apikey("key1") is True
        assert check_apikey("key2") is False
    
    def test_key_in_both_list_and_map(self, clean_env):
        """Test key validation with both list and map."""
        os.environ["FLASK_MCP_API_KEYS"] = "key1"
        os.environ["FLASK_MCP_API_KEYS_MAP"] = "key2:admin"
        assert check_apikey("key1") is True
        assert check_apikey("key2") is True
        assert check_apikey("key3") is False


class TestCheckHmacSignature:
    """Test check_hmac_signature function."""
    
    def test_none_signature(self):
        """Test None signature is invalid."""
        assert check_hmac_signature("secret", b"body", None) is False
    
    def test_empty_secret(self):
        """Test empty secret is invalid."""
        assert check_hmac_signature("", b"body", "sha256=signature") is False
    
    def test_invalid_signature_format(self):
        """Test invalid signature format."""
        assert check_hmac_signature("secret", b"body", "invalid") is False
    
    def test_unsupported_algorithm(self):
        """Test unsupported hash algorithm."""
        assert check_hmac_signature("secret", b"body", "md5=signature") is False
    
    def test_valid_sha256_signature(self):
        """Test valid SHA256 signature."""
        secret = "test_secret"
        body = b"test body"
        
        # Generate valid signature
        mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        signature = f"sha256={mac}"
        
        assert check_hmac_signature(secret, body, signature) is True
    
    def test_valid_sha512_signature(self):
        """Test valid SHA512 signature."""
        secret = "test_secret"
        body = b"test body"
        
        # Generate valid signature
        mac = hmac.new(secret.encode(), body, hashlib.sha512).hexdigest()
        signature = f"sha512={mac}"
        
        assert check_hmac_signature(secret, body, signature) is True
    
    def test_invalid_signature_value(self):
        """Test invalid signature value."""
        assert check_hmac_signature("secret", b"body", "sha256=invalid") is False
    
    def test_wrong_secret(self):
        """Test wrong secret."""
        secret = "test_secret"
        wrong_secret = "wrong_secret"
        body = b"test body"
        
        # Generate signature with wrong secret
        mac = hmac.new(wrong_secret.encode(), body, hashlib.sha256).hexdigest()
        signature = f"sha256={mac}"
        
        assert check_hmac_signature(secret, body, signature) is False


class TestParseRate:
    """Test parse_rate function."""
    
    def test_empty_rule(self):
        """Test empty rule returns None."""
        assert parse_rate("") is None
        assert parse_rate(None) is None
    
    def test_valid_rates(self):
        """Test valid rate formats."""
        assert parse_rate("100/s") == (100, 1)
        assert parse_rate("60/m") == (60, 60)
        assert parse_rate("24/h") == (24, 3600)
        assert parse_rate("1/d") == (1, 86400)
    
    def test_invalid_format(self):
        """Test invalid format."""
        assert parse_rate("invalid") is None
        assert parse_rate("100") is None
    
    def test_invalid_number(self):
        """Test invalid number."""
        assert parse_rate("abc/s") is None
        assert parse_rate("-10/s") is None
        assert parse_rate("0/s") is None
    
    def test_invalid_period(self):
        """Test invalid period."""
        assert parse_rate("100/x") is None
        assert parse_rate("100/sec") is None


class TestValidateEnvironmentConfig:
    """Test validate_environment_config function."""
    
    def test_valid_config(self, clean_env):
        """Test valid configuration."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "none"
        errors = validate_environment_config()
        assert errors == {}
    
    def test_invalid_auth_mode(self, clean_env):
        """Test invalid auth mode."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "invalid"
        errors = validate_environment_config()
        assert "FLASK_MCP_AUTH_MODE" in errors
    
    def test_apikey_mode_without_keys(self, clean_env):
        """Test apikey mode without API keys."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "apikey"
        errors = validate_environment_config()
        assert "FLASK_MCP_API_KEYS" in errors
    
    def test_hmac_mode_without_secret(self, clean_env):
        """Test HMAC mode without secret."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "hmac"
        errors = validate_environment_config()
        assert "FLASK_MCP_HMAC_SECRET" in errors
    
    def test_short_hmac_secret(self, clean_env):
        """Test short HMAC secret."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "hmac"
        os.environ["FLASK_MCP_HMAC_SECRET"] = "short"
        errors = validate_environment_config()
        assert "FLASK_MCP_HMAC_SECRET" in errors
    
    def test_invalid_rate_limit(self, clean_env):
        """Test invalid rate limit format."""
        os.environ["FLASK_MCP_RATE_LIMIT"] = "invalid"
        errors = validate_environment_config()
        assert "FLASK_MCP_RATE_LIMIT" in errors
    
    def test_invalid_rate_scope(self, clean_env):
        """Test invalid rate scope."""
        os.environ["FLASK_MCP_RATE_SCOPE"] = "invalid"
        errors = validate_environment_config()
        assert "FLASK_MCP_RATE_SCOPE" in errors

    def test_valid_complete_config(self, clean_env):
        """Test valid complete configuration."""
        os.environ["FLASK_MCP_AUTH_MODE"] = "apikey"
        os.environ["FLASK_MCP_API_KEYS"] = "key1,key2"
        os.environ["FLASK_MCP_RATE_LIMIT"] = "100/m"
        os.environ["FLASK_MCP_RATE_SCOPE"] = "key"
        errors = validate_environment_config()
        assert errors == {}
