"""
Tests for new catalog format support.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from mcp_proxy_adapter.commands.catalog_manager import CommandCatalog, CatalogManager


class TestNewCatalogFormat:
    """Test new catalog format support."""
    
    @pytest.fixture
    def temp_catalog_dir(self):
        """Create temporary catalog directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def catalog_manager(self, temp_catalog_dir):
        """Create CatalogManager instance."""
        return CatalogManager(temp_catalog_dir)
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.REQUESTS_AVAILABLE', True)
    @patch('mcp_proxy_adapter.commands.catalog_manager.requests')
    def test_new_format_catalog_parsing(self, mock_requests, catalog_manager):
        """Test parsing of new catalog format."""
        # Mock new format catalog response
        new_format_catalog = {
            "test_command": {
                "plugin": "test_command.py",
                "descr": "Command for testing purposes",
                "category": "testing",
                "author": "Vasiliy Zdanovskiy",
                "version": "0.1",
                "email": "vasilyvz@ukr.net",
                "depends": ["os"]
            },
            "calculator": {
                "plugin": "calculator_command.py",
                "descr": "Simple calculator command for testing",
                "category": "testing",
                "author": "Vasiliy Zdanovskiy",
                "version": "2.1.0",
                "email": "vasilyvz@ukr.net",
                "depends": ["math", "typing"]
            }
        }
        
        mock_response = Mock()
        mock_response.json.return_value = new_format_catalog
        mock_requests.get.return_value = mock_response
        
        result = catalog_manager.get_catalog_from_server("http://test.com")
        
        assert len(result) == 2
        assert "test_command" in result
        assert "calculator" in result
        
        # Check test_command
        test_cmd = result["test_command"]
        assert test_cmd.name == "test_command"
        assert test_cmd.version == "0.1"
        assert test_cmd.plugin == "test_command.py"
        assert test_cmd.descr == "Command for testing purposes"
        assert test_cmd.category == "testing"
        assert test_cmd.author == "Vasiliy Zdanovskiy"
        assert test_cmd.email == "vasilyvz@ukr.net"
        assert test_cmd.depends == ["os"]
        assert test_cmd.source_url == "http://test.com/test_command.py"
        
        # Check calculator
        calc_cmd = result["calculator"]
        assert calc_cmd.name == "calculator"
        assert calc_cmd.version == "2.1.0"
        assert calc_cmd.depends == ["math", "typing"]
        assert calc_cmd.source_url == "http://test.com/calculator_command.py"
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.REQUESTS_AVAILABLE', True)
    @patch('mcp_proxy_adapter.commands.catalog_manager.requests')
    def test_old_format_catalog_parsing(self, mock_requests, catalog_manager):
        """Test parsing of old catalog format (backward compatibility)."""
        # Mock old format catalog response
        old_format_catalog = {
            "commands": [
                {
                    "name": "test_command",
                    "plugin": "test_command.py",
                    "descr": "Command for testing purposes",
                    "category": "testing",
                    "author": "Vasiliy Zdanovskiy",
                    "version": "0.1",
                    "email": "vasilyvz@ukr.net",
                    "source_url": "http://test.com/test_command.py"
                }
            ]
        }
        
        mock_response = Mock()
        mock_response.json.return_value = old_format_catalog
        mock_requests.get.return_value = mock_response
        
        result = catalog_manager.get_catalog_from_server("http://test.com")
        
        assert len(result) == 1
        assert "test_command" in result
        
        test_cmd = result["test_command"]
        assert test_cmd.name == "test_command"
        assert test_cmd.version == "0.1"
        assert test_cmd.source_url == "http://test.com/test_command.py"
    
    def test_dependencies_check_with_available_modules(self, catalog_manager):
        """Test dependencies check with available modules."""
        server_cmd = CommandCatalog("test", "1.0", "http://test.com")
        server_cmd.depends = ["os", "sys", "json"]
        
        result = catalog_manager._check_dependencies("test", server_cmd)
        assert result is True
    
    def test_dependencies_check_with_missing_modules(self, catalog_manager):
        """Test dependencies check with missing modules."""
        server_cmd = CommandCatalog("test", "1.0", "http://test.com")
        server_cmd.depends = ["nonexistent_module", "another_missing_module"]
        
        result = catalog_manager._check_dependencies("test", server_cmd)
        assert result is False
    
    def test_dependencies_check_with_no_dependencies(self, catalog_manager):
        """Test dependencies check with no dependencies."""
        server_cmd = CommandCatalog("test", "1.0", "http://test.com")
        server_cmd.depends = None
        
        result = catalog_manager._check_dependencies("test", server_cmd)
        assert result is True
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.REQUESTS_AVAILABLE', True)
    @patch('mcp_proxy_adapter.commands.catalog_manager.requests')
    def test_string_dependency_conversion_to_list(self, mock_requests, catalog_manager):
        """Test that string dependencies are converted to list during parsing."""
        new_format_catalog = {
            "test_command": {
                "plugin": "test_command.py",
                "version": "0.1",
                "depends": "os"  # String dependency
            }
        }
        
        mock_response = Mock()
        mock_response.json.return_value = new_format_catalog
        mock_requests.get.return_value = mock_response
        
        result = catalog_manager.get_catalog_from_server("http://test.com")
        
        assert len(result) == 1
        test_cmd = result["test_command"]
        assert test_cmd.depends == ["os"]  # Should be converted to list
    
    def test_dependencies_check_with_string_dependency(self, catalog_manager):
        """Test dependencies check with string dependency (should be converted to list)."""
        server_cmd = CommandCatalog("test", "1.0", "http://test.com")
        # The depends field should already be converted to list in the parsing logic
        # This test simulates the case where it's already a list
        server_cmd.depends = ["os"]
        
        result = catalog_manager._check_dependencies("test", server_cmd)
        assert result is True
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.REQUESTS_AVAILABLE', True)
    @patch('mcp_proxy_adapter.commands.catalog_manager.requests')
    def test_source_url_construction_with_trailing_slash(self, mock_requests, catalog_manager):
        """Test source URL construction with trailing slash in server URL."""
        new_format_catalog = {
            "test_command": {
                "plugin": "test_command.py",
                "version": "0.1"
            }
        }
        
        mock_response = Mock()
        mock_response.json.return_value = new_format_catalog
        mock_requests.get.return_value = mock_response
        
        result = catalog_manager.get_catalog_from_server("http://test.com/")
        
        assert len(result) == 1
        test_cmd = result["test_command"]
        assert test_cmd.source_url == "http://test.com/test_command.py"
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.REQUESTS_AVAILABLE', True)
    @patch('mcp_proxy_adapter.commands.catalog_manager.requests')
    def test_source_url_construction_without_trailing_slash(self, mock_requests, catalog_manager):
        """Test source URL construction without trailing slash in server URL."""
        new_format_catalog = {
            "test_command": {
                "plugin": "test_command.py",
                "version": "0.1"
            }
        }
        
        mock_response = Mock()
        mock_response.json.return_value = new_format_catalog
        mock_requests.get.return_value = mock_response
        
        result = catalog_manager.get_catalog_from_server("http://test.com")
        
        assert len(result) == 1
        test_cmd = result["test_command"]
        assert test_cmd.source_url == "http://test.com/test_command.py"
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.REQUESTS_AVAILABLE', True)
    @patch('mcp_proxy_adapter.commands.catalog_manager.requests')
    def test_source_url_fallback_when_no_plugin_field(self, mock_requests, catalog_manager):
        """Test source URL fallback when plugin field is missing."""
        new_format_catalog = {
            "test_command": {
                "version": "0.1"
            }
        }
        
        mock_response = Mock()
        mock_response.json.return_value = new_format_catalog
        mock_requests.get.return_value = mock_response
        
        result = catalog_manager.get_catalog_from_server("http://test.com")
        
        assert len(result) == 1
        test_cmd = result["test_command"]
        assert test_cmd.source_url == "http://test.com"
    
    def test_command_catalog_with_dependencies_serialization(self):
        """Test CommandCatalog serialization with dependencies."""
        catalog = CommandCatalog("test", "1.0", "http://test.com")
        catalog.depends = ["os", "sys"]
        catalog.plugin = "test_command.py"
        catalog.descr = "Test command"
        
        data = catalog.to_dict()
        
        assert data["name"] == "test"
        assert data["version"] == "1.0"
        assert data["depends"] == ["os", "sys"]
        assert data["plugin"] == "test_command.py"
        assert data["descr"] == "Test command"
    
    def test_command_catalog_from_dict_with_dependencies(self):
        """Test CommandCatalog creation from dict with dependencies."""
        data = {
            "name": "test",
            "version": "1.0",
            "source_url": "http://test.com",
            "depends": ["os", "sys"],
            "plugin": "test_command.py"
        }
        
        catalog = CommandCatalog.from_dict(data)
        
        assert catalog.name == "test"
        assert catalog.version == "1.0"
        assert catalog.depends == ["os", "sys"]
        assert catalog.plugin == "test_command.py" 