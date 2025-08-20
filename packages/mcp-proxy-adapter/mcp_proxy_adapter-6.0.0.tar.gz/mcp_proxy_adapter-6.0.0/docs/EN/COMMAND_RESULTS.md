# Command Results and Schema Generation

## Base Result Class

All commands return a result inherited from the base class `CommandResult`:

```python
from typing import Any, Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class CommandResult(ABC):
    """Base class for command results"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Converts the result to a dictionary for serialization"""
        pass
        
    @abstractmethod
    def to_jsonrpc(self, id: Optional[str] = None) -> Dict[str, Any]:
        """Converts the result to JSON-RPC format"""
        return {
            "jsonrpc": "2.0",
            "result": self.to_dict(),
            "id": id
        }

    @classmethod
    @abstractmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Returns the OpenAPI schema of the result"""
        pass
```

## Implementation Examples

### Simple Result

```python
@dataclass
class StatusResult(CommandResult):
    """Result of the status retrieval command"""
    status: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"status": self.status}
        if self.details:
            result["details"] = self.details
        return result

    def to_jsonrpc(self, id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "result": self.to_dict(),
            "id": id
        }

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Operation status"
                },
                "details": {
                    "type": "object",
                    "description": "Additional details",
                    "additionalProperties": True
                }
            }
        }
```

### Complex Result with Nested Objects

```python
@dataclass
class FileInfo:
    """File information"""
    name: str
    size: int
    modified: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "size": self.size,
            "modified": self.modified
        }

@dataclass
class FileListResult(CommandResult):
    """Result of the file list retrieval command"""
    files: List[FileInfo]
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "files": [f.to_dict() for f in self.files],
            "total_count": self.total_count
        }

    def to_jsonrpc(self, id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "result": self.to_dict(),
            "id": id
        }

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["files", "total_count"],
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "size", "modified"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "File name"
                            },
                            "size": {
                                "type": "integer",
                                "description": "File size in bytes"
                            },
                            "modified": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Modification date"
                            }
                        }
                    }
                },
                "total_count": {
                    "type": "integer",
                    "description": "Total number of files"
                }
            }
        }
```

## Integration with Commands

Commands use typed results:

```python
@registry.command
async def get_status() -> StatusResult:
    """
    Gets the system status
    Returns:
        StatusResult: Current system status
    """
    return StatusResult(
        status="ok",
        details={"version": "1.0.0"}
    )

@registry.command
async def list_files(path: str) -> FileListResult:
    """
    Gets a list of files in a directory
    Args:
        path: Directory path
    Returns:
        FileListResult: List of files and their metadata
    """
    files = []
    # ... logic for getting the file list
    return FileListResult(files=files, total_count=len(files))
```

## Schema Generation

The OpenAPI schema is dynamically generated based on:
1. Command metadata (name, description, parameters)
2. Command result schemas
3. Base JSON-RPC schema

### Generation Process

1. **Command Registration**
   ```python
   class CommandRegistry:
       def register(self, func: Callable) -> None:
           command = Command(
               name=func.__name__,
               func=func,
               doc=parse_docstring(func.__doc__),
               result_type=get_return_annotation(func)
           )
           self.commands[command.name] = command
   ```

2. **Getting the Result Schema**
   ```python
   def get_command_schema(command: Command) -> Dict[str, Any]:
       # Get schema from result type
       result_schema = command.result_type.get_schema()
       
       # Add to the general schema
       return {
           "type": "object",
           "properties": {
               "jsonrpc": {"type": "string", "enum": ["2.0"]},
               "result": result_schema,
               "id": {"type": ["string", "integer", "null"]}
           }
       }
   ```

3. **Forming the Complete Schema**
   ```python
   def generate_schema(registry: CommandRegistry) -> Dict[str, Any]:
       schema = load_base_schema()
       
       for command in registry.commands.values():
           # Add parameter schema
           add_params_schema(schema, command)
           
           # Add result schema
           add_result_schema(schema, command)
           
       return schema
   ```

## Approach Advantages

1. **Type Safety**
   - All results are strictly typed
   - IDE provides autocompletion
   - Errors are detected at compile time

2. **Uniformity**
   - All commands return results in the same format
   - JSON-RPC wrapper is added automatically
   - Schema is generated uniformly

3. **Extensibility**
   - Easy to add new result types
   - Complex nested structures are supported
   - Extensible schema generation 