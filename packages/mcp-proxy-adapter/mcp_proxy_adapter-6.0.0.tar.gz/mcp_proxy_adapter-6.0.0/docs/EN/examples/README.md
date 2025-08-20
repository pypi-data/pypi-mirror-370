# Examples Documentation

This directory contains documentation for example microservices built with MCP Microservice framework.

## Structure

Each example is documented in a separate file describing its architecture, purpose, and usage.

## Available Examples

- [Minimal Example](minimal_example.md) - A minimal microservice with a single command
- [Basic Example](basic_example.md) - A basic microservice with multiple commands in separate files
- [Complete Example](complete_example.md) - A complete microservice with Docker support
- [Anti-Patterns](anti_patterns.md) - Examples of anti-patterns and bad practices to avoid

## How to Run Examples

All examples are included in the package as part of the codebase. You can import and use them directly:

```python
import examples.minimal_example
import examples.basic_example
import examples.complete_example
```

Or run the example servers directly:

```bash
# Run minimal example
python -m examples.minimal_example.simple_server

# Run basic example
python -m examples.basic_example.server

# Run complete example
python -m examples.complete_example.server
``` 