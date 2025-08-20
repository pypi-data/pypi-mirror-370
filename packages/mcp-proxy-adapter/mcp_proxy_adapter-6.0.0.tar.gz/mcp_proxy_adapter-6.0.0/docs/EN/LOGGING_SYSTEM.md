# Logging System

## Contents

1. [Introduction](#introduction)
2. [Logging Configuration](#logging-configuration)
3. [Log Formatting](#log-formatting)
4. [Log Rotation](#log-rotation)
5. [Logging Levels](#logging-levels)
6. [Context Logging](#context-logging)
7. [Usage in Code](#usage-in-code)
8. [Examples](#examples)

## Introduction

The logging system in the microservice is designed to track application operation, diagnose errors, and monitor performance. It supports various logging levels, message formatting, log file rotation, and contextual request logging.

Main components of the logging system:

1. **Basic Logging** - standard logging functions for all modules
2. **Context Logging** - specialized logging with request context
3. **Log Rotation** - automatic management of log file sizes
4. **Formatting** - customizable log output format

## Logging Configuration

Logging settings are specified in the `config.json` configuration file:

```json
{
    "logging": {
        "level": "DEBUG",
        "file": "logs/app.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "rotation": {
            "type": "size",
            "max_bytes": 10485760,
            "backup_count": 5,
            "when": "D",
            "interval": 1
        },
        "levels": {
            "uvicorn": "INFO",
            "uvicorn.access": "WARNING",
            "fastapi": "INFO"
        }
    }
}
```

### Configuration Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `level` | Logging level | `"INFO"` |
| `file` | Path to log file | `null` (console output only) |
| `format` | Log message format | `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"` |
| `date_format` | Date/time format | `"%Y-%m-%d %H:%M:%S"` |
| `rotation.type` | Log rotation type (`"size"` or `"time"`) | `"size"` |
| `rotation.max_bytes` | Maximum log file size (bytes) | `10485760` (10 MB) |
| `rotation.backup_count` | Number of rotation files | `5` |
| `rotation.when` | Time units for time-based rotation (`"S"`, `"M"`, `"H"`, `"D"`, `"W0"`-`"W6"`) | `"D"` (day) |
| `rotation.interval` | Rotation interval | `1` |
| `levels` | Logging levels for external libraries | `{}` |

## Log Formatting

The logging system uses two different formatters:

1. **ConsoleFormatter** - for console output with color formatting
2. **FileFormatter** - for file output with standard formatting

### Console Formatter

```
2023-05-10 12:34:56 - mcp_microservice - INFO - Log message
```

With color indication of the logging level:
- DEBUG - gray
- INFO - gray
- WARNING - yellow
- ERROR - red
- CRITICAL - bright red

### File Formatter

```
2023-05-10 12:34:56 - mcp_microservice - INFO - Log message
```

## Log Rotation

The logging system supports two types of log rotation:

### 1. Size-based Rotation

The log file is rotated when its size exceeds the specified `max_bytes` value.

Example configuration:
```json
"rotation": {
    "type": "size",
    "max_bytes": 10485760,
    "backup_count": 5
}
```

This configuration will create the following files:
```
app.log
app.log.1
app.log.2
app.log.3
app.log.4
app.log.5
```

### 2. Time-based Rotation

The log file is rotated at specified time intervals.

Example configuration:
```json
"rotation": {
    "type": "time",
    "when": "D",
    "interval": 1,
    "backup_count": 7
}
```

This configuration will create the following files:
```
app.log
app.log.2023-05-09
app.log.2023-05-08
app.log.2023-05-07
app.log.2023-05-06
app.log.2023-05-05
app.log.2023-05-04
app.log.2023-05-03
```

## Logging Levels

The system supports standard logging levels:

- **DEBUG** - Detailed information for debugging
- **INFO** - General information about application operation
- **WARNING** - Warning messages about potential issues
- **ERROR** - Error messages about problems that occurred
- **CRITICAL** - Critical errors that may cause application failure

### Special Logging Rules

#### OpenAPI Schema Requests

Requests to `/openapi.json` are automatically logged at **DEBUG** level instead of **INFO** to reduce log noise:

```
# Before (INFO level - noisy)
2025-08-12 20:15:17 [    INFO] Request started: GET http://192.168.252.17:8060/openapi.json | Client: 192.168.252.17

# After (DEBUG level - quiet)
2025-08-12 20:15:17 [   DEBUG] Request started: GET http://192.168.252.17:8060/openapi.json | Client: 192.168.252.17
```

This applies to:
- Request start logging
- Request completion logging  
- Request error logging

To see these logs, set the logging level to DEBUG:

```json
{
    "logging": {
        "level": "DEBUG"
    }
}
```

## Context Logging

Context logging is used to associate logs with a specific request. Each request receives a unique identifier (`request_id`) that is added to log messages.

### RequestLogger Class

The `RequestLogger` class provides context logging for requests:

```python
from mcp_proxy_adapter.core.logging import RequestLogger

# Create logger for request
request_id = "unique-request-id"
logger = RequestLogger("module_name", request_id)

# Logging with context
logger.info("Request processing started")
logger.debug("Request details")
logger.error("Request processing error")
```

Format of context logging messages:
```
2023-05-10 12:34:56 - module_name - INFO - [unique-request-id] Request processing started
```

## Usage in Code

### Basic Logging

```python
from mcp_proxy_adapter.core.logging import logger, get_logger

# Using global logger
logger.info("Service started")

# Creating module logger
module_logger = get_logger(__name__)
module_logger.debug("Detailed information")
```

### Context Logging for Requests

```python
from mcp_proxy_adapter.core.logging import RequestLogger

# In request handler
async def handle_request(request):
    request_id = getattr(request.state, "request_id", None)
    req_logger = RequestLogger("api.handler", request_id)
    
    req_logger.info("Request received")
    # Request processing
    req_logger.info("Request processed successfully")
```

### Exception Logging

```python
try:
    # Code that may raise an exception
    result = process_data()
except Exception as e:
    # Logging exception with stack trace
    logger.exception("Error processing data")
    # or with context logger
    req_logger.exception("Error processing data")
```

## Examples

### Application Startup Log Example

```
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Initializing logging configuration
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log level: DEBUG
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log file: logs/app.log
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log rotation type: size
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log rotation: when size reaches 10.0 MB
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log backups: 5
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Starting server on 0.0.0.0:8000
2023-05-10 12:00:01 - mcp_microservice - INFO - Application started with 5 commands registered
```

### Request Processing Log Example

```
2023-05-10 12:01:00 - mcp_microservice.api.middleware - INFO - [bc1e3d4a] Request started: POST /api/jsonrpc | Client: 127.0.0.1
2023-05-10 12:01:00 - mcp_microservice.api.handlers - INFO - [bc1e3d4a] Executing JSON-RPC method: hello_world
2023-05-10 12:01:00 - mcp_microservice.api.handlers - INFO - [bc1e3d4a] Command 'hello_world' executed in 0.015 sec
2023-05-10 12:01:00 - mcp_microservice.api.middleware - INFO - [bc1e3d4a] Request completed: POST /api/jsonrpc | Status: 200 | Time: 0.020s
```

### Error Log Example

```
2023-05-10 12:02:00 - mcp_microservice.api.middleware - INFO - [cd2f4e5b] Request started: POST /api/jsonrpc | Client: 127.0.0.1
2023-05-10 12:02:00 - mcp_microservice.api.handlers - INFO - [cd2f4e5b] Executing JSON-RPC method: unknown_command
2023-05-10 12:02:00 - mcp_microservice.api.handlers - WARNING - [cd2f4e5b] Method not found: unknown_command
2023-05-10 12:02:00 - mcp_microservice.api.middleware - INFO - [cd2f4e5b] Request completed: POST /api/jsonrpc | Status: 200 | Time: 0.005s
``` 