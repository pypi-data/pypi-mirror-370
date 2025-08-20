# API Documentation

## Introduction

MCP Proxy API provides a JSON-RPC interface for executing commands. The API is designed to be simple, consistent, and reliable.

### Key Features

- JSON-RPC 2.0 compatible interface
- Asynchronous command execution
- Standardized error handling
- Comprehensive documentation

### Endpoint

The API is accessible through a single endpoint:

```
POST /api/v1/execute
```

All commands are executed through this endpoint, with the command name specified in the `method` field of the JSON-RPC request.

### Authentication

The API uses API key authentication. The API key should be provided in the `X-API-Key` header of the request.

### Content Type

All requests and responses use the `application/json` content type. 