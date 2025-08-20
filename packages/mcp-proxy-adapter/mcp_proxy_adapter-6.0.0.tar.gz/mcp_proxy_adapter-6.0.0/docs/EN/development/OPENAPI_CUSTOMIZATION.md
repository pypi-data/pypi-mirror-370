# Improving OpenAPI Customization

## Problem

In the current implementation of the MCP Proxy Adapter framework, the OpenAPI schema parameters (such as `title`, `description`, `version`) are hardcoded in the base schema `mcp_proxy_adapter/schemas/openapi_schema.json`:

```json
"info": {
  "title": "MCP Microservice API",
  "description": "API для выполнения команд микросервиса",
  "version": "1.0.0"
}
```

This limits customization capabilities when using the framework in specific projects.

Additionally, the current implementation lacks comprehensive metadata for tools and the help command, which makes it difficult for users to understand the available commands and their usage.

## Proposed Solution

1. Implement the ability to configure OpenAPI schema parameters through the `create_app()` function and pass them to the OpenAPI schema generator.

2. Enhance the metadata generation for tools and improve the help command to provide more comprehensive information.

## Implementation Plan

### 1. OpenAPI Customization

1. Modify the `create_app()` function to accept OpenAPI parameters:

```python
def create_app(
    title: str = "MCP Microservice API",
    description: str = "API for executing microservice commands",
    version: str = "1.0.0",
    **kwargs
) -> FastAPI:
    """
    Creates and configures FastAPI application.

    Args:
        title: API title for OpenAPI schema
        description: API description for OpenAPI schema
        version: API version for OpenAPI schema
        **kwargs: Additional parameters for FastAPI

    Returns:
        Configured FastAPI application.
    """
    # Create application
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        **kwargs
    )
    
    # ... rest of the code ...
```

2. Modify the OpenAPI schema generator to use parameters from the FastAPI application:

```python
def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """
    Create a custom OpenAPI schema for the FastAPI application.
    
    Args:
        app: The FastAPI application.
        
    Returns:
        Dict containing the custom OpenAPI schema.
    """
    generator = CustomOpenAPIGenerator()
    openapi_schema = generator.generate(
        title=app.title,
        description=app.description,
        version=app.version
    )
    
    # Cache the schema
    app.openapi_schema = openapi_schema
    
    return openapi_schema
```

3. Update the `CustomOpenAPIGenerator` class to account for OpenAPI parameters:

```python
def generate(self, title: str = None, description: str = None, version: str = None) -> Dict[str, Any]:
    """
    Generate the complete OpenAPI schema compatible with MCP-Proxy.
    
    Args:
        title: API title for OpenAPI schema
        description: API description for OpenAPI schema
        version: API version for OpenAPI schema
        
    Returns:
        Dict containing the complete OpenAPI schema.
    """
    # Deep copy the base schema to avoid modifying it
    schema = deepcopy(self.base_schema)
    
    # Update info if provided
    if title:
        schema["info"]["title"] = title
    if description:
        schema["info"]["description"] = description
    if version:
        schema["info"]["version"] = version
    
    # Add commands to schema
    self._add_commands_to_schema(schema)
    
    logger.info(f"Generated OpenAPI schema with {len(registry.get_all_commands())} commands")
    
    return schema
```

### 2. Help Command and Tool Metadata Enhancement

1. Improve the `HelpCommand` class to provide more comprehensive information:

```python
class HelpCommand(Command):
    """
    Command for getting help information about available commands.
    
    Usage:
    - Without parameters: Returns a list of available commands with brief descriptions and usage instructions
    - With cmdname parameter: Returns detailed information about the specified command
    """
    
    # ... existing code ...
    
    async def execute(self, cmdname: Optional[str] = None) -> HelpResult:
        # ... existing code ...
        
        # When getting list of all commands, add information about the tool
        # and how to use the help command
        if not cmdname:
            commands_info = {}
            
            # Add meta-information about help command and tool
            commands_info["help_usage"] = {
                "description": "Get information about commands",
                "examples": [
                    {"command": "help", "description": "List all available commands"},
                    {"command": "help", "params": {"cmdname": "command_name"}, "description": "Get detailed info about a specific command"}
                ]
            }
            
            commands_info["tool_info"] = {
                "name": "MCP-Proxy API Service",
                "description": "JSON-RPC API for executing microservice commands",
                "version": "1.0.0"
            }
            
            # Add information about commands
            for name, cmd_class in commands.items():
                # ... existing code ...
                # Add brief usage information
                commands_info[name] = {
                    "description": description,
                    "summary": _get_first_line(description),
                    "params_count": len(cmd_class.get_param_info())
                }
            
            return HelpResult(commands_info=commands_info)
```

2. Enhance the `HelpResult` class to support extended metadata:

