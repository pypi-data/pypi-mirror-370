"""
Extended tests for API handlers module.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException

from mcp_proxy_adapter.api.handlers import (
    execute_command, handle_json_rpc, handle_batch_json_rpc,
    get_server_health, get_commands_list
)
from mcp_proxy_adapter.core.errors import MethodNotFoundError, InternalError, MicroserviceError, InvalidRequestError


class TestExecuteCommandExtended:
    """Extended tests for execute_command function."""
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_execute_command_with_valid_params(self, mock_registry):
        """Test execute_command with valid parameters."""
        # Mock command class
        mock_command_class = MagicMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"success": True, "data": "test"}
        mock_command_class.run = AsyncMock(return_value=mock_result)
        
        mock_registry.get_command.return_value = mock_command_class
        
        result = await execute_command("test_command", {"param": "value"})
        
        assert result == {"success": True, "data": "test"}
        mock_command_class.run.assert_called_once_with(param="value")
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_execute_command_with_no_params(self, mock_registry):
        """Test execute_command with no parameters."""
        # Mock command class
        mock_command_class = MagicMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"success": True}
        mock_command_class.run = AsyncMock(return_value=mock_result)
        
        mock_registry.get_command.return_value = mock_command_class
        
        result = await execute_command("test_command", {})
        
        assert result == {"success": True}
        mock_command_class.run.assert_called_once_with()
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_execute_command_not_found(self, mock_registry):
        """Test execute_command with command not found."""
        from mcp_proxy_adapter.core.errors import NotFoundError
        
        mock_registry.get_command.side_effect = NotFoundError("Command not found")
        
        with pytest.raises(MethodNotFoundError):
            await execute_command("nonexistent_command", {})
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_execute_command_execution_error(self, mock_registry):
        """Test execute_command with execution error."""
        # Mock command class that raises exception
        mock_command_class = MagicMock()
        mock_command_class.run = AsyncMock(side_effect=Exception("Execution error"))
        
        mock_registry.get_command.return_value = mock_command_class
        
        with pytest.raises(InternalError):
            await execute_command("test_command", {})
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_execute_command_microservice_error(self, mock_registry):
        """Test execute_command with MicroserviceError (covers line 62)."""
        # Mock command class that raises MicroserviceError
        mock_command_class = MagicMock()
        mock_command_class.run = AsyncMock(side_effect=MicroserviceError("Custom error"))
        
        mock_registry.get_command.return_value = mock_command_class
        
        with pytest.raises(MicroserviceError):
            await execute_command("test_command", {})


class TestHandleJsonRpcExtended:
    """Extended tests for handle_json_rpc function."""
    
    @patch('mcp_proxy_adapter.api.handlers.execute_command')
    async def test_handle_json_rpc_with_valid_request(self, mock_execute_command):
        """Test handle_json_rpc with valid request."""
        mock_execute_command.return_value = {"success": True}
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "test_command",
            "params": {"param": "value"},
            "id": 1
        }
        
        result = await handle_json_rpc(request_data)
        
        assert result["jsonrpc"] == "2.0"
        assert result["result"] == {"success": True}
        assert result["id"] == 1
        mock_execute_command.assert_called_once_with("test_command", {"param": "value"}, None)
    
    @patch('mcp_proxy_adapter.api.handlers.execute_command')
    async def test_handle_json_rpc_with_null_params(self, mock_execute_command):
        """Test handle_json_rpc with null parameters."""
        mock_execute_command.return_value = {"success": True}
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "test_command",
            "params": None,
            "id": 1
        }
        
        result = await handle_json_rpc(request_data)
        
        assert result["jsonrpc"] == "2.0"
        assert result["result"] == {"success": True}
        assert result["id"] == 1
        mock_execute_command.assert_called_once_with("test_command", None, None)
    
    @patch('mcp_proxy_adapter.api.handlers.execute_command')
    async def test_handle_json_rpc_with_execution_error(self, mock_execute_command):
        """Test handle_json_rpc with execution error."""
        mock_execute_command.side_effect = InternalError("Execution error")
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "test_command",
            "params": {},
            "id": 1
        }
        
        result = await handle_json_rpc(request_data)
        
        assert result["jsonrpc"] == "2.0"
        assert result["error"]["code"] == -32603
        assert result["id"] == 1
    
    @patch('mcp_proxy_adapter.api.handlers.execute_command')
    async def test_handle_json_rpc_with_no_id(self, mock_execute_command):
        """Test handle_json_rpc with no id."""
        mock_execute_command.return_value = {"success": True}
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "test_command",
            "params": {}
        }
        
        result = await handle_json_rpc(request_data)
        
        assert result["jsonrpc"] == "2.0"
        assert result["result"] == {"success": True}
        # When id is not provided, it's set to None in the response
        assert result["id"] is None
    
    async def test_handle_json_rpc_invalid_version(self):
        """Test handle_json_rpc with invalid JSON-RPC version (covers line 107)."""
        request_data = {
            "jsonrpc": "1.0",  # Invalid version
            "method": "test_command",
            "params": {},
            "id": 1
        }
        
        result = await handle_json_rpc(request_data)
        
        assert result["jsonrpc"] == "2.0"
        assert "error" in result
        assert result["error"]["code"] == -32600  # Invalid Request
        assert result["id"] == 1
    
    async def test_handle_json_rpc_missing_method(self):
        """Test handle_json_rpc with missing method (covers line 118)."""
        request_data = {
            "jsonrpc": "2.0",
            "params": {},
            "id": 1
        }
        
        result = await handle_json_rpc(request_data)
        
        assert result["jsonrpc"] == "2.0"
        assert "error" in result
        assert result["error"]["code"] == -32600  # Invalid Request
        assert result["id"] == 1
    
    @patch('mcp_proxy_adapter.api.handlers.execute_command')
    async def test_handle_json_rpc_unhandled_exception(self, mock_execute_command):
        """Test handle_json_rpc with unhandled exception (covers lines 139-142)."""
        mock_execute_command.side_effect = Exception("Unexpected error")
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "test_command",
            "params": {},
            "id": 1
        }
        
        result = await handle_json_rpc(request_data)
        
        assert result["jsonrpc"] == "2.0"
        assert "error" in result
        assert result["error"]["code"] == -32603  # Internal error
        assert result["id"] == 1


class TestHandleBatchJsonRpcExtended:
    """Extended tests for handle_batch_json_rpc function."""
    
    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc_with_multiple_requests(self):
        """Test handle_batch_json_rpc with multiple requests."""
        request_data = [
            {
                "jsonrpc": "2.0",
                "method": "command1",
                "params": {"param1": "value1"},
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "command2",
                "params": {"param2": "value2"},
                "id": 2
            }
        ]
        
        with patch('mcp_proxy_adapter.api.handlers.handle_json_rpc') as mock_handle:
            mock_handle.side_effect = [
                {"jsonrpc": "2.0", "result": {"success": True, "data": "result1"}, "id": 1},
                {"jsonrpc": "2.0", "result": {"success": True, "data": "result2"}, "id": 2}
            ]
            
            result = await handle_batch_json_rpc(request_data)
            
            assert len(result) == 2
            assert result[0]["jsonrpc"] == "2.0"
            assert result[0]["result"] == {"success": True, "data": "result1"}
            assert result[0]["id"] == 1
            assert result[1]["jsonrpc"] == "2.0"
            assert result[1]["result"] == {"success": True, "data": "result2"}
            assert result[1]["id"] == 2
    
    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc_with_mixed_results(self):
        """Test handle_batch_json_rpc with mixed success and error results."""
        request_data = [
            {
                "jsonrpc": "2.0",
                "method": "command1",
                "params": {},
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "command2",
                "params": {},
                "id": 2
            }
        ]
        
        with patch('mcp_proxy_adapter.api.handlers.handle_json_rpc') as mock_handle:
            mock_handle.side_effect = [
                {"jsonrpc": "2.0", "result": {"success": True, "data": "result1"}, "id": 1},
                {"jsonrpc": "2.0", "error": {"code": 404, "message": "Not found"}, "id": 2}
            ]
            
            result = await handle_batch_json_rpc(request_data)
            
            assert len(result) == 2
            assert result[0]["jsonrpc"] == "2.0"
            assert "result" in result[0]
            assert result[1]["jsonrpc"] == "2.0"
            assert "error" in result[1]
            assert result[1]["error"]["code"] == 404
    
    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc_with_empty_batch(self):
        """Test handle_batch_json_rpc with empty batch."""
        request_data = []
        
        result = await handle_batch_json_rpc(request_data)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc_with_single_request(self):
        """Test handle_batch_json_rpc with single request."""
        request_data = [
            {
                "jsonrpc": "2.0",
                "method": "test_command",
                "params": {"param1": "value1"},
                "id": 1
            }
        ]
        
        with patch('mcp_proxy_adapter.api.handlers.handle_json_rpc') as mock_handle:
            mock_handle.return_value = {"jsonrpc": "2.0", "result": {"success": True, "data": "test"}, "id": 1}
            
            result = await handle_batch_json_rpc(request_data)
            
            assert len(result) == 1
            assert result[0]["jsonrpc"] == "2.0"
            assert result[0]["result"] == {"success": True, "data": "test"}
            assert result[0]["id"] == 1


class TestGetServerHealthExtended:
    """Extended tests for get_server_health function."""
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_get_server_health_success(self, mock_registry):
        """Test get_server_health success."""
        mock_registry.get_all_commands.return_value = {"cmd1": {}, "cmd2": {}}
        
        result = await get_server_health()
        
        assert "status" in result
        assert "version" in result
        assert "uptime" in result
        assert "components" in result
        assert result["status"] == "ok"
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_get_server_health_with_commands(self, mock_registry):
        """Test get_server_health with commands."""
        mock_registry.get_all_commands.return_value = {"cmd1": {}, "cmd2": {}, "cmd3": {}}
        
        result = await get_server_health()
        
        assert result["components"]["commands"]["registered_count"] == 3


class TestGetCommandsListExtended:
    """Extended tests for get_commands_list function."""
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_get_commands_list_with_commands(self, mock_registry):
        """Test get_commands_list with commands."""
        # Mock commands
        mock_command1 = MagicMock()
        mock_command1.name = "command1"
        mock_command1.description = ""
        mock_command1.get_schema.return_value = {"type": "object"}
        
        mock_command2 = MagicMock()
        mock_command2.name = "command2"
        mock_command2.description = ""
        mock_command2.get_schema.return_value = {"type": "object"}
        
        mock_registry.get_all_commands.return_value = {
            "command1": mock_command1,
            "command2": mock_command2
        }
        
        result = await get_commands_list()
        
        assert "command1" in result
        assert "command2" in result
        assert result["command1"]["name"] == "command1"
        assert result["command2"]["name"] == "command2"
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_get_commands_list_with_no_commands(self, mock_registry):
        """Test get_commands_list with no commands."""
        mock_registry.get_all_commands.return_value = {}
        
        result = await get_commands_list()
        
        assert result == {}
    
    @patch('mcp_proxy_adapter.api.handlers.registry')
    async def test_get_commands_list_with_schema_error(self, mock_registry):
        """Test get_commands_list with schema error."""
        # Mock command that raises exception
        mock_command = MagicMock()
        mock_command.name = "command1"
        mock_command.description = ""
        mock_command.get_schema.side_effect = Exception("Schema error")
        
        mock_registry.get_all_commands.return_value = {"command1": mock_command}
        
        with pytest.raises(Exception):
            await get_commands_list() 