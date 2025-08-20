# Ideology and Architectural Principles of mcp_microservice

## Main Goal

mcp_microservice is designed to provide a reliable, standardized, and extensible mechanism for interacting with MCP Proxy. Its task is to automatically register commands and form a correct JSON schema for them that is understood by MCP Proxy. All work with commands is carried out through a single RPC endpoint `/cmd`.

## Key Principles

### 1. Single Entry Point (Single Endpoint)
- **Interaction with external systems occurs only through the `/cmd` endpoint** (JSON-RPC 2.0).
- All other endpoints (REST, auxiliary) are considered duplicative and should not be used for integration with MCP Proxy.

### 2. Automatic Command Registration
- **Commands are registered automatically**: the developer implements a handler function, and the system itself analyzes its signature, type annotations, and docstring.
- For each command, a detailed description of parameters, return value, and errors is formed.
- **Each parameter must be described in detail**: type, required status, description, possible values (enum), default values, etc.
- All information about commands is aggregated into a single structure (`commands_info`), which is used to generate the schema.

### 3. Automatic Schema Generation
- **The schema (OpenAPI/JSON Schema) is generated automatically** based on registered commands and their metadata.
- The schema fully complies with MCP Proxy requirements:
    - Describes all commands, parameters, types, constraints, return values, and possible errors.
    - Each parameter is necessarily provided with a detailed description.
    - The schema is available upon request (for example, via curl to port 8001).
- Example of a schema request:
    ```bash
    curl http://localhost:8001/openapi.json
    ```

### 4. Support for Standard Commands
- **Common commands (for example, `help`, `version`, `health`) must always be implemented**, even if they are not in the user code.
- mcp_microservice automatically adds such commands to the schema and implements their handlers by default.
- This ensures predictability and compatibility with the MCP Proxy infrastructure.

### 5. Extensibility and Strict Typing
- New commands are added simply — it is enough to implement a function with correct type annotation and docstring.
- All validation of parameters and results happens automatically.
- Errors in the command description (for example, missing parameter description) are detected at the schema generation stage.

### 6. Transparency and Documentation
- All logic of registration, analysis, and schema generation is as transparent and documented as possible.
- Code examples and documentation are always up-to-date and correspond to the actual behavior of the system.

---

## Example of Command Lifecycle

1. **Developer implements a handler function:**
    ```python
    async def add_note(text: str) -> dict:
        """
        Add a note.
        
        Args:
            text (str): Note text
        Returns:
            dict: Note object
        """
        ...
    ```
2. **Adapter automatically registers the command** and extracts all necessary information.
3. **A schema is generated**, where the `text` parameter will be described with type, required status, and description.
4. **MCP Proxy receives the schema** (for example, via curl) and uses it for validation and UI auto-generation.
5. **Command invocation** occurs through `/cmd` with parameters passed in JSON-RPC format.

---

## Requirements for Parameters and Schema
- Each parameter must have:
    - Type (string, integer, boolean, object, array, etc.)
    - Description
    - Required status
    - Default value (if applicable)
    - Possible values (enum, if applicable)
- The return value and possible errors must also be described.
- All this data goes into the final schema.

---

## Support for REST and RPC Endpoints

- The project supports the ability to query commands using both REST and RPC schema (JSON-RPC 2.0).
- Regardless of whether a REST endpoint or RPC endpoint is used, **the response is always returned strictly in JSON-RPC format**.
- The result of command execution must be absolutely identical for any method of access (REST or RPC).
- This ensures uniformity of integration and predictability of behavior for all MCP Proxy clients.

---

## Recommended Project Structure and Architectural Conventions

### 1. One Command — One File
- Each command is implemented in a separate file (for example, `add_note.py`, `delete_note.py`).
- This facilitates the support, testing, and extension of commands.

### 2. Separate File with Registry Class
- A separate file with a registry class (for example, `registry.py`) is used to register all commands.
- The registry is responsible for automatic search, registration, and analysis of commands.

### 3. Separate File with Manager
- The manager (for example, `manager.py`) uses the registry to execute commands and manage the application lifecycle.
- The manager encapsulates the logic of starting the server, integrating with FastAPI, and interacting with MCP Proxy.

### 4. Import of Dependencies
- Commands import the registry and necessary settings (including logger) from centralized modules.
- This ensures uniformity and code reuse.

### 5. Service Commands and Naming Rules
- Service analogues of common commands (for example, service `help`, `version`, `health`) should start with the symbol `_` (for example, `_help`).
- When publishing in OpenAPI and in the cmd endpoint, such commands are automatically substituted without the `_` prefix (for example, `_help` becomes available as `help`).
- This allows separating service implementations from user ones, but always providing a standard set of commands.

### 6. Server Readiness "Out of the Box"
- The project should be a ready server even without adding user commands.
- By default, the server provides:
    - A set of common OpenAPI endpoints (for example, `/openapi.json`, `/docs`, `/health`, `/version`, `/help`, etc.)
    - A single endpoint `/cmd` for executing commands via JSON-RPC
- This ensures instant integration with MCP Proxy and the ability to extend without additional configuration.

---

## Command Abstraction and Schema Formation

- The project architecture provides an abstraction layer for commands so that business logic is completely separated from the details of parameter retrieval and result formatting.
- For this, an abstract class `BaseCommand` is implemented, which defines mandatory methods:
    - `get_metadata()` — returns a description of the command, its parameters, types, required status, default values, etc.
    - (optionally) other methods for describing the return value and errors.
- Concrete commands inherit from `BaseCommand` and implement only business logic and parameter description.
- The code of the current project (mcp_microservice) provides:
    - Getting parameters from the request (REST/RPC)
    - Validation of types and required status
    - Formatting the result in JSON-RPC
    - Automatic schema generation based on metadata returned by `get_metadata()`
- In production projects, only subcommands and their business logic are added, and all infrastructure tasks (validation, schema, response format) remain on the mcp_microservice side.

---

## Summary

**mcp_microservice is a tool that provides automatic, strict, and transparent integration with MCP Proxy, minimizing manual work and errors, and guaranteeing compatibility and extensibility.** 