"""
Integration tests for the mcp_microservice package.
"""

import pytest
import json
from typing import Dict, Any

from fastapi.testclient import TestClient

from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.tests.stubs.echo_command import EchoCommand
from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.config import Config


@pytest.fixture
def integration_config():
    """
    Fixture for integration test configuration.
    
    Returns:
        Config instance for integration tests.
    """
    config = Config()
    # Загружаем тестовую конфигурацию
    config._config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8889
        },
        "logging": {
            "level": "DEBUG",
            "file": None
        },
        "auth_enabled": False,
        "rate_limit_enabled": False
    }
    return config


@pytest.fixture
def integration_app(integration_config):
    """
    Fixture for integration test application.
    
    Args:
        integration_config: Configuration for integration tests.
        
    Returns:
        FastAPI application instance.
    """
    return create_app()


@pytest.fixture
def integration_client(integration_app):
    """
    Fixture for integration test client.
    
    Args:
        integration_app: FastAPI application for integration tests.
        
    Returns:
        FastAPI test client.
    """
    return TestClient(integration_app)


@pytest.mark.integration
def test_command_registry_with_api(integration_client, clean_registry):
    """
    Test integration between command registry and API.
    
    Args:
        integration_client: FastAPI test client.
        clean_registry: Fixture to clean registry before and after test.
    """
    # Register command
    registry.register(EchoCommand)
    
    # Create JSON-RPC request
    request_data = {
        "jsonrpc": "2.0",
        "method": "echo",
        "params": {"test_key": "test_value"},
        "id": "test-id"
    }
    
    # Send request
    response = integration_client.post("/api/jsonrpc", json=request_data)
    
    # Check response
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "jsonrpc" in data and data["jsonrpc"] == "2.0"
    assert "result" in data
    assert "id" in data and data["id"] == request_data["id"]
    
    # Check result content
    assert "params" in data["result"]
    assert data["result"]["params"] == {"test_key": "test_value"}
    
    # Clean up
    registry.clear()


@pytest.mark.integration
def test_command_execution_through_api(integration_client, clean_registry):
    """
    Test command execution through API with complex parameters.
    
    Args:
        integration_client: FastAPI test client.
        clean_registry: Fixture to clean registry before and after test.
    """
    # Register command
    registry.register(EchoCommand)
    
    # Create JSON-RPC request with parameters
    request_data = {
        "jsonrpc": "2.0",
        "method": "echo",
        "params": {"complex_param": {"nested": "value", "array": [1, 2, 3]}},
        "id": "test-id"
    }
    
    # Send request
    response = integration_client.post("/api/jsonrpc", json=request_data)
    
    # Check response
    assert response.status_code == 200
    
    # Check response content
    data = response.json()
    assert "params" in data["result"]
    assert data["result"]["params"]["complex_param"]["nested"] == "value"
    assert data["result"]["params"]["complex_param"]["array"] == [1, 2, 3]
    
    # Clean up
    registry.clear()


@pytest.mark.integration
def test_api_error_handling_with_command(integration_client, clean_registry):
    """
    Test API error handling with command errors.
    
    Args:
        integration_client: FastAPI test client.
        clean_registry: Fixture to clean registry before and after test.
    """
    # Register command
    registry.register(EchoCommand)
    
    # Create JSON-RPC request with parameters
    request_data = {
        "jsonrpc": "2.0",
        "method": "echo",
        "params": {"test": "value"},
        "id": "test-id"
    }
    
    # Send request
    response = integration_client.post("/api/jsonrpc", json=request_data)
    
    # Check response
    assert response.status_code == 200
    
    # Clean up
    registry.clear()


@pytest.mark.integration
def test_api_commands_endpoint_with_registry(integration_client, clean_registry):
    """
    Test API commands endpoint with loaded registry.
    
    Args:
        integration_client: FastAPI test client.
        clean_registry: Fixture to clean registry before and after test.
    """
    # Register command
    registry.register(EchoCommand)
    
    # Get commands list
    response = integration_client.get("/api/commands")
    
    # Check response
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "commands" in data
    assert isinstance(data["commands"], dict)
    
    # Check that echo command is in the list
    assert "echo" in data["commands"]
    assert "description" in data["commands"]["echo"]
    
    # Clean up
    registry.clear()


@pytest.mark.integration
def test_batch_requests_integration(integration_client, clean_registry):
    """
    Test batch requests processing.
    
    Args:
        integration_client: FastAPI test client.
        clean_registry: Fixture to clean registry before and after test.
    """
    # Register command
    registry.register(EchoCommand)
    
    # Create batch request
    batch_request = [
        {
            "jsonrpc": "2.0",
            "method": "echo",
            "params": {"request_id": "1"},
            "id": "1"
        },
        {
            "jsonrpc": "2.0",
            "method": "echo",
            "params": {"request_id": "2"},
            "id": "2"
        }
    ]
    
    # Send request
    response = integration_client.post("/api/jsonrpc", json=batch_request)
    
    # Check response
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Check individual responses
    for i, resp in enumerate(data):
        assert "jsonrpc" in resp and resp["jsonrpc"] == "2.0"
        assert "result" in resp
        assert "params" in resp["result"]
        assert resp["result"]["params"]["request_id"] == str(i + 1)
        assert resp["id"] == str(i + 1)
    
    # Clean up
    registry.clear() 