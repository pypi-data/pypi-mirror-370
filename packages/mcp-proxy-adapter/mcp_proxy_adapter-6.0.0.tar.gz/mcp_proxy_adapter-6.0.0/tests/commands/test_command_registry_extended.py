"""
Extended tests for command registry functionality.
"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import pytest

from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult
from mcp_proxy_adapter.core.errors import NotFoundError


class TestCommand(Command):
    """Test command class for testing."""
    
    name = "test"
    
    async def execute(self, **kwargs):
        return SuccessResult(data={"result": "test"})


class TestCommandWithInstance(Command):
    """Test command class that requires instance."""
    
    name = "test_instance"
    
    def __init__(self, dependency=None):
        super().__init__()
        self.dependency = dependency
    
    async def execute(self, **kwargs):
        return SuccessResult(data={"result": "test_instance", "dependency": self.dependency})


class TestCommandRegistryExtended:
    """Extended tests for CommandRegistry class."""
    
    @pytest.fixture
    def registry(self):
        """Create CommandRegistry instance."""
        return CommandRegistry()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_register_builtin_success(self, registry):
        """Test successful built-in command registration."""
        registry.register_builtin(TestCommand)
        
        assert "test" in registry._builtin_commands
        assert registry._builtin_commands["test"] == TestCommand
    
    def test_register_builtin_duplicate(self, registry):
        """Test built-in command registration with duplicate."""
        registry.register_builtin(TestCommand)
        
        with pytest.raises(ValueError, match="Built-in command 'test' is already registered"):
            registry.register_builtin(TestCommand)
    
    def test_register_builtin_overrides_loaded(self, registry):
        """Test built-in command overrides loaded command."""
        # Register loaded command first
        registry.register_loaded(TestCommand)
        assert "test" in registry._loaded_commands
        
        # Register built-in command
        registry.register_builtin(TestCommand)
        
        assert "test" in registry._builtin_commands
        assert "test" not in registry._loaded_commands
    
    def test_register_custom_success(self, registry):
        """Test successful custom command registration."""
        registry.register_custom(TestCommand)
        
        assert "test" in registry._custom_commands
        assert registry._custom_commands["test"] == TestCommand
    
    def test_register_custom_duplicate(self, registry):
        """Test custom command registration with duplicate."""
        registry.register_custom(TestCommand)
        
        with pytest.raises(ValueError, match="Custom command 'test' is already registered"):
            registry.register_custom(TestCommand)
    
    def test_register_custom_overrides_builtin(self, registry):
        """Test custom command overrides built-in command."""
        # Register built-in command first
        registry.register_builtin(TestCommand)
        assert "test" in registry._builtin_commands
        
        # Register custom command
        registry.register_custom(TestCommand)
        
        assert "test" in registry._custom_commands
        assert "test" not in registry._builtin_commands
    
    def test_register_custom_overrides_loaded(self, registry):
        """Test custom command overrides loaded command."""
        # Register loaded command first
        registry.register_loaded(TestCommand)
        assert "test" in registry._loaded_commands
        
        # Register custom command
        registry.register_custom(TestCommand)
        
        assert "test" in registry._custom_commands
        assert "test" not in registry._loaded_commands
    
    def test_register_loaded_success(self, registry):
        """Test successful loaded command registration."""
        result = registry.register_loaded(TestCommand)
        
        assert result is True
        assert "test" in registry._loaded_commands
        assert registry._loaded_commands["test"] == TestCommand
    
    def test_register_loaded_conflicts_with_custom(self, registry):
        """Test loaded command conflicts with custom command."""
        registry.register_custom(TestCommand)
        
        result = registry.register_loaded(TestCommand)
        
        assert result is False
        assert "test" not in registry._loaded_commands
    
    def test_register_loaded_conflicts_with_builtin(self, registry):
        """Test loaded command conflicts with built-in command."""
        registry.register_builtin(TestCommand)
        
        result = registry.register_loaded(TestCommand)
        
        assert result is False
        assert "test" not in registry._loaded_commands
    
    def test_register_loaded_duplicate(self, registry):
        """Test loaded command registration with duplicate."""
        registry.register_loaded(TestCommand)
        
        result = registry.register_loaded(TestCommand)
        
        assert result is False
    
    def test_register_command_instance(self, registry):
        """Test registering command instance."""
        instance = TestCommandWithInstance(dependency="test_dep")
        
        registry.register_builtin(instance)
        
        assert "test_instance" in registry._builtin_commands
        assert "test_instance" in registry._instances
        assert registry._instances["test_instance"] == instance
    
    def test_register_invalid_command(self, registry):
        """Test registering invalid command type."""
        with pytest.raises(ValueError, match="Invalid command type"):
            registry._register_command("not_a_command", registry._builtin_commands, "built-in")
    
    def test_get_command_name_with_name_attribute(self, registry):
        """Test getting command name with name attribute."""
        name = registry._get_command_name(TestCommand)
        assert name == "test"
    
    def test_get_command_name_without_name_attribute(self, registry):
        """Test getting command name without name attribute."""
        class CommandWithoutName(Command):
            async def execute(self, **kwargs):
                return {}
        
        name = registry._get_command_name(CommandWithoutName)
        assert name == "commandwithoutname"
    
    def test_get_command_name_removes_command_suffix(self, registry):
        """Test getting command name removes Command suffix."""
        class TestCommandClass(Command):
            async def execute(self, **kwargs):
                return {}
        
        name = registry._get_command_name(TestCommandClass)
        assert name == "testcommandclass"
    
    def test_command_exists(self, registry):
        """Test command_exists method."""
        registry.register_builtin(TestCommand)
        
        assert registry.command_exists("test") is True
        assert registry.command_exists("nonexistent") is False
    
    def test_get_command_priority_order(self, registry):
        """Test get_command priority order."""
        # Register commands in different categories
        registry.register_loaded(TestCommand)
        
        class BuiltinCommand(Command):
            name = "test"
            async def execute(self, **kwargs):
                return {}
        
        registry.register_builtin(BuiltinCommand)
        
        class CustomCommand(Command):
            name = "test"
            async def execute(self, **kwargs):
                return {}
        
        registry.register_custom(CustomCommand)
        
        # Should return custom command (highest priority)
        command_class = registry.get_command("test")
        assert command_class == CustomCommand
    
    def test_get_command_not_found(self, registry):
        """Test get_command with non-existent command."""
        with pytest.raises(NotFoundError, match="Command 'nonexistent' not found"):
            registry.get_command("nonexistent")
    
    def test_get_command_instance_existing(self, registry):
        """Test get_command_instance with existing instance."""
        instance = TestCommandWithInstance(dependency="test_dep")
        registry.register_builtin(instance)
        
        result = registry.get_command_instance("test_instance")
        assert result == instance
    
    def test_get_command_instance_create_new(self, registry):
        """Test get_command_instance creates new instance."""
        registry.register_builtin(TestCommand)
        
        result = registry.get_command_instance("test")
        assert isinstance(result, TestCommand)
    
    def test_get_command_instance_not_found(self, registry):
        """Test get_command_instance with non-existent command."""
        with pytest.raises(NotFoundError, match="Command 'nonexistent' not found"):
            registry.get_command_instance("nonexistent")
    
    def test_get_command_instance_creation_error(self, registry):
        """Test get_command_instance with creation error."""
        class CommandWithError(Command):
            name = "error_command"
            
            def __init__(self):
                raise Exception("Creation error")
            
            async def execute(self, **kwargs):
                return {}
        
        registry.register_builtin(CommandWithError)
        
        with pytest.raises(ValueError, match="requires dependencies but was registered as class"):
            registry.get_command_instance("error_command")
    
    def test_has_instance(self, registry):
        """Test has_instance method."""
        instance = TestCommandWithInstance(dependency="test_dep")
        registry.register_builtin(instance)
        
        assert registry.has_instance("test_instance") is True
        assert registry.has_instance("nonexistent") is False
    
    def test_get_all_commands_priority_order(self, registry):
        """Test get_all_commands priority order."""
        # Register commands in different categories
        registry.register_loaded(TestCommand)
        
        class BuiltinCommand(Command):
            name = "test"
            async def execute(self, **kwargs):
                return {}
        
        registry.register_builtin(BuiltinCommand)
        
        class CustomCommand(Command):
            name = "test"
            async def execute(self, **kwargs):
                return {}
        
        registry.register_custom(CustomCommand)
        
        all_commands = registry.get_all_commands()
        
        # Should only have custom command (highest priority)
        assert len(all_commands) == 1
        assert "test" in all_commands
        assert all_commands["test"] == CustomCommand
    
    def test_get_commands_by_type(self, registry):
        """Test get_commands_by_type method."""
        registry.register_builtin(TestCommand)
        
        class CustomCommand(Command):
            name = "custom"
            async def execute(self, **kwargs):
                return {}
        
        registry.register_custom(CustomCommand)
        
        class LoadedCommand(Command):
            name = "loaded"
            async def execute(self, **kwargs):
                return {}
        
        registry.register_loaded(LoadedCommand)
        
        commands_by_type = registry.get_commands_by_type()
        
        assert "custom" in commands_by_type["custom"]
        assert "test" in commands_by_type["builtin"]
        assert "loaded" in commands_by_type["loaded"]
    
    def test_get_all_metadata(self, registry):
        """Test get_all_metadata method."""
        registry.register_builtin(TestCommand)
        
        metadata = registry.get_all_metadata()
        
        assert "test" in metadata
        assert metadata["test"]["name"] == "test"
        assert "version" in metadata["test"]
        assert "summary" in metadata["test"]
    
    def test_get_all_metadata_with_error(self, registry):
        """Test get_all_metadata with command that raises error."""
        class CommandWithError(Command):
            name = "error_command"
            
            @classmethod
            def get_metadata(cls):
                raise Exception("Metadata error")
            
            async def execute(self, **kwargs):
                return {}
        
        registry.register_builtin(CommandWithError)
        
        metadata = registry.get_all_metadata()
        
        assert "error_command" in metadata
        assert "error" in metadata["error_command"]
        assert "Metadata error" in metadata["error_command"]["error"]
    
    def test_clear(self, registry):
        """Test clear method."""
        registry.register_builtin(TestCommand)
        registry.register_custom(TestCommandWithInstance)
        
        registry.clear()
        
        assert len(registry._builtin_commands) == 0
        assert len(registry._custom_commands) == 0
        assert len(registry._loaded_commands) == 0
        assert len(registry._instances) == 0
    
    @patch('mcp_proxy_adapter.commands.command_registry.config')
    @patch('mcp_proxy_adapter.core.logging.setup_logging')
    @patch('mcp_proxy_adapter.commands.builtin_commands.register_builtin_commands')
    @patch('mcp_proxy_adapter.commands.command_registry.hooks')
    def test_reload_system_success(self, mock_hooks, mock_register_builtin, mock_setup_logging, mock_config, registry):
        """Test successful system reload."""
        # Mock all dependencies
        mock_config.load_from_file.return_value = None
        mock_config.load_config.return_value = None
        mock_register_builtin.return_value = 5
        mock_hooks.execute_custom_commands_hooks.return_value = 3
        mock_hooks.execute_before_init_hooks.return_value = None
        mock_hooks.execute_after_init_hooks.return_value = None
        
        # Mock _load_all_commands
        with patch.object(registry, '_load_all_commands') as mock_load_all:
            mock_load_all.return_value = {"remote_commands": 2, "loaded_commands": 1}
            
            result = registry.reload_system()
        
        assert result["config_reloaded"] is True
        assert result["builtin_commands"] == 5
        assert result["custom_commands"] == 3
        assert result["loaded_commands"] == 1
        assert result["remote_commands"] == 2
        assert result["total_commands"] == 0  # No commands registered in test
    
    @patch('mcp_proxy_adapter.commands.command_registry.config')
    @patch('mcp_proxy_adapter.core.logging.setup_logging')
    @patch('mcp_proxy_adapter.commands.builtin_commands.register_builtin_commands')
    @patch('mcp_proxy_adapter.commands.command_registry.hooks')
    def test_reload_system_config_error(self, mock_hooks, mock_register_builtin, mock_setup_logging, mock_config, registry):
        """Test system reload with config error."""
        # Mock config error
        mock_config.load_config.side_effect = Exception("Config error")
        mock_register_builtin.return_value = 0
        mock_hooks.execute_custom_commands_hooks.return_value = 0
        mock_hooks.execute_before_init_hooks.return_value = None
        mock_hooks.execute_after_init_hooks.return_value = None
        
        # Mock _load_all_commands
        with patch.object(registry, '_load_all_commands') as mock_load_all:
            mock_load_all.return_value = {"remote_commands": 0, "loaded_commands": 0}
            
            result = registry.reload_system()
        
        assert result["config_reloaded"] is False
        assert result["builtin_commands"] == 0
        assert result["custom_commands"] == 0
    
    @patch('mcp_proxy_adapter.commands.command_registry.config')
    @patch('mcp_proxy_adapter.core.logging.setup_logging')
    @patch('mcp_proxy_adapter.commands.builtin_commands.register_builtin_commands')
    @patch('mcp_proxy_adapter.commands.command_registry.hooks')
    def test_reload_system_logging_error(self, mock_hooks, mock_register_builtin, mock_setup_logging, mock_config, registry):
        """Test system reload with logging error."""
        # Mock logging error
        mock_config.load_from_file.return_value = None
        mock_setup_logging.side_effect = Exception("Logging error")
        mock_register_builtin.return_value = 0
        mock_hooks.execute_custom_commands_hooks.return_value = 0
        mock_hooks.execute_before_init_hooks.return_value = None
        mock_hooks.execute_after_init_hooks.return_value = None
        
        # Mock _load_all_commands
        with patch.object(registry, '_load_all_commands') as mock_load_all:
            mock_load_all.return_value = {"remote_commands": 0, "loaded_commands": 0}
            
            result = registry.reload_system()
        
        assert result["config_reloaded"] is True
        assert result["builtin_commands"] == 0
        assert result["custom_commands"] == 0
    
    @patch('mcp_proxy_adapter.commands.command_registry.config')
    def test_load_all_commands_success(self, mock_config, registry):
        """Test successful loading of all commands."""
        # Mock configuration
        mock_config.get.side_effect = lambda key, default=None: {
            "commands.commands_directory": "/test/commands",
            "commands.plugin_servers": ["http://test.com"]
        }.get(key, default)
        
        # Mock directory exists
        with patch('os.path.exists', return_value=True):
            with patch('pathlib.Path.glob') as mock_glob:
                mock_glob.return_value = [Path("/test/commands/test_command.py")]
                
                with patch.object(registry, 'load_command_from_source') as mock_load:
                    mock_load.return_value = {"success": True, "commands_loaded": 1}
                    
                    # Mock catalog manager
                    with patch('mcp_proxy_adapter.commands.command_registry.CatalogManager') as mock_catalog:
                        mock_catalog_instance = Mock()
                        mock_catalog.return_value = mock_catalog_instance
                        mock_catalog_instance.get_catalog_from_server.return_value = {
                            "test_remote": Mock()
                        }
                        
                        result = registry._load_all_commands()
        
        assert result["loaded_commands"] == 1
        assert result["remote_commands"] == 0  # Mock load returns 0 for remote
    
    @patch('mcp_proxy_adapter.commands.command_registry.config')
    def test_load_all_commands_no_directory(self, mock_config, registry):
        """Test loading commands with no directory."""
        # Mock configuration - no directory
        mock_config.get.side_effect = lambda key, default=None: {
            "commands.commands_directory": None,
            "commands.plugin_servers": []
        }.get(key, default)
        
        result = registry._load_all_commands()
        
        assert result["loaded_commands"] == 0
        assert result["remote_commands"] == 0
    
    @patch('mcp_proxy_adapter.commands.command_registry.config')
    def test_load_all_commands_directory_not_exists(self, mock_config, registry):
        """Test loading commands with non-existent directory."""
        # Mock configuration
        mock_config.get.side_effect = lambda key, default=None: {
            "commands.commands_directory": "/nonexistent",
            "commands.plugin_servers": []
        }.get(key, default)
        
        # Mock directory doesn't exist
        with patch('os.path.exists', return_value=False):
            result = registry._load_all_commands()
        
        assert result["loaded_commands"] == 0
        assert result["remote_commands"] == 0
    
    @patch('mcp_proxy_adapter.commands.command_registry.config')
    def test_load_all_commands_with_error(self, mock_config, registry):
        """Test loading commands with error."""
        # Mock configuration
        mock_config.get.side_effect = Exception("Config error")
        
        result = registry._load_all_commands()
        
        assert result["loaded_commands"] == 0
        assert result["remote_commands"] == 0
        assert "error" in result
    
    def test_get_all_commands_info(self, registry):
        """Test get_all_commands_info method."""
        registry.register_builtin(TestCommand)
        
        info = registry.get_all_commands_info()
        
        assert "commands" in info
        assert "total" in info
        assert "test" in info["commands"]
        assert info["total"] == 1
    
    def test_get_all_commands_info_with_error(self, registry):
        """Test get_all_commands_info with command that raises error."""
        class CommandWithError(Command):
            name = "error_command"
            
            @classmethod
            def get_metadata(cls):
                raise Exception("Metadata error")
            
            async def execute(self, **kwargs):
                return {}
        
        registry.register_builtin(CommandWithError)
        
        info = registry.get_all_commands_info()
        
        assert "error_command" in info["commands"]
        assert "error" in info["commands"]["error_command"]
    
    def test_get_command_info_success(self, registry):
        """Test get_command_info with existing command."""
        registry.register_builtin(TestCommand)
        
        info = registry.get_command_info("test")
        
        assert info["name"] == "test"
        assert "metadata" in info
        assert "schema" in info
        assert info["type"] == "built-in"
    
    def test_get_command_info_not_found(self, registry):
        """Test get_command_info with non-existent command."""
        info = registry.get_command_info("nonexistent")
        
        assert info is None
    
    def test_get_command_info_with_error(self, registry):
        """Test get_command_info with command that raises error."""
        class CommandWithError(Command):
            name = "error_command"
            
            @classmethod
            def get_metadata(cls):
                raise Exception("Metadata error")
            
            async def execute(self, **kwargs):
                return {}
        
        registry.register_builtin(CommandWithError)
        
        info = registry.get_command_info("error_command")
        
        assert info["name"] == "error_command"
        assert "error" in info
    
    def test_get_command_type(self, registry):
        """Test _get_command_type method."""
        registry.register_builtin(TestCommand)
        
        class CustomCommand(Command):
            name = "custom"
            async def execute(self, **kwargs):
                return {}
        
        registry.register_custom(CustomCommand)
        
        class LoadedCommand(Command):
            name = "loaded"
            async def execute(self, **kwargs):
                return {}
        
        registry.register_loaded(LoadedCommand)
        
        assert registry._get_command_type("test") == "built-in"
        assert registry._get_command_type("custom") == "custom"
        assert registry._get_command_type("loaded") == "loaded"
        assert registry._get_command_type("nonexistent") == "unknown"
    
    def test_load_command_from_source_local_file(self, registry, temp_dir):
        """Test loading command from local file."""
        # Create test command file
        test_file = Path(temp_dir) / "test_command.py"
        test_file.write_text("""
