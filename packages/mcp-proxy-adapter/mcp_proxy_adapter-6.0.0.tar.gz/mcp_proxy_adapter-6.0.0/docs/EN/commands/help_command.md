# Help Command

## Description

The `help` command is designed to provide reference information about available commands in the system. It can be used in two modes:
1. **Without parameters**: returns a list of all available commands with a brief description
2. **With parameter `cmdname`**: returns detailed information about a specific command

## Result

The result of the command execution is represented by the `HelpResult` class and has the following structure:

```python
class HelpResult(CommandResult):
    """
    Result of the help command execution.
    """
    
    def __init__(self, commands_info: Optional[Dict[str, Any]] = None, command_info: Optional[Dict[str, Any]] = None):
        """
        Initialize help command result.
        
        Args:
            commands_info: Information about all commands (for request without parameters)
            command_info: Information about a specific command (for request with cmdname parameter)
        """
        self.commands_info = commands_info
        self.command_info = command_info
```

## Command

The `help` command is implemented in the `HelpCommand` class:

```python
class HelpCommand(Command):
    """
    Command for getting help information about available commands.
    """
    
    name = "help"
    result_class = HelpResult
    
    async def execute(self, cmdname: Optional[str] = None) -> HelpResult:
        """
        Execute help command.
        
        Args:
            cmdname: Name of the command to get information about (optional)
            
        Returns:
            HelpResult: Help command result
            
        Raises:
            NotFoundError: If specified command not found
        """
        # Command implementation code
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cmdname` | `string` | No | Name of the command to get detailed information about |

## Implementation Details

The `help` command interacts with the command registry (`CommandRegistry`) to get information about registered commands. When requested without parameters, the command returns a list of all commands with their brief descriptions. When requested with the `cmdname` parameter, the command returns detailed information about a specific command, including:
- Command name
- Full description
- Information about parameters
- Result schema

The `help` command is a system command and is registered in the command registry when the application is initialized.

## Usage Examples

### Python

```python
from mcp_proxy_adapter.commands.help_command import HelpCommand

# Get list of all commands
help_cmd = HelpCommand()
result = await help_cmd.execute()
commands = result.to_dict()

# Get information about a specific command
result = await help_cmd.execute(cmdname="health")
command_info = result.to_dict()
```

### HTTP REST (/cmd endpoint)

**Request to get list of all commands:**
```http
POST /cmd HTTP/1.1
Content-Type: application/json

{
    "command": "help"
}
```

**Response:**
```json
{
    "result": {
        "commands": {
            "help": {
                "description": "Get help information about available commands"
            },
            "health": {
                "description": "Check server health"
            },
            "echo": {
                "description": "Return provided parameters"
            }
        }
    }
}
```

**Request to get information about a specific command:**
```http
POST /cmd HTTP/1.1
Content-Type: application/json

{
    "command": "help",
    "params": {
        "cmdname": "health"
    }
}
```

**Response:**
```json
{
    "result": {
        "command": {
            "name": "health",
            "description": "Check server health",
            "params": {
                "check_type": {
                    "type": "string",
                    "description": "Type of check (basic or detailed)",
                    "required": false,
                    "default": "basic"
                }
            },
            "schema": {
                "type": "object",
                "properties": {
                    "check_type": {
                        "type": "string",
                        "enum": ["basic", "detailed"]
                    }
                }
            },
            "result_schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string"
                    },
                    "uptime": {
                        "type": "number"
                    }
                }
            }
        }
    }
}
```

### JSON-RPC

**Request to get list of all commands:**
```json
{
    "jsonrpc": "2.0",
    "method": "help",
    "params": {},
    "id": 1
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "commands": {
            "help": {
                "description": "Get help information about available commands"
            },
            "health": {
                "description": "Check server health"
            }
        }
    },
    "id": 1
}
```

**Request to get information about a specific command:**
```json
{
    "jsonrpc": "2.0",
    "method": "help",
    "params": {
        "cmdname": "health"
    },
    "id": 2
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "command": {
            "name": "health",
            "description": "Check server health",
            "params": {
                "check_type": {
                    "type": "string",
                    "description": "Type of check (basic or detailed)",
                    "required": false,
                    "default": "basic"
                }
            }
        }
    },
    "id": 2
}
``` 