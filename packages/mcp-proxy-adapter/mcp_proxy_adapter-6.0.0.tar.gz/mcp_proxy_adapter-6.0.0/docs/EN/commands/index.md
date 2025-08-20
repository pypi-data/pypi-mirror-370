# Command Reference

This document provides an overview of all available commands in the MCP Proxy service.

## Available Commands

| Command | Description | Parameters | Result |
|---------|-------------|------------|--------|
| [get_date](./get_date_command.md) | Returns the current date and time in ISO 8601 format | none | date |
| [new_uuid4](./new_uuid4_command.md) | Generates a new UUID version 4 (random) | none | uuid |

## Command Structure

Each command in the MCP Proxy service follows a consistent structure:

1. **Command Class**: Implements the command logic
2. **Result Class**: Defines the result structure
3. **Parameter Validation**: Validates input parameters
4. **Error Handling**: Handles errors and exceptions

## Making Command Requests

Commands can be executed through the JSON-RPC interface:

```json
{
  "jsonrpc": "2.0",
  "method": "command_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "id": 1
}
```

## Command Response

A successful command execution returns a response with this structure:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "field1": "value1",
    "field2": "value2"
  },
  "id": 1
}
```

## Adding New Commands

To add a new command, see the [Project Extension Guide](../PROJECT_EXTENSION_GUIDE.md). 