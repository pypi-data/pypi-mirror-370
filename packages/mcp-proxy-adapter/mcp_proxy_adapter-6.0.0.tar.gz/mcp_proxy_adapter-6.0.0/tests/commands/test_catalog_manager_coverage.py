"""
Additional tests for catalog_manager.py to achieve higher coverage.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from packaging import version

from mcp_proxy_adapter.commands.catalog_manager import CommandCatalog, CatalogManager


class TestCommandCatalogCoverage:
    """Additional tests to cover missing lines in CommandCatalog."""
    
    def test_command_catalog_init_with_file_path(self):
        """Test CommandCatalog initialization with file_path."""
        catalog = CommandCatalog(
            name="test_command",
            version="1.0.0",
            source_url="http://example.com",
            file_path="/path/to/file.py"
        )
        
        assert catalog.name == "test_command"
        assert catalog.version == "1.0.0"
        assert catalog.source_url == "http://example.com"
        assert catalog.file_path == "/path/to/file.py"
        assert catalog.metadata == {}
    
    def test_command_catalog_to_dict_with_all_fields(self):
        """Test CommandCatalog.to_dict with all fields populated."""
        catalog = CommandCatalog(
            name="test_command",
            version="1.0.0",
            source_url="http://example.com",
            file_path="/path/to/file.py"
        )
        catalog.plugin = "test_plugin"
        catalog.descr = "Test description"
        catalog.category = "test_category"
        catalog.author = "Test Author"
        catalog.email = "test@example.com"
        catalog.metadata = {"key": "value"}
        
        result = catalog.to_dict()
        
        assert result["name"] == "test_command"
        assert result["version"] == "1.0.0"
        assert result["source_url"] == "http://example.com"
        assert result["file_path"] == "/path/to/file.py"
        assert result["plugin"] == "test_plugin"
        assert result["descr"] == "Test description"
        assert result["category"] == "test_category"
        assert result["author"] == "Test Author"
        assert result["email"] == "test@example.com"
        assert result["metadata"] == {"key": "value"}
    
    def test_command_catalog_from_dict_with_all_fields(self):
        """Test CommandCatalog.from_dict with all fields."""
        data = {
            "name": "test_command",
            "version": "1.0.0",
            "source_url": "http://example.com",
            "file_path": "/path/to/file.py",
            "plugin": "test_plugin",
            "descr": "Test description",
            "category": "test_category",
            "author": "Test Author",
            "email": "test@example.com",
            "metadata": {"key": "value"}
        }
        
        catalog = CommandCatalog.from_dict(data)
        
        assert catalog.name == "test_command"
        assert catalog.version == "1.0.0"
        assert catalog.source_url == "http://example.com"
        assert catalog.file_path == "/path/to/file.py"
        assert catalog.plugin == "test_plugin"
        assert catalog.descr == "Test description"
        assert catalog.category == "test_category"
        assert catalog.author == "Test Author"
        assert catalog.email == "test@example.com"
        assert catalog.metadata == {"key": "value"}
    
    def test_command_catalog_from_dict_with_minimal_fields(self):
        """Test CommandCatalog.from_dict with minimal fields."""
        data = {
            "name": "test_command",
            "version": "1.0.0",
            "source_url": "http://example.com"
        }
        
        catalog = CommandCatalog.from_dict(data)
        
        assert catalog.name == "test_command"
        assert catalog.version == "1.0.0"
        assert catalog.source_url == "http://example.com"
        assert catalog.file_path is None
        assert catalog.plugin is None
        assert catalog.descr is None
        assert catalog.category is None
        assert catalog.author is None
        assert catalog.email is None
        assert catalog.metadata == {}


class TestCatalogManagerCoverage:
    """Additional tests to cover missing lines in CatalogManager."""
    
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
    
    def test_load_catalog_deprecated(self, catalog_manager):
        """Test deprecated _load_catalog method."""
        catalog_manager._load_catalog()
        # Should just log a warning
    
    def test_save_catalog_deprecated(self, catalog_manager):
        """Test deprecated _save_catalog method."""
        catalog_manager._save_catalog()
        # Should just log a warning
    
    def test_get_catalog_from_server_invalid_url_format(self, catalog_manager):
        """Test get_catalog_from_server with invalid URL format."""
        result = catalog_manager.get_catalog_from_server("invalid_url")
        assert result == {}
    
    def test_should_download_command_local_file_not_exists(self, catalog_manager):
        """Test _should_download_command when local file doesn't exist."""
        server_cmd = CommandCatalog("test_command", "1.0.0", "http://example.com")
        
        result = catalog_manager._should_download_command("test_command", server_cmd)
        assert result is True
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.CatalogManager.extract_metadata_from_file')
    def test_should_download_command_newer_version_available(self, mock_extract, catalog_manager):
        """Test _should_download_command when newer version is available."""
        # Create local file
        local_file = catalog_manager.commands_dir / "test_command_command.py"
        local_file.write_text("# test file")
        
        mock_extract.return_value = {"version": "0.5.0"}
        server_cmd = CommandCatalog("test_command", "1.0.0", "http://example.com")
        
        result = catalog_manager._should_download_command("test_command", server_cmd)
        assert result is True
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.CatalogManager.extract_metadata_from_file')
    def test_should_download_command_local_version_newer(self, mock_extract, catalog_manager):
        """Test _should_download_command when local version is newer."""
        # Create local file
        local_file = catalog_manager.commands_dir / "test_command_command.py"
        local_file.write_text("# test file")
        
        mock_extract.return_value = {"version": "2.0.0"}
        server_cmd = CommandCatalog("test_command", "1.0.0", "http://example.com")
        
        result = catalog_manager._should_download_command("test_command", server_cmd)
        assert result is False
    
    @patch('mcp_proxy_adapter.commands.catalog_manager.CatalogManager.extract_metadata_from_file')
    def test_should_download_command_version_comparison_fails(self, mock_extract, catalog_manager):
        """Test _should_download_command when version comparison fails."""
        # Create local file
        local_file = catalog_manager.commands_dir / "test_command_command.py"
        local_file.write_text("# test file")
        
        mock_extract.side_effect = Exception("Version comparison failed")
        server_cmd = CommandCatalog("test_command", "1.0.0", "http://example.com")
        
        result = catalog_manager._should_download_command("test_command", server_cmd)
        assert result is True
    
    def test_update_command_deprecated(self, catalog_manager):
        """Test deprecated update_command method."""
        server_catalog = {
            "test_command": CommandCatalog("test_command", "1.0.0", "http://example.com")
        }
        
        with patch.object(catalog_manager, '_download_command', return_value=True):
            result = catalog_manager.update_command("test_command", server_catalog)
            assert result is True
    
    def test_update_command_not_in_catalog(self, catalog_manager):
        """Test update_command when command is not in catalog."""
        server_catalog = {}
        
        result = catalog_manager.update_command("test_command", server_catalog)
        assert result is False
    
    def test_download_command_invalid_source_url(self, catalog_manager):
        """Test _download_command with invalid source URL."""
        server_cmd = CommandCatalog("test_command", "1.0.0", "invalid_url")
        
        result = catalog_manager._download_command("test_command", server_cmd)
        assert result is False

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

    def test_sync_with_servers_empty_catalog(self, catalog_manager):
        """Test sync_with_servers with empty catalog from server."""
        with patch.object(catalog_manager, 'get_catalog_from_server', return_value={}):
            result = catalog_manager.sync_with_servers(["http://test.com"])
            assert result["servers_processed"] == 0  # Fixed: should be 0 when catalog is empty
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