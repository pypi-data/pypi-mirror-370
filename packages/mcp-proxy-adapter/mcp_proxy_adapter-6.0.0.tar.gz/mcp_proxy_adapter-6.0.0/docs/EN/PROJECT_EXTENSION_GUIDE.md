# Project Extension Guide

## Overview

This guide provides step-by-step instructions for extending the MCP Proxy Adapter project for real-world tasks. It covers the process from initial setup to adding a custom command and deploying the application.

## Extension Process

### 1. Project Setup

```
# Clone the base repository
git clone https://github.com/maverikod/vvz-mcp-proxy-adapter.git my_project
cd my_project

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 2. Configure the Project

Create or modify the configuration file to match your requirements:

```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 8000
    },
    "logging": {
        "level": "INFO",
        "file": "application.log",
        "rotation": {
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "stderr_file": "error.log"
    },
    "commands": {
        "enabled": ["echo", "get_date", "new_uuid4"]
    }
}
```

### 3. Create a New Command

For this example, we'll create an `echo` command that returns the input message.

#### 3.1. Define the Command Result Class

Create a file `mcp_microservice/commands/echo_command.py`:

```python
"""
Echo Command Module.

This module implements a simple echo command that returns the input message.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass

from mcp_proxy_adapter.interfaces.command_result import CommandResult
from mcp_proxy_adapter.interfaces.command import Command


@dataclass
class EchoResult(CommandResult):
    """
    Result of the echo command.
    
    Attributes:
        message: The echoed message
    """
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the result to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the result
        """
        return {
            "message": self.message
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get the JSON schema for this result.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The echoed message"
                }
            },
            "required": ["message"]
        }


class EchoCommand(Command):
    """
    Command that echoes back the given message.
    
    This is a simple demonstration command that returns the input message.
    """
    
    async def execute(self, message: str, prefix: Optional[str] = None) -> EchoResult:
        """
        Execute the echo command.
        
        Args:
            message: The message to echo
            prefix: Optional prefix to add to the message
            
        Returns:
            EchoResult: The result containing the echoed message
        """
        if prefix:
            final_message = f"{prefix}: {message}"
        else:
            final_message = message
            
        self.logger.debug(f"Echoing message: {final_message}")
        return EchoResult(message=final_message)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get the JSON schema for this command.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to echo"
                },
                "prefix": {
                    "type": "string",
                    "description": "Optional prefix to add to the message"
                }
            },
            "required": ["message"]
        }
```

#### 3.2. Register the Command

Create or modify `mcp_microservice/commands/__init__.py` to register your command:

```python
from mcp_proxy_adapter.commands.echo_command import EchoCommand
from mcp_proxy_adapter.commands.get_date_command import GetDateCommand
from mcp_proxy_adapter.commands.new_uuid4_command import NewUUID4Command

# Command registry
COMMANDS = {
    "echo": EchoCommand,
    "get_date": GetDateCommand,
    "new_uuid4": NewUUID4Command
}
```

### 4. Write Tests for the Command

Create a test file `tests/unit/commands/test_echo_command.py`:

```python
import pytest
from mcp_proxy_adapter.commands.echo_command import EchoCommand, EchoResult


class TestEchoCommand:
    """Tests for the Echo command."""
    
    @pytest.fixture
    def command(self):
        """Create an instance of the command for testing."""
        return EchoCommand()
    
    @pytest.mark.asyncio
    async def test_echo_basic(self, command):
        """Test basic echo functionality."""
        result = await command.execute(message="Hello, World!")
        assert isinstance(result, EchoResult)
        assert result.message == "Hello, World!"
        
    @pytest.mark.asyncio
    async def test_echo_with_prefix(self, command):
        """Test echo with prefix."""
        result = await command.execute(message="Hello, World!", prefix="PREFIX")
        assert result.message == "PREFIX: Hello, World!"
    
    def test_result_to_dict(self):
        """Test result serialization."""
        result = EchoResult(message="Test message")
        data = result.to_dict()
        assert data == {"message": "Test message"}
    
    def test_schema(self, command):
        """Test schema generation."""
        schema = command.get_schema()
        assert schema["type"] == "object"
        assert "message" in schema["properties"]
        assert "prefix" in schema["properties"]
        assert "message" in schema["required"]
