# Command Removal Guide

This guide outlines the proper procedure for removing commands from the MCP Proxy Adapter.

## Overview

When a command is no longer needed, it's important to completely remove all related components to keep the codebase clean and maintainable. Simply commenting out or leaving unused files in the project can lead to confusion and technical debt.

## Complete Removal Checklist

To properly remove a command, follow these steps:

- [ ] Delete command implementation file (`{command_name}_command.py`)
- [ ] Delete result class file if it exists in a separate file (`{command_name}_result.py`)
- [ ] Delete test files (`test_{command_name}_command.py`)
- [ ] Remove any references in documentation
- [ ] Update any examples or tutorials that reference the command
- [ ] Verify the command is properly unregistered from the registry

## Step-by-Step Procedure

### 1. Remove Command Files

Delete the following files associated with the command:

```bash
# Delete command implementation
rm mcp_microservice/commands/{command_name}_command.py

# Delete result file if it exists separately
rm mcp_microservice/commands/{command_name}_result.py

# Delete test files
rm mcp_microservice/tests/commands/test_{command_name}_command.py
```

### 2. Restart the Application

The command will be automatically unregistered because the auto-discovery system won't find the deleted files on the next application restart.

```bash
# Restart the application
# The command registry's discovery mechanism won't find the deleted files
```

### 3. Manual Unregistration (Alternative)

If you need to remove a command without restarting the application, you can manually unregister it:

```python
from mcp_proxy_adapter.commands.command_registry import registry

# Unregister the command by name
registry.unregister("{command_name}")
```

This approach is useful in dynamic scenarios but typically unnecessary since commands are discovered automatically on application startup.

### 4. Update Documentation

Ensure you update any documentation that references the removed command:

- Remove command examples from appropriate documentation files
- Update any API documentation that includes the command
- Update tutorials or guides that use the command

### 5. Update Tests

If there are integration tests that use the command, these should be updated or removed:

- Check for test cases in `mcp_microservice/tests/integration/` that may use the command
- Check for test cases in `mcp_microservice/tests/api/` that may reference the command endpoints

### 6. Verify Removal

To verify the command has been properly removed:

1. Start the application
2. Check that the command doesn't appear in the list of available commands
3. Verify that calling the removed command returns a "command not found" error

```python
# This should raise a NotFoundError or return an appropriate error response
await registry.get_command("{command_name}")
```

## Notes and Considerations

### Dependencies Between Commands

If the command being removed is a dependency for other commands, make sure to update those dependent commands first.

### Backward Compatibility

Consider whether removing the command will break backward compatibility. If the command is part of a public API, consider:

- Marking it as deprecated first
- Providing alternative commands
- Communicating the removal to users before actually removing it

### Command Registry Behavior

The command registry operates as follows:

1. On application startup, it scans the `mcp_microservice/commands/` directory
2. It automatically registers all valid command classes it discovers
3. If a command file is deleted, it won't be discovered on the next scan
4. Manual unregistration can be performed using `registry.unregister()`

## Example: Removing the "hello_world" Command

```bash
# Delete command files
rm mcp_microservice/commands/hello_world_command.py
rm mcp_microservice/commands/hello_world_result.py
rm mcp_microservice/tests/commands/test_hello_world_command.py

# Restart the application to apply changes
# The command registry won't find the deleted hello_world command files
```

After restart, the "hello_world" command will no longer be available. 