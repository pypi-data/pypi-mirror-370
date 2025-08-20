# Minimal Example

The minimal example demonstrates the simplest possible microservice with a single command.

## Structure

```
minimal_example/
├── __init__.py           # Package initialization
├── config.yaml           # Configuration file
├── README.md             # Documentation
├── simple_server.py      # Server with a single command
└── tests/                # Tests directory
```

## Key Components

### Server Setup

The server is initialized with minimal configuration:

```python
# Create microservice
service = mcp.MicroService(
    title="Minimal Example Microservice",
    description="Simple example of microservice with a single command",
    version="1.0.0"
)

# Register command
service.register_command(HelloCommand)

# Run server
service.run(host="0.0.0.0", port=8000, reload=True)
```

### Command Implementation

The example implements a simple `hello` command that returns a greeting message:

```python
class HelloCommand(Command):
    """Command that returns hello message."""
    
    name = "hello"
    result_class = HelloResult
    
    async def execute(self, name: str = "World") -> HelloResult:
        """
        Execute command.
        
        Args:
            name: Name to greet
            
        Returns:
            Hello result
        """
        return HelloResult(f"Hello, {name}!")
```

### Result Implementation

The command returns a `HelloResult` class:

```python
class HelloResult(SuccessResult):
    """Result of hello command."""
    
    def __init__(self, message: str):
        """
        Initialize result.
        
        Args:
            message: Hello message
        """
        self.message = message
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {"message": self.message}
```

## Running the Example

```bash
# Navigate to the project directory
cd examples/minimal_example

# Run the server
python simple_server.py
```

The server will be available at http://localhost:8000.

## Testing the API

### Via Web Interface

Open http://localhost:8000/docs in your browser to access the Swagger UI interactive documentation.

### Via Command Line

```bash
# Call hello command via JSON-RPC
curl -X POST "http://localhost:8000/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "hello", "params": {"name": "User"}, "id": 1}'

# Call hello command via simplified endpoint
curl -X POST "http://localhost:8000/cmd" \
  -H "Content-Type: application/json" \
  -d '{"command": "hello", "params": {"name": "User"}}'
```

## Key Concepts Demonstrated

1. Creating a minimal microservice
2. Defining a simple command
3. Basic API endpoints
4. Working with JSON-RPC
5. Command result structure
6. Schema generation for validation 