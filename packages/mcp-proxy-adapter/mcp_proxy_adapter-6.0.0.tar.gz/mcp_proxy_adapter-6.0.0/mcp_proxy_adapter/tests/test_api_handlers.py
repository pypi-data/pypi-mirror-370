"""
Tests for API handlers.
"""

import json
import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, patch, MagicMock

from mcp_proxy_adapter.api.handlers import (
    execute_command, handle_json_rpc, handle_batch_json_rpc,
    get_server_health, get_commands_list
)
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.tests.stubs.echo_command import EchoResult
from mcp_proxy_adapter.core.errors import (
    ValidationError, CommandError, NotFoundError, MethodNotFoundError,
    InvalidRequestError, ParseError, InternalError
)


@pytest.fixture
def success_result():
    """Fixture for test success result."""
    result = SuccessResult(data={"key": "value"}, message="Success")
    return result


@pytest.fixture
def error_result():
    """Fixture for test error result."""
    result = ErrorResult(message="Error message", code=400)
    return result


class TestExecuteCommand:
    """Tests for execute_command function."""
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Test successful command execution."""
        # Mock successful result
        mock_result = EchoResult(params={"test_key": "test_value"})
        
        # Mock command class and registry
        with patch("mcp_proxy_adapter.commands.command_registry.registry.get_command") as mock_get_command:
            # Создаем асинхронную mock-функцию
            mock_run = AsyncMock(return_value=mock_result)
            mock_command_class = MagicMock()
            # Присваиваем асинхронную функцию методу run
            mock_command_class.run = mock_run
            mock_get_command.return_value = mock_command_class
            
            # Execute command
            result = await execute_command("test_command", {"param": "value"})
            
            # Assert command was called correctly
            mock_get_command.assert_called_once_with("test_command")
            mock_run.assert_called_once_with(param="value")
            
            # Assert result is as expected
            assert result == mock_result.to_dict()
    
    @pytest.mark.asyncio
    async def test_execute_command_not_found(self):
        """Test command not found error."""
        # Mock registry raising NotFoundError
        with patch("mcp_proxy_adapter.commands.command_registry.registry.get_command") as mock_get_command:
            mock_get_command.side_effect = NotFoundError("Command not found")
            
            # Execute command and expect MethodNotFoundError
            with pytest.raises(MethodNotFoundError) as exc_info:
                await execute_command("unknown_command", {})
            
            # Check error message
            assert "Method not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_command_internal_error(self):
        """Test internal error during command execution."""
        # Mock registry raising an unexpected error
        with patch("mcp_proxy_adapter.commands.command_registry.registry.get_command") as mock_get_command:
            mock_get_command.side_effect = Exception("Unexpected error")
            
            # Execute command and expect InternalError
            with pytest.raises(InternalError) as exc_info:
                await execute_command("test_command", {})
            
            # Check error details
            assert "Error executing command" in str(exc_info.value)
            assert "original_error" in exc_info.value.data


class TestHandleJsonRpc:
    """Tests for handle_json_rpc function."""
    
    @pytest.mark.asyncio
    async def test_handle_json_rpc_success(self):
        """Test successful JSON-RPC request handling."""
        # Mock execute_command
        with patch("mcp_proxy_adapter.api.handlers.execute_command") as mock_execute:
            # AsyncMock для асинхронной функции
            mock_execute.return_value = {"result": "success"}
            
            # Create request data
            request_data = {
                "jsonrpc": "2.0",
                "method": "test_command",
                "params": {"param": "value"},
                "id": 123
            }
            
            # Handle request
            response = await handle_json_rpc(request_data)
            
            # Assert command was executed
            mock_execute.assert_called_once_with("test_command", {"param": "value"}, None)
            
            # Assert response format
            assert response["jsonrpc"] == "2.0"
            assert response["result"] == {"result": "success"}
            assert response["id"] == 123
    
    @pytest.mark.asyncio
    async def test_handle_json_rpc_invalid_version(self):
        """Test invalid JSON-RPC version."""
        # Create request with invalid version
        request_data = {
            "jsonrpc": "1.0",
            "method": "test_command",
            "id": 123
        }
        
        # Handle request
        response = await handle_json_rpc(request_data)
        
        # Assert error response
        assert response["jsonrpc"] == "2.0"
        assert response["error"]["code"] == -32600
        assert "Invalid Request" in response["error"]["message"]
        assert response["id"] == 123
    
    @pytest.mark.asyncio
    async def test_handle_json_rpc_missing_method(self):
        """Test missing method in JSON-RPC request."""
        # Create request with missing method
        request_data = {
            "jsonrpc": "2.0",
            "params": {},
            "id": 123
        }
        
        # Handle request
        response = await handle_json_rpc(request_data)
        
        # Assert error response
        assert response["jsonrpc"] == "2.0"
        assert response["error"]["code"] == -32600
        assert "Method is required" in response["error"]["message"]
        assert response["id"] == 123
    
    @pytest.mark.asyncio
    async def test_handle_json_rpc_microservice_error(self):
        """Test microservice error during command execution."""
        # Mock execute_command raising MicroserviceError
        with patch("mcp_proxy_adapter.api.handlers.execute_command") as mock_execute:
            mock_execute.side_effect = CommandError("Command failed", data={"reason": "test"})
            
            # Create request data
            request_data = {
                "jsonrpc": "2.0",
                "method": "test_command",
                "params": {},
                "id": 123
            }
            
            # Handle request
            response = await handle_json_rpc(request_data)
            
            # Assert error response
            assert response["jsonrpc"] == "2.0"
            assert response["error"]["code"] == -32000
            assert "Command failed" in response["error"]["message"]
            assert response["error"]["data"]["reason"] == "test"
            assert response["id"] == 123
    
    @pytest.mark.asyncio
    async def test_handle_json_rpc_unhandled_error(self):
        """Test unhandled error during command execution."""
        # Mock execute_command raising unexpected error
        with patch("mcp_proxy_adapter.api.handlers.execute_command") as mock_execute:
            mock_execute.side_effect = Exception("Unexpected error")
            
            # Create request data
            request_data = {
                "jsonrpc": "2.0",
                "method": "test_command",
                "params": {},
                "id": 123
            }
            
            # Handle request
            response = await handle_json_rpc(request_data)
            
            # Assert error response
            assert response["jsonrpc"] == "2.0"
            assert response["error"]["code"] == -32603
            assert "Internal error" in response["error"]["message"]
            assert "Unexpected error" in response["error"]["data"]["error"]
            assert response["id"] == 123


class TestHandleBatchJsonRpc:
    """Tests for handle_batch_json_rpc function."""
    
    @pytest.mark.asyncio
    async def test_handle_batch_json_rpc(self):
        """Test batch JSON-RPC request handling."""
        # Mock handle_json_rpc
        with patch("mcp_proxy_adapter.api.handlers.handle_json_rpc") as mock_handle:
            # AsyncMock для асинхронных результатов
            mock_handle.side_effect = [
                {"jsonrpc": "2.0", "result": "result1", "id": 1},
                {"jsonrpc": "2.0", "result": "result2", "id": 2}
            ]
            
            # Create batch request
            batch_requests = [
                {"jsonrpc": "2.0", "method": "method1", "id": 1},
                {"jsonrpc": "2.0", "method": "method2", "id": 2}
            ]
            
            # Handle batch request
            responses = await handle_batch_json_rpc(batch_requests)
            
            # Assert responses
            assert len(responses) == 2
            assert responses[0]["result"] == "result1"
            assert responses[1]["result"] == "result2"


class TestGetServerHealth:
    """Tests for get_server_health function."""
    
    @pytest.mark.asyncio
    async def test_get_server_health(self):
        """Test getting server health information."""
        # Call server health function
        result = await get_server_health()
        
        # Check basic structure and keys
        assert "status" in result
        assert result["status"] == "ok"
        assert "version" in result
        assert "uptime" in result
        assert "components" in result
        assert "system" in result["components"]
        assert "process" in result["components"]
        assert "commands" in result["components"]


class TestGetCommandsList:
    """Tests for get_commands_list function."""
    
    @pytest.mark.asyncio
    async def test_get_commands_list(self):
        """Test getting commands list."""
        # Mock registry.get_all_commands
        with patch("mcp_proxy_adapter.commands.command_registry.registry.get_all_commands") as mock_get_all:
            # Create mock command class
            mock_command = MagicMock()
            mock_command.get_schema.return_value = {
                "type": "object",
                "description": "Test command description"
            }
            
            # Setup mock to return test commands
            mock_get_all.return_value = {
                "test_command": mock_command
            }
            
            # Call get_commands_list
            result = await get_commands_list()
            
            # Check result structure
            assert "test_command" in result
            assert result["test_command"]["name"] == "test_command"
            assert result["test_command"]["description"] == "Test command description"
            assert result["test_command"]["schema"]["type"] == "object" 