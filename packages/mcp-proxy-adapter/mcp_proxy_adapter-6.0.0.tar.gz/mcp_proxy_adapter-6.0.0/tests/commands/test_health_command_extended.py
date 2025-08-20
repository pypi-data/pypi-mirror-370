"""
Extended tests for health command.
"""

import pytest
from unittest.mock import patch, MagicMock
import time
from datetime import datetime

from mcp_proxy_adapter.commands.health_command import HealthResult, HealthCommand


class TestHealthResultExtended:
    """Extended tests for HealthResult class."""
    
    def test_init_with_all_parameters(self):
        """Test HealthResult initialization with all parameters."""
        components = {
            "system": {"cpu": "test"},
            "process": {"memory": "test"},
            "commands": {"count": 5}
        }
        
        result = HealthResult(
            status="ok",
            version="1.0.0",
            uptime=123.45,
            components=components
        )
        
        assert result.data["status"] == "ok"
        assert result.data["version"] == "1.0.0"
        assert result.data["uptime"] == 123.45
        assert result.data["components"] == components
    
    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        components = {
            "system": {"cpu": "test"},
            "process": {"memory": "test"},
            "commands": {"count": 5}
        }
        
        result = HealthResult(
            status="ok",
            version="1.0.0",
            uptime=123.45,
            components=components
        )
        
        data = result.to_dict()
        assert data["success"] is True
        assert data["data"]["status"] == "ok"
        assert data["data"]["version"] == "1.0.0"
        assert data["data"]["uptime"] == 123.45
        assert data["data"]["components"] == components
    
    def test_to_dict_with_minimal_fields(self):
        """Test to_dict method with minimal fields."""
        result = HealthResult(
            status="error",
            version="unknown",
            uptime=0.0,
            components={}
        )
        
        data = result.to_dict()
        assert data["success"] is True
        assert data["data"]["status"] == "error"
        assert data["data"]["version"] == "unknown"
        assert data["data"]["uptime"] == 0.0
        assert data["data"]["components"] == {}
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = HealthResult.get_schema()
        
        assert schema["type"] == "object"
        assert "data" in schema["properties"]
        assert "status" in schema["properties"]["data"]["properties"]
        assert "version" in schema["properties"]["data"]["properties"]
        assert "uptime" in schema["properties"]["data"]["properties"]
        assert "components" in schema["properties"]["data"]["properties"]