from mcp_proxy_adapter.commands.base import Command

class TestCommand(Command):
    name = "test"
    
    async def execute(self, **kwargs):
        return {"result": "test"}
""")
        
        result = registry.load_command_from_source(str(test_file))
        
        assert result["success"] is True
        assert result["commands_loaded"] == 1
        assert result["source"] == str(test_file)
    
    def test_load_command_from_source_url(self, registry):
        """Test loading command from URL."""
        with patch.object(registry, '_load_command_from_url') as mock_load_url:
            mock_load_url.return_value = {"success": True, "commands_loaded": 1}
            
            result = registry.load_command_from_source("http://test.com/command.py")
        
        assert result["success"] is True
        assert result["commands_loaded"] == 1
        mock_load_url.assert_called_once_with("http://test.com/command.py")
    
    def test_load_command_from_source_with_registry_check(self, registry):
        """Test loading command with registry check."""
        with patch.object(registry, '_load_command_with_registry_check') as mock_load_registry:
            mock_load_registry.return_value = {"success": True, "commands_loaded": 1}
            
            result = registry.load_command_from_source("test_command")
        
        assert result["success"] is True
        assert result["commands_loaded"] == 1
        mock_load_registry.assert_called_once_with("test_command")
    
    def test_load_command_with_registry_check_success(self, registry):
        """Test loading command with registry check success."""
        with patch('mcp_proxy_adapter.commands.command_registry.config') as mock_config:
            mock_config.get.return_value = ["http://test.com"]
            
            with patch('mcp_proxy_adapter.commands.command_registry.CatalogManager') as mock_catalog:
                mock_catalog_instance = Mock()
                mock_catalog.return_value = mock_catalog_instance
                mock_catalog_instance.get_catalog_from_server.return_value = {
                    "test_command": Mock()
                }
                mock_catalog_instance._download_command.return_value = True
                mock_catalog_instance.commands_dir = Path("/test/catalog/commands")
                
                with patch.object(registry, '_load_command_from_file') as mock_load_file:
                    mock_load_file.return_value = {"success": True, "commands_loaded": 1}
                    
                    result = registry._load_command_with_registry_check("test_command")
        
        assert result["success"] is True
        assert result["commands_loaded"] == 1
    
    def test_load_command_with_registry_check_error(self, registry):
        """Test loading command with registry check error."""
        with patch('mcp_proxy_adapter.commands.command_registry.config') as mock_config:
            mock_config.get.side_effect = Exception("Config error")
            
            result = registry._load_command_with_registry_check("test_command")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_load_command_from_url_success(self, registry):
        """Test loading command from URL success."""
        with patch('mcp_proxy_adapter.commands.command_registry.REQUESTS_AVAILABLE', True):
            with patch('mcp_proxy_adapter.commands.command_registry.requests') as mock_requests:
                mock_response = Mock()
                mock_response.text = """
