# {CommandName} Command

**Contents**: 1. Overview • 2. Parameters • 3. Result • 4. Implementation • 5. Examples • 6. Testing • 7. Implementation Details • 8. Error Handling

> **Naming convention note**: 
> - `{CommandName}` = PascalCase (e.g., GetFileInfo)
> - `{command_name}` = snake_case (e.g., get_file_info)

## 1. Overview

Brief description of what the command does and when it should be used.

## 2. Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| param1 | string | Yes | - | Description of parameter 1 |
| param2 | integer | No | 0 | Description of parameter 2 |

## 3. Result

The command returns a `{CommandName}Result` object with the following structure:

```python
@dataclass
class {CommandName}Result(CommandResult):
    field1: str
    field2: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field1": self.field1,
            "field2": self.field2
        }
        
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["field1"],
            "properties": {
                "field1": {
                    "type": "string",
                    "description": "Description of field1"
                },
                "field2": {
                    "type": "integer",
                    "description": "Description of field2"
                }
            }
        }
```

## 4. Implementation

Example of command implementation:

```python
# File: mcp_microservice/commands/{command_name}_command.py

from dataclasses import dataclass
from typing import Dict, Any, Optional

from mcp_proxy_adapter.common import CommandResult, Command
from mcp_proxy_adapter.validators import validate_string, validate_integer

@dataclass
class {CommandName}Result(CommandResult):
    field1: str
    field2: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field1": self.field1,
            "field2": self.field2
        }
        
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["field1"],
            "properties": {
                "field1": {
                    "type": "string",
                    "description": "Description of field1"
                },
                "field2": {
                    "type": "integer",
                    "description": "Description of field2"
                }
            }
        }


class {CommandName}Command(Command):
    """
    Implementation of the {CommandName} command.
    
    Brief description of the command's purpose and functionality.
    """
    
    async def execute(self, param1: str, param2: int = 0) -> {CommandName}Result:
        """
        Executes the {CommandName} command.
        
        Args:
            param1: Description of parameter 1
            param2: Description of parameter 2
            
        Returns:
            {CommandName}Result: Result of the command execution
            
        Raises:
            ValidationError: If parameters fail validation
            OperationError: If an error occurs during operation execution
        """
        # Parameter validation
        validate_string(param1, "param1", required=True)
        validate_integer(param2, "param2", required=False, default=0)
        
        # Command logic
        # ...
        
        # Return result
        return {CommandName}Result(
            field1="execution result",
            field2=param2
        )
```

## 5. Examples

### Python Example

```python
from mcp_proxy_adapter import execute_command

result = await execute_command("{command_name}", {
    "param1": "value1",
    "param2": 42
})

print(result.field1)  # Output: expected output
```

### JSON-RPC Example

Request:
```json
{
    "jsonrpc": "2.0",
    "method": "{command_name}",
    "params": {
        "param1": "value1",
        "param2": 42
    },
    "id": 1
}
```

Response:
```json
{
    "jsonrpc": "2.0",
    "result": {
        "field1": "expected output",
        "field2": 42
    },
    "id": 1
}
```

### HTTP REST Example

Request:
```
POST /api/v1/commands/{command_name}
Content-Type: application/json

{
    "param1": "value1",
    "param2": 42
}
```

Response:
```json
{
    "field1": "expected output",
    "field2": 42
}
```

## 6. Testing

Example of command testing:

```python
# File: tests/commands/test_{command_name}_command.py

import pytest
from mcp_proxy_adapter.commands.{command_name}_command import {CommandName}Command, {CommandName}Result

async def test_{command_name}_success():
    # Setup
    command = {CommandName}Command()
    
    # Execution
    result = await command.execute(param1="value1", param2=42)
    
    # Verification
    assert isinstance(result, {CommandName}Result)
    assert result.field1 == "execution result"
    assert result.field2 == 42
    
    # Serialization check
    result_dict = result.to_dict()
    assert result_dict["field1"] == "execution result"
    assert result_dict["field2"] == 42

async def test_{command_name}_validation_error():
    # Setup
    command = {CommandName}Command()
    
    # Execution and verification
    with pytest.raises(ValidationError, match="Parameter 'param1' is required"):
        await command.execute(param1=None, param2=42)

async def test_{command_name}_schema():
    # Schema verification
    schema = {CommandName}Result.get_schema()
    assert schema["type"] == "object"
    assert "field1" in schema["required"]
    assert schema["properties"]["field1"]["type"] == "string"
    assert schema["properties"]["field2"]["type"] == "integer"
```

## 7. Implementation Details

Additional notes about implementation details, specific behavior, or edge cases.

### Project Structure
The command should be placed in the project structure as follows:
```
mcp_microservice/
├── commands/
│   ├── __init__.py
│   └── {command_name}_command.py  # Command file
└── ...

tests/
└── commands/
    ├── __init__.py
    └── test_{command_name}_command.py  # Command tests
```

### Relationship with Other Components
- **Registry**: The command is automatically registered in the global command registry upon import
- **API**: Available through REST API and JSON-RPC interfaces
- **Asynchronous Nature**: All command methods are asynchronous to ensure high performance

See [CommandResult definition](../GLOSSARY.md#commandresult) for more details on the result format.

## 8. Error Handling

| Error Code | Condition | Message |
|------------|-----------|---------|
| 400        | Missing required parameter | "Parameter 'param1' is required" |
| 422        | Invalid parameter type | "Parameter 'param2' must be an integer" |
| 500        | Internal server error | "Failed to process request" |

Error Response Example:
```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": 400,
        "message": "Parameter 'param1' is required"
    },
    "id": 1
}
``` 