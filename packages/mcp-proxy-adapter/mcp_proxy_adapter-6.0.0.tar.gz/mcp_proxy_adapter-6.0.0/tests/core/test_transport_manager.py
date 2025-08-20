"""
Unit tests for TransportManager.

This module contains unit tests for the transport management functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from mcp_proxy_adapter.core.transport_manager import (
    TransportManager, 
    TransportType, 
    TransportConfig
)


class TestTransportManager:
    """Test cases for TransportManager."""
    
    def setup_method(self):
        """Setup test method."""
        self.manager = TransportManager()
    
    def test_load_config_http(self):
        """Test loading HTTP configuration."""
        config = {
            "transport": {
                "type": "http",
                "port": None,
                "ssl": {"enabled": False}
            }
        }
        
        assert self.manager.load_config(config) == True
        assert self.manager.get_transport_type() == TransportType.HTTP
        assert self.manager.get_port() == 8000
        assert self.manager.is_ssl_enabled() == False
        assert self.manager.is_http() == True
        assert self.manager.is_https() == False
        assert self.manager.is_mtls() == False
    
    def test_load_config_https(self):
        """Test loading HTTPS configuration."""
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key"
                }
            }
        }
        
        assert self.manager.load_config(config) == True
        assert self.manager.get_transport_type() == TransportType.HTTPS
        assert self.manager.get_port() == 8443
        assert self.manager.is_ssl_enabled() == True
        assert self.manager.is_http() == False
        assert self.manager.is_https() == True
        assert self.manager.is_mtls() == False
    
    def test_load_config_mtls(self):
        """Test loading MTLS configuration."""
        config = {
            "transport": {
                "type": "mtls",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key",
                    "ca_cert": "test_env/ca/ca.crt",
                    "verify_client": True
                }
            }
        }
        
        assert self.manager.load_config(config) == True
        assert self.manager.get_transport_type() == TransportType.MTLS
        assert self.manager.get_port() == 9443
        assert self.manager.is_ssl_enabled() == True
        assert self.manager.is_http() == False
        assert self.manager.is_https() == False
        assert self.manager.is_mtls() == True
    
    def test_load_config_custom_port(self):
        """Test loading configuration with custom port."""
        config = {
            "transport": {
                "type": "http",
                "port": 9000,
                "ssl": {"enabled": False}
            }
        }
        
        assert self.manager.load_config(config) == True
        assert self.manager.get_port() == 9000
    
    def test_load_config_invalid_type(self):
        """Test loading configuration with invalid transport type."""
        config = {
            "transport": {
                "type": "invalid",
                "port": None,
                "ssl": {"enabled": False}
            }
        }
        
        assert self.manager.load_config(config) == False
    
    def test_load_config_https_without_ssl(self):
        """Test loading HTTPS configuration without SSL enabled."""
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {"enabled": False}
            }
        }
        
        assert self.manager.load_config(config) == False
    
    def test_get_ssl_config_http(self):
        """Test getting SSL config for HTTP transport."""
        config = {
            "transport": {
                "type": "http",
                "port": None,
                "ssl": {"enabled": False}
            }
        }
        
        self.manager.load_config(config)
        ssl_config = self.manager.get_ssl_config()
        assert ssl_config is None
    
    def test_get_ssl_config_https(self):
        """Test getting SSL config for HTTPS transport."""
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key"
                }
            }
        }
        
        self.manager.load_config(config)
        ssl_config = self.manager.get_ssl_config()
        
        assert ssl_config is not None
        assert ssl_config["cert_file"] == "test_env/server/server.crt"
        assert ssl_config["key_file"] == "test_env/server/server.key"
        assert ssl_config["verify_client"] == False
    
    def test_get_transport_info(self):
        """Test getting transport information."""
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key"
                }
            }
        }
        
        self.manager.load_config(config)
        info = self.manager.get_transport_info()
        
        assert info["type"] == "https"
        assert info["port"] == 8443
        assert info["ssl_enabled"] == True
        assert info["is_https"] == True
        assert info["ssl_config"] is not None
    
    def test_get_transport_info_not_configured(self):
        """Test getting transport info when not configured."""
        info = self.manager.get_transport_info()
        assert "error" in info
        assert info["error"] == "Transport not configured"
    
    @patch('pathlib.Path.exists')
    def test_validate_ssl_files_success(self, mock_exists):
        """Test SSL files validation success."""
        mock_exists.return_value = True
        
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key"
                }
            }
        }
        
        self.manager.load_config(config)
        assert self.manager.validate_ssl_files() == True
    
    @patch('pathlib.Path.exists')
    def test_validate_ssl_files_missing(self, mock_exists):
        """Test SSL files validation with missing files."""
        mock_exists.return_value = False
        
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key"
                }
            }
        }
        
        self.manager.load_config(config)
        assert self.manager.validate_ssl_files() == False
    
    def test_validate_ssl_files_http(self):
        """Test SSL files validation for HTTP transport."""
        config = {
            "transport": {
                "type": "http",
                "port": None,
                "ssl": {"enabled": False}
            }
        }
        
        self.manager.load_config(config)
        assert self.manager.validate_ssl_files() == True
    
    @patch('mcp_proxy_adapter.core.ssl_utils.SSLUtils.get_ssl_config_for_uvicorn')
    def test_get_uvicorn_config_http(self, mock_get_ssl_config):
        """Test getting uvicorn config for HTTP transport."""
        config = {
            "transport": {
                "type": "http",
                "port": None,
                "ssl": {"enabled": False}
            }
        }
        
        self.manager.load_config(config)
        uvicorn_config = self.manager.get_uvicorn_config()
        
        assert uvicorn_config["host"] == "0.0.0.0"
        assert uvicorn_config["port"] == 8000
        assert uvicorn_config["log_level"] == "info"
        assert "ssl_certfile" not in uvicorn_config
        mock_get_ssl_config.assert_not_called()
    
    @patch('mcp_proxy_adapter.core.ssl_utils.SSLUtils.get_ssl_config_for_uvicorn')
    def test_get_uvicorn_config_https(self, mock_get_ssl_config):
        """Test getting uvicorn config for HTTPS transport."""
        mock_get_ssl_config.return_value = {
            "ssl_certfile": "test_env/server/server.crt",
            "ssl_keyfile": "test_env/server/server.key"
        }
        
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key"
                }
            }
        }
        
        self.manager.load_config(config)
        uvicorn_config = self.manager.get_uvicorn_config()
        
        assert uvicorn_config["host"] == "0.0.0.0"
        assert uvicorn_config["port"] == 8443
        assert uvicorn_config["log_level"] == "info"
        assert uvicorn_config["ssl_certfile"] == "test_env/server/server.crt"
        assert uvicorn_config["ssl_keyfile"] == "test_env/server/server.key"
        mock_get_ssl_config.assert_called_once()
    
    def test_validate_config_not_configured(self):
        """Test config validation when not configured."""
        assert self.manager.validate_config() == False
    
    @patch('mcp_proxy_adapter.core.transport_manager.TransportManager.validate_ssl_files')
    def test_validate_config_https_success(self, mock_validate_ssl):
        """Test config validation for HTTPS transport."""
        mock_validate_ssl.return_value = True
        
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key"
                }
            }
        }
        
        self.manager.load_config(config)
        assert self.manager.validate_config() == True
        mock_validate_ssl.assert_called_once()
    
    @patch('mcp_proxy_adapter.core.transport_manager.TransportManager.validate_ssl_files')
    def test_validate_config_https_missing_files(self, mock_validate_ssl):
        """Test config validation for HTTPS transport with missing files."""
        mock_validate_ssl.return_value = False
        
        config = {
            "transport": {
                "type": "https",
                "port": None,
                "ssl": {
                    "enabled": True,
                    "cert_file": "test_env/server/server.crt",
                    "key_file": "test_env/server/server.key"
                }
            }
        }
        
        self.manager.load_config(config)
        assert self.manager.validate_config() == False
        mock_validate_ssl.assert_called_once() 