from mcp_proxy_adapter.commands.base import Command

class TestCommand(Command):
    name = "test"
    
    async def execute(self, **kwargs):
        return {"result": "test"}
"""
                mock_requests.get.return_value = mock_response
                
                with patch.object(registry, '_load_command_from_file') as mock_load_file:
                    mock_load_file.return_value = {"success": True, "commands_loaded": 1}
                    
                    result = registry._load_command_from_url("http://test.com/command.py")
        
        assert result["success"] is True
        assert result["commands_loaded"] == 1
        assert result["source"] == "http://test.com/command.py"
    
    def test_load_command_from_url_requests_not_available(self, registry):
        """Test loading command from URL with requests not available."""
        with patch('mcp_proxy_adapter.commands.command_registry.REQUESTS_AVAILABLE', False):
            result = registry._load_command_from_url("http://test.com/command.py")
        
        assert result["success"] is False
        assert "requests library not available" in result["error"]
    
    def test_load_command_from_url_error(self, registry):
        """Test loading command from URL with error."""
        with patch('mcp_proxy_adapter.commands.command_registry.REQUESTS_AVAILABLE', True):
            with patch('mcp_proxy_adapter.commands.command_registry.requests') as mock_requests:
                mock_requests.get.side_effect = Exception("Network error")
                
                result = registry._load_command_from_url("http://test.com/command.py")
        
        assert result["success"] is False
        assert "Network error" in result["error"]
    
    def test_load_command_from_file_success(self, registry, temp_dir):
        """Test loading command from file success."""
        # Create test command file
        test_file = Path(temp_dir) / "test_command.py"
        test_file.write_text("""
