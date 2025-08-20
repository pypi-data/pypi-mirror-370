# Command Auto-Discovery and Configuration Reload

## Overview

The MCP Proxy Adapter system supports automatic command discovery and the ability to reload configuration without restarting the server. During reload, custom commands are preserved while built-in commands are reloaded fresh.

## Command Auto-Discovery Process

### How It Works

Command auto-discovery works according to the following principles:

1. **Package Scanning**: The system scans specified packages for modules with names ending in `_command`
2. **Class Analysis**: In each module, it looks for classes that inherit from `Command`
3. **Automatic Registration**: Found commands are automatically registered in the registry

### Auto-Discovery Configuration

```json
{
  "commands": {
    "auto_discovery": true,
    "discovery_path": "mcp_proxy_adapter.commands",
    "custom_commands_path": "./custom_commands"
  }
}
```

### `discover_commands()` Method

```python
def discover_commands(self, package_path: str = "mcp_proxy_adapter.commands") -> int:
    """
    Automatically discovers and registers commands in the specified package.
    
    Args:
        package_path: Path to package with commands
        
    Returns:
        Number of discovered and registered commands
    """
```

## Command Types

### 1. Built-in Commands

Commands provided with the framework:
- `help` - command help
- `health` - server health check
- `config` - configuration management
- `reload` - configuration reload
- `settings` - settings management
- `reload_settings` - settings reload

### 2. Auto-Discovered Commands

Commands found automatically in packages:
- Must be located in modules with names `*_command.py`
- Must inherit from the base `Command` class
- Are registered automatically at startup

### 3. Custom Commands

Commands registered manually:
- Registered via `register_custom_command()`
- Have priority over built-in commands
- Are preserved during configuration reload

## Command Priority Hierarchy

1. **Custom Commands** (highest priority)
2. **Auto-Discovered Commands**
3. **Built-in Commands** (lowest priority)

## Configuration Reload

### `reload_config_and_commands()` Method

```python
def reload_config_and_commands(self, package_path: str = "mcp_proxy_adapter.commands") -> Dict[str, Any]:
    """
    Reloads configuration and re-discovers commands.
    
    Args:
        package_path: Path to package with commands
        
    Returns:
        Dictionary with reload information:
        - config_reloaded: Configuration reload success
        - commands_discovered: Number of discovered commands
        - custom_commands_preserved: Number of preserved custom commands
        - total_commands: Total number of commands after reload
        - built_in_commands: Number of built-in commands
        - custom_commands: Number of custom commands
    """
```

### Reload Process

1. **Preserve Custom Commands**: Create backup of custom commands
2. **Reload Configuration**: Load new configuration from file
3. **Reinitialize Logging**: Configure logging with new parameters
4. **Clear Registry**: Remove all commands except custom ones
5. **Restore Custom Commands**: Restore saved custom commands
6. **Re-discover Commands**: Re-discover and register commands

### Custom Command Preservation

Custom commands are preserved during reload thanks to:

```python
# Preserve custom commands
custom_commands_backup = self._custom_commands.copy()

# Clear all commands
self._commands.clear()
self._instances.clear()

# Restore custom commands
self._custom_commands = custom_commands_backup
```

## Usage Examples

### Registering Custom Commands

```python
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.base import Command

class MyCustomCommand(Command):
    name = "my_custom"
    
    async def execute(self, **kwargs):
        return SuccessResult(message="Custom command executed")

# Register with priority
registry.register_custom_command(MyCustomCommand)
```

### Configuration Reload

```python
# Reload via command
result = await reload_command.execute()

# Direct reload
reload_info = registry.reload_config_and_commands()
print(f"Discovered commands: {reload_info['commands_discovered']}")
print(f"Preserved custom: {reload_info['custom_commands_preserved']}")
```

### Checking Command Types

```python
# Check custom command existence
if registry.custom_command_exists("my_custom"):
    print("Custom command exists")

# Get command with priority
command = registry.get_command_with_priority("my_custom")

# Get all commands with info
all_commands = registry.get_all_commands_info()
```

## Work Demonstration

Create file `demo_reload.py`:

```python
#!/usr/bin/env python3
"""
Demonstration of command auto-discovery and configuration reload.
"""

from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult

class DemoCommand(Command):
    name = "demo"
    result_class = SuccessResult
    
    async def execute(self, message: str = "Hello!", **kwargs):
        return SuccessResult(message=f"Demo: {message}")

def main():
    # Register custom command
    registry.register_custom_command(DemoCommand)
    print(f"Before reload: {len(registry.get_all_commands())} commands")
    
    # Reload configuration
    result = registry.reload_config_and_commands()
    print(f"After reload: {result['total_commands']} commands")
    print(f"Preserved custom: {result['custom_commands_preserved']}")
    
    # Check preservation
    if registry.custom_command_exists("demo"):
        print("✅ Custom command preserved!")
    else:
        print("❌ Custom command lost!")

if __name__ == "__main__":
    main()
```

## System Advantages

1. **Flexibility**: Ability to add commands without code changes
2. **Reliability**: Preservation of custom commands during reload
3. **Performance**: Automatic discovery without manual registration
4. **Prioritization**: Custom commands have priority over built-in ones
5. **Monitoring**: Detailed information about reload process

## Behavior When Deleting Commands

### What Happens When a Command File is Deleted

1. **Before Reload**: Command remains available as it's already loaded in memory
2. **After Reload**: Command disappears from registry as the file no longer exists

### Process for Handling Deleted Commands

```python
# During configuration reload:
def reload_config_and_commands(self, package_path: str = "mcp_proxy_adapter.commands") -> Dict[str, Any]:
    # 1. Preserve custom commands
    custom_commands_backup = self._custom_commands.copy()
    
    # 2. Clear all commands (except custom ones)
    self._commands.clear()
    self._instances.clear()
    
    # 3. Re-discover commands (deleted files are ignored)
    commands_discovered = self.discover_commands(package_path)
    
    # 4. Restore custom commands
    self._custom_commands = custom_commands_backup
```

### Import Error Handling

The system correctly handles situations where command files are deleted:

```python
try:
    module = importlib.import_module(module_path)
    # Process command...
except Exception as e:
    logger.error(f"Error loading command module {module_path}: {e}")
    # Module is skipped, error is logged
```

### Advantages of This Behavior

1. **Safety**: Deleted commands don't remain in the system
2. **Consistency**: Command registry always matches the file system
3. **Fault Tolerance**: Import errors don't interrupt system operation
4. **Flexibility**: Commands can be dynamically added and removed

## Limitations

1. **Naming Requirements**: Modules must end with `_command`
2. **Inheritance**: Commands must inherit from base `Command` class
3. **Server Restart**: Some configuration changes may require server restart
4. **Dependencies**: Custom commands with dependencies must be registered as instances
5. **Command Deletion**: Configuration reload is required to remove commands from registry

## Recommendations

1. **Use Custom Commands** to override built-in ones
2. **Group Commands** in separate packages for better organization
3. **Test Reload** before deploying to production
4. **Monitor Logs** to track auto-discovery process
5. **Document Custom Commands** to facilitate maintenance 