"""tests/api/test_rate_limit.py
Unit tests for RateLimitMiddleware.
"""

import asyncio
import time
import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request
from starlette.responses import Response, JSONResponse

from mcp_proxy_adapter.api.middleware.rate_limit import RateLimitMiddleware


class DummyApp:  # Minimal ASGI app stub
    async def __call__(self, scope, receive, send):
        pass


def make_request(path="/api/test", username=None, client_ip="127.0.0.1"):
    """Utility to create a mock Request."""
    req = MagicMock(spec=Request)
    req.url.path = path
    req.client = MagicMock()
    req.client.host = client_ip
    req.state = MagicMock()
    if username:
        setattr(req.state, "username", username)
    return req


@pytest.mark.asyncio
async def test_public_path_skips_limiting():
    middleware = RateLimitMiddleware(DummyApp(), rate_limit=1, time_window=60)
    request = make_request(path="/docs")  # public path
    call_next = AsyncMock(return_value=Response(content=b"ok"))

    response = await middleware.dispatch(request, call_next)

    call_next.assert_called_once_with(request)
    assert response.body == b"ok"


@pytest.mark.asyncio
async def test_rate_limit_by_ip_exceeded():
    middleware = RateLimitMiddleware(DummyApp(), rate_limit=2, time_window=60)

    call_next = AsyncMock(return_value=Response(content=b"ok"))
    request = make_request()

    with patch("time.time", return_value=1000):
        # First two requests pass
        for _ in range(2):
            resp = await middleware.dispatch(request, call_next)
            assert resp.body == b"ok"
        # Third exceeds limit
        response = await middleware.dispatch(request, call_next)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 429
    content = json.loads(response.body.decode())
    assert content["error"]["message"] == "Rate limit exceeded"


@pytest.mark.asyncio
async def test_rate_limit_resets_after_window():
    middleware = RateLimitMiddleware(DummyApp(), rate_limit=1, time_window=10)
    call_next = AsyncMock(return_value=Response(content=b"ok"))
    request = make_request()

    # First request at t=0
    with patch("time.time", return_value=0):
        await middleware.dispatch(request, call_next)
    # Second request at t=11 (outside window) should succeed
    with patch("time.time", return_value=11):
        resp = await middleware.dispatch(request, call_next)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_by_username():
    middleware = RateLimitMiddleware(DummyApp(), rate_limit=1, time_window=60)
    call_next = AsyncMock(return_value=Response(content=b"ok"))
    request = make_request(username="alice")

    # First request ok
    await middleware.dispatch(request, call_next)
    # Second should fail
    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 429


@pytest.mark.asyncio
async def test_disable_ip_and_username_checks():
    middleware = RateLimitMiddleware(DummyApp(), rate_limit=1, time_window=60,
                                     by_ip=False, by_user=False)
    call_next = AsyncMock(return_value=Response(content=b"ok"))
    request = make_request(username="bob")

    # Even multiple requests should pass because limiting disabled
    for _ in range(3):
        resp = await middleware.dispatch(request, call_next)
        assert resp.status_code == 200 