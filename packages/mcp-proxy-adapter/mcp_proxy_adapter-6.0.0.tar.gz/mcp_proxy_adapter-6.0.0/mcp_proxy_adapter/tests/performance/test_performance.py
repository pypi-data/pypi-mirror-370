"""
Performance tests for the API.
"""

import asyncio
import time
from typing import Dict, Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.tests.stubs.echo_command import EchoCommand


@pytest_asyncio.fixture
async def async_client(test_config):
    """
    Fixture for async HTTP client.
    
    Args:
        test_config: Test configuration instance.
        
    Returns:
        AsyncClient instance for making async requests.
    """
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def register_echo_command(clean_registry):
    """
    Fixture to register the Echo command for testing.
    
    Args:
        clean_registry: Fixture to clean registry before and after test.
    """
    registry.register(EchoCommand)
    yield
    registry.clear()


@pytest.mark.performance
@pytest.mark.asyncio
async def test_sequential_requests(async_client: AsyncClient, json_rpc_request: Dict[str, Any], 
                                   register_echo_command):
    """
    Test sequential API requests performance.
    
    Args:
        async_client: Async HTTP client.
        json_rpc_request: Base JSON-RPC request.
        register_echo_command: Fixture to register test command.
    """
    num_requests = 50
    
    # Create JSON-RPC request
    request_data = json_rpc_request.copy()
    request_data["method"] = "echo"
    request_data["params"] = {"test": "value"}
    
    # Measure execution time
    start_time = time.time()
    
    for i in range(num_requests):
        response = await async_client.post("/api/jsonrpc", json=request_data)
        assert response.status_code == 200
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate requests per second
    rps = num_requests / total_time
    
    print(f"Sequential requests: {num_requests} requests in {total_time:.2f}s ({rps:.2f} req/s)")
    
    # Check that performance is within expected range
    # This threshold should be adjusted based on actual performance measurements
    assert rps > 30, f"Performance too low: {rps:.2f} req/s"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_requests(async_client: AsyncClient, json_rpc_request: Dict[str, Any],
                                  register_echo_command):
    """
    Test concurrent API requests performance.
    
    Args:
        async_client: Async HTTP client.
        json_rpc_request: Base JSON-RPC request.
        register_echo_command: Fixture to register test command.
    """
    num_requests = 50
    
    # Create JSON-RPC request
    request_data = json_rpc_request.copy()
    request_data["method"] = "echo"
    request_data["params"] = {"test": "value"}
    
    # Create task list
    tasks = []
    for i in range(num_requests):
        task = asyncio.create_task(async_client.post("/api/jsonrpc", json=request_data))
        tasks.append(task)
    
    # Measure execution time
    start_time = time.time()
    
    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Check that all responses are successful
    for response in responses:
        assert response.status_code == 200
    
    # Calculate requests per second
    rps = num_requests / total_time
    
    print(f"Concurrent requests: {num_requests} requests in {total_time:.2f}s ({rps:.2f} req/s)")
    
    # Check that performance is within expected range
    # This threshold should be adjusted based on actual performance measurements
    assert rps > 100, f"Concurrent performance too low: {rps:.2f} req/s"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_batch_requests_performance(async_client: AsyncClient, json_rpc_request: Dict[str, Any],
                                         register_echo_command):
    """
    Test batch requests performance.
    
    Args:
        async_client: Async HTTP client.
        json_rpc_request: Base JSON-RPC request.
        register_echo_command: Fixture to register test command.
    """
    num_batches = 10
    batch_size = 5
    
    # Create base request
    base_request = json_rpc_request.copy()
    base_request["method"] = "echo"
    base_request["params"] = {"test": "value"}
    
    # Prepare batch requests
    batch_requests = []
    for i in range(num_batches):
        batch = []
        for j in range(batch_size):
            request = base_request.copy()
            request["id"] = f"batch-{i}-{j}"
            batch.append(request)
        batch_requests.append(batch)
    
    # Measure execution time
    start_time = time.time()
    
    # Execute batch requests
    for batch in batch_requests:
        response = await async_client.post("/api/jsonrpc", json=batch)
        assert response.status_code == 200
        
        # Check response structure
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == batch_size
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate total requests and requests per second
    total_requests = num_batches * batch_size
    rps = total_requests / total_time
    
    print(f"Batch requests: {total_requests} requests in {total_time:.2f}s ({rps:.2f} req/s)")
    
    # Check that performance is within expected range
    assert rps > 50, f"Batch performance too low: {rps:.2f} req/s" 