```python
class HelpResult(CommandResult):
    # ... existing code ...
    
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
                    "summary": _get_first_line(self.command_info["description"]),
                    "params": self.command_info["params"],
                    # Add example of command usage
                    "examples": _generate_examples(self.command_info)
                }
            }
        
        # For list of all commands, include meta-information
        result = {"commands": {}}
        
        # Copy special meta-fields
        if "help_usage" in self.commands_info:
            result["help_usage"] = self.commands_info.pop("help_usage")
        
        if "tool_info" in self.commands_info:
            result["tool_info"] = self.commands_info.pop("tool_info")
        
        # Add information about available commands
        result["commands"] = self.commands_info
        result["total"] = len(self.commands_info)
        
        # Add hint about help command format with parameter
        result["note"] = "To get info about a specific command, call help with parameter: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}. Only the 'cmdname' parameter is supported. Calling 'help <command>' (with space) is NOT supported."
        
        return result
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        # ... update schema to support extended metadata ...
```

3. Add utility functions for formatting information:

```python
def _get_first_line(text: str) -> str:
    """
    Extract the first non-empty line from text.
    """
    if not text:
        return ""
    
    lines = [line.strip() for line in text.strip().split("\n")]
    return next((line for line in lines if line), "")


def _generate_examples(command_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate usage examples for a command.
    """
    name = command_info["name"]
    params = command_info["params"]
    
    # Simple example without parameters
    examples = [{"command": name}]
    
    # Example with required parameters
    required_params = {k: v for k, v in params.items() if v.get("required", False)}
    if required_params:
        example_params = {}
        for param_name, param_info in required_params.items():
            # Generate example value based on type
            param_type = param_info.get("type", "")
            if "string" in param_type.lower():
                example_params[param_name] = f"example_{param_name}"
            elif "int" in param_type.lower():
                example_params[param_name] = 123
            elif "float" in param_type.lower():
                example_params[param_name] = 123.45
            elif "bool" in param_type.lower():
                example_params[param_name] = True
            else:
                example_params[param_name] = f"value_{param_name}"
        
        examples.append({"command": name, "params": example_params})
    
    return examples
```

4. Enhance the `get_command_info` method in `CommandRegistry` class:

```python
def get_command_info(self, command_name: str) -> Dict[str, Any]:
    """
    Gets information about a command.

    Args:
        command_name: Command name.

    Returns:
        Dictionary with command information.

    Raises:
        NotFoundError: If command is not found.
    """
    command_class = self.get_command(command_name)
    
    # Get docstring and format it
    doc = command_class.__doc__ or ""
    description = inspect.cleandoc(doc) if doc else ""
    
    param_info = command_class.get_param_info()
    
    # Add more information for each parameter
    for param_name, param in param_info.items():
        # Extract information from docstring if available
        param_doc = _extract_param_doc(doc, param_name)
        if param_doc:
            param["description"] = param_doc
    
    return {
        "name": command_name,
        "description": description,
        "params": param_info,
        "schema": command_class.get_schema(),
        "result_schema": command_class.get_result_schema()
    }
```

5. Enhance the OpenAPI schema with more information about the tool:

```python
def _add_commands_to_schema(self, schema: Dict[str, Any]) -> None:
    # ... existing code ...
    
    # Add tool description to the operation description
    endpoint_path = "/cmd"
    if endpoint_path in schema["paths"]:
        cmd_endpoint = schema["paths"][endpoint_path]["post"]
        
        # Expand endpoint description
        cmd_endpoint["description"] = """
        Executes a command via JSON-RPC protocol.
        
        This endpoint supports two request formats:
        1. Simple command format: {"command": "command_name", "params": {...}}
        2. JSON-RPC format: {"jsonrpc": "2.0", "method": "command_name", "params": {...}, "id": 123}
        
        To get help about available commands, call:
        - {"command": "help"} - List all available commands
        - {"command": "help", "params": {"cmdname": "command_name"}} - Get detailed info about a specific command
        """
```

## Expected Results

### 1. Enhanced help command response without parameters:

```json
{
  "help_usage": {
    "description": "Get information about commands",
    "examples": [
      {"command": "help", "description": "List all available commands"},
      {"command": "help", "params": {"cmdname": "command_name"}, "description": "Get detailed info about a specific command"}
    ]
  },
  "tool_info": {
    "name": "MCP-Proxy API Service",
    "description": "JSON-RPC API for executing microservice commands",
    "version": "1.0.0"
  },
  "commands": {
    "help": {
      "summary": "Command for getting help information about available commands",
      "description": "Command for getting help information about available commands.\n\nUsage:\n- Without parameters: Returns a list of available commands...",
      "params_count": 1
    },
    ...other commands...
  },
  "total": 4,
  "note": "To get info about a specific command, call help with parameter: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}. Only the 'cmdname' parameter is supported. Calling 'help <command>' (with space) is NOT supported."
}
```

### 2. Enhanced help command response with parameter:

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
      {"command": "echo"},
      {"command": "echo", "params": {"message": "example_message"}}
    ]
  }
}
```

## Benefits

1. More flexible framework configuration for specific projects
2. Ability to specify custom title, description, and API version
3. Better alignment with framework design principles
4. Improved user experience when working with the API
5. Enhanced documentation and self-discovery capabilities
6. Better tool metadata for integration with other systems

## Usage Example After Changes

```python
from mcp_proxy_adapter import create_app

# Create application with custom OpenAPI parameters
app = create_app(
    title="My Microservice",
    description="API for working with text data",
    version="2.1.3"
)
``` 