from mcp_proxy_adapter.commands.base import Command

class TestCommand(Command):
    name = "test"
    
    async def execute(self, **kwargs):
        return {"result": "test"}
""")
        
        result = registry._load_command_from_file(str(test_file))
        
        assert result["success"] is True
        assert result["commands_loaded"] == 1
        assert result["source"] == str(test_file)
    
    def test_load_command_from_file_not_exists(self, registry):
        """Test loading command from non-existent file."""
        result = registry._load_command_from_file("/nonexistent/file.py")
        
        assert result["success"] is False
        assert "does not exist" in result["error"]
    
    def test_load_command_from_file_invalid_name(self, registry, temp_dir):
        """Test loading command from file with invalid name."""
        # Create a file with invalid name
        invalid_file = os.path.join(temp_dir, "invalid.py")
        with open(invalid_file, 'w') as f:
            f.write("class InvalidCommand: pass")
        
        result = registry._load_command_from_file(invalid_file)
        
        assert result["success"] is False
        assert "must end with '_command.py'" in result["error"]
    
    def test_load_command_from_file_temporary_allowed(self, registry):
        """Test loading command from temporary file."""
        with patch('os.path.exists', return_value=True):
            with patch('importlib.util.spec_from_file_location') as mock_spec:
                mock_spec.return_value = None
                
                result = registry._load_command_from_file("/test/temp.py", is_temporary=True)
        
        assert result["success"] is False
        assert "Failed to create module spec" in result["error"]
    
    def test_load_command_from_file_import_error(self, registry, temp_dir):
        """Test loading command from file with import error."""
        # Create invalid command file
        test_file = Path(temp_dir) / "test_command.py"
        test_file.write_text("invalid python code")
        
        result = registry._load_command_from_file(str(test_file))
        
        assert result["success"] is False
        assert "Error loading command" in result["error"]
    
    def test_unload_command_success(self, registry):
        """Test successful command unloading."""
        registry.register_loaded(TestCommand)
        
        result = registry.unload_command("test")
        
        assert result["success"] is True
        assert result["command_name"] == "test"
        assert "test" not in registry._loaded_commands
    
    def test_unload_command_not_found(self, registry):
        """Test unloading non-existent command."""
        result = registry.unload_command("nonexistent")
        
        assert result["success"] is False
        assert "not a loaded command" in result["error"]
    
    def test_unload_command_with_instance(self, registry):
        """Test unloading command with instance."""
        instance = TestCommandWithInstance(dependency="test_dep")
        registry.register_loaded(instance)
        
        result = registry.unload_command("test_instance")
        
        assert result["success"] is True
        assert "test_instance" not in registry._instances
    
    def test_unload_command_error(self, registry):
        """Test unloading command with error."""
        registry.register_loaded(TestCommand)
        
        # Mock error during unloading by patching the method
        with patch.object(registry, '_loaded_commands') as mock_commands:
            mock_commands.__delitem__.side_effect = Exception("Unload error")
            mock_commands.__contains__.return_value = True
            
            result = registry.unload_command("test")
        
        assert result["success"] is False
        assert "Unload error" in result["error"] 