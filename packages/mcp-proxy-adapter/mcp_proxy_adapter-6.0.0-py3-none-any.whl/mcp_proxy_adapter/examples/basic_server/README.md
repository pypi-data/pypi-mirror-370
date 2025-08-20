# Basic Server Example

A minimal example of MCP Proxy Adapter server without additional commands.

## Features

This example demonstrates:
- Basic server setup
- Built-in commands only (help, health)
- Default configuration
- No custom commands

## Available Commands

- `help` - Get information about available commands
- `health` - Get server health status

## Usage

### Run the server

```bash
python server.py
```

### Test the server

```bash
# Get help
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "help"}'

# Get health status
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "health"}'
```

## API Endpoints

- `POST /cmd` - Execute commands
- `GET /health` - Health check
- `GET /commands` - List available commands
- `GET /docs` - API documentation

## Configuration

The server uses default configuration. You can customize it by:

1. Creating a `config.json` file
2. Setting environment variables
3. Passing configuration to `create_app()`

## Notes

- This is the simplest possible setup
- No custom commands are registered
- Uses framework defaults
- Good starting point for understanding the framework 