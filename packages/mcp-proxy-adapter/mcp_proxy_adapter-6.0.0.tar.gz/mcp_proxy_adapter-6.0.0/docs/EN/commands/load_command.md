# Load Command

## Description

The `load` command allows dynamic loading of command modules from either local file system or remote HTTP/HTTPS URLs. This command automatically detects whether the source is a local path or URL and handles the loading accordingly.

For local paths, the command loads Python modules ending with '_command.py'. For URLs, the command downloads the Python code and loads it as a temporary module.

The loaded commands are registered in the command registry and become immediately available for execution. Only commands that inherit from the base Command class and are properly structured will be loaded and registered.

## Security Considerations

- Local paths are validated for existence and proper naming
- URLs are downloaded with timeout protection
- Temporary files are automatically cleaned up after loading
- Only files ending with '_command.py' are accepted

## Result

```python
class LoadResult(SuccessResult):
    def __init__(self, success: bool, commands_loaded: int, loaded_commands: list, source: str, error: Optional[str] = None):
        data = {
            "success": success,
            "commands_loaded": commands_loaded,
            "loaded_commands": loaded_commands,
            "source": source
        }
        if error:
            data["error"] = error
```

## Command

```python
class LoadCommand(Command):
    name = "load"
    result_class = LoadResult
    
    async def execute(self, source: str, **kwargs) -> LoadResult:
        """
        Execute load command.
        
        Args:
            source: Source path or URL to load command from
            **kwargs: Additional parameters
            
        Returns:
            LoadResult: Load command result
        """
```

## Implementation Details

The command uses the following logic:

1. **Source Detection**: Parses the source string to determine if it's a URL or local path
2. **Local Loading**: For local paths, validates file existence and naming convention
3. **Remote Loading**: For URLs, downloads content with timeout and creates temporary file
4. **Module Loading**: Uses Python's importlib to load the module dynamically
5. **Command Registration**: Registers found command classes in the command registry
6. **Cleanup**: Removes temporary files for remote loading

## Usage Examples

### Python

```python
# Load from local file
result = await execute_command("load", {"source": "./my_command.py"})

# Load from URL
result = await execute_command("load", {"source": "https://example.com/remote_command.py"})
```

### HTTP REST

```bash
# Load from local file
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "load", "params": {"source": "./my_command.py"}}'

# Load from URL
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "load", "params": {"source": "https://example.com/remote_command.py"}}'
```

### JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "method": "load",
  "params": {
    "source": "./my_command.py"
  },
  "id": 1
}
```

## Examples

### Load from Local File

```json
{
  "command": "load",
  "params": {
    "source": "./custom_command.py"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "commands_loaded": 1,
    "loaded_commands": ["custom_command"],
    "source": "./custom_command.py"
  },
  "message": "Loaded 1 commands from ./custom_command.py"
}
```

### Load from GitHub

```json
{
  "command": "load",
  "params": {
    "source": "https://raw.githubusercontent.com/user/repo/main/remote_command.py"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "commands_loaded": 1,
    "loaded_commands": ["remote_command"],
    "source": "https://raw.githubusercontent.com/user/repo/main/remote_command.py"
  },
  "message": "Loaded 1 commands from https://raw.githubusercontent.com/user/repo/main/remote_command.py"
}
```

### Error - File Not Found

```json
{
  "command": "load",
  "params": {
    "source": "/nonexistent/path/test_command.py"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": false,
    "commands_loaded": 0,
    "loaded_commands": [],
    "source": "/nonexistent/path/test_command.py",
    "error": "Command file does not exist: /nonexistent/path/test_command.py"
  },
  "message": "Failed to load commands from /nonexistent/path/test_command.py: Command file does not exist: /nonexistent/path/test_command.py"
}
```

### Error - Invalid Filename

```json
{
  "command": "load",
  "params": {
    "source": "./invalid.py"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": false,
    "commands_loaded": 0,
    "loaded_commands": [],
    "source": "./invalid.py",
    "error": "Command file must end with '_command.py': ./invalid.py"
  },
  "message": "Failed to load commands from ./invalid.py: Command file must end with '_command.py': ./invalid.py"
}
```

## Error Handling

The command handles various error scenarios:

- **File Not Found**: Returns error when local file doesn't exist
- **Invalid Filename**: Returns error when file doesn't end with '_command.py'
- **Network Errors**: Returns error when URL download fails
- **Import Errors**: Returns error when Python module cannot be loaded
- **Missing Requests Library**: Returns error when requests library is not available for URL loading

## Dependencies

- `requests` library for HTTP/HTTPS URL loading (optional, gracefully handled if missing)
- `urllib.parse` for URL parsing
- `tempfile` for temporary file management
- `importlib` for dynamic module loading 