```

### 5. Create Documentation for the Command

Create documentation files for both languages:

For English: `docs/EN/commands/echo_command.md`:

```markdown
# Echo Command

## Description

The echo command returns the input message, optionally with a prefix.

## Result

```python
@dataclass
class EchoResult(CommandResult):
    message: str
```

## Command

```python
class EchoCommand(Command):
    async def execute(self, message: str, prefix: Optional[str] = None) -> EchoResult:
        # Implementation details...
```

## Parameters

| Parameter | Type   | Required | Description                        |
|-----------|--------|----------|------------------------------------|
| message   | string | Yes      | The message to echo                |
| prefix    | string | No       | Optional prefix to add to the message |

## Examples

### Python

```python
from mcp_proxy_adapter.client import Client

client = Client("http://localhost:8000")
result = await client.execute("echo", {"message": "Hello, World!"})
print(result.message)  # Output: Hello, World!

# With prefix
result = await client.execute("echo", {"message": "Hello, World!", "prefix": "ECHO"})
print(result.message)  # Output: ECHO: Hello, World!
```

### HTTP REST

Request:

```
POST /api/commands/echo
Content-Type: application/json

{
    "message": "Hello, World!",
    "prefix": "ECHO"
}
```

Response:

```
200 OK
Content-Type: application/json

{
    "message": "ECHO: Hello, World!"
}
```

### JSON-RPC

Request:

```json
{
    "jsonrpc": "2.0",
    "method": "echo",
    "params": {
        "message": "Hello, World!",
        "prefix": "ECHO"
    },
    "id": 1
}
```

Response:

```json
{
    "jsonrpc": "2.0",
    "result": {
        "message": "ECHO: Hello, World!"
    },
    "id": 1
}
```

## Error Handling

| Error Code | Description                   | Cause                          |
|------------|-------------------------------|--------------------------------|
| 400        | Bad Request                   | Missing required parameter     |
| 500        | Internal Server Error         | Unexpected server-side error   |
```

Create the Russian version in `docs/RU/commands/echo_command.md`.

### 6. Configure Extended Settings (Optional)

If you need custom configuration behavior, create a custom settings class:

```python
# mcp_microservice/config.py
from mcp_proxy_adapter.config import Settings

class ExtendedSettings(Settings):
    def _read_config_file(self, config_path):
        """Support for YAML configuration files."""
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return self._read_yaml_config(config_path)
        return super()._read_config_file(config_path)
    
    def _read_yaml_config(self, config_path):
        """Read YAML configuration file."""
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_configuration(self):
        """Add custom validation."""
        super().validate_configuration()
        
        # Validate custom configuration items
        if 'commands' not in self.config:
            raise ValueError("Missing 'commands' section in configuration")
        
        if 'enabled' not in self.config['commands']:
            raise ValueError("Missing 'enabled' list in commands configuration")
```

### 7. Run Tests

```
# Run all tests
pytest

# Run specific tests
pytest tests/unit/commands/test_echo_command.py
```

### 8. Start the Service

```
# Development mode
python -m mcp_microservice.server --config-path /path/to/config.json

# Production mode 
gunicorn -k uvicorn.workers.UvicornWorker mcp_microservice.server:app
```

### 9. Try Your Command

Using curl:

```
curl -X POST http://localhost:8000/api/commands/echo \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, MCP!", "prefix": "TEST"}'
```

Response:

```json
{
    "message": "TEST: Hello, MCP!"
}
```

### 10. Create System Service Integration

Create a systemd service file `/etc/systemd/system/mcp-service.service`:

```ini
[Unit]
Description=MCP Proxy Adapter
After=network.target

