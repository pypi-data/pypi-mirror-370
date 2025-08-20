# Dependency Management System

## Overview

The MCP Proxy Adapter includes a comprehensive dependency management system that automatically handles plugin dependencies during the remote command loading process. This system ensures that all required dependencies are available before a plugin is loaded and executed.

## Features

- **Automatic dependency detection**: Checks if required dependencies are already installed
- **Automatic installation**: Installs missing dependencies using pip
- **Dependency verification**: Verifies that installed dependencies are properly importable
- **Configurable behavior**: Can be enabled/disabled through configuration
- **Error handling**: Provides clear error messages when dependencies cannot be installed

## How It Works

### 1. Dependency Declaration

Dependencies are declared in the plugin catalog using the `depends` field:

```json
{
  "test_command": {
    "plugin": "test_command.py",
    "descr": "Command for testing purposes",
    "version": "0.1",
    "depends": ["os", "requests", "numpy"]
  }
}
```

### 2. Dependency Checking

When a plugin is being loaded, the system:

1. **Checks existing dependencies**: Verifies if dependencies are already installed and importable
2. **Identifies missing dependencies**: Determines which dependencies need to be installed
3. **Attempts installation**: Uses pip to install missing dependencies
4. **Verifies installation**: Confirms that all dependencies are properly installed

### 3. Installation Process

The dependency installation process:

```python
# Check current dependencies
all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies(deps)

if not all_satisfied:
    # Install missing dependencies
    success, installed_deps, failed_deps = dependency_manager.install_dependencies(missing_deps)
    
    if success:
        # Verify installation
        all_verified, failed_verifications = dependency_manager.verify_installation(deps)
```

## Configuration

### Auto-Install Setting

Control automatic dependency installation through configuration:

```json
{
  "commands": {
    "auto_install_dependencies": true
  }
}
```

- `true`: Automatically install missing dependencies (default)
- `false`: Only check dependencies, don't install automatically

### Environment Variable

You can also control this via environment variable:

```bash
export SERVICE_COMMANDS_AUTO_INSTALL_DEPENDENCIES=false
```

## Usage Examples

### Basic Dependency Declaration

```json
{
  "calculator": {
    "plugin": "calculator_command.py",
    "descr": "Advanced calculator with scientific functions",
    "version": "2.1.0",
    "depends": ["math", "numpy", "scipy"]
  }
}
```

### Single Dependency

```json
{
  "simple_command": {
    "plugin": "simple_command.py",
    "descr": "Simple command",
    "version": "1.0.0",
    "depends": "requests"
  }
}
```

### No Dependencies

```json
{
  "basic_command": {
    "plugin": "basic_command.py",
    "descr": "Basic command without dependencies",
    "version": "1.0.0"
  }
}
```

## Error Handling

### Missing Dependencies

When dependencies cannot be installed:

```
ERROR: Failed to install dependencies for test_command: ['nonexistent_package']
ERROR: Please install manually: pip install nonexistent_package
```

### Installation Failures

Common reasons for installation failures:

- **Network issues**: No internet connection
- **Permission issues**: Insufficient permissions to install packages
- **Package not found**: Package doesn't exist on PyPI
- **Version conflicts**: Incompatible package versions

### Manual Installation

When auto-install fails, you can install dependencies manually:

```bash
pip install package_name
```

## API Reference

### DependencyManager

The main class for managing dependencies:

```python
from mcp_proxy_adapter.commands.dependency_manager import dependency_manager

# Check dependencies
all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies(["requests", "numpy"])

# Install dependencies
success, installed_deps, failed_deps = dependency_manager.install_dependencies(["requests"])

# Verify installation
all_verified, failed_verifications = dependency_manager.verify_installation(["requests"])

# Get dependency info
info = dependency_manager.get_dependency_info("requests")
```

### Methods

#### `check_dependencies(dependencies: List[str]) -> Tuple[bool, List[str], List[str]]`

Check if dependencies are satisfied.

**Parameters:**
- `dependencies`: List of dependency names

**Returns:**
- `all_satisfied`: True if all dependencies are satisfied
- `missing_deps`: List of missing dependencies
- `installed_deps`: List of already installed dependencies

#### `install_dependencies(dependencies: List[str], user_install: bool = False) -> Tuple[bool, List[str], List[str]]`

Install dependencies using pip.

**Parameters:**
- `dependencies`: List of dependency names to install
- `user_install`: Whether to install for current user only

**Returns:**
- `success`: True if all dependencies were installed successfully
- `installed_deps`: List of successfully installed dependencies
- `failed_deps`: List of dependencies that failed to install

#### `verify_installation(dependencies: List[str]) -> Tuple[bool, List[str]]`

Verify that dependencies are properly installed.

**Parameters:**
- `dependencies`: List of dependencies to verify

**Returns:**
- `all_verified`: True if all dependencies are verified
- `failed_verifications`: List of dependencies that failed verification

#### `get_dependency_info(dependency: str) -> Dict[str, Any]`

Get information about a dependency.

**Parameters:**
- `dependency`: Dependency name

**Returns:**
- Dictionary with dependency information (installed, version, importable)

## Security Considerations

### Package Sources

- Dependencies are installed from PyPI by default
- No custom package sources are supported
- All packages are subject to PyPI's security policies

### Installation Permissions

- Dependencies are installed in the current Python environment
- Consider using virtual environments for isolation
- System-wide installation may require elevated permissions

### Package Validation

- The system validates that installed packages are importable
- No additional security scanning is performed
- Users should review dependencies before enabling auto-install

## Best Practices

### Dependency Specification

1. **Use specific versions** when possible:
   ```json
   "depends": ["requests>=2.25.0", "numpy==1.21.0"]
   ```

2. **Minimize dependencies**: Only include essential packages

3. **Document dependencies**: Provide clear descriptions of why each dependency is needed

### Configuration

1. **Enable auto-install in development**: Faster iteration
2. **Disable auto-install in production**: More control over package versions
3. **Use virtual environments**: Isolate plugin dependencies

### Error Handling

1. **Monitor installation logs**: Check for failed installations
2. **Provide fallback options**: Manual installation instructions
3. **Test dependencies**: Verify compatibility before deployment

## Troubleshooting

### Common Issues

1. **ImportError after installation**: Package may be installed but not importable
2. **Version conflicts**: Multiple packages requiring different versions
3. **Permission denied**: Insufficient permissions for package installation

### Debugging

Enable debug logging to see detailed dependency information:

```python
import logging
logging.getLogger('mcp_proxy_adapter').setLevel(logging.DEBUG)
```

### Manual Verification

Check dependency status manually:

```python
from mcp_proxy_adapter.commands.dependency_manager import dependency_manager

# Check specific dependency
info = dependency_manager.get_dependency_info("requests")
print(f"Requests info: {info}")

# List all installed packages
packages = dependency_manager.list_installed_dependencies()
print(f"Installed packages: {packages}")
``` 