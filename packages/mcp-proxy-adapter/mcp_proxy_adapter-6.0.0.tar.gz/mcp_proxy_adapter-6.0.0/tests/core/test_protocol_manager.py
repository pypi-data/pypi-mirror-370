"""
Tests for protocol manager module.
"""

import pytest
from unittest.mock import patch, MagicMock
from mcp_proxy_adapter.core.protocol_manager import ProtocolManager


class TestProtocolManager:
    """Test cases for ProtocolManager class."""
    
    def setup_method(self):
        """Setup test method."""
        self.protocol_manager = ProtocolManager()
    
    def test_init_default_config(self):
        """Test initialization with default configuration."""
        assert self.protocol_manager.enabled is True
        assert self.protocol_manager.allowed_protocols == ["http", "https", "mtls"]
    
    @patch('mcp_proxy_adapter.core.protocol_manager.config')
    def test_init_custom_config(self, mock_config):
        """Test initialization with custom configuration."""
        mock_config.get.return_value = {
            "enabled": False,
            "allowed_protocols": ["https", "mtls"],
            "http": {"enabled": False, "port": 8080},
            "https": {"enabled": True, "port": 8443},
            "mtls": {"enabled": True, "port": 9443}
        }
        
        manager = ProtocolManager()
        assert manager.enabled is False
        assert manager.allowed_protocols == ["https", "mtls"]
    
    def test_is_protocol_allowed_disabled(self):
        """Test protocol allowed check when management is disabled."""
        self.protocol_manager.enabled = False
        assert self.protocol_manager.is_protocol_allowed("http") is True
        assert self.protocol_manager.is_protocol_allowed("https") is True
        assert self.protocol_manager.is_protocol_allowed("mtls") is True
    
    def test_is_protocol_allowed_enabled(self):
        """Test protocol allowed check when management is enabled."""
        self.protocol_manager.enabled = True
        self.protocol_manager.allowed_protocols = ["http", "https"]
        
        assert self.protocol_manager.is_protocol_allowed("http") is True
        assert self.protocol_manager.is_protocol_allowed("https") is True
        assert self.protocol_manager.is_protocol_allowed("mtls") is False
        assert self.protocol_manager.is_protocol_allowed("HTTP") is True  # Case insensitive
    
    def test_get_protocol_port_enabled(self):
        """Test getting port for enabled protocol."""
        self.protocol_manager.protocols_config = {
            "http": {"enabled": True, "port": 8000},
            "https": {"enabled": False, "port": 8443}
        }
        
        assert self.protocol_manager.get_protocol_port("http") == 8000
        assert self.protocol_manager.get_protocol_port("https") is None
    
    def test_get_protocol_port_disabled(self):
        """Test getting port for disabled protocol."""
        self.protocol_manager.protocols_config = {
            "http": {"enabled": False, "port": 8000}
        }
        
        assert self.protocol_manager.get_protocol_port("http") is None
    
    def test_get_allowed_protocols(self):
        """Test getting allowed protocols list."""
        self.protocol_manager.allowed_protocols = ["http", "https", "mtls"]
        allowed = self.protocol_manager.get_allowed_protocols()
        
        assert allowed == ["http", "https", "mtls"]
        assert allowed is not self.protocol_manager.allowed_protocols  # Should be a copy
    
    def test_get_protocol_config(self):
        """Test getting protocol configuration."""
        self.protocol_manager.protocols_config = {
            "http": {"enabled": True, "port": 8000, "custom": "value"}
        }
        
        config = self.protocol_manager.get_protocol_config("http")
        assert config == {"enabled": True, "port": 8000, "custom": "value"}
        assert config is not self.protocol_manager.protocols_config["http"]  # Should be a copy
    
    def test_validate_url_protocol_valid(self):
        """Test URL protocol validation with valid URLs."""
        self.protocol_manager.allowed_protocols = ["http", "https"]
        
        is_valid, error = self.protocol_manager.validate_url_protocol("http://example.com")
        assert is_valid is True
        assert error is None
        
        is_valid, error = self.protocol_manager.validate_url_protocol("https://example.com")
        assert is_valid is True
        assert error is None
    
    def test_validate_url_protocol_invalid(self):
        """Test URL protocol validation with invalid protocols."""
        self.protocol_manager.allowed_protocols = ["http"]
        
        is_valid, error = self.protocol_manager.validate_url_protocol("https://example.com")
        assert is_valid is False
        assert "not allowed" in error
    
    def test_validate_url_protocol_no_protocol(self):
        """Test URL protocol validation with no protocol."""
        is_valid, error = self.protocol_manager.validate_url_protocol("example.com")
        assert is_valid is False
        assert "No protocol specified" in error
    
    def test_validate_url_protocol_invalid_url(self):
        """Test URL protocol validation with invalid URL format."""
        is_valid, error = self.protocol_manager.validate_url_protocol("invalid://url:format:")
        assert is_valid is False
        assert "Protocol 'invalid' is not allowed" in error
    
    @patch('mcp_proxy_adapter.core.ssl_utils.SSLUtils')
    def test_get_ssl_context_for_protocol_https(self, mock_ssl_utils):
        """Test getting SSL context for HTTPS protocol."""
        mock_context = MagicMock()
        mock_ssl_utils.create_ssl_context.return_value = mock_context
        
        with patch('mcp_proxy_adapter.core.protocol_manager.config') as mock_config:
            mock_config.get.return_value = {
                "enabled": True,
                "cert_file": "cert.pem",
                "key_file": "key.pem",
                "ca_cert": "ca.pem",
                "verify_client": False,
                "cipher_suites": ["TLS_AES_256_GCM_SHA384"],
                "min_tls_version": "1.2",
                "max_tls_version": "1.3"
            }
            
            ssl_context = self.protocol_manager.get_ssl_context_for_protocol("https")
            assert ssl_context == mock_context
            mock_ssl_utils.create_ssl_context.assert_called_once()
    
    def test_get_ssl_context_for_protocol_http(self):
        """Test getting SSL context for HTTP protocol."""
        ssl_context = self.protocol_manager.get_ssl_context_for_protocol("http")
        assert ssl_context is None
    
    @patch('mcp_proxy_adapter.core.protocol_manager.config')
    def test_get_ssl_context_ssl_disabled(self, mock_config):
        """Test getting SSL context when SSL is disabled."""
        mock_config.get.return_value = {"enabled": False}
        
        ssl_context = self.protocol_manager.get_ssl_context_for_protocol("https")
        assert ssl_context is None
    
    def test_get_protocol_info(self):
        """Test getting protocol information."""
        self.protocol_manager.protocols_config = {
            "http": {"enabled": True, "port": 8000},
            "https": {"enabled": False, "port": 8443},
            "mtls": {"enabled": True, "port": 9443}
        }
        self.protocol_manager.allowed_protocols = ["http", "mtls"]
        
        with patch.object(self.protocol_manager, 'get_ssl_context_for_protocol') as mock_ssl:
            mock_ssl.return_value = MagicMock()  # SSL context available
            
            info = self.protocol_manager.get_protocol_info()
            
            assert "http" in info
            assert "https" in info
            assert "mtls" in info
            
            assert info["http"]["enabled"] is True
            assert info["http"]["allowed"] is True
            assert info["http"]["port"] == 8000
            assert info["http"]["requires_ssl"] is False
            
            assert info["https"]["enabled"] is False
            assert info["https"]["allowed"] is False
            assert info["https"]["requires_ssl"] is True
    
    def test_validate_protocol_configuration_valid(self):
        """Test protocol configuration validation with valid config."""
        self.protocol_manager.enabled = True
        self.protocol_manager.allowed_protocols = ["http", "https"]
        self.protocol_manager.protocols_config = {
            "http": {"enabled": True, "port": 8000},
            "https": {"enabled": True, "port": 8443}
        }
        
        with patch('mcp_proxy_adapter.core.protocol_manager.config') as mock_config:
            mock_config.get.return_value = {
                "enabled": True,
                "cert_file": "cert.pem",
                "key_file": "key.pem"
            }
            
            errors = self.protocol_manager.validate_protocol_configuration()
            assert len(errors) == 0
    
    def test_validate_protocol_configuration_disabled(self):
        """Test protocol configuration validation when disabled."""
        self.protocol_manager.enabled = False
        errors = self.protocol_manager.validate_protocol_configuration()
        assert len(errors) == 0
    
    def test_validate_protocol_configuration_unknown_protocol(self):
        """Test protocol configuration validation with unknown protocol."""
        self.protocol_manager.enabled = True
        self.protocol_manager.allowed_protocols = ["http", "unknown"]
        
        errors = self.protocol_manager.validate_protocol_configuration()
        assert len(errors) == 1
        assert "Unknown protocol" in errors[0]
    
    def test_validate_protocol_configuration_not_enabled(self):
        """Test protocol configuration validation with protocol not enabled."""
        self.protocol_manager.enabled = True
        self.protocol_manager.allowed_protocols = ["http"]
        self.protocol_manager.protocols_config = {
            "http": {"enabled": False, "port": 8000}
        }
        
        errors = self.protocol_manager.validate_protocol_configuration()
        assert len(errors) == 1
        assert "not enabled" in errors[0]
    
    def test_validate_protocol_configuration_no_port(self):
        """Test protocol configuration validation with no port configured."""
        self.protocol_manager.enabled = True
        self.protocol_manager.allowed_protocols = ["http"]
        self.protocol_manager.protocols_config = {
            "http": {"enabled": True}
        }
        
        errors = self.protocol_manager.validate_protocol_configuration()
        assert len(errors) == 1
        assert "no port configured" in errors[0] 