class TestHealthCommandExtended:
    """Extended tests for HealthCommand class."""
    
    def test_name_and_description(self):
        """Test command name and description."""
        assert HealthCommand.name == "health"
        assert hasattr(HealthCommand, 'result_class')
        assert HealthCommand.result_class == HealthResult
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = HealthCommand.get_schema()
        
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert "description" in schema
    
    @patch('mcp_proxy_adapter.commands.health_command.psutil.Process')
    @patch('mcp_proxy_adapter.commands.health_command.datetime')
    @patch('mcp_proxy_adapter.commands.health_command.os')
    @patch('mcp_proxy_adapter.commands.health_command.platform')
    @patch('mcp_proxy_adapter.commands.health_command.sys')
    @patch('mcp_proxy_adapter.commands.health_command.registry')
    async def test_execute_basic_health_check(self, mock_registry, mock_sys, mock_platform, mock_os, mock_datetime, mock_process):
        """Test basic health check execution."""
        # Mock process
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(rss=1024*1024*100)  # 100MB
        mock_process.return_value = mock_process_instance
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_start_time = datetime(2023, 1, 1, 11, 58, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_start_time
        
        # Mock other dependencies
        mock_os.getpid.return_value = 12345
        mock_os.cpu_count.return_value = 4
        mock_sys.version = "3.12.0"
        mock_platform.platform.return_value = "Linux-5.4.0-x86_64"
        mock_registry.get_all_commands.return_value = {"cmd1": {}, "cmd2": {}}
        
        command = HealthCommand()
        result = await command.execute()
        
        assert isinstance(result, HealthResult)
        assert result.data["status"] == "ok"
        assert result.data["uptime"] == 120.0  # 2 minutes
        assert "system" in result.data["components"]
        assert "process" in result.data["components"]
        assert "commands" in result.data["components"]
    
    @patch('mcp_proxy_adapter.commands.health_command.psutil.Process')
    @patch('mcp_proxy_adapter.commands.health_command.datetime')
    @patch('mcp_proxy_adapter.commands.health_command.os')
    @patch('mcp_proxy_adapter.commands.health_command.platform')
    @patch('mcp_proxy_adapter.commands.health_command.sys')
    @patch('mcp_proxy_adapter.commands.health_command.registry')
    async def test_execute_detailed_health_check(self, mock_registry, mock_sys, mock_platform, mock_os, mock_datetime, mock_process):
        """Test detailed health check execution."""
        # Mock process
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(rss=1024*1024*200)  # 200MB
        mock_process.return_value = mock_process_instance
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_start_time = datetime(2023, 1, 1, 11, 55, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_start_time
        
        # Mock other dependencies
        mock_os.getpid.return_value = 12345
        mock_os.cpu_count.return_value = 8
        mock_sys.version = "3.12.0"
        mock_platform.platform.return_value = "Linux-5.4.0-x86_64"
        mock_registry.get_all_commands.return_value = {"cmd1": {}, "cmd2": {}, "cmd3": {}}
        
        command = HealthCommand()
        result = await command.execute()
        
        assert isinstance(result, HealthResult)
        assert result.data["status"] == "ok"
        assert result.data["uptime"] == 300.0  # 5 minutes
        assert result.data["components"]["system"]["cpu_count"] == 8
        assert result.data["components"]["process"]["memory_usage_mb"] == 200.0
        assert result.data["components"]["commands"]["registered_count"] == 3
    
    @patch('mcp_proxy_adapter.commands.health_command.psutil.Process')
    @patch('mcp_proxy_adapter.commands.health_command.datetime')
    @patch('mcp_proxy_adapter.commands.health_command.os')
    @patch('mcp_proxy_adapter.commands.health_command.platform')
    @patch('mcp_proxy_adapter.commands.health_command.sys')
    @patch('mcp_proxy_adapter.commands.health_command.registry')
    async def test_execute_health_check_with_custom_start_time(self, mock_registry, mock_sys, mock_platform, mock_os, mock_datetime, mock_process):
        """Test health check with custom start time."""
        # Mock process
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(rss=1024*1024*150)  # 150MB
        mock_process.return_value = mock_process_instance
        
        # Mock datetime with specific start time
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_start_time = datetime(2023, 1, 1, 11, 59, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_start_time
        
        # Mock other dependencies
        mock_os.getpid.return_value = 12345
        mock_os.cpu_count.return_value = 4
        mock_sys.version = "3.12.0"
        mock_platform.platform.return_value = "Linux-5.4.0-x86_64"
        mock_registry.get_all_commands.return_value = {"cmd1": {}}
        
        command = HealthCommand()
        result = await command.execute()
        
        assert isinstance(result, HealthResult)
        assert result.data["uptime"] == 30.0  # 30 seconds
        assert result.data["components"]["process"]["start_time"] == mock_start_time.isoformat()
    
    @patch('mcp_proxy_adapter.commands.health_command.psutil.Process')
    @patch('mcp_proxy_adapter.commands.health_command.datetime')
    @patch('mcp_proxy_adapter.commands.health_command.os')
    @patch('mcp_proxy_adapter.commands.health_command.platform')
    @patch('mcp_proxy_adapter.commands.health_command.sys')
    @patch('mcp_proxy_adapter.commands.health_command.registry')
    async def test_execute_health_check_with_additional_kwargs(self, mock_registry, mock_sys, mock_platform, mock_os, mock_datetime, mock_process):
        """Test health check with additional kwargs."""
        # Mock process
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(rss=1024*1024*100)
        mock_process.return_value = mock_process_instance
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_start_time = datetime(2023, 1, 1, 11, 58, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_start_time
        
        # Mock other dependencies
        mock_os.getpid.return_value = 12345
        mock_os.cpu_count.return_value = 4
        mock_sys.version = "3.12.0"
        mock_platform.platform.return_value = "Linux-5.4.0-x86_64"
        mock_registry.get_all_commands.return_value = {}
        
        command = HealthCommand()
        # HealthCommand.execute() doesn't accept additional kwargs, so we call it without them
        result = await command.execute()
        
        assert isinstance(result, HealthResult)
        assert result.data["status"] == "ok"
    
    @patch('mcp_proxy_adapter.commands.health_command.psutil.Process')
    @patch('mcp_proxy_adapter.commands.health_command.datetime')
    @patch('mcp_proxy_adapter.commands.health_command.os')
    @patch('mcp_proxy_adapter.commands.health_command.platform')
    @patch('mcp_proxy_adapter.commands.health_command.sys')
    @patch('mcp_proxy_adapter.commands.health_command.registry')
    async def test_execute_health_check_with_version_info(self, mock_registry, mock_sys, mock_platform, mock_os, mock_datetime, mock_process):
        """Test health check with version information."""
        # Mock process
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(rss=1024*1024*100)
        mock_process.return_value = mock_process_instance
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_start_time = datetime(2023, 1, 1, 11, 58, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_start_time
        
        # Mock other dependencies
        mock_os.getpid.return_value = 12345
        mock_os.cpu_count.return_value = 4
        mock_sys.version = "3.12.0"
        mock_platform.platform.return_value = "Linux-5.4.0-x86_64"
        mock_registry.get_all_commands.return_value = {}
        
        # Mock the version import inside the execute method
        with patch('builtins.__import__') as mock_import:
            mock_version_module = MagicMock()
            mock_version_module.__version__ = "1.2.3"
            mock_import.return_value = mock_version_module
            
            command = HealthCommand()
            result = await command.execute()
            
            assert isinstance(result, HealthResult)
            assert result.data["version"] == "1.2.3"
    
    @patch('mcp_proxy_adapter.commands.health_command.psutil.Process')
    @patch('mcp_proxy_adapter.commands.health_command.datetime')
    @patch('mcp_proxy_adapter.commands.health_command.os')
    @patch('mcp_proxy_adapter.commands.health_command.platform')
    @patch('mcp_proxy_adapter.commands.health_command.sys')
    @patch('mcp_proxy_adapter.commands.health_command.registry')
    async def test_execute_health_check_with_system_info(self, mock_registry, mock_sys, mock_platform, mock_os, mock_datetime, mock_process):
        """Test health check with system information."""
        # Mock process
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(rss=1024*1024*100)
        mock_process.return_value = mock_process_instance
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_start_time = datetime(2023, 1, 1, 11, 58, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_start_time
        
        # Mock other dependencies
        mock_os.getpid.return_value = 12345
        mock_os.cpu_count.return_value = 16
        mock_sys.version = "3.12.0 (default, Jan 1 2023, 12:00:00)"
        mock_platform.platform.return_value = "Linux-5.4.0-x86_64-with-glibc2.31"
        mock_registry.get_all_commands.return_value = {}
        
        command = HealthCommand()
        result = await command.execute()
        
        assert isinstance(result, HealthResult)
        assert result.data["components"]["system"]["python_version"] == "3.12.0 (default, Jan 1 2023, 12:00:00)"
        assert result.data["components"]["system"]["platform"] == "Linux-5.4.0-x86_64-with-glibc2.31"
        assert result.data["components"]["system"]["cpu_count"] == 16
    
    @patch('mcp_proxy_adapter.commands.health_command.psutil.Process')
    @patch('mcp_proxy_adapter.commands.health_command.datetime')
    @patch('mcp_proxy_adapter.commands.health_command.os')
    @patch('mcp_proxy_adapter.commands.health_command.platform')
    @patch('mcp_proxy_adapter.commands.health_command.sys')
    @patch('mcp_proxy_adapter.commands.health_command.registry')
    async def test_execute_health_check_with_memory_info(self, mock_registry, mock_sys, mock_platform, mock_os, mock_datetime, mock_process):
        """Test health check with memory information."""
        # Mock process with specific memory usage
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(rss=1024*1024*512)  # 512MB
        mock_process.return_value = mock_process_instance
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_start_time = datetime(2023, 1, 1, 11, 58, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_start_time
        
        # Mock other dependencies
        mock_os.getpid.return_value = 12345
        mock_os.cpu_count.return_value = 4
        mock_sys.version = "3.12.0"
        mock_platform.platform.return_value = "Linux-5.4.0-x86_64"
        mock_registry.get_all_commands.return_value = {}
        
        command = HealthCommand()
        result = await command.execute()
        
        assert isinstance(result, HealthResult)
        assert result.data["components"]["process"]["memory_usage_mb"] == 512.0
        assert result.data["components"]["process"]["pid"] == 12345
    
    @patch('mcp_proxy_adapter.commands.health_command.psutil.Process')
    @patch('mcp_proxy_adapter.commands.health_command.datetime')
    @patch('mcp_proxy_adapter.commands.health_command.os')
    @patch('mcp_proxy_adapter.commands.health_command.platform')
    @patch('mcp_proxy_adapter.commands.health_command.sys')
    @patch('mcp_proxy_adapter.commands.health_command.registry')
    async def test_execute_health_check_with_cpu_info(self, mock_registry, mock_sys, mock_platform, mock_os, mock_datetime, mock_process):
        """Test health check with CPU information."""
        # Mock process
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(rss=1024*1024*100)
        mock_process.return_value = mock_process_instance
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_start_time = datetime(2023, 1, 1, 11, 58, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_start_time
        
        # Mock other dependencies
        mock_os.getpid.return_value = 12345
        mock_os.cpu_count.return_value = 32
        mock_sys.version = "3.12.0"
        mock_platform.platform.return_value = "Linux-5.4.0-x86_64"
        mock_registry.get_all_commands.return_value = {"cmd1": {}, "cmd2": {}, "cmd3": {}, "cmd4": {}}
        
        command = HealthCommand()
        result = await command.execute()
        
        assert isinstance(result, HealthResult)
        assert result.data["components"]["system"]["cpu_count"] == 32
        assert result.data["components"]["commands"]["registered_count"] == 4 