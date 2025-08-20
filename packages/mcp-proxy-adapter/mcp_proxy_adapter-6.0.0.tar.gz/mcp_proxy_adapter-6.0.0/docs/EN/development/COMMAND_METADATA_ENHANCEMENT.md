# Enhancing Command Metadata

## Problem

Currently, the command registry stores command classes, but does not provide a convenient way to access command metadata without creating an instance of the command. Metadata about commands should be more readily available and structured to:

1. Support better documentation 
2. Provide AI tools with rich information about available commands
3. Improve the help command's output
4. Enable better introspection capabilities

## Proposed Solution

Enhance the Command class and CommandRegistry to support comprehensive metadata retrieval:

1. Add a `get_metadata()` class method to the base Command class
2. Update the CommandRegistry to provide access to command metadata
3. Keep the existing command class storage for backward compatibility

## Implementation Plan

### 1. Enhance the Command Base Class

Add a new `get_metadata()` class method to the Command base class:

```python
@classmethod
def get_metadata(cls) -> Dict[str, Any]:
    """
    Returns comprehensive metadata about the command.
    
    This provides a single entry point for all command metadata.
    
    Returns:
        Dict with command metadata
    """
    # Get docstring and format it
    doc = cls.__doc__ or ""
    description = inspect.cleandoc(doc) if doc else ""
    
    # Extract first line for summary
    summary = description.split("\n")[0] if description else ""
    
    # Get parameter info
    param_info = cls.get_param_info()
    
    # Generate example(s) based on parameters
    examples = cls._generate_examples(param_info)
    
    return {
        "name": cls.name,
        "summary": summary,
        "description": description,
        "params": param_info,
        "examples": examples,
        "schema": cls.get_schema(),
        "result_schema": cls.get_result_schema(),
        "result_class": cls.result_class.__name__ if hasattr(cls, "result_class") else None,
    }

@classmethod
def _generate_examples(cls, params: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate usage examples for the command based on its parameters.
    
    Args:
        params: Command parameters information
        
    Returns:
        List of examples
    """
    examples = []
    
    # Simple example without parameters if all parameters are optional
    if not any(param.get("required", False) for param in params.values()):
        examples.append({
            "command": cls.name,
            "description": f"Call the {cls.name} command without parameters"
        })
    
    # Example with all required parameters
    required_params = {k: v for k, v in params.items() if v.get("required", False)}
    if required_params:
        example_params = {}
        for param_name, param_info in required_params.items():
            # Generate appropriate example value based on parameter type
            param_type = param_info.get("type", "")
            if "str" in param_type.lower():
                example_params[param_name] = f"example_{param_name}"
            elif "int" in param_type.lower():
                example_params[param_name] = 123
            elif "float" in param_type.lower():
                example_params[param_name] = 123.45
            elif "bool" in param_type.lower():
                example_params[param_name] = True
            else:
                example_params[param_name] = f"value_for_{param_name}"
        
        examples.append({
            "command": cls.name,
            "params": example_params,
            "description": f"Call the {cls.name} command with required parameters"
        })
    
    # Add an example with all parameters if there are optional ones
    optional_params = {k: v for k, v in params.items() if not v.get("required", False)}
    if optional_params and required_params:
        full_example_params = dict(example_params) if 'example_params' in locals() else {}
        
        for param_name, param_info in optional_params.items():
            # Get default value or generate appropriate example
            if "default" in param_info:
                full_example_params[param_name] = param_info["default"]
            else:
                # Generate appropriate example value based on parameter type
                param_type = param_info.get("type", "")
                if "str" in param_type.lower():
                    full_example_params[param_name] = f"optional_{param_name}"
                elif "int" in param_type.lower():
                    full_example_params[param_name] = 456
                elif "float" in param_type.lower():
                    full_example_params[param_name] = 45.67
                elif "bool" in param_type.lower():
                    full_example_params[param_name] = False
                else:
                    full_example_params[param_name] = f"optional_value_for_{param_name}"
        
        examples.append({
            "command": cls.name,
            "params": full_example_params,
            "description": f"Call the {cls.name} command with all parameters"
        })
    
    return examples
```

### 2. Enhance the CommandRegistry

Update the CommandRegistry to provide access to command metadata:

```python
def get_command_metadata(self, command_name: str) -> Dict[str, Any]:
    """
    Get comprehensive metadata for a command.
    
    Args:
        command_name: Name of the command
        
    Returns:
        Dict with command metadata
        
    Raises:
        NotFoundError: If command is not found
    """
    command_class = self.get_command(command_name)
    return command_class.get_metadata()

def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
    """
    Get metadata for all registered commands.
    
    Returns:
        Dict with command names as keys and metadata as values
    """
    metadata = {}
    for name, command_class in self._commands.items():
        metadata[name] = command_class.get_metadata()
    return metadata
```

### 3. Update the Help Command

Enhance the HelpCommand to use the new metadata:

```python
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
    # If cmdname is provided, return information about specific command
    if cmdname:
        try:
            # Get command metadata from registry
            command_metadata = registry.get_command_metadata(cmdname)
            return HelpResult(command_info=command_metadata)
        except NotFoundError:
            # If command not found, raise error
            raise NotFoundError(f"Command '{cmdname}' not found")
    
    # Otherwise, return information about all available commands
    # and tool metadata
    
    # Get metadata for all commands
    all_metadata = registry.get_all_metadata()
    
    # Prepare response format with tool metadata
    result = {
        "tool_info": {
            "name": "MCP-Proxy API Service",
            "description": "JSON-RPC API for executing microservice commands",
            "version": "1.0.0"
        },
        "help_usage": {
            "description": "Get information about commands",
            "examples": [
                {"command": "help", "description": "List all available commands"},
                {"command": "help", "params": {"cmdname": "command_name"}, "description": "Get detailed info about a specific command"}
            ]
        },
        "commands": {}
    }
    
    # Add command summaries
    for name, metadata in all_metadata.items():
        result["commands"][name] = {
            "summary": metadata["summary"],
            "params_count": len(metadata["params"])
        }
    
    return HelpResult(commands_info=result)
```

### 4. Update the HelpResult Class

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
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        if self.command_info:
            return {
                "cmdname": self.command_info["name"],
                "info": {
                    "description": self.command_info["description"],
                    "summary": self.command_info["summary"],
                    "params": self.command_info["params"],
                    "examples": self.command_info["examples"]
                }
            }
        
        # For list of all commands, return as is (already formatted)
        result = self.commands_info.copy()
        
        # Add total count and usage note
        result["total"] = len(result["commands"])
        result["note"] = "To get detailed information about a specific command, call help with parameter: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}. Only the 'cmdname' parameter is supported."
        
        return result
```

## Expected Results

### 1. Detailed command information

```json
{
  "cmdname": "echo",
  "info": {
    "description": "Command that echoes back input message.\n\nThis command demonstrates simple parameter handling.",
    "summary": "Command that echoes back input message",
    "params": {
      "message": {
        "name": "message",
        "required": true,
        "type": "str",
        "description": "Message to echo back"
      }
    },
    "examples": [
      {
        "command": "echo",
        "params": {"message": "example_message"},
        "description": "Call the echo command with required parameters"
      }
    ]
  }
}
```

### 2. Enhanced command list with metadata

```json
{
  "tool_info": {
    "name": "MCP-Proxy API Service",
    "description": "JSON-RPC API for executing microservice commands",
    "version": "1.0.0"
  },
  "help_usage": {
    "description": "Get information about commands",
    "examples": [
      {"command": "help", "description": "List all available commands"},
      {"command": "help", "params": {"cmdname": "command_name"}, "description": "Get detailed info about a specific command"}
    ]
  },
  "commands": {
    "help": {
      "summary": "Command for getting help information about available commands",
      "params_count": 1
    },
    "echo": {
      "summary": "Command that echoes back input message",
      "params_count": 1
    },
    "math": {
      "summary": "Command for performing basic math operations",
      "params_count": 3
    }
  },
  "total": 3,
  "note": "To get detailed information about a specific command, call help with parameter: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}. Only the 'cmdname' parameter is supported."
}
```

## Benefits

1. More comprehensive command metadata
2. Better documentation capabilities
3. Enhanced help command output with usage examples
4. Improved API self-description
5. Better support for AI tools integration
6. Cleaner separation of metadata and implementation 