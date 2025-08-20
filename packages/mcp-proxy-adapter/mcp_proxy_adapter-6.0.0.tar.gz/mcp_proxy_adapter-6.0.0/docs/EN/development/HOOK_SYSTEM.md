# Hook System

## Overview

The hook system in MCP Proxy Adapter provides a flexible way to extend application functionality without modifying core code. It allows you to:

- Execute custom code before and after request processing
- Override default `help` and `health` commands with custom implementations
- Add logging, validation, monitoring, and analytics capabilities
- Implement rate limiting and other middleware functionality

## Architecture

The hook system consists of several key components:

### HookManager

The central manager that handles hook registration and execution:

```python
from mcp_proxy_adapter.core.hooks import hook_manager

# Register hooks
hook_manager.register_hook(HookType.PRE_REQUEST, my_pre_hook)
hook_manager.register_hook(HookType.POST_REQUEST, my_post_hook)

# Register custom commands
hook_manager.register_custom_command("help", CustomHelpCommand)
hook_manager.register_custom_command("health", CustomHealthCommand)
```

### HookContext

A dataclass that contains all relevant information about the request and response:

```python
@dataclass
class HookContext:
    command_name: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    execution_time: Optional[float] = None
```

### Hook Types

Available hook types:

- `PRE_REQUEST`: Executed before command processing
- `POST_REQUEST`: Executed after command processing
- `CUSTOM_HELP`: For custom help command implementation
- `CUSTOM_HEALTH`: For custom health command implementation

## Usage Examples

### Pre-Request Hooks

Pre-request hooks are useful for:

- Logging and monitoring
- Parameter validation and modification
- Rate limiting
- Authentication and authorization

```python
import asyncio
from mcp_proxy_adapter.core.hooks import register_pre_request_hook, HookContext

async def logging_hook(context: HookContext) -> None:
    """Log detailed request information."""
    print(f"Processing command: {context.command_name}")
    print(f"Parameters: {context.params}")

async def validation_hook(context: HookContext) -> None:
    """Validate and modify parameters."""
    if context.command_name == "echo":
        message = context.params.get("message", "")
        if len(message) > 1000:
            context.params["message"] = message[:1000] + "..."

# Register hooks
register_pre_request_hook(logging_hook)
register_pre_request_hook(validation_hook)
```

### Post-Request Hooks

Post-request hooks are useful for:

- Analytics and metrics collection
- Response logging
- Performance monitoring
- Error tracking

```python
import time
from mcp_proxy_adapter.core.hooks import register_post_request_hook, HookContext

async def analytics_hook(context: HookContext) -> None:
    """Collect analytics data."""
    analytics_data = {
        "command": context.command_name,
        "execution_time": context.execution_time,
        "success": context.error is None,
        "timestamp": time.time()
    }
    
    # Send to analytics service
    print(f"Analytics: {analytics_data}")

async def performance_hook(context: HookContext) -> None:
    """Monitor performance."""
    if context.execution_time and context.execution_time > 1.0:
        print(f"Slow command detected: {context.command_name} took {context.execution_time}s")

# Register hooks
register_post_request_hook(analytics_hook)
register_post_request_hook(performance_hook)
```

### Custom Commands

You can override the default `help` and `health` commands with custom implementations:

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult
from mcp_proxy_adapter.core.hooks import register_custom_help_command

class CustomHelpCommand(Command):
    """Custom help command with enhanced features."""
    
    name = "help"
    result_class = SuccessResult
    
    async def execute(self, cmdname: Optional[str] = None, **kwargs):
        # Custom help implementation
        return SuccessResult(data={
            "custom_help": True,
            "command": cmdname or "all"
        })

# Register custom command
register_custom_help_command(CustomHelpCommand)
```

## Integration Points

### Command Execution Flow

The hook system is integrated into the command execution flow:

1. **Pre-request hooks** are executed before command processing
2. **Custom command check** - if a custom command is registered, it's used instead of the default
3. **Command execution** - the command is executed
4. **Post-request hooks** are executed after command processing

```python
# In execute_command function
context = HookContext(command_name=command_name, params=params, request_id=request_id)

# Execute pre-request hooks
await hook_manager.execute_hooks(HookType.PRE_REQUEST, context)

# Check for custom commands
if hook_manager.has_custom_command(command_name):
    command_class = hook_manager.get_custom_command(command_name)
else:
    command_class = registry.get_command(command_name)