[Service]
User=mcp
Group=mcp
WorkingDirectory=/opt/mcp_microservice
ExecStart=/opt/mcp_microservice/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker mcp_microservice.server:app
Restart=on-failure
Environment=MCP_CONFIG_PATH=/etc/mcp_microservice/config.json

[Install]
WantedBy=multi-user.target
```

Create a SystemV init script `/etc/init.d/mcp-service`:

```bash
#!/bin/bash
### BEGIN INIT INFO
# Provides:          mcp-service
# Required-Start:    $network $local_fs $remote_fs
# Required-Stop:     $network $local_fs $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: MCP Proxy Adapter
# Description:       MCP Proxy Adapter
### END INIT INFO

NAME="mcp-service"
DAEMON="/opt/mcp_microservice/venv/bin/gunicorn"
DAEMON_OPTS="-k uvicorn.workers.UvicornWorker mcp_microservice.server:app"
DAEMON_USER="mcp"
PIDFILE="/var/run/$NAME.pid"
LOGFILE="/var/log/$NAME.log"

# Load init functions
. /lib/lsb/init-functions

# Export environment variables
export MCP_CONFIG_PATH="/etc/mcp_microservice/config.json"

do_start() {
    log_daemon_msg "Starting $NAME"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile \
        --chuid $DAEMON_USER --chdir /opt/mcp_microservice \
        --exec $DAEMON -- $DAEMON_OPTS >> $LOGFILE 2>&1
    log_end_msg $?
}

do_stop() {
    log_daemon_msg "Stopping $NAME"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}

do_reload() {
    log_daemon_msg "Reloading $NAME"
    start-stop-daemon --stop --signal HUP --pidfile $PIDFILE
    log_end_msg $?
}

case "$1" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    restart)
        do_stop
        do_start
        ;;
    reload)
        do_reload
        ;;
    status)
        status_of_proc -p $PIDFILE "$DAEMON" "$NAME"
        ;;
    *)
        echo "Usage: $NAME {start|stop|restart|reload|status}"
        exit 1
        ;;
esac

exit 0
```

Make the script executable:

```bash
chmod +x /etc/init.d/mcp-service
```

### 11. Package for PyPI Distribution

To prepare your project for PyPI distribution, you need to set up the package structure correctly:

#### 11.1. Update setup.py

```python
from setuptools import setup, find_packages

setup(
    name="mcp-proxy-adapter",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.2",
        "gunicorn>=20.1.0",
    ],
    python_requires=">=3.8",
    description="MCP Proxy Adapter with custom commands",
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
```

#### 11.2. Create MANIFEST.in

```
include README.md
include LICENSE
include requirements.txt
recursive-include mcp_microservice *.py
recursive-include docs *.md
```

#### 11.3. Build the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*
```

#### 11.4. Upload to PyPI

```bash
# Upload to Test PyPI first
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# If everything looks good, upload to PyPI
twine upload dist/*
```

### 12. Deploy from PyPI

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install from PyPI
pip install mcp_microservice

# Create configuration directory
mkdir -p /etc/mcp_microservice
# Create your config.json

# Set up the service
systemctl daemon-reload
systemctl enable mcp-service
systemctl start mcp-service

