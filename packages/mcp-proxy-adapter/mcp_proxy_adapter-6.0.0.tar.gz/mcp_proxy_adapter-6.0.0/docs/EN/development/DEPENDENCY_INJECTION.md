# Dependency Injection

MCP Proxy Adapter version 3.1.6 introduces support for Dependency Injection (DI).
This feature allows creating more flexible and testable commands that can
use shared services and resources.

## Core Concepts

**Dependency Injection (DI)** is a design pattern where an object receives its
dependencies from external sources rather than creating them itself. In the context of microservice-command-protocol:

1. **Commands** - classes that receive dependencies through their constructor
2. **Dependencies** - services, repositories, or other objects needed by commands
3. **Container** - an object for storing and managing dependencies
4. **Registration** - the process of adding a command instance to the registry

## Using DI in Commands

### 1. Creating a Command with Dependencies

```python
from mcp_proxy_adapter.commands import Command, SuccessResult

class DatabaseService:
    """Service for data operations."""
    
    def get_data(self, key):
        # ... data retrieval logic
        return {"result": f"Data for {key}"}


class DataCommand(Command):
    """Command using an injected dependency."""
    
    name = "get_data"
    result_class = SuccessResult
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize command with dependencies.
        
        Args:
            db_service: Service for data operations
        """
        self.db_service = db_service
    
    async def execute(self, key: str) -> SuccessResult:
        """Execute command."""
        data = self.db_service.get_data(key)
        return self.result_class(**data)
```

### 2. Registering a Command with Dependencies

```python
from mcp_proxy_adapter.commands import registry, container

# Create services
db_service = DatabaseService()

# Register in container (optional)
container.register("db_service", db_service)

# Create command instance with dependencies
data_command = DataCommand(db_service)

# Register the instance
registry.register(data_command)
```

### 3. Executing the Command via API

After registering a command with dependencies, it can be called via API just like regular commands. The system will automatically find the registered command instance:

```json
{
  "jsonrpc": "2.0",
  "method": "get_data",
  "params": {
    "key": "user_123"
  },
  "id": 1
}
```

## Registration Types and Lifecycle Management

### 1. Command Instance Registration

```python
# Create instance
command = MyCommand(dependency)

# Register instance
registry.register(command)
```

### 2. Command Class Registration (for commands without dependencies)

```python
# Register class
registry.register(MySimpleCommand)
```

## Dependency Container

MCP Proxy Adapter includes a simple dependency container (`DependencyContainer`) that can be used for centralized dependency management:

```python
from mcp_proxy_adapter.commands import container

# Register a simple dependency
container.register("config", config_service)

# Register a factory (creates a new instance on each request)
container.register_factory("logger", lambda: create_logger())

# Register a singleton (creates instance only on first request)
container.register_singleton("db", lambda: create_db_connection())

# Get a dependency
db = container.get("db")
```

## Full Integration Example

```python
import asyncio
from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.commands import registry, container

# Create services
db_service = DatabaseService("sqlite://:memory:")
config_service = ConfigService("config.json")
time_service = TimeService()

# Register in container
container.register("db", db_service)
container.register("config", config_service)
container.register("time", time_service)

# Register commands
registry.register(DataCommand(db_service, time_service))
registry.register(ConfigCommand(config_service))
registry.register(StatusCommand(db_service, config_service, time_service))

# Create FastAPI application
app = create_app()

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## DI Benefits

1. **Testability** - ability to replace real dependencies with mocks during testing
2. **Flexibility** - ability to change dependencies without modifying command code
3. **Lifecycle Management** - centralized resource management
4. **Reusability** - ability to use the same services across different commands

## Best Practices

1. **Interfaces** - define clear interfaces for services
2. **Initialization** - initialize dependencies at application startup
3. **Resource Cleanup** - add handlers for proper resource cleanup
4. **Grouping** - group logically related dependencies in a single service

## Complete Examples

Complete examples of DI usage can be found in the `examples/di_example/` directory and `examples/commands/echo_command_di.py`.

## Backward Compatibility

The DI implementation is fully backward compatible with previous library versions. Commands without dependencies will continue to work without changes. 