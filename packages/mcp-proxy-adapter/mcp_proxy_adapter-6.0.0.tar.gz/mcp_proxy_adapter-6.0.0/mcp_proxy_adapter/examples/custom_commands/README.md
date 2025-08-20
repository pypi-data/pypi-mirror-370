# Custom Commands Server Example

This example demonstrates both auto-registration and manual registration of commands in the MCP Proxy Adapter framework.

## Registration Methods

### 1. Auto-Registration

Commands are automatically discovered and registered by the framework if they:
- Are located in packages that follow the naming convention
- Have class names ending with "Command"
- Inherit from the `Command` base class

**Location:** `auto_commands/` package
**Files:** 
- `auto_echo_command.py` - AutoEchoCommand
- `auto_info_command.py` - AutoInfoCommand

**How it works:**
```python
# Framework automatically discovers commands in auto_commands/ package
registry.discover_commands("mcp_proxy_adapter.examples.custom_commands.auto_commands")
```

### 2. Manual Registration

Commands are explicitly registered in the server code using:
- `registry.register()` - for regular commands
- `registry.register_custom_command()` - for commands that override built-ins

**Location:** Main server file
**Files:**
- `echo_command.py` - EchoCommand
- `custom_help_command.py` - CustomHelpCommand
- `custom_health_command.py` - CustomHealthCommand
- `data_transform_command.py` - DataTransformCommand
- `intercept_command.py` - InterceptCommand
- `manual_echo_command.py` - ManualEchoCommand

**How it works:**
```python
# Explicit registration in server code
registry.register(EchoCommand)
registry.register_custom_command(CustomHelpCommand)  # Overrides built-in
```

### 3. Built-in Commands

Framework provides default commands that are registered automatically:
- `help` - HelpCommand
- `health` - HealthCommand

These can be overridden by custom commands using `register_custom_command()`.

## Command Hierarchy

1. **Custom Commands** (highest priority) - registered with `register_custom_command()`
2. **Manually Registered Commands** - registered with `register()`
3. **Auto-Registered Commands** - discovered automatically
4. **Built-in Commands** (lowest priority) - framework defaults

## Testing Commands

### Auto-Registered Commands
```bash
# Test auto-registered echo
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "auto_echo", "params": {"message": "Hello!"}, "id": 1}'

# Test auto-registered info
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "auto_info", "params": {"topic": "test"}, "id": 2}'
```

### Manually Registered Commands
```bash
# Test manually registered echo
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "manual_echo", "params": {"message": "Hello!"}, "id": 3}'

# Test other manually registered commands
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello!"}, "id": 4}'
```

### Built-in Commands (or overridden)
```bash
# Test help command (custom or built-in)
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "help", "id": 5}'

# Test health command (custom or built-in)
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "health", "id": 6}'
```

## Features Demonstrated

### Auto-Registration
- ✅ Automatic command discovery
- ✅ Naming convention compliance
- ✅ Package-based organization
- ✅ Framework integration

### Manual Registration
- ✅ Explicit command registration
- ✅ Custom command overrides
- ✅ Priority management
- ✅ Dependency control

### Built-in Commands
- ✅ Framework defaults
- ✅ Override capability
- ✅ Fallback behavior
- ✅ Consistent API

### Advanced Features
- ✅ Command hierarchy
- ✅ Priority resolution
- ✅ Hook integration
- ✅ Error handling 