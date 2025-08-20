"""
Tests for security components.

This module contains tests for SecurityAdapter, SecurityFactory, and ConfigConverter.
"""

import pytest
import json
from unittest.mock import Mock, patch
from typing import Dict, Any

from mcp_proxy_adapter.core.security_adapter import SecurityAdapter
from mcp_proxy_adapter.core.security_factory import SecurityFactory
from mcp_proxy_adapter.core.config_converter import ConfigConverter


class TestSecurityAdapter:
    """Tests for SecurityAdapter class."""
    
    def test_init_with_framework_available(self):
        """Test SecurityAdapter initialization when framework is available."""
        config = {
            "security": {
                "auth": {"enabled": True, "methods": ["api_key"]},
                "ssl": {"enabled": False},
                "permissions": {"enabled": True},
                "rate_limit": {"enabled": True}
            }
        }
        
        with patch('mcp_proxy_adapter.core.security_adapter.SECURITY_FRAMEWORK_AVAILABLE', True):
            with patch('mcp_proxy_adapter.core.security_adapter.SecurityManager') as mock_manager:
                adapter = SecurityAdapter(config)
                assert adapter.config == config
                assert adapter.security_manager is not None
    
    def test_init_with_framework_unavailable(self):
        """Test SecurityAdapter initialization when framework is unavailable."""
        config = {"security": {"auth": {"enabled": True}}}
        
        with patch('mcp_proxy_adapter.core.security_adapter.SECURITY_FRAMEWORK_AVAILABLE', False):
            adapter = SecurityAdapter(config)
            assert adapter.config == config
            assert adapter.security_manager is None
    
    def test_convert_auth_config(self):
        """Test authentication configuration conversion."""
        config = {
            "security": {
                "auth": {
                    "enabled": True,
                    "methods": ["api_key", "jwt"],
                    "api_keys": {"admin": "key123"},
                    "jwt_secret": "secret123"
                }
            }
        }
        
        adapter = SecurityAdapter(config)
        auth_config = adapter._convert_auth_config(config["security"])
        
        assert auth_config["enabled"] is True
        assert "api_key" in auth_config["methods"]
        assert "jwt" in auth_config["methods"]
        assert auth_config["api_keys"]["admin"] == "key123"
        assert auth_config["jwt_secret"] == "secret123"
    
    def test_convert_ssl_config(self):
        """Test SSL configuration conversion."""
        config = {
            "security": {
                "ssl": {
                    "enabled": True,
                    "cert_file": "server.crt",
                    "key_file": "server.key",
                    "min_tls_version": "TLSv1.3"
                }
            }
        }
        
        adapter = SecurityAdapter(config)
        ssl_config = adapter._convert_ssl_config(config["security"])
        
        assert ssl_config["enabled"] is True
        assert ssl_config["cert_file"] == "server.crt"
        assert ssl_config["key_file"] == "server.key"
        assert ssl_config["min_tls_version"] == "TLSv1.3"
    
    def test_fallback_validation(self):
        """Test fallback validation when framework is unavailable."""
        config = {
            "security": {
                "auth": {
                    "api_keys": {"admin": "admin_key_123"}
                }
            }
        }
        
        adapter = SecurityAdapter(config)
        
        # Test valid API key
        request_data = {
            "headers": {"X-API-Key": "admin_key_123"},
            "query_params": {},
            "body": {}
        }
        
        result = adapter._fallback_validation(request_data)
        assert result["is_valid"] is True
        assert result["user_id"] == "admin"
        
        # Test invalid API key
        request_data = {
            "headers": {"X-API-Key": "invalid_key"},
            "query_params": {},
            "body": {}
        }
        
        result = adapter._fallback_validation(request_data)
        assert result["is_valid"] is False
        assert result["error_code"] == -32000