# Or for SystemV
update-rc.d mcp-service defaults
service mcp-service start
```

## Complete File Structure

The complete file structure of the project should look like this:

```
mcp_microservice/
├── config.json                        # Main configuration file
├── pyproject.toml                     # Python project settings and build configurations
├── setup.py                           # Package setup script for PyPI
├── setup.cfg                          # Package configuration
├── MANIFEST.in                        # Package manifest
├── LICENSE                            # License file
├── README.md                          # Project description and documentation
├── requirements.txt                   # Main dependencies
├── requirements-dev.txt               # Development dependencies
├── mcp_microservice/                  # Main package directory
│   ├── __init__.py                    # Package initialization
│   ├── server.py                      # Server entry point
│   ├── config.py                      # Configuration handling
│   ├── adapter.py                     # Adapter module
│   ├── commands/                      # Command implementations
│   │   ├── __init__.py                # Command registry
│   │   ├── echo_command.py            # Echo command
│   │   ├── get_date_command.py        # Get Date command
│   │   └── new_uuid4_command.py       # New UUID4 command
│   ├── core/                          # Core functionality
│   │   ├── __init__.py                # Core package initialization
│   │   ├── command_registry.py        # Command registry implementation
│   │   └── exceptions.py              # Custom exceptions
│   ├── interfaces/                    # Abstract interfaces
│   │   ├── __init__.py                # Interfaces package initialization
│   │   ├── command.py                 # Command interface
│   │   └── command_result.py          # Command result interface
│   └── utils/                         # Utility functions
│       ├── __init__.py                # Utils package initialization
│       ├── validation.py              # Validation utilities
│       └── logging.py                 # Logging utilities
├── docs/                              # Documentation
│   ├── EN/                            # English documentation
│   │   ├── commands/                  # Command documentation
│   │   │   ├── echo_command.md        # Echo command documentation
│   │   │   ├── get_date_command.md    # Get Date command documentation
│   │   │   └── new_uuid4_command.md   # New UUID4 command documentation
│   │   ├── CONFIGURATION_PRINCIPLES.md# Configuration principles
│   │   ├── PROJECT_EXTENSION_GUIDE.md # Project extension guide
│   │   ├── PROJECT_STRUCTURE.md       # Project structure
│   │   ├── DOCUMENTATION_MAP.md       # Documentation map
│   │   └── ...                        # Other documentation files
│   └── RU/                            # Russian documentation
│       ├── commands/                  # Command documentation
│       │   ├── echo_command.md        # Echo command documentation
│       │   ├── get_date_command.md    # Get Date command documentation
│       │   └── new_uuid4_command.md   # New UUID4 command documentation
│       ├── CONFIGURATION_PRINCIPLES.md# Configuration principles
│       ├── PROJECT_EXTENSION_GUIDE.md # Project extension guide
│       ├── PROJECT_STRUCTURE.md       # Project structure
│       ├── DOCUMENTATION_MAP.md       # Documentation map
│       └── ...                        # Other documentation files
├── tests/                             # Test suite
│   ├── conftest.py                    # PyTest fixtures
│   ├── unit/                          # Unit tests
│   │   ├── commands/                  # Command tests
│   │   │   ├── test_echo_command.py   # Echo command test
│   │   │   ├── test_get_date_command.py # Get Date command test
│   │   │   └── test_new_uuid4_command.py # New UUID4 command test
│   │   ├── test_config.py             # Configuration tests
│   │   └── test_server.py             # Server tests
│   └── integration/                   # Integration tests
│       ├── test_api.py                # API tests
│       └── test_commands.py           # End-to-end command tests
└── scripts/                           # Utility scripts
    ├── deploy.sh                      # Deployment script
    ├── build_docs.py                  # Documentation builder
    └── release.py                     # Release script
```

## Best Practices

1. **Follow the Single Responsibility Principle**: Each command should do one thing well.
2. **Ensure Proper Documentation**: Document your code and create command documentation in both languages.
3. **Write Comprehensive Tests**: Aim for high test coverage with unit and integration tests.
4. **Validate Input Parameters**: Always validate command inputs for security and reliability.
5. **Follow Existing Patterns**: Use the established project structure and coding conventions.
6. **Use Type Hints**: Make your code more maintainable with proper typing.
7. **Keep Backward Compatibility**: Ensure changes don't break existing clients.
8. **Log Appropriately**: Use the unified logger with appropriate log levels.
9. **Consider Security**: Protect sensitive data and validate inputs.
10. **Check Performance**: Ensure your commands are efficient and avoid blocking operations.
11. **Package Properly for PyPI**: Follow Python packaging best practices for easy distribution.
12. **Version Your API**: Use semantic versioning to communicate changes to users.

By following this guide, you can successfully extend the MCP Proxy Adapter project with custom commands for your specific needs and publish it to PyPI for wider distribution. 