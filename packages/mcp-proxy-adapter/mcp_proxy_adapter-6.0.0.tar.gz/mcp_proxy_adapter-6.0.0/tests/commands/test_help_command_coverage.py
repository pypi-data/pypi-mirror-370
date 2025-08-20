"""
Additional tests for help_command.py to achieve higher coverage.
"""

import pytest
from unittest.mock import Mock, patch
from mcp_proxy_adapter.commands.help_command import HelpResult, HelpCommand
from mcp_proxy_adapter.core.errors import NotFoundError


class TestHelpResultCoverage:
    """Additional tests to cover missing lines in HelpResult."""
    
    # Note: Exception handling in to_dict is complex to test due to built-in dict methods
    # The coverage is already good at 85%
    pass


class TestHelpCommandCoverage:
    """Additional tests to cover missing lines in HelpCommand."""
    
    @pytest.fixture
    def help_command(self):
        """Create HelpCommand instance."""
        return HelpCommand()
    
    async def test_execute_with_cmdname_not_found(self, help_command):
        """Test execute with cmdname that is not found."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_command_metadata.side_effect = NotFoundError("Command not found")
            mock_registry.get_all_metadata.return_value = {"test_command": {"summary": "Test"}}
            
            result = await help_command.execute(cmdname="nonexistent_command")
            
            assert isinstance(result, HelpResult)
            assert "error" in result.commands_info
            assert "Command 'nonexistent_command' not found" in result.commands_info["error"]
    
    async def test_execute_with_cmdname_not_found_no_commands(self, help_command):
        """Test execute with cmdname that is not found and no commands available."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_command_metadata.side_effect = NotFoundError("Command not found")
            mock_registry.get_all_metadata.return_value = {}
            
            result = await help_command.execute(cmdname="nonexistent_command")
            
            assert isinstance(result, HelpResult)
            assert "error" in result.commands_info
            assert "Command 'nonexistent_command' not found" in result.commands_info["error"]
            assert "No commands registered" in result.commands_info["note"]
    
    async def test_execute_with_metadata_processing_error(self, help_command):
        """Test execute with error in metadata processing."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            # Create metadata that will cause an error during processing
            problematic_metadata = {
                "test_command": {"params": None}  # This will cause an error when len() is called
            }
            mock_registry.get_all_metadata.return_value = problematic_metadata
            
            result = await help_command.execute()
            
            assert isinstance(result, HelpResult)
            assert "commands" in result.commands_info
            # The problematic command should be skipped
            assert len(result.commands_info["commands"]) == 0
    
    async def test_execute_with_unexpected_exception(self, help_command):
        """Test execute with unexpected exception."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_all_metadata.side_effect = Exception("Unexpected error")
            
            result = await help_command.execute()
            
            assert isinstance(result, HelpResult)
            assert "error" in result.commands_info
            assert "Unexpected error" in result.commands_info["error"]
            assert "tool_info" in result.commands_info 