# Execute command
result = await command_class.run(**params)

# Update context for post-request hooks
context.response_data = result.to_dict()
context.execution_time = execution_time

# Execute post-request hooks
await hook_manager.execute_hooks(HookType.POST_REQUEST, context)
```

## Best Practices

### Hook Design

1. **Keep hooks lightweight** - avoid heavy operations that could slow down request processing
2. **Handle errors gracefully** - hooks should not break the main execution flow
3. **Use async hooks** - for I/O operations, use async functions
4. **Modify context carefully** - be aware that context modifications affect subsequent hooks

### Performance Considerations

1. **Limit hook count** - too many hooks can impact performance
2. **Use async operations** - for database queries, API calls, etc.
3. **Cache expensive operations** - avoid repeated expensive computations
4. **Monitor hook execution time** - track how long hooks take to execute

### Error Handling

Hooks are executed in a try-catch block, so errors in hooks don't break the main execution:

```python
async def safe_hook(context: HookContext) -> None:
    try:
        # Your hook logic here
        pass
    except Exception as e:
        # Log error but don't raise
        logger.error(f"Hook error: {e}")
```

## Advanced Usage

### Rate Limiting Hook

```python
import time
from mcp_proxy_adapter.core.hooks import register_pre_request_hook

class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    async def rate_limit_hook(self, context: HookContext) -> None:
        current_time = time.time()
        command = context.command_name
        
        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items()
            if current_time - v["timestamp"] < 60
        }
        
        if command not in self.requests:
            self.requests[command] = {"count": 1, "timestamp": current_time}
        else:
            self.requests[command]["count"] += 1
            
            if self.requests[command]["count"] > 10:
                raise Exception(f"Rate limit exceeded for {command}")

rate_limiter = RateLimiter()
register_pre_request_hook(rate_limiter.rate_limit_hook)
```

### Analytics Hook

```python
import json
from mcp_proxy_adapter.core.hooks import register_post_request_hook

async def analytics_hook(context: HookContext) -> None:
    """Send analytics data to external service."""
    analytics_data = {
        "command": context.command_name,
        "execution_time": context.execution_time,
        "success": context.error is None,
        "timestamp": time.time(),
        "params_count": len(context.params) if context.params else 0
    }
    
    # Send to analytics service (example)
    try:
        # await analytics_service.send(analytics_data)
        print(f"Analytics sent: {json.dumps(analytics_data)}")
    except Exception as e:
        logger.error(f"Failed to send analytics: {e}")

register_post_request_hook(analytics_hook)
```

## Testing

The hook system includes comprehensive tests. You can test your hooks:

```python
import pytest
from mcp_proxy_adapter.core.hooks import hook_manager, HookContext, HookType

@pytest.mark.asyncio
async def test_my_hook():
    hook_called = False
    
    async def test_hook(context: HookContext) -> None:
        nonlocal hook_called
        hook_called = True
        assert context.command_name == "test_command"
    
    hook_manager.register_hook(HookType.PRE_REQUEST, test_hook)
    
    context = HookContext(command_name="test_command")
    await hook_manager.execute_hooks(HookType.PRE_REQUEST, context)
    
    assert hook_called
```

## Configuration

Hooks can be configured in your application startup:

```python
from mcp_proxy_adapter.core.hooks import (
    register_pre_request_hook, register_post_request_hook,
    register_custom_help_command, register_custom_health_command
)

def setup_hooks():
    """Configure all application hooks."""
    
    # Register monitoring hooks
    register_pre_request_hook(logging_hook)
    register_post_request_hook(analytics_hook)
    
    # Register custom commands if needed
    if config.get("use_custom_help"):
        register_custom_help_command(CustomHelpCommand)
    
    if config.get("use_custom_health"):
        register_custom_health_command(CustomHealthCommand)

# Call during application startup
setup_hooks()
```

## Troubleshooting

### Common Issues

1. **Hooks not executing**: Check that hooks are registered before command execution
2. **Performance issues**: Monitor hook execution time and optimize slow hooks
3. **Memory leaks**: Ensure hooks don't accumulate data indefinitely
4. **Error propagation**: Hooks should handle their own errors gracefully

### Debugging

Enable debug logging to see hook execution:

```python
import logging
logging.getLogger("mcp_proxy_adapter.core.hooks").setLevel(logging.DEBUG)
```

This will show detailed information about hook registration and execution. 