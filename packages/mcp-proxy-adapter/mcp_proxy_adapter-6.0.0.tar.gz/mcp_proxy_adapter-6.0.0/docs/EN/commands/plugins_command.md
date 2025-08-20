# Plugins Command

## Description

The `plugins` command reads and displays available plugins from a configured plugins server. This command fetches a JSON file from a plugins server URL that contains a list of available plugins with their metadata.

## Result

The command returns a `PluginsResult` object with the following structure:

```python
{
    "success": True,
    "plugins_server": "https://plugins.techsup.od.ua/plugins.json",
    "plugins": [
        {
            "name": "test_command",
            "description": "Test command for loadable commands testing",
            "url": "https://plugins.techsup.od.ua/test_command.py",
            "version": "1.0.0",
            "author": "MCP Proxy Team"
        }
    ],
    "total_plugins": 1
}
```

## Command

```python
class PluginsCommand(Command):
    name = "plugins"
    result_class = PluginsResult
    
    async def execute(self, **kwargs) -> PluginsResult:
        # Fetches plugins list from configured server
        # Returns PluginsResult with available plugins
```

## Implementation Details

The command works as follows:

1. **Configuration Check**: Reads the `plugins_server` URL from the configuration
2. **HTTP Request**: Fetches the JSON file from the plugins server
3. **JSON Parsing**: Parses the response to extract the plugins list
4. **Result Generation**: Returns a structured result with plugin metadata

The expected JSON structure from the plugins server:

```json
{
    "plugins": [
        {
            "name": "plugin_name",
            "description": "Plugin description",
            "url": "https://server.com/plugin.py",
            "version": "1.0.0",
            "author": "Author Name"
        }
    ]
}
```

## Usage Examples

### Python

```python
from mcp_proxy_adapter.commands.plugins_command import PluginsCommand

command = PluginsCommand()
result = await command.execute()

if result.data["success"]:
    print(f"Found {result.data['total_plugins']} plugins")
    for plugin in result.data["plugins"]:
        print(f"- {plugin['name']}: {plugin['description']}")
```

### HTTP REST

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "plugins"}'
```

### JSON-RPC

```json
{
    "jsonrpc": "2.0",
    "method": "plugins",
    "id": 1
}
```

## Error Handling

The command handles various error scenarios:

- **No Configuration**: Returns error if `plugins_server` URL is not configured
- **Network Errors**: Handles HTTP request failures
- **JSON Parsing Errors**: Handles malformed JSON responses
- **Missing Requests Library**: Graceful fallback if requests library is not available

## Configuration

Add the plugins server URL to your configuration:

```json
{
    "commands": {
        "plugins_server": "https://plugins.techsup.od.ua/plugins.json"
    }
}
```

## Use Cases

- **Plugin Discovery**: Find available plugins without manual browsing
- **Metadata Retrieval**: Get plugin information before loading
- **Plugin Management**: Build interfaces for plugin management
- **Version Checking**: Check plugin availability and versions 