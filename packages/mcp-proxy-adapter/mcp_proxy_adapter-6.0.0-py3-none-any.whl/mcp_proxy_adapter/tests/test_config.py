"""
Test module for configuration class.
"""

import os
import json
import tempfile
from pathlib import Path

import pytest

from mcp_proxy_adapter.config import Config


def test_config_initialization(temp_config_file):
    """
    Test configuration initialization.
    """
    config = Config(temp_config_file)
    assert config.config_path == temp_config_file
    assert isinstance(config.config_data, dict)


def test_config_get_existing_values(test_config):
    """
    Test getting existing values from configuration.
    """
    # Test top-level key
    server_config = test_config.get("server")
    assert server_config.get("host") == "127.0.0.1"
    assert server_config.get("port") == 8888
    
    # Test nested key with dot notation
    assert test_config.get("server.host") == "127.0.0.1"
    assert test_config.get("server.port") == 8888
    
    # Test logging values
    assert test_config.get("logging.level") == "DEBUG"
    assert test_config.get("logging.file") is None


def test_config_get_default_values(test_config):
    """
    Test getting default values for non-existent keys.
    """
    # Non-existent key with default
    assert test_config.get("non_existent", "default") == "default"
    
    # Non-existent nested key with default
    assert test_config.get("server.non_existent", 42) == 42
    
    # Non-existent top level with nested key
    assert test_config.get("non_existent.key", False) is False


def test_config_set_values(test_config):
    """
    Test setting values in configuration.
    """
    # Set top-level value
    test_config.set("new_key", "value")
    assert test_config.get("new_key") == "value"
    
    # Set nested value for existing parent
    test_config.set("server.api_key", "secret")
    assert test_config.get("server.api_key") == "secret"
    
    # Set nested value with non-existent parent
    test_config.set("database.url", "postgres://localhost")
    assert test_config.get("database.url") == "postgres://localhost"
    
    # Overwrite existing value
    test_config.set("server.host", "0.0.0.0")
    assert test_config.get("server.host") == "0.0.0.0"


def test_config_save_load(temp_config_file):
    """
    Test saving and loading configuration.
    """
    # Create and modify config
    config = Config(temp_config_file)
    config.set("test_key", "test_value")
    config.set("nested.key", 123)
    
    # Save config
    config.save()
    
    # Create new config instance to load from the same file
    new_config = Config(temp_config_file)
    
    # Verify values were saved and loaded
    assert new_config.get("test_key") == "test_value"
    assert new_config.get("nested.key") == 123
    assert new_config.get("server.host") == "127.0.0.1"


def test_config_environment_variables():
    """
    Test environment variables override configuration values.
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as temp:
        temp_path = temp.name
        json.dump({"server": {"host": "localhost", "port": 8000}}, temp)
    
    try:
        # Set environment variables
        os.environ["SERVICE_SERVER_HOST"] = "192.168.1.1"
        os.environ["SERVICE_SERVER_PORT"] = "9000"
        os.environ["SERVICE_LOGGING_LEVEL"] = "INFO"
        
        # Create config that should load from env vars
        config = Config(temp_path)
        
        # Check values are overridden by environment
        assert config.get("server.host") == "192.168.1.1"
        assert config.get("server.port") == 9000
        assert config.get("logging.level") == "INFO"
    finally:
        # Clean up
        os.unlink(temp_path)
        if "SERVICE_SERVER_HOST" in os.environ:
            del os.environ["SERVICE_SERVER_HOST"]
        if "SERVICE_SERVER_PORT" in os.environ:
            del os.environ["SERVICE_SERVER_PORT"]
        if "SERVICE_LOGGING_LEVEL" in os.environ:
            del os.environ["SERVICE_LOGGING_LEVEL"]
