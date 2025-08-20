# Architecture

This document describes the architecture of the MCP Proxy service.

## Overview

MCP Proxy is built using a modular, command-based architecture. The main components are:

1. **API Layer**: Handles HTTP requests and responses
2. **Command Registry**: Manages available commands
3. **Command Implementations**: The actual command logic
4. **Core Utilities**: Logging, error handling, and configuration

## Component Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Client      │────▶│    API Layer    │────▶│ Command Registry │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Core Utilities │◀───▶│Command Execution│◀────│    Commands     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## API Layer

The API layer is built on FastAPI and provides a JSON-RPC interface for executing commands. It handles:

- Request parsing and validation
- Command dispatch
- Response formatting
- Error handling
- Authentication
- CORS

## Command Registry

The Command Registry is a singleton that manages all available commands. It provides:

- Command registration
- Command lookup
- Command metadata
- Automatic command discovery

## Command Implementations

Each command is implemented as a class that extends `BaseCommand`. A command implementation consists of:

- The command class
- The result class
- Parameter validation
- Business logic
- Error handling

## Core Utilities

The core utilities provide common functionality used by other components:

- Configuration management
- Logging
- Error handling
- Helpers and utilities

## Execution Flow

1. Client sends a JSON-RPC request to the API endpoint
2. API layer parses and validates the request
3. Command is looked up in the Command Registry
4. Command is instantiated and executed with the provided parameters
5. Result is formatted and returned to the client
6. Any errors are caught, logged, and returned as JSON-RPC error responses

## Directory Structure

```
mcp_microservice/
├── __init__.py
├── api/                    # API implementation
│   ├── __init__.py
│   ├── app.py              # FastAPI application setup
│   ├── handlers.py         # Request handlers
│   ├── middleware.py       # API middleware components
│   └── schemas.py          # API schema definitions
├── commands/               # Command implementations
│   ├── __init__.py
│   ├── base.py             # Base command class
│   ├── command_registry.py # Command registration
│   └── result.py           # Command result classes
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── errors.py           # Error definitions
│   ├── logging.py          # Logging setup
│   └── utils.py            # Utility functions
└── main.py                 # Application entry point
``` 