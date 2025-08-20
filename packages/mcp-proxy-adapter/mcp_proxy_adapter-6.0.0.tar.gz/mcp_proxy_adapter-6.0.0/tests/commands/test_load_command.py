"""
Tests for load command.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from mcp_proxy_adapter.commands.load_command import LoadCommand, LoadResult
from mcp_proxy_adapter.commands.command_registry import registry


class TestLoadCommand:
    """Test cases for LoadCommand."""
    
    def setup_method(self):
        """Setup test method."""
        self.command = LoadCommand()
    
    def test_command_name(self):
        """Test command name."""
        assert LoadCommand.name == "load"
    
    def test_result_class(self):
        """Test result class."""
        assert LoadCommand.result_class == LoadResult
    
    @pytest.mark.asyncio
    async def test_execute_success_local_file(self):
        """Test successful execution with local file."""
        # Create temporary command file
        with tempfile.NamedTemporaryFile(mode='w', suffix='_command.py', delete=False) as temp_file:
            temp_file.write("""
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult

class TestResult(SuccessResult):
    def __init__(self, message):
        super().__init__(data={"message": message}, message=message)
    
    @classmethod
    def get_schema(cls):
        return {"type": "object"}

class TestCommand(Command):
    name = "test_command"
    result_class = TestResult
    
    async def execute(self, **kwargs):
        return TestResult("test message")
""")
            temp_file_path = temp_file.name
        
        try:
            # Execute command
            result = await self.command.execute(source=temp_file_path)
            
            # Verify result
            assert isinstance(result, LoadResult)
            assert result.data["success"] is True
            assert result.data["commands_loaded"] == 1
            assert "test_command" in result.data["loaded_commands"]
            assert result.data["source"] == temp_file_path
            
        finally:
            # Cleanup
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_execute_success_url(self):
        """Test successful execution with URL."""
        mock_response = MagicMock()
        mock_response.text = """
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult

class TestResult(SuccessResult):
    def __init__(self, message):
        super().__init__(data={"message": message}, message=message)
    
    @classmethod
    def get_schema(cls):
        return {"type": "object"}

class TestCommand(Command):
    name = "test_command"
    result_class = TestResult
    
    async def execute(self, **kwargs):
        return TestResult("test message")
"""
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get', return_value=mock_response):
            # Execute command
            result = await self.command.execute(source="https://example.com/test_command.py")
            
            # Verify result
            assert isinstance(result, LoadResult)
            assert result.data["success"] is True
            assert result.data["commands_loaded"] == 1
            assert "test_command" in result.data["loaded_commands"]
            assert result.data["source"] == "https://example.com/test_command.py"
    
    @pytest.mark.asyncio
    async def test_execute_file_not_found(self):
        """Test execution with non-existent file."""
        result = await self.command.execute(source="/nonexistent/path/test_command.py")
        
        assert isinstance(result, LoadResult)
        assert result.data["success"] is False
        assert "error" in result.data
        assert "does not exist" in result.data["error"]
    
    @pytest.mark.asyncio
    async def test_execute_invalid_filename(self):
        """Test execution with invalid filename."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write("print('test')")
            temp_file_path = temp_file.name
        
        try:
            result = await self.command.execute(source=temp_file_path)
            
            assert isinstance(result, LoadResult)
            assert result.data["success"] is False
            assert "error" in result.data
            assert "must end with '_command.py'" in result.data["error"]
            
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_execute_url_error(self):
        """Test execution with URL error."""
        with patch('requests.get', side_effect=Exception("Network error")):
            result = await self.command.execute(source="https://example.com/test_command.py")
            
            assert isinstance(result, LoadResult)
            assert result.data["success"] is False
            assert "error" in result.data
            assert "Network error" in result.data["error"]
    
    def test_get_schema(self):
        """Test command schema."""
        schema = LoadCommand.get_schema()
        
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "source" in schema["properties"]
        assert "required" in schema
        assert "source" in schema["required"]


class TestLoadResult:
    """Test cases for LoadResult."""
    
    def test_success_result(self):
        """Test successful result creation."""
        result = LoadResult(
            success=True,
            commands_loaded=2,
            loaded_commands=["cmd1", "cmd2"],
            source="/path/to/commands"
        )
        
        assert result.data["success"] is True
        assert result.data["commands_loaded"] == 2
        assert result.data["loaded_commands"] == ["cmd1", "cmd2"]
        assert result.data["source"] == "/path/to/commands"
        assert "error" not in result.data
    
    def test_error_result(self):
        """Test error result creation."""
        result = LoadResult(
            success=False,
            commands_loaded=0,
            loaded_commands=[],
            source="/path/to/commands",
            error="File not found"
        )
        
        assert result.data["success"] is False
        assert result.data["commands_loaded"] == 0
        assert result.data["loaded_commands"] == []
        assert result.data["source"] == "/path/to/commands"
        assert result.data["error"] == "File not found"
    
    def test_get_schema(self):
        """Test result schema."""
        schema = LoadResult.get_schema()
        
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "data" in schema["properties"] 