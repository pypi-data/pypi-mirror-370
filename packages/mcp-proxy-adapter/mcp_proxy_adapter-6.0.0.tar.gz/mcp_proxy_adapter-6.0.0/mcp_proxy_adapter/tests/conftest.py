"""
Module with fixtures and configuration for tests.
"""

import json
import os
import tempfile
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.config import Config


@pytest.fixture
def temp_config_file() -> Generator[str, None, None]:
    """
    Creates temporary configuration file for tests.

    Returns:
        Path to temporary configuration file.
    """
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=".json")
    
    # Write test configuration
    test_config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8888
        },
        "logging": {
            "level": "DEBUG",
            "file": None
        },
        # Отключаем аутентификацию и ограничение скорости для тестов
        "auth_enabled": False,
        "rate_limit_enabled": False
    }
    
    with os.fdopen(fd, "w") as f:
        json.dump(test_config, f)
    
    yield path
    
    # Remove temporary file after tests
    os.unlink(path)


@pytest.fixture
def test_config(temp_config_file: str) -> Config:
    """
    Creates test configuration instance.

    Args:
        temp_config_file: Path to temporary configuration file.

    Returns:
        Test configuration instance.
    """
    return Config(temp_config_file)


@pytest.fixture
def test_client() -> TestClient:
    """
    Creates test client for FastAPI application.

    Returns:
        FastAPI test client.
    """
    app = create_app()
    return TestClient(app)


@pytest.fixture
def clean_registry() -> Generator[None, None, None]:
    """
    Cleans command registry before test and restores it after.

    Yields:
        None
    """
    # Save current commands
    original_commands = dict(registry._commands)
    
    # Clear registry
    registry.clear()
    
    yield
    
    # Restore registry
    registry.clear()
    for name, command in original_commands.items():
        registry._commands[name] = command


@pytest.fixture
def json_rpc_request() -> Dict[str, Any]:
    """
    Creates base JSON-RPC request.

    Returns:
        Dictionary with JSON-RPC request data.
    """
    return {
        "jsonrpc": "2.0",
        "method": "test_command",
        "params": {},
        "id": "test-id"
    }


@pytest.fixture(autouse=True)
def register_test_commands():
    """
    Регистрирует тестовые команды в registry для всех тестов.
    """
    from mcp_proxy_adapter.tests.stubs.echo_command import EchoCommand
    from mcp_proxy_adapter.commands.command_registry import registry
    
    # Регистрируем команды для тестирования
    registry.register(EchoCommand)
    
    yield
    
    # Очищаем registry после тестов
    registry.clear()
