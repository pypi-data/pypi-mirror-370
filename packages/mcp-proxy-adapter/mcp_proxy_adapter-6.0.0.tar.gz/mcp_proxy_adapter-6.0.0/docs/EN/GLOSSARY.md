# MCP Microservice Glossary

**Contents**: 1. Core Concepts • 2. Architecture • 3. Command Components • 4. Documentation Standards

## 1. Core Concepts

### Command
A discrete unit of functionality that performs a specific task and returns a standardized result. In MCP, commands are implemented as Python functions with the `@registry.command` decorator.

### Command Registry
The central system that manages command registration, discovery, and metadata. Provides interfaces for executing commands through JSON-RPC and REST API endpoints.

### JSON-RPC
The primary protocol used for command execution in MCP. Allows for method invocation with named parameters and standardized error handling.

## 2. Architecture

### Microservice
A self-contained service that implements a specific set of related functions and can be deployed independently.

### MCP Adapter
The component that translates between external systems and MCP microservices, providing standardized communication channels.

### Proxy
An intermediary component that routes requests to appropriate handlers and may perform additional tasks like authentication, logging, and request transformation.

## 3. Command Components

### CommandResult
The base class for all command result objects. Provides serialization methods like `to_dict()` and schema generation through `get_schema()`.

### Result Class
A dataclass that inherits from CommandResult and defines the structure of a command's return value.

### Command Function
An async function decorated with `@registry.command` that implements the business logic of a command.

### Parameter Validation
The process of checking command inputs against defined schemas before execution.

## 4. Documentation Standards

### Bilingual Documentation
The requirement to maintain all documentation in both English and Russian with identical structure and content.

### Command Documentation
Markdown files describing commands, their parameters, return values, and usage examples.

### Code Block
A section of documentation that contains code examples, marked with triple backticks and language identifier (```python, ```json).

### Schema
JSON structure that defines the expected format of command parameters and results, used for validation and API documentation generation. 