class TestSecurityFactory:
    """Tests for SecurityFactory class."""
    
    def test_create_security_adapter(self):
        """Test SecurityAdapter creation."""
        config = {"security": {"auth": {"enabled": True}}}
        
        with patch('mcp_proxy_adapter.core.security_adapter.SECURITY_FRAMEWORK_AVAILABLE', False):
            adapter = SecurityFactory.create_security_adapter(config)
            assert isinstance(adapter, SecurityAdapter)
            assert adapter.config == config
    
    def test_create_security_manager(self):
        """Test SecurityManager creation."""
        config = {"security": {"auth": {"enabled": True}}}
        
        with patch('mcp_proxy_adapter.core.security_adapter.SECURITY_FRAMEWORK_AVAILABLE', False):
            manager = SecurityFactory.create_security_manager(config)
            assert manager is None  # Should be None when framework unavailable
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid config."""
        config = {
            "security": {
                "auth": {"enabled": True, "methods": ["api_key"], "api_keys": {}},
                "ssl": {"enabled": False},
                "permissions": {"enabled": True},
                "rate_limit": {"enabled": True, "requests_per_minute": 60}
            }
        }
        
        assert SecurityFactory.validate_config(config) is True
    
    def test_validate_config_invalid(self):
        """Test configuration validation with invalid config."""
        config = {
            "security": {
                "auth": "invalid",  # Should be dict
                "ssl": {"enabled": False},
                "permissions": {"enabled": True},
                "rate_limit": {"enabled": True}
            }
        }
        
        assert SecurityFactory.validate_config(config) is False
    
    def test_get_default_config(self):
        """Test default configuration generation."""
        config = SecurityFactory.get_default_config()
        
        assert "security" in config
        assert "auth" in config["security"]
        assert "ssl" in config["security"]
        assert "permissions" in config["security"]
        assert "rate_limit" in config["security"]
    
    def test_merge_config(self):
        """Test configuration merging."""
        base_config = {"server": {"port": 8000}}
        security_config = {"auth": {"enabled": True}}
        
        merged = SecurityFactory.merge_config(base_config, security_config)
        
        assert merged["server"]["port"] == 8000
        assert merged["security"]["auth"]["enabled"] is True


class TestConfigConverter:
    """Tests for ConfigConverter class."""
    
    def test_to_security_framework_config(self):
        """Test conversion to security framework config."""
        mcp_config = {
            "security": {
                "auth": {
                    "enabled": True,
                    "methods": ["api_key", "jwt"],
                    "api_keys": {"admin": "key123"}
                },
                "ssl": {
                    "enabled": True,
                    "cert_file": "server.crt"
                }
            }
        }
        
        security_config = ConfigConverter.to_security_framework_config(mcp_config)
        
        assert security_config["auth"]["enabled"] is True
        assert "api_key" in security_config["auth"]["methods"]
        assert "jwt" in security_config["auth"]["methods"]
        assert security_config["auth"]["api_keys"]["admin"] == "key123"
        assert security_config["ssl"]["enabled"] is True
        assert security_config["ssl"]["cert_file"] == "server.crt"
    
    def test_from_security_framework_config(self):
        """Test conversion from security framework config."""
        security_config = {
            "auth": {
                "enabled": True,
                "methods": ["api_key"],
                "api_keys": {"admin": "key123"}
            },
            "ssl": {
                "enabled": False
            }
        }
        
        mcp_config = ConfigConverter.from_security_framework_config(security_config)
        
        assert "security" in mcp_config
        assert mcp_config["security"]["auth"]["enabled"] is True
        assert mcp_config["security"]["auth"]["api_keys"]["admin"] == "key123"
        assert mcp_config["security"]["ssl"]["enabled"] is False
    
    def test_legacy_config_conversion(self):
        """Test conversion from legacy configuration format."""
        legacy_config = {
            "ssl": {
                "enabled": True,
                "cert_file": "server.crt",
                "api_keys": {"admin": "key123"}
            },
            "roles": {
                "enabled": True,
                "config_file": "roles.json"
            }
        }
        
        security_config = ConfigConverter.to_security_framework_config(legacy_config)
        
        assert security_config["ssl"]["enabled"] is True
        assert security_config["ssl"]["cert_file"] == "server.crt"
        assert security_config["auth"]["api_keys"]["admin"] == "key123"
        assert security_config["permissions"]["enabled"] is True
        assert security_config["permissions"]["roles_file"] == "roles.json"
    
    def test_validate_security_config_valid(self):
        """Test security configuration validation with valid config."""
        config = {
            "security": {
                "auth": {"enabled": True, "methods": ["api_key"], "api_keys": {}},
                "ssl": {"enabled": False},
                "permissions": {"enabled": True},
                "rate_limit": {"enabled": True, "requests_per_minute": 60}
            }
        }
        
        assert ConfigConverter.validate_security_config(config) is True
    
    def test_validate_security_config_invalid(self):
        """Test security configuration validation with invalid config."""
        config = {
            "security": {
                "auth": {"enabled": True, "methods": "invalid"},  # Should be list
                "ssl": {"enabled": False},
                "permissions": {"enabled": True},
                "rate_limit": {"enabled": True}
            }
        }
        
        assert ConfigConverter.validate_security_config(config) is False
    
    def test_migrate_legacy_config(self, tmp_path):
        """Test legacy configuration migration."""
        legacy_config = {
            "ssl": {
                "enabled": True,
                "cert_file": "server.crt",
                "api_keys": {"admin": "key123"}
            }
        }
        
        config_file = tmp_path / "legacy_config.json"
        with open(config_file, 'w') as f:
            json.dump(legacy_config, f)
        
        output_file = tmp_path / "migrated_config.json"
        success = ConfigConverter.migrate_legacy_config(str(config_file), str(output_file))
        
        assert success is True
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            migrated_config = json.load(f)
        
        assert "security" in migrated_config
        assert migrated_config["security"]["ssl"]["enabled"] is True
        assert migrated_config["security"]["auth"]["api_keys"]["admin"] == "key123"


if __name__ == "__main__":
    pytest.main([__file__])
