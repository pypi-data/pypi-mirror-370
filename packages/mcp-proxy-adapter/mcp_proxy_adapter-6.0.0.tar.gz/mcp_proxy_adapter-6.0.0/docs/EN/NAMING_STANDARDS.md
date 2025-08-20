# File Naming and Location Standards

## Project Structure

```
mcp_microservice/
├── __init__.py
├── api/                    # API interfaces
│   ├── __init__.py
│   ├── rest/              # REST API endpoints
│   └── jsonrpc/           # JSON-RPC handlers
├── commands/              # Commands
│   ├── __init__.py
│   └── {command_name}_command.py
├── core/                  # System core
│   ├── __init__.py
│   ├── registry.py       # Command registry
│   ├── errors.py         # Error handling
│   └── types.py          # Base types
├── models/               # Data models
│   ├── __init__.py
│   └── results.py        # Base result classes
└── utils/               # Helper functions
    └── __init__.py

tests/
├── __init__.py
├── conftest.py
└── commands/            # Command tests
    └── test_{command_name}_command.py

docs/
├── EN/                 # English documentation
└── RU/                # Russian documentation
    ├── commands/       # Command documentation
    │   └── {command_name}_command.md
    └── api/            # API documentation
```

## Naming Standards

### 1. Python Files

#### Commands
- Format: `{command_name}_command.py`
- Examples:
  ```
  get_status_command.py
  create_user_command.py
  delete_file_command.py
  ```

#### Tests
- Format: `test_{module_name}.py`
- Examples:
  ```
  test_get_status_command.py
  test_registry.py
  test_errors.py
  ```

#### Modules
- Singular nouns
- Lowercase
- Underscore separator `_`
- Examples:
  ```
  registry.py
  error_handler.py
  type_converter.py
  ```

### 2. Python Classes

#### Command Results
- Format: `{CommandName}Result`
- PascalCase
- Examples:
  ```python
  class GetStatusResult(CommandResult):
  class CreateUserResult(CommandResult):
  class DeleteFileResult(CommandResult):
  ```

#### Exceptions
- Suffix `Error`
- PascalCase
- Examples:
  ```python
  class ValidationError(Exception):
  class CommandNotFoundError(Exception):
  class ExecutionError(Exception):
  ```

### 3. Methods and Functions

#### Commands
- Format: `{command_name}`
- snake_case
- Verb + noun
- Examples:
  ```python
  async def get_status():
  async def create_user():
  async def delete_file():
  ```

#### Internal Methods
- Prefix `_` for protected
- Prefix `__` for private
- snake_case
- Examples:
  ```python
  def _validate_input():
  def __prepare_context():
  ```

### 4. Documentation

#### Documentation Files
- Format: `{TOPIC_NAME}.md`
- UPPER_CASE
- Examples:
  ```
  API_REFERENCE.md
  COMMAND_GUIDE.md
  ERROR_CODES.md
  ```

#### Command Documentation
- Format: `{command_name}_command.md`
- snake_case
- Examples:
  ```
  get_status_command.md
  create_user_command.md
  ```

## Code File Structure Rules

### 1. Command File
```python
"""Module description"""

# Standard library imports
import datetime
import uuid

# Third-party imports
from pydantic import BaseModel

# Project imports
from mcp_proxy_adapter.core import CommandResult
from mcp_proxy_adapter.registry import registry

# Types and constants
TIMEOUT = 30
MAX_RETRIES = 3

# Result class
@dataclass
class CommandResult:
    pass

# Helper functions
def _helper_function():
    pass

# Command
@registry.command
async def command_name():
    pass
```

### 2. Test File
```python
"""Tests for module"""

# Imports
import pytest

# Fixtures
@pytest.fixture
def fixture_name():
    pass

# Success scenario tests
def test_success_case():
    pass

# Error tests
def test_error_case():
    pass
```

## Recommendations

1. **Variable Naming**
   - Use nouns
   - Avoid abbreviations
   - Use typing

2. **Documentation**
   - Docstring for all public elements
   - Usage examples
   - Parameter and return value descriptions

3. **Import Organization**
   - Group by type
   - Sort alphabetically
   - Empty line between groups

4. **Typing**
   - Type annotations for all parameters
   - Return value annotations
   - Use typing for complex types 