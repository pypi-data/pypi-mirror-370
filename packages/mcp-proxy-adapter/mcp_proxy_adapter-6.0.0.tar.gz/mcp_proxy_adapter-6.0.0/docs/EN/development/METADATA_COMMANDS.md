# Command Metadata

The command metadata system provides a unified mechanism for obtaining structured information about commands, their parameters, results, and usage examples.

## Contents

1. [Overview](#overview)
2. [Metadata Structure](#metadata-structure)
3. [Retrieving Metadata](#retrieving-metadata)
4. [Example Generation](#example-generation)
5. [Usage in the help Command](#usage-in-the-help-command)
6. [Extending Metadata](#extending-metadata)

## Overview

Command metadata allows unified access to information about available microservice commands for:

- Auto-documenting API
- Generating client libraries
- Building interactive interfaces
- Improving user experience when using the API

## Metadata Structure

Command metadata is a dictionary with the following keys:

```python
{
    "name": "command_name",
    "summary": "Brief command description",
    "description": "Full command description...",
    "params": {
        "parameter_name": {
            "name": "parameter_name",
            "required": True/False,
            "type": "parameter_type",
            "default": "default_value"  # if available
        },
        # other parameters
    },
    "examples": [
        {
            "command": "command_name",
            "params": {"parameter": "value"},
            "description": "Example description"
        },
        # other examples
    ],
    "schema": { /* Command JSON-schema */ },
    "result_schema": { /* Result JSON-schema */ },
    "result_class": "ResultClassName"
}
```

## Retrieving Metadata

The base `Command` class provides two methods for retrieving metadata:

### Getting metadata for a single command

```python
# Via command class
metadata = SomeCommand.get_metadata()

# Via command registry
metadata = registry.get_command_metadata("command_name")
```

### Getting metadata for all commands

```python
# Get metadata for all commands
all_metadata = registry.get_all_metadata()
```

## Example Generation

The system automatically generates command usage examples based on parameters:

1. Example without parameters (if all parameters are optional)
2. Example with required parameters
3. Example with all parameters (required and optional)

Values for examples are generated based on parameter type:
- `str` → `"example_param_name"`
- `int` → `123`
- `float` → `123.45`
- `bool` → `True`

## Usage in the help Command

The `help` command uses metadata to provide information about available commands:

```bash
# Get a list of all commands
{"command": "help"}

# Get information about a specific command
{"command": "help", "params": {"cmdname": "command_name"}}
```

The help command result contains:

1. When requested without parameters:
   - Information about the microservice
   - List of all available commands with brief descriptions
   - Examples of help command usage

2. When requested with the cmdname parameter:
   - Full command description
   - List of parameters with types and required flags
   - Command usage examples

## Extending Metadata

To extend metadata in specific commands, you can override the `get_metadata()` method:

```python
@classmethod
def get_metadata(cls) -> Dict[str, Any]:
    # Get base metadata
    metadata = super().get_metadata()
    
    # Extend metadata
    metadata["category"] = "system"
    metadata["permissions"] = ["admin"]
    
    return metadata
```

### Custom Examples

To provide special examples, you can override the `_generate_examples()` method:

```python
@classmethod
def _generate_examples(cls, params: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Get standard examples
    examples = super()._generate_examples(params)
    
    # Add custom example
    examples.append({
        "command": cls.name,
        "params": {"special_param": "special_value"},
        "description": "Special usage example"
    })
    
    return examples
``` 