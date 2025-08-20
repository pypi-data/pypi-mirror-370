# Basic Example

The basic example demonstrates a more structured microservice with multiple commands in separate files and comprehensive tests.

## Structure

```
basic_example/
├── __init__.py           # Package initialization
├── config.yaml           # Configuration file
├── README.md             # Documentation
├── server.py             # Server initialization
├── commands/             # Commands directory
│   ├── __init__.py
│   ├── echo_command.py   # Echo command implementation
│   ├── math_command.py   # Math operations command
│   └── time_command.py   # Time-related command
├── docs/                 # Documentation
└── tests/                # Tests directory
    ├── conftest.py       # Test configuration
    ├── test_echo.py      # Echo command tests
    ├── test_math.py      # Math command tests
    └── test_time.py      # Time command tests
```

## Key Components

### Server Setup

The server is initialized with a more structured approach:

```python
def main():
    """Run the microservice."""
    # Create microservice
    service = mcp.MicroService(
        title="Basic Example Microservice",
        description="Basic example of microservice with multiple commands",
        version="1.0.0",
        config_path="config.yaml"
    )
    
    # Register commands from separate files
    service.register_command(EchoCommand)
    service.register_command(MathCommand)
    service.register_command(TimeCommand)
    
    # Run server
    service.run(host="0.0.0.0", port=8000, reload=True)
```

### Command Organization

Each command is implemented in a separate file for better code organization:

```
commands/
├── echo_command.py  # Simple echo command
├── math_command.py  # Mathematical operations
└── time_command.py  # Time-related operations
```

### Command Example: Math Command

The Math command provides basic mathematical operations:

```python
class MathCommand(Command):
    """Command for performing mathematical operations."""
    
    name = "math"
    result_class = MathResult
    
    async def execute(self, operation: str, a: float, b: float) -> MathResult:
        """
        Execute mathematical operation.
        
        Args:
            operation: Operation to perform (add, subtract, multiply, divide)
            a: First number
            b: Second number
            
        Returns:
            Result of operation
            
        Raises:
            InvalidParamsError: If operation is invalid
            CommandError: If division by zero is attempted
        """
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                raise CommandError("Division by zero")
            result = a / b
        else:
            raise InvalidParamsError(f"Unknown operation: {operation}")
            
        return MathResult(operation, a, b, result)
```

### Comprehensive Testing

The basic example includes comprehensive tests for all commands using pytest and the pytest-asyncio plugin for testing asynchronous code:

```python
@pytest.mark.asyncio
async def test_math_add():
    """Test math add operation."""
    command = MathCommand()
    result = await command.execute(operation="add", a=5, b=3)
    
    assert result.operation == "add"
    assert result.a == 5
    assert result.b == 3
    assert result.result == 8
```

## Running the Example

```bash
# Navigate to the project directory
cd examples/basic_example

# Run the server
python server.py
```

The server will be available at http://localhost:8000.

## Testing the API

### Via Web Interface

Open http://localhost:8000/docs in your browser to access the Swagger UI interactive documentation.

### Via Command Line

```bash
# Call echo command
curl -X POST "http://localhost:8000/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello World"}, "id": 1}'

# Call math command
curl -X POST "http://localhost:8000/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "math", "params": {"operation": "add", "a": 5, "b": 3}, "id": 2}'

# Call time command
curl -X POST "http://localhost:8000/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "time", "params": {"format": "iso"}, "id": 3}'
```

## Key Concepts Demonstrated

1. Structured organization of commands in separate files
2. Multiple command types with different functionality
3. Configuration management
4. Comprehensive testing strategy
5. Error handling
6. Parameter validation
7. Different result types 