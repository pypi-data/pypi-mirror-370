# Custom Project Example with Commands

This example shows how to create your own project with commands and configure `discovery_path` for their automatic discovery.

## Project Structure

```
myproject/
├── config.json
├── main.py
├── myproject/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── echo_command.py
│       └── info_command.py
└── README.md
```

## Configuration

In the `config.json` file, specify the path to our commands:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8001,
    "debug": true,
    "log_level": "DEBUG"
  },
  "logging": {
    "level": "DEBUG",
    "log_dir": "./logs",
    "log_file": "myproject.log"
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "myproject.commands"
  }
}
```

## Commands

### echo_command.py

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult

class EchoCommand(Command):
    """Echo command that returns the input text."""
    
    name = "echo"
    
    def execute(self, text: str) -> CommandResult:
        return CommandResult(success=True, data={"echo": text})
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {
            "text": {
                "type": "string",
                "description": "Text to echo",
                "required": True
            }
        }
```

### info_command.py

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult

class InfoCommand(Command):
    """Info command that returns project information."""
    
    name = "info"
    
    def execute(self) -> CommandResult:
        return CommandResult(
            success=True, 
            data={
                "project": "myproject",
                "version": "1.0.0",
                "description": "Example project with custom commands"
            }
        )
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {}
```

## Running

```bash
python main.py
```

When starting, the service will automatically discover commands from the `myproject.commands` package thanks to the `discovery_path` configuration setting. 