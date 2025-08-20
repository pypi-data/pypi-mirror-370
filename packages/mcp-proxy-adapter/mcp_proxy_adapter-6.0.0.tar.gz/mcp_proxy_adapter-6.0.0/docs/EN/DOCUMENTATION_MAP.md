# Documentation Map

**Contents**: 1. Overview • 2. Required Files • 3. Documentation Navigator • 4. Search Index

## 1. Overview

This document provides a navigational overview of all available documentation for the MCP Microservice project.
It serves as a centralized documentation map for the MCP Microservice. It provides links to key documentation files and helps navigate the documentation structure.

## 2. Required Files

The following files must exist in both language versions:

### 2.1. Core Documentation

| Documentation | English | Russian |
|---------------|---------|---------|
| Project Rules | [PROJECT_RULES.md](./PROJECT_RULES.md) | [PROJECT_RULES.md](../RU/PROJECT_RULES.md) |
| Naming Standards | [NAMING_STANDARDS.md](./NAMING_STANDARDS.md) | [NAMING_STANDARDS.md](../RU/NAMING_STANDARDS.md) |
| Project Architecture | [BASIC_ARCHITECTURE.md](./BASIC_ARCHITECTURE.md) | [BASIC_ARCHITECTURE.md](../RU/BASIC_ARCHITECTURE.md) |
| Project Structure | [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | [PROJECT_STRUCTURE.md](../RU/PROJECT_STRUCTURE.md) |
| Project Ideology | [PROJECT_IDEOLOGY.md](./PROJECT_IDEOLOGY.md) | [PROJECT_IDEOLOGY.md](../RU/PROJECT_IDEOLOGY.md) |
| API Schema | [API_SCHEMA.md](./API_SCHEMA.md) | [API_SCHEMA.md](../RU/API_SCHEMA.md) |
| Documentation Standards | [DOCUMENTATION_STANDARDS.md](./DOCUMENTATION_STANDARDS.md) | [DOCUMENTATION_STANDARDS.md](../RU/DOCUMENTATION_STANDARDS.md) |
| Command Template | [COMMAND_TEMPLATE.md](./COMMAND_TEMPLATE.md) | [COMMAND_TEMPLATE.md](../RU/COMMAND_TEMPLATE.md) |
| Command Checklist | [COMMAND_CHECKLIST.md](./COMMAND_CHECKLIST.md) | [COMMAND_CHECKLIST.md](../RU/COMMAND_CHECKLIST.md) |
| Logging | [LOGGING_SYSTEM.md](./LOGGING_SYSTEM.md) | [LOGGING_SYSTEM.md](../RU/LOGGING_SYSTEM.md) |
| Error Handling | [ERROR_HANDLING.md](./ERROR_HANDLING.md) | [ERROR_HANDLING.md](../RU/ERROR_HANDLING.md) |
| Command Results | [COMMAND_RESULTS.md](./COMMAND_RESULTS.md) | [COMMAND_RESULTS.md](../RU/COMMAND_RESULTS.md) |
| Configuration Principles | [CONFIGURATION_PRINCIPLES.md](./CONFIGURATION_PRINCIPLES.md) | [CONFIGURATION_PRINCIPLES.md](../RU/CONFIGURATION_PRINCIPLES.md) |
| Project Extension | [PROJECT_EXTENSION_GUIDE.md](./PROJECT_EXTENSION_GUIDE.md) | [PROJECT_EXTENSION_GUIDE.md](../RU/PROJECT_EXTENSION_GUIDE.md) |
| Publishing to PyPI | [PUBLISHING_TO_PYPI.md](./PUBLISHING_TO_PYPI.md) | [PUBLISHING_TO_PYPI.md](../RU/PUBLISHING_TO_PYPI.md) |
| Automated Publishing | [AUTOMATED_PUBLISHING.md](./AUTOMATED_PUBLISHING.md) | [AUTOMATED_PUBLISHING.md](../RU/AUTOMATED_PUBLISHING.md) |

### 2.2. Command Documentation

| Command | English | Russian |
|---------|---------|---------|
| get_date | [get_date_command.md](./commands/get_date_command.md) | [get_date_command.md](../RU/commands/get_date_command.md) |
| new_uuid4 | [new_uuid4_command.md](./commands/new_uuid4_command.md) | [new_uuid4_command.md](../RU/commands/new_uuid4_command.md) |

## 3. Documentation Navigator

### 3.1. For Developers

- **New to the project?** Start with [PROJECT_RULES.md](./PROJECT_RULES.md)
- **Adding a command?** Follow the [COMMAND_CHECKLIST.md](./COMMAND_CHECKLIST.md) and use [COMMAND_TEMPLATE.md](./COMMAND_TEMPLATE.md)
- **Naming conventions?** See [NAMING_STANDARDS.md](./NAMING_STANDARDS.md)
- **Documentation guide?** Read [DOCUMENTATION_STANDARDS.md](./DOCUMENTATION_STANDARDS.md)
- **Terminology reference?** Check [GLOSSARY.md](./GLOSSARY.md)
- **Configuration setup?** See [CONFIGURATION_PRINCIPLES.md](./CONFIGURATION_PRINCIPLES.md)
- **Extending the project?** Follow [PROJECT_EXTENSION_GUIDE.md](./PROJECT_EXTENSION_GUIDE.md)
- **Error handling?** Study [ERROR_HANDLING.md](./ERROR_HANDLING.md)
- **Package publication?** Follow [PUBLISHING_TO_PYPI.md](./PUBLISHING_TO_PYPI.md)

### 3.2. For Contributors

- **Command implementation checklist** - [COMMAND_CHECKLIST.md](./COMMAND_CHECKLIST.md)
- **Documentation requirements** - [DOCUMENTATION_STANDARDS.md](./DOCUMENTATION_STANDARDS.md)
- **Naming conventions** - [NAMING_STANDARDS.md](./NAMING_STANDARDS.md)
- **Configuration guide** - [CONFIGURATION_PRINCIPLES.md](./CONFIGURATION_PRINCIPLES.md)
- **Project extension steps** - [PROJECT_EXTENSION_GUIDE.md](./PROJECT_EXTENSION_GUIDE.md)
- **Error handling guide** - [ERROR_HANDLING.md](./ERROR_HANDLING.md)
- **Publication guide** - [PUBLISHING_TO_PYPI.md](./PUBLISHING_TO_PYPI.md)

### 3.3. For API Users

- **Available commands** - Browse the [commands directory](./commands/)
- **Command usage examples** - Each command's documentation includes examples in Python, JSON-RPC, and HTTP REST
- **Error handling** - See [ERROR_HANDLING.md](./ERROR_HANDLING.md) and section 6 in each command's documentation
- **Service configuration** - [CONFIGURATION_PRINCIPLES.md](./CONFIGURATION_PRINCIPLES.md)

## 4. Search Index

### 4.1. By Topic

- **Commands** - [Command Template](./COMMAND_TEMPLATE.md), [Command Checklist](./COMMAND_CHECKLIST.md)
- **Standards** - [Naming Standards](./NAMING_STANDARDS.md), [Documentation Standards](./DOCUMENTATION_STANDARDS.md)
- **Project Information** - [Project Rules](./PROJECT_RULES.md)
- **Reference** - [Glossary](./GLOSSARY.md)
- **Configuration** - [Configuration Principles](./CONFIGURATION_PRINCIPLES.md)
- **Development** - [Project Extension Guide](./PROJECT_EXTENSION_GUIDE.md)
- **Errors and Exceptions** - [Error Handling](./ERROR_HANDLING.md)
- **Publication** - [Publishing to PyPI](./PUBLISHING_TO_PYPI.md)

### 4.2. By Role

- **Developer** - [Command Checklist](./COMMAND_CHECKLIST.md), [Naming Standards](./NAMING_STANDARDS.md), [Configuration Principles](./CONFIGURATION_PRINCIPLES.md), [Project Extension Guide](./PROJECT_EXTENSION_GUIDE.md), [Error Handling](./ERROR_HANDLING.md), [Publishing to PyPI](./PUBLISHING_TO_PYPI.md)
- **Technical Writer** - [Documentation Standards](./DOCUMENTATION_STANDARDS.md), [Command Template](./COMMAND_TEMPLATE.md)
- **Project Manager** - [Project Rules](./PROJECT_RULES.md)
- **API Consumer** - Command documentation in the [commands directory](./commands/), [Error Handling](./ERROR_HANDLING.md)
- **System Administrator** - [Configuration Principles](./CONFIGURATION_PRINCIPLES.md), [Project Extension Guide](./PROJECT_EXTENSION_GUIDE.md), [Publishing to PyPI](./PUBLISHING_TO_PYPI.md) 