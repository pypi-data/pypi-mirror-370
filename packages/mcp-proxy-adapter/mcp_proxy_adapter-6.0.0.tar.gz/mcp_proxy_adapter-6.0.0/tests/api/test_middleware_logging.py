"""
Tests for logging middleware.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, Response

from mcp_proxy_adapter.api.middleware.logging import LoggingMiddleware


class TestLoggingMiddleware:
    """Tests for LoggingMiddleware."""
    
    @pytest.fixture
    def middleware(self):
        """Create LoggingMiddleware instance."""
        app = MagicMock()
        return LoggingMiddleware(app)
    
    @pytest.mark.asyncio
    async def test_openapi_request_logged_at_debug_level(self, middleware):
        """Test that /openapi.json requests are logged at DEBUG level."""
        request = MagicMock(spec=Request)
        request.url = "http://localhost:8000/openapi.json"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        request.body = AsyncMock(return_value=b"")
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="{}", status_code=200)
        
        with patch('mcp_proxy_adapter.api.middleware.logging.RequestLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            await middleware.dispatch(request, call_next)
            
            # Check that debug was called for start
            mock_logger.debug.assert_any_call(
                "Request started: GET http://localhost:8000/openapi.json | Client: 127.0.0.1"
            )
            
            # Check that debug was called for completion (check all debug calls)
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            completion_call_found = any("Request completed" in call and "openapi.json" in call for call in debug_calls)
            assert completion_call_found, f"Completion call not found in debug calls: {debug_calls}"
            
            # Check that info was NOT called
            mock_logger.info.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_regular_request_logged_at_info_level(self, middleware):
        """Test that regular requests are logged at INFO level."""
        request = MagicMock(spec=Request)
        request.url = "http://localhost:8000/api/jsonrpc"
        request.method = "POST"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        request.body = AsyncMock(return_value=b"")
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="{}", status_code=200)
        
        with patch('mcp_proxy_adapter.api.middleware.logging.RequestLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            await middleware.dispatch(request, call_next)
            
            # Check that info was called for start
            mock_logger.info.assert_any_call(
                "Request started: POST http://localhost:8000/api/jsonrpc | Client: 127.0.0.1"
            )
            
            # Check that info was called for completion (check all info calls)
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            completion_call_found = any("Request completed" in call and "api/jsonrpc" in call for call in info_calls)
            assert completion_call_found, f"Completion call not found in info calls: {info_calls}"
    
    @pytest.mark.asyncio
    async def test_openapi_request_with_error_logged_at_debug_level(self, middleware):
        """Test that /openapi.json request errors are logged at DEBUG level."""
        request = MagicMock(spec=Request)
        request.url = "http://localhost:8000/openapi.json"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        request.body = AsyncMock(return_value=b"")
        
        call_next = AsyncMock()
        call_next.side_effect = Exception("Test error")
        
        with patch('mcp_proxy_adapter.api.middleware.logging.RequestLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            with pytest.raises(Exception):
                await middleware.dispatch(request, call_next)
            
            # Check that debug was called for start
            mock_logger.debug.assert_any_call(
                "Request started: GET http://localhost:8000/openapi.json | Client: 127.0.0.1"
            )
            
            # Check that debug was called for error (check all debug calls)
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            error_call_found = any("Request failed" in call and "openapi.json" in call for call in debug_calls)
            assert error_call_found, f"Error call not found in debug calls: {debug_calls}"
            
            # Check that error was NOT called
            mock_logger.error.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_regular_request_with_error_logged_at_error_level(self, middleware):
        """Test that regular request errors are logged at ERROR level."""
        request = MagicMock(spec=Request)
        request.url = "http://localhost:8000/api/jsonrpc"
        request.method = "POST"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        request.body = AsyncMock(return_value=b"")
        
        call_next = AsyncMock()
        call_next.side_effect = Exception("Test error")
        
        with patch('mcp_proxy_adapter.api.middleware.logging.RequestLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            with pytest.raises(Exception):
                await middleware.dispatch(request, call_next)
            
            # Check that error was called (check all error calls)
            error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
            error_call_found = any("Request failed" in call and "api/jsonrpc" in call for call in error_calls)
            assert error_call_found, f"Error call not found in error calls: {error_calls}"
    
    @pytest.mark.asyncio
    async def test_openapi_request_with_query_params(self, middleware):
        """Test that /openapi.json with query parameters is still detected."""
        request = MagicMock(spec=Request)
        request.url = "http://localhost:8000/openapi.json?format=json"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        request.body = AsyncMock(return_value=b"")
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="{}", status_code=200)
        
        with patch('mcp_proxy_adapter.api.middleware.logging.RequestLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            await middleware.dispatch(request, call_next)
            
            # Check that debug was called
            mock_logger.debug.assert_any_call(
                "Request started: GET http://localhost:8000/openapi.json?format=json | Client: 127.0.0.1"
            )
            
            # Check that info was NOT called
            mock_logger.info.assert_not_called() 