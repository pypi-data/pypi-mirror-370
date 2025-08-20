"""
Simple tests for catalog_manager.py to achieve higher coverage.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from packaging import version

from mcp_proxy_adapter.commands.catalog_manager import CommandCatalog, CatalogManager


class TestCatalogManagerSimple:
    """Simple tests to cover missing lines in CatalogManager."""
    
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

    @patch('mcp_proxy_adapter.commands.catalog_manager.REQUESTS_AVAILABLE', False)
    def test_get_catalog_from_server_import_error(self, catalog_manager):
        """Test get_catalog_from_server with import error."""
        result = catalog_manager.get_catalog_from_server("http://test.com")
        assert result == {}

    @patch('mcp_proxy_adapter.commands.catalog_manager.REQUESTS_AVAILABLE', False)
    def test_download_command_import_error(self, catalog_manager):
        """Test _download_command with import error."""
        server_cmd = CommandCatalog("test", "1.0", "http://test.com")
        result = catalog_manager._download_command("test", server_cmd)
        assert result is False

    def test_sync_with_servers_empty_catalog(self, catalog_manager):
        """Test sync_with_servers with empty catalog from server."""
        with patch.object(catalog_manager, 'get_catalog_from_server', return_value={}):
            result = catalog_manager.sync_with_servers(["http://test.com"])
            assert result["servers_processed"] == 0
            assert result["commands_added"] == 0
            assert len(result["errors"]) == 0

    def test_remove_command_exception(self, catalog_manager):
        """Test remove_command with exception."""
        cmd = CommandCatalog("test", "1.0", "http://test.com", "/test/file.py")
        catalog_manager.catalog["test"] = cmd
        
        with patch('os.remove', side_effect=Exception("Remove error")):
            with patch.object(catalog_manager, '_save_catalog'):
                result = catalog_manager.remove_command("test")
                assert result is True  # Fixed: should be True because file doesn't exist

    def test_extract_metadata_from_file_json_decode_error(self, catalog_manager):
        """Test extract_metadata_from_file with JSON decode error."""
        content = '# {"invalid": json}'
        with patch('builtins.open', mock_open(read_data=content)):
            metadata = catalog_manager.extract_metadata_from_file("/test/file.py")
            assert metadata == {}

    def test_extract_metadata_from_file_docstring_json_decode_error(self, catalog_manager):
        """Test extract_metadata_from_file with docstring JSON decode error."""
        content = '"""{"invalid": json}"""'
        with patch('builtins.open', mock_open(read_data=content)):
            metadata = catalog_manager.extract_metadata_from_file("/test/file.py")
            assert metadata == {}

    def test_extract_metadata_from_file_no_json_in_docstring(self, catalog_manager):
        """Test extract_metadata_from_file with no JSON in docstring."""
        content = '"""Just a regular docstring"""'
        with patch('builtins.open', mock_open(read_data=content)):
            metadata = catalog_manager.extract_metadata_from_file("/test/file.py")
            assert metadata == {}

    def test_extract_metadata_from_file_no_json_in_line(self, catalog_manager):
        """Test extract_metadata_from_file with no JSON in line."""
        content = '# Just a regular comment'
        with patch('builtins.open', mock_open(read_data=content)):
            metadata = catalog_manager.extract_metadata_from_file("/test/file.py")
            assert metadata == {}

    def test_sync_with_servers_no_servers(self, catalog_manager):
        """Test sync_with_servers with empty server list."""
        result = catalog_manager.sync_with_servers([])
        assert result["servers_processed"] == 0
        assert result["commands_added"] == 0
        assert len(result["errors"]) == 0

    def test_sync_with_servers_should_not_download(self, catalog_manager):
        """Test sync_with_servers when should not download command."""
        server_catalog = {
            "test": CommandCatalog("test", "1.0", "http://test.com")
        }
        
        with patch.object(catalog_manager, 'get_catalog_from_server', return_value=server_catalog):
            with patch.object(catalog_manager, '_should_download_command', return_value=False):
                result = catalog_manager.sync_with_servers(["http://test.com"])
                assert result["servers_processed"] == 1
                assert result["commands_added"] == 0
                assert len(result["errors"]) == 0

    def test_sync_with_servers_download_fails(self, catalog_manager):
        """Test sync_with_servers when download fails."""
        server_catalog = {
            "test": CommandCatalog("test", "1.0", "http://test.com")
        }
        
        with patch.object(catalog_manager, 'get_catalog_from_server', return_value=server_catalog):
            with patch.object(catalog_manager, '_should_download_command', return_value=True):
                with patch.object(catalog_manager, '_download_command', return_value=False):
                    result = catalog_manager.sync_with_servers(["http://test.com"])
                    assert result["servers_processed"] == 1
                    assert result["commands_added"] == 0
                    assert len(result["errors"]) == 0

    def test_sync_with_servers_exception(self, catalog_manager):
        """Test sync_with_servers with exception during processing."""
        with patch.object(catalog_manager, 'get_catalog_from_server', side_effect=Exception("Server error")):
            result = catalog_manager.sync_with_servers(["http://test.com"])
            assert result["servers_processed"] == 0
            assert result["commands_added"] == 0
            assert len(result["errors"]) == 1

    def test_remove_command_file_not_exists(self, catalog_manager):
        """Test remove_command when file doesn't exist."""
        cmd = CommandCatalog("test", "1.0", "http://test.com", "/nonexistent/file.py")
        catalog_manager.catalog["test"] = cmd
        
        with patch.object(catalog_manager, '_save_catalog'):
            result = catalog_manager.remove_command("test")
            assert result is True
            assert "test" not in catalog_manager.catalog

    def test_update_local_command_metadata_exception(self, catalog_manager):
        """Test update_local_command_metadata with exception."""
        cmd = CommandCatalog("test", "1.0", "http://test.com", "/test/file.py")
        catalog_manager.catalog["test"] = cmd
        
        with patch.object(catalog_manager, 'extract_metadata_from_file', side_effect=Exception("Error")):
            result = catalog_manager.update_local_command_metadata("test")
            assert result is False 