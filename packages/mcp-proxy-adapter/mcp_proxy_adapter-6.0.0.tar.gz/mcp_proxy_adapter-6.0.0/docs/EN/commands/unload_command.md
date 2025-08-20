# Unload Command

## Description

The `unload` command allows removal of dynamically loaded commands from the command registry. Only commands that were loaded via the 'load' command or from the commands directory can be unloaded. Built-in commands and custom commands registered with higher priority cannot be unloaded using this command.

When a command is unloaded:
- The command class is removed from the loaded commands registry
- Any command instances are also removed
- The command becomes unavailable for execution
- Built-in and custom commands with the same name remain unaffected

This is useful for:
- Removing outdated or problematic commands
- Managing memory usage by unloading unused commands
- Testing different versions of commands
- Cleaning up temporary commands loaded for testing

Note: Unloading a command does not affect other commands and does not require a system restart. The command can be reloaded later if needed.

## Result

```python
class UnloadResult(SuccessResult):
    def __init__(self, success: bool, command_name: str, message: str, error: Optional[str] = None):
        data = {
            "success": success,
            "command_name": command_name
        }
        if error:
            data["error"] = error
```

## Command

```python
class UnloadCommand(Command):
    name = "unload"
    result_class = UnloadResult
    
    async def execute(self, command_name: str, **kwargs) -> UnloadResult:
        """
        Execute unload command.
        
        Args:
            command_name: Name of the command to unload
            **kwargs: Additional parameters
            
        Returns:
            UnloadResult: Unload command result
        """
```

## Implementation Details

The command uses the following logic:

1. **Command Validation**: Checks if the specified command exists in the loaded commands registry
2. **Permission Check**: Verifies that the command is a loaded command (not built-in or custom)
3. **Removal Process**: Removes the command class and any associated instances
4. **Registry Update**: Updates the command registry to reflect the changes
5. **Result Generation**: Returns success or error information

## Usage Examples

### Python

```python
# Unload a previously loaded command
result = await execute_command("unload", {"command_name": "test_command"})
```

### HTTP REST

```bash
# Unload a command
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "unload", "params": {"command_name": "test_command"}}'
```

### JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "method": "unload",
  "params": {
    "command_name": "test_command"
  },
  "id": 1
}
```

## Examples

### Successful Unload

```json
{
  "command": "unload",
  "params": {
    "command_name": "test_command"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "command_name": "test_command"
  },
  "message": "Command 'test_command' unloaded successfully"
}
```

### Error - Command Not Found

```json
{
  "command": "unload",
  "params": {
    "command_name": "nonexistent_command"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": false,
    "command_name": "nonexistent_command",
    "error": "Command 'nonexistent_command' is not a loaded command or does not exist"
  },
  "message": "Failed to unload commands from nonexistent_command: Command 'nonexistent_command' is not a loaded command or does not exist"
}
```

### Error - Built-in Command

```json
{
  "command": "unload",
  "params": {
    "command_name": "help"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": false,
    "command_name": "help",
    "error": "Command 'help' is not a loaded command or does not exist"
  },
  "message": "Failed to unload commands from help: Command 'help' is not a loaded command or does not exist"
}
```

## Error Handling

The command handles various error scenarios:

- **Command Not Found**: Returns error when the specified command doesn't exist
- **Not a Loaded Command**: Returns error when trying to unload built-in or custom commands
- **Registry Errors**: Returns error when there are issues with the command registry

## Command Priority

The unload command respects the command priority hierarchy:

1. **Custom Commands** (highest priority) - Cannot be unloaded
2. **Built-in Commands** - Cannot be unloaded
3. **Loaded Commands** (lowest priority) - Can be unloaded

This ensures that system stability is maintained by preventing the removal of critical commands.

## Workflow Example

```python
# 1. Load a command
load_result = await execute_command("load", {"source": "./my_command.py"})

# 2. Use the loaded command
use_result = await execute_command("my_command", {"param": "value"})

# 3. Unload the command when no longer needed
unload_result = await execute_command("unload", {"command_name": "my_command"})

# 4. The command is no longer available
# This would fail:
# error_result = await execute_command("my_command", {"param": "value"})
```

## Best Practices

1. **Load Before Use**: Always load commands before attempting to use them
2. **Unload When Done**: Unload commands when they are no longer needed to free up memory
3. **Check Status**: Use the load command's response to verify successful loading before unloading
4. **Error Handling**: Always check the success status of unload operations
5. **Reuse**: Commands can be reloaded after unloading if needed again 