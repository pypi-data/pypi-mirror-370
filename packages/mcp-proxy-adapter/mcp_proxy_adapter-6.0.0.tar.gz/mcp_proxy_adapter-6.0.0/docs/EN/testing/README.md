# Testing MCP Proxy Adapter

This document describes the testing system for MCP Proxy Adapter.

## Overview

The testing system is based on the pytest framework and includes various types of tests:

1. **Unit tests** - test individual system components in isolation
2. **Integration tests** - test the interaction between components
3. **Functional tests** - test API endpoints and system functionality
4. **Performance tests** - verify the speed and efficiency of the system

## Test Structure

```
mcp_microservice/tests/
├── __init__.py
├── conftest.py             # Common fixtures for tests
├── unit/                   # Unit tests
│   ├── __init__.py
│   ├── test_base_command.py
│   └── test_config.py
├── integration/            # Integration tests
│   ├── __init__.py
│   └── test_integration.py
├── functional/             # Functional tests
│   ├── __init__.py
│   └── test_api.py
└── performance/            # Performance tests
    ├── __init__.py
    └── test_performance.py
```

## Running Tests

### Running All Tests

```bash
python -m pytest mcp_microservice/tests
```

### Running Specific Test Types

```bash
# Unit tests
python -m pytest mcp_microservice/tests/unit

# Integration tests
python -m pytest mcp_microservice/tests/integration

# Functional tests
python -m pytest mcp_microservice/tests/functional

# Performance tests
python -m pytest mcp_microservice/tests/performance
```

### Running Tests by Markers

```bash
# Unit tests
python -m pytest mcp_microservice/tests -m unit

# Integration tests
python -m pytest mcp_microservice/tests -m integration

# Functional tests
python -m pytest mcp_microservice/tests -m functional

# Performance tests
python -m pytest mcp_microservice/tests -m performance
```

### Running with Coverage Report

```bash
python -m pytest mcp_microservice/tests --cov=mcp_microservice
```

## Fixtures

Various fixtures defined in the `conftest.py` file are used for testing:

1. `test_config` - creates a test configuration
2. `test_client` - creates a test HTTP client for the API
3. `clean_registry` - clears the command registry before and after the test
4. `json_rpc_request` - creates a base JSON-RPC request
5. `async_client` - creates an asynchronous HTTP client for performance tests

## Creating New Tests

### Unit Tests

```python
import pytest

@pytest.mark.unit
def test_example():
    # Test code
    assert True
```

### Integration Tests

```python
import pytest

@pytest.mark.integration
def test_integration_example(clean_registry):
    # Test code
    assert True
```

### Functional Tests

```python
import pytest

@pytest.mark.functional
def test_api_example(test_client):
    # Test code
    response = test_client.get("/health")
    assert response.status_code == 200
```

### Performance Tests

```python
import pytest
import time

@pytest.mark.performance
@pytest.mark.asyncio
async def test_performance_example(async_client):
    # Test code
    start_time = time.time()
    # Perform operation
    end_time = time.time()
    total_time = end_time - start_time
    assert total_time < 1.0  # Performance check
```

## Continuous Integration (CI)

Tests are automatically run in GitHub Actions on each pull request and push to main branches.

The configuration file `.github/workflows/tests.yml` defines the following steps:

1. Running the linter (flake8)
2. Checking code formatting (black)
3. Running all types of tests
4. Measuring code test coverage
5. Uploading coverage report

## Best Practices

1. All tests should be independent and have no side effects
2. Use appropriate fixtures for setting up and cleaning the environment
3. Add appropriate markers to tests
4. Use separate tests for separate aspects of functionality
5. For API tests, use test_client, and for performance tests, use async_client
6. Remember to check success and failure scenarios

## Extending the Testing System

To add new types of tests:

1. Create a new directory in `mcp_microservice/tests/`
2. Add the corresponding marker in `pytest.ini`
3. Create fixtures in `conftest.py` if necessary
4. Add tests to the new directory with appropriate markers 