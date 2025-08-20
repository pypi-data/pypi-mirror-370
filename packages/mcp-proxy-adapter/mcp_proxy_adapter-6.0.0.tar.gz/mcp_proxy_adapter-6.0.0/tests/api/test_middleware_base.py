"""
Tests for base middleware module.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import Request, Response
from starlette.responses import JSONResponse
import json

from mcp_proxy_adapter.api.middleware.base import BaseMiddleware


class TestBaseMiddleware:
    """Tests for BaseMiddleware class."""

    def setup_method(self):
        """Set up test method."""
        self.mock_app = MagicMock()
        self.middleware = BaseMiddleware(self.mock_app)

    @pytest.mark.asyncio
    async def test_dispatch_success(self):
        """Test dispatch with successful request processing."""
        request = MagicMock(spec=Request)
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        # Mock before_request and after_response to do nothing
        with patch.object(self.middleware, 'before_request', new_callable=AsyncMock) as mock_before:
            with patch.object(self.middleware, 'after_response', new_callable=AsyncMock) as mock_after:
                mock_after.return_value = response
                
                result = await self.middleware.dispatch(request, call_next)
                
                assert result == response
                mock_before.assert_called_once_with(request)
                mock_after.assert_called_once_with(request, response)
                call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_dispatch_with_exception(self, caplog):
        """Test dispatch with exception during processing."""
        request = MagicMock(spec=Request)
        call_next = AsyncMock(side_effect=Exception("Test error"))
        
        # Mock handle_error to return a response
        error_response = JSONResponse(content={"error": "Test error"}, status_code=500)
        with patch.object(self.middleware, 'handle_error', new_callable=AsyncMock) as mock_handle_error:
            mock_handle_error.return_value = error_response
            
            result = await self.middleware.dispatch(request, call_next)
            
            assert result == error_response
            mock_handle_error.assert_called_once()
            # Check that handle_error was called with the correct exception
            call_args = mock_handle_error.call_args
            assert call_args[0][0] == request
            assert isinstance(call_args[0][1], Exception)
            # Verify that error was logged
            assert "Error in middleware" in caplog.text

    @pytest.mark.asyncio
    async def test_dispatch_with_exception_in_before_request(self, caplog):
        """Test dispatch with exception in before_request."""
        request = MagicMock(spec=Request)
        call_next = AsyncMock()
        
        # Mock before_request to raise an exception
        with patch.object(self.middleware, 'before_request', new_callable=AsyncMock) as mock_before:
            mock_before.side_effect = Exception("Before request error")
            
            # Mock handle_error to return a response
            error_response = JSONResponse(content={"error": "Before request error"}, status_code=500)
            with patch.object(self.middleware, 'handle_error', new_callable=AsyncMock) as mock_handle_error:
                mock_handle_error.return_value = error_response
                
                result = await self.middleware.dispatch(request, call_next)
                
                assert result == error_response
                mock_handle_error.assert_called_once()
                # Check that handle_error was called with the correct exception
                call_args = mock_handle_error.call_args
                assert call_args[0][0] == request
                assert isinstance(call_args[0][1], Exception)
                # Verify that error was logged
                assert "Error in middleware" in caplog.text

    @pytest.mark.asyncio
    async def test_dispatch_with_exception_in_after_response(self, caplog):
        """Test dispatch with exception in after_response."""
        request = MagicMock(spec=Request)
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        # Mock before_request to succeed
        with patch.object(self.middleware, 'before_request', new_callable=AsyncMock):
            # Mock after_response to raise an exception
            with patch.object(self.middleware, 'after_response', new_callable=AsyncMock) as mock_after:
                mock_after.side_effect = Exception("After response error")
                
                # Mock handle_error to return a response
                error_response = JSONResponse(content={"error": "After response error"}, status_code=500)
                with patch.object(self.middleware, 'handle_error', new_callable=AsyncMock) as mock_handle_error:
                    mock_handle_error.return_value = error_response
                    
                    result = await self.middleware.dispatch(request, call_next)
                    
                    assert result == error_response
                    mock_handle_error.assert_called_once()
                    # Check that handle_error was called with the correct exception
                    call_args = mock_handle_error.call_args
                    assert call_args[0][0] == request
                    assert isinstance(call_args[0][1], Exception)
                    # Verify that error was logged
                    assert "Error in middleware" in caplog.text

    @pytest.mark.asyncio
    async def test_before_request_default_implementation(self):
        """Test before_request default implementation."""
        request = MagicMock(spec=Request)
        
        # Default implementation should do nothing
        await self.middleware.before_request(request)
        # No assertion needed as it should not raise any exception

    @pytest.mark.asyncio
    async def test_after_response_default_implementation(self):
        """Test after_response default implementation."""
        request = MagicMock(spec=Request)
        response = JSONResponse(content={"success": True})
        
        # Default implementation should return the response unchanged
        result = await self.middleware.after_response(request, response)
        
        assert result == response

    @pytest.mark.asyncio
    async def test_handle_error_default_implementation(self):
        """Test handle_error default implementation."""
        request = MagicMock(spec=Request)
        exception = Exception("Test error")
        
        # Default implementation should re-raise the exception
        with pytest.raises(Exception, match="Test error"):
            await self.middleware.handle_error(request, exception)

    @pytest.mark.asyncio
    async def test_dispatch_with_custom_before_request(self):
        """Test dispatch with custom before_request implementation."""
        class CustomMiddleware(BaseMiddleware):
            async def before_request(self, request: Request) -> None:
                # Add custom header to request
                request.state.custom_header = "test_value"
        
        custom_middleware = CustomMiddleware(self.mock_app)
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        with patch.object(custom_middleware, 'after_response', new_callable=AsyncMock) as mock_after:
            mock_after.return_value = response
            
            result = await custom_middleware.dispatch(request, call_next)
            
            assert result == response
            assert request.state.custom_header == "test_value"

    @pytest.mark.asyncio
    async def test_dispatch_with_custom_after_response(self):
        """Test dispatch with custom after_response implementation."""
        class CustomMiddleware(BaseMiddleware):
            async def after_response(self, request: Request, response: Response) -> Response:
                # Add custom header to response
                response.headers["X-Custom-Header"] = "test_value"
                return response
        
        custom_middleware = CustomMiddleware(self.mock_app)
        request = MagicMock(spec=Request)
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        with patch.object(custom_middleware, 'before_request', new_callable=AsyncMock):
            result = await custom_middleware.dispatch(request, call_next)
            
            assert result == response
            assert result.headers["X-Custom-Header"] == "test_value"

    @pytest.mark.asyncio
    async def test_dispatch_with_custom_handle_error(self, caplog):
        """Test dispatch with custom handle_error implementation."""
        
        class CustomMiddleware(BaseMiddleware):
            async def handle_error(self, request: Request, exception: Exception) -> Response:
                return JSONResponse(
                    content={"custom_error": str(exception)},
                    status_code=500
                )
        
        custom_middleware = CustomMiddleware(self.mock_app)
        request = MagicMock(spec=Request)
        call_next = AsyncMock(side_effect=Exception("Test error"))
        
        result = await custom_middleware.dispatch(request, call_next)
        
        assert result.status_code == 500
        content = json.loads(result.body.decode())
        assert content["custom_error"] == "Test error"
        # Verify that error was logged
        assert "Error in middleware" in caplog.text

    @pytest.mark.asyncio
    async def test_dispatch_logging_on_exception(self):
        """Test that exceptions are logged during dispatch."""
        request = MagicMock(spec=Request)
        call_next = AsyncMock(side_effect=Exception("Test error"))
        
        with patch('mcp_proxy_adapter.api.middleware.base.logger') as mock_logger:
            with patch.object(self.middleware, 'handle_error', new_callable=AsyncMock) as mock_handle_error:
                mock_handle_error.side_effect = Exception("Handle error failed")
                
                with pytest.raises(Exception, match="Handle error failed"):
                    await self.middleware.dispatch(request, call_next)
                
                # Verify that the exception was logged
                mock_logger.exception.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_with_response_modification(self):
        """Test dispatch with response modification in after_response."""
        class CustomMiddleware(BaseMiddleware):
            async def after_response(self, request: Request, response: Response) -> Response:
                # Add custom header to response
                response.headers["X-Modified"] = "true"
                return response
        
        custom_middleware = CustomMiddleware(self.mock_app)
        request = MagicMock(spec=Request)
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        with patch.object(custom_middleware, 'before_request', new_callable=AsyncMock):
            result = await custom_middleware.dispatch(request, call_next)
            
            assert result.headers["X-Modified"] == "true" 