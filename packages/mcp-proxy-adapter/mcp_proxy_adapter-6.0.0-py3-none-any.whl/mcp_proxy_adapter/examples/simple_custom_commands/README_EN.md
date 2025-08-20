# Simple Custom Commands Example

This example shows how to configure `discovery_path` in the configuration for automatic discovery of commands from your project.

## Project Structure

```
simple_custom_commands/
├── config.json          # Configuration with discovery_path
├── main.py              # Entry point
├── my_commands/         # Package with commands
│   ├── __init__.py
│   ├── hello_command.py
│   └── calc_command.py
└── README.md
```

## Configuration (config.json)

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
    "log_file": "simple_commands.log"
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "my_commands"
  }
}
```

**Key point**: In `discovery_path` we specify `"my_commands"` - this is the package where commands are located.

## Commands

### hello_command.py

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult

class HelloCommand(Command):
    """Simple greeting command."""
    
    name = "hello"
    
    def execute(self, name: str = "World") -> CommandResult:
        return CommandResult(
            success=True, 
            data={"message": f"Hello, {name}!"}
        )
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {
            "name": {
                "type": "string",
                "description": "Name for greeting",
                "required": False,
                "default": "World"
            }
        }
```

### calc_command.py

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult

class CalcCommand(Command):
    """Simple calculator command."""
    
    name = "calc"
    
    def execute(self, a: float, b: float, operation: str = "add") -> CommandResult:
        if operation == "add":
            result = a + b
        elif operation == "sub":
            result = a - b
        elif operation == "mul":
            result = a * b
        elif operation == "div":
            if b == 0:
                return CommandResult(success=False, error="Division by zero")
            result = a / b
        else:
            return CommandResult(success=False, error=f"Unknown operation: {operation}")
        
        return CommandResult(
            success=True, 
            data={"result": result, "operation": operation}
        )
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {
            "a": {
                "type": "number",
                "description": "First number",
                "required": True
            },
            "b": {
                "type": "number", 
                "description": "Second number",
                "required": True
            },
            "operation": {
                "type": "string",
                "description": "Operation (add, sub, mul, div)",
                "required": False,
                "default": "add"
            }
        }
```

## Running

```bash
python main.py
```

When starting, the service will automatically discover commands from the `my_commands` package thanks to the `discovery_path` configuration setting.

## Testing

```bash
# Greeting
curl -X POST http://127.0.0.1:8001/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "hello", "params": {"name": "Alice"}}'

# Calculator
curl -X POST http://127.0.0.1:8001/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "calc", "params": {"a": 10, "b": 5, "operation": "add"}}'
```

## Result

The service will automatically discover and register the `hello` and `calc` commands from the `my_commands` package specified in `discovery_path`. 