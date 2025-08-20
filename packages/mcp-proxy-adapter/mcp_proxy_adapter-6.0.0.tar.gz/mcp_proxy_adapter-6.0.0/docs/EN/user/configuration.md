# Configuration

This guide describes how to configure the MCP Proxy service.

## Configuration File

The MCP Proxy service is configured using a JSON configuration file. By default, it looks for a file named `config.json` in the current directory.

You can specify a different configuration file using the `--config` command-line option:

```bash
mcp-proxy --config /path/to/config.json
```

## Configuration Options

The configuration is organized into sections. Here are the available options:

### Server Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| server.host | string | "0.0.0.0" | The host to bind the service to |
| server.port | number | 8000 | The port to listen on |
| server.debug | boolean | false | Enable debug mode |
| server.log_level | string | "INFO" | The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

### Logging Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| logging.level | string | "INFO" | The logging level |
| logging.log_dir | string | "./logs" | Directory for log files |
| logging.log_file | string | "mcp_proxy_adapter.log" | Main log file name |
| logging.error_log_file | string | "mcp_proxy_adapter_error.log" | Error log file name |
| logging.access_log_file | string | "mcp_proxy_adapter_access.log" | Access log file name |
| logging.max_file_size | string | "10MB" | Maximum log file size |
| logging.backup_count | number | 5 | Number of backup log files |
| logging.console_output | boolean | true | Enable console logging |
| logging.file_output | boolean | true | Enable file logging |

### Commands Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| commands.auto_discovery | boolean | true | Enable automatic command discovery |
| commands.discovery_path | string | "mcp_proxy_adapter.commands" | **Path to package with commands** |
| commands.custom_commands_path | string | null | Path to custom commands (deprecated) |

**Important**: The `commands.discovery_path` parameter specifies the Python package path where your commands are located. For example:
- `"mcp_proxy_adapter.commands"` - built-in commands
- `"myproject.commands"` - your project's commands
- `"custom_commands.commands"` - custom commands package

## Example Configuration

Here's an example configuration file:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "log_level": "INFO"
  },
  "logging": {
    "level": "INFO",
    "log_dir": "./logs",
    "log_file": "mcp_proxy_adapter.log",
    "error_log_file": "mcp_proxy_adapter_error.log",
    "access_log_file": "mcp_proxy_adapter_access.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "console_output": true,
    "file_output": true
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "mcp_proxy_adapter.commands",
    "custom_commands_path": null
  }
}
```

### Example with Custom Commands

If you have your own commands in a package called `myproject.commands`:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8001,
    "debug": true,
    "log_level": "DEBUG"
  },
  "logging": {
    "level": "DEBUG",
    "log_dir": "./logs",
    "log_file": "myproject.log"
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "myproject.commands"
  }
}
```

## Environment Variables

You can also configure the service using environment variables. Environment variables take precedence over the configuration file.

The environment variable format is `MCP_UPPERCASE_OPTION_NAME`. For example, to set the port:

```bash
export MCP_PORT=8000
```

## Testing the Configuration

To verify your configuration, you can run the service with the `--validate-config` option:

```bash
mcp-proxy --config /path/to/config.json --validate-config
```

This will validate the configuration file and exit without starting the service. 