"""
Tests for performance middleware module.
"""

import pytest
import time
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.api.middleware.performance import PerformanceMiddleware


class TestPerformanceMiddleware:
    """Tests for PerformanceMiddleware class."""

    def setup_method(self):
        """Set up test method."""
        self.mock_app = MagicMock()
        self.middleware = PerformanceMiddleware(self.mock_app)

    def test_initialization(self):
        """Test middleware initialization."""
        assert self.middleware.request_times == {}
        assert self.middleware.log_interval == 100
        assert self.middleware.request_count == 0

    @pytest.mark.asyncio
    async def test_dispatch_successful_request(self):
        """Test dispatch with successful request."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response
        assert "/api/test" in self.middleware.request_times
        assert len(self.middleware.request_times["/api/test"]) == 1
        assert self.middleware.request_count == 1

    @pytest.mark.asyncio
    async def test_dispatch_multiple_requests_same_path(self):
        """Test dispatch with multiple requests to the same path."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        # Make multiple requests
        for _ in range(3):
            await self.middleware.dispatch(request, call_next)
        
        assert len(self.middleware.request_times["/api/test"]) == 3
        assert self.middleware.request_count == 3

    @pytest.mark.asyncio
    async def test_dispatch_multiple_paths(self):
        """Test dispatch with requests to different paths."""
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        # Request to first path
        request1 = MagicMock(spec=Request)
        request1.url.path = "/api/test1"
        await self.middleware.dispatch(request1, call_next)
        
        # Request to second path
        request2 = MagicMock(spec=Request)
        request2.url.path = "/api/test2"
        await self.middleware.dispatch(request2, call_next)
        
        assert "/api/test1" in self.middleware.request_times
        assert "/api/test2" in self.middleware.request_times
        assert len(self.middleware.request_times["/api/test1"]) == 1
        assert len(self.middleware.request_times["/api/test2"]) == 1
        assert self.middleware.request_count == 2

    @pytest.mark.asyncio
    async def test_dispatch_with_logging_interval(self):
        """Test dispatch with logging interval reached."""
        # Set log interval to 2 for testing
        self.middleware.log_interval = 2
        
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            # First request - should not log
            await self.middleware.dispatch(request, call_next)
            mock_logger.info.assert_not_called()
            
            # Second request - should log statistics
            await self.middleware.dispatch(request, call_next)
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_dispatch_with_exception(self):
        """Test dispatch with exception during processing."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        
        call_next = AsyncMock(side_effect=Exception("Processing error"))
        
        with pytest.raises(Exception, match="Processing error"):
            await self.middleware.dispatch(request, call_next)
        
        # Exception should be re-raised, so no time should be recorded
        assert "/api/test" not in self.middleware.request_times
        assert self.middleware.request_count == 0

    def test_log_stats_single_request(self):
        """Test _log_stats with single request (should not log)."""
        self.middleware.request_times["/api/test"] = [0.1]
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            self.middleware._log_stats()
            
            # Should only log the header for single request
            mock_logger.info.assert_called_once_with("Performance statistics:")

    def test_log_stats_multiple_requests(self):
        """Test _log_stats with multiple requests."""
        # Add multiple request times
        self.middleware.request_times["/api/test"] = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            self.middleware._log_stats()
            
            # Should log statistics
            mock_logger.info.assert_called()
            call_args = mock_logger.info.call_args[0][0]
            assert "Path: /api/test" in call_args
            assert "Requests: 5" in call_args
            assert "Avg:" in call_args
            assert "Min:" in call_args
            assert "Max:" in call_args
            assert "p95:" in call_args

    def test_log_stats_multiple_paths(self):
        """Test _log_stats with multiple paths."""
        self.middleware.request_times["/api/test1"] = [0.1, 0.2]
        self.middleware.request_times["/api/test2"] = [0.3, 0.4, 0.5]
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            self.middleware._log_stats()
            
            # Should log for both paths
            assert mock_logger.info.call_count >= 2

    def test_log_stats_empty_times(self):
        """Test _log_stats with empty request times."""
        self.middleware.request_times = {}
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            self.middleware._log_stats()
            
            # Should only log the header
            mock_logger.info.assert_called_once_with("Performance statistics:")

    def test_log_stats_single_request_per_path(self):
        """Test _log_stats with single request per path."""
        self.middleware.request_times["/api/test1"] = [0.1]
        self.middleware.request_times["/api/test2"] = [0.2]
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            self.middleware._log_stats()
            
            # Should only log the header, not individual paths
            assert mock_logger.info.call_count == 1
            mock_logger.info.assert_called_once_with("Performance statistics:")

    @pytest.mark.asyncio
    async def test_dispatch_timing_accuracy(self):
        """Test that timing measurements are accurate."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        
        # Mock call_next to simulate processing time
        async def slow_call_next(req):
            await asyncio.sleep(0.01)  # 10ms delay
            return JSONResponse(content={"success": True})
        
        call_next = slow_call_next
        
        start_time = time.time()
        result = await self.middleware.dispatch(request, call_next)
        end_time = time.time()
        
        assert result.status_code == 200
        
        # Check that recorded time is reasonable
        recorded_time = self.middleware.request_times["/api/test"][0]
        actual_time = end_time - start_time
        
        # Recorded time should be close to actual time (within 50ms tolerance)
        assert abs(recorded_time - actual_time) < 0.05

    @pytest.mark.asyncio
    async def test_dispatch_with_custom_log_interval(self):
        """Test dispatch with custom log interval."""
        # Set custom log interval
        self.middleware.log_interval = 3
        
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            # First two requests - should not log
            await self.middleware.dispatch(request, call_next)
            await self.middleware.dispatch(request, call_next)
            mock_logger.info.assert_not_called()
            
            # Third request - should log statistics
            await self.middleware.dispatch(request, call_next)
            mock_logger.info.assert_called()

    def test_log_stats_percentile_calculation(self):
        """Test _log_stats percentile calculation."""
        # Add exactly 20 request times for easy percentile calculation
        times = [i * 0.01 for i in range(1, 21)]  # 0.01, 0.02, ..., 0.20
        self.middleware.request_times["/api/test"] = times
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            self.middleware._log_stats()
            
            # Check that p95 calculation is correct (19th element in sorted list)
            call_args = mock_logger.info.call_args[0][0]
            assert "p95: 0.200" in call_args  # 19th element should be 0.20 (20th element)

    def test_log_stats_edge_cases(self):
        """Test _log_stats with edge cases."""
        # Test with very small times
        self.middleware.request_times["/api/test"] = [0.001, 0.002, 0.003]
        
        with patch('mcp_proxy_adapter.api.middleware.performance.logger') as mock_logger:
            self.middleware._log_stats()
            
            call_args = mock_logger.info.call_args[0][0]
            assert "Avg: 0.002" in call_args
            assert "Min: 0.001" in call_args
            assert "Max: 0.003" in call_args

    @pytest.mark.asyncio
    async def test_dispatch_request_count_increment(self):
        """Test that request count increments correctly."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        initial_count = self.middleware.request_count
        
        await self.middleware.dispatch(request, call_next)
        
        assert self.middleware.request_count == initial_count + 1 