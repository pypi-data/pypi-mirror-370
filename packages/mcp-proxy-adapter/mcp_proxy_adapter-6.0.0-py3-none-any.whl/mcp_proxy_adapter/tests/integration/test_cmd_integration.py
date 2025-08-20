"""
Integration tests for /cmd endpoint and help command.
"""

import pytest
from fastapi.testclient import TestClient

from mcp_proxy_adapter.api.app import app
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.help_command import HelpCommand


@pytest.fixture(autouse=True)
def setup_registry():
    """Setup command registry for tests."""
    # Store original commands
    original_commands = dict(registry._commands)
    
    # Clear registry
    registry._commands.clear()
    
    # Register help command
    registry.register(HelpCommand)
    
    yield
    
    # Restore original commands
    registry._commands.clear()
    for name, command in original_commands.items():
        registry._commands[name] = command


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


def test_cmd_help_without_params(client):
    """Test /cmd endpoint with help command without parameters."""
    response = client.post(
        "/cmd",
        json={"command": "help"}
    )
    
    assert response.status_code == 200
    assert "result" in response.json()
    result = response.json()["result"]
    
    assert "commands" in result
    assert "help" in result["commands"]
    assert "summary" in result["commands"]["help"]


def test_cmd_help_with_cmdname(client):
    """Test /cmd endpoint with help command with cmdname parameter."""
    response = client.post(
        "/cmd",
        json={
            "command": "help",
            "params": {
                "cmdname": "help"
            }
        }
    )
    
    assert response.status_code == 200
    assert "result" in response.json()
    result = response.json()["result"]
    
    assert "cmdname" in result
    assert result["cmdname"] == "help"
    assert "info" in result
    assert "description" in result["info"]
    assert "params" in result["info"]
    assert "cmdname" in result["info"]["params"]


def test_cmd_help_unknown_command(client):
    """Test /cmd endpoint with help command for unknown command."""
    response = client.post(
        "/cmd",
        json={
            "command": "help",
            "params": {
                "cmdname": "unknown_command"
            }
        }
    )
    
    assert response.status_code == 200
    assert "result" in response.json()
    result = response.json()["result"]
    
    assert "error" in result
    assert "example" in result
    assert "note" in result
    assert result["error"].startswith("Command")
    assert result["example"]["command"] == "help"


def test_cmd_unknown_command(client):
    """Test /cmd endpoint with unknown command."""
    response = client.post(
        "/cmd",
        json={"command": "unknown_command"}
    )
    
    assert response.status_code == 200
    assert "error" in response.json()
    error = response.json()["error"]
    
    assert error["code"] == -32601
    assert "не найдена" in error["message"]


def test_cmd_invalid_request(client):
    """Test /cmd endpoint with invalid request format."""
    response = client.post(
        "/cmd",
        json={"invalid": "request"}
    )
    
    assert response.status_code == 200
    assert "error" in response.json()
    error = response.json()["error"]
    
    assert error["code"] == -32600
    assert "Отсутствует обязательное поле 'command'" in error["message"] 