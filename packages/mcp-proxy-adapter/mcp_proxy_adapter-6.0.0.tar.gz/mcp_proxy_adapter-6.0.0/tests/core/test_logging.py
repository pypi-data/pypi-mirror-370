"""
Tests for logging module.
"""

import logging
import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from mcp_proxy_adapter.core.logging import (
    CustomFormatter,
    RequestContextFilter,
    RequestLogger,
    setup_logging,
    get_logger,
    logger
)


class TestCustomFormatter:
    """Tests for CustomFormatter class."""

    def test_format_debug(self):
        """Test formatting DEBUG level message."""
        formatter = CustomFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Test debug message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "Test debug message" in result
        assert result.startswith("\x1b[38;20m")
        assert result.endswith("\x1b[0m")

    def test_format_info(self):
        """Test formatting INFO level message."""
        formatter = CustomFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test info message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "Test info message" in result
        assert result.startswith("\x1b[38;20m")
        assert result.endswith("\x1b[0m")

    def test_format_warning(self):
        """Test formatting WARNING level message."""
        formatter = CustomFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Test warning message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "Test warning message" in result
        assert result.startswith("\x1b[33;20m")
        assert result.endswith("\x1b[0m")

    def test_format_error(self):
        """Test formatting ERROR level message."""
        formatter = CustomFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "Test error message" in result
        assert result.startswith("\x1b[31;20m")
        assert result.endswith("\x1b[0m")

    def test_format_critical(self):
        """Test formatting CRITICAL level message."""
        formatter = CustomFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.CRITICAL,
            pathname="test.py",
            lineno=1,
            msg="Test critical message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "Test critical message" in result
        assert result.startswith("\x1b[31;1m")
        assert result.endswith("\x1b[0m")

    def test_format_unknown_level(self):
        """Test formatting message with unknown level."""
        formatter = CustomFormatter()
        record = logging.LogRecord(
            name="test",
            level=999,  # Unknown level
            pathname="test.py",
            lineno=1,
            msg="Test unknown message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "Test unknown message" in result
        # Should use default formatting (no color codes)
        assert not result.startswith("\x1b")


class TestRequestContextFilter:
    """Tests for RequestContextFilter class."""

    def test_filter_with_request_id(self):
        """Test filter with specific request ID."""
        filter_obj = RequestContextFilter("test-request-123")
        record = MagicMock()
        
        result = filter_obj.filter(record)
        
        assert result is True
        assert record.request_id == "test-request-123"

    def test_filter_without_request_id(self):
        """Test filter without request ID."""
        filter_obj = RequestContextFilter()
        record = MagicMock()
        
        result = filter_obj.filter(record)
        
        assert result is True
        assert record.request_id == "no-request-id"

    def test_filter_with_none_request_id(self):
        """Test filter with None request ID."""
        filter_obj = RequestContextFilter(None)
        record = MagicMock()
        
        result = filter_obj.filter(record)
        
        assert result is True
        assert record.request_id == "no-request-id"


class TestRequestLogger:
    """Tests for RequestLogger class."""

    def test_init_with_request_id(self):
        """Test initialization with specific request ID."""
        request_logger = RequestLogger("test_logger", "test-request-123")
        
        assert request_logger.request_id == "test-request-123"
        assert request_logger.logger.name == "test_logger"

    def test_init_without_request_id(self):
        """Test initialization without request ID."""
        request_logger = RequestLogger("test_logger")
        
        assert request_logger.request_id is not None
        assert len(request_logger.request_id) > 0
        assert request_logger.logger.name == "test_logger"

    def test_log_methods(self):
        """Test all logging methods."""
        request_logger = RequestLogger("test_logger", "test-request")
        
        with patch.object(request_logger.logger, 'debug') as mock_debug:
            request_logger.debug("Debug message")
            mock_debug.assert_called_once_with("[test-request] Debug message")
        
        with patch.object(request_logger.logger, 'info') as mock_info:
            request_logger.info("Info message")
            mock_info.assert_called_once_with("[test-request] Info message")
        
        with patch.object(request_logger.logger, 'warning') as mock_warning:
            request_logger.warning("Warning message")
            mock_warning.assert_called_once_with("[test-request] Warning message")
        
        with patch.object(request_logger.logger, 'error') as mock_error:
            request_logger.error("Error message")
            mock_error.assert_called_once_with("[test-request] Error message")
        
        with patch.object(request_logger.logger, 'critical') as mock_critical:
            request_logger.critical("Critical message")
            mock_critical.assert_called_once_with("[test-request] Critical message")
        
        with patch.object(request_logger.logger, 'exception') as mock_exception:
            request_logger.exception("Exception message")
            mock_exception.assert_called_once_with("[test-request] Exception message")


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        with patch('mcp_proxy_adapter.core.logging.config') as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                "logging.level": "INFO",
                "logging.file": None,
                "logging.rotation.type": "size",
                "logging.rotation.max_bytes": 10485760,
                "logging.rotation.backup_count": 5,
                "logging.rotation.when": "D",
                "logging.rotation.interval": 1,
                "logging.levels": {}
            }.get(key, default)
            
            logger = setup_logging()
            
            assert logger.name == "mcp_proxy_adapter"
            assert logger.level == logging.INFO

    def test_setup_logging_with_file(self):
        """Test setup_logging with log file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name
        
        try:
            with patch('mcp_proxy_adapter.core.logging.config') as mock_config:
                mock_config.get.side_effect = lambda key, default=None: {
                    "logging.level": "DEBUG",
                    "logging.file": log_file,
                    "logging.rotation.type": "size",
                    "logging.rotation.max_bytes": 10485760,
                    "logging.rotation.backup_count": 5,
                    "logging.rotation.when": "D",
                    "logging.rotation.interval": 1,
                    "logging.levels": {}
                }.get(key, default)
                
                logger = setup_logging()
                
                assert logger.name == "mcp_proxy_adapter"
                assert logger.level == logging.DEBUG
                assert len(logger.handlers) == 4  # Console + main file + error file + access file
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_setup_logging_with_time_rotation(self):
        """Test setup_logging with time-based rotation."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name
        
        try:
            with patch('mcp_proxy_adapter.core.logging.config') as mock_config:
                mock_config.get.side_effect = lambda key, default=None: {
                    "logging.level": "INFO",
                    "logging.file": log_file,
                    "logging.rotation.type": "time",
                    "logging.rotation.max_bytes": 10485760,
                    "logging.rotation.backup_count": 5,
                    "logging.rotation.when": "H",
                    "logging.rotation.interval": 2,
                    "logging.levels": {}
                }.get(key, default)
                
                logger = setup_logging()
                
                assert logger.name == "mcp_proxy_adapter"
                assert len(logger.handlers) == 4  # Console + main file + error file + access file
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_setup_logging_with_custom_levels(self):
        """Test setup_logging with custom log levels."""
        with patch('mcp_proxy_adapter.core.logging.config') as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                "logging.level": "INFO",
                "logging.file": None,
                "logging.rotation.type": "size",
                "logging.rotation.max_bytes": 10485760,
                "logging.rotation.backup_count": 5,
                "logging.rotation.when": "D",
                "logging.rotation.interval": 1,
                "logging.levels": {
                    "requests": "WARNING",
                    "urllib3": "ERROR"
                }
            }.get(key, default)
            
            logger = setup_logging()
            
            assert logger.name == "mcp_proxy_adapter"
            
            # Check that external loggers are configured
            requests_logger = logging.getLogger("requests")
            urllib3_logger = logging.getLogger("urllib3")
            
            assert requests_logger.level == logging.WARNING
            assert urllib3_logger.level == logging.ERROR

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid logging level."""
        with patch('mcp_proxy_adapter.core.logging.config') as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                "logging.level": "INVALID_LEVEL",
                "logging.file": None,
                "logging.rotation.type": "size",
                "logging.rotation.max_bytes": 10485760,
                "logging.rotation.backup_count": 5,
                "logging.rotation.when": "D",
                "logging.rotation.interval": 1,
                "logging.levels": {}
            }.get(key, default)
            
            logger = setup_logging()
            
            assert logger.name == "mcp_proxy_adapter"
            assert logger.level == logging.INFO  # Should default to INFO

    def test_setup_logging_with_custom_parameters(self):
        """Test setup_logging with custom parameters."""
        with patch('mcp_proxy_adapter.core.logging.config') as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                "logging.level": "DEBUG",
                "logging.file": None,
                "logging.rotation.type": "size",
                "logging.rotation.max_bytes": 10485760,
                "logging.rotation.backup_count": 5,
                "logging.rotation.when": "D",
                "logging.rotation.interval": 1,
                "logging.levels": {}
            }.get(key, default)
            
            logger = setup_logging(
                level="ERROR",
                log_file=None,
                max_bytes=1024,
                backup_count=3,
                rotation_type="time",
                rotation_when="M",
                rotation_interval=5
            )
            
            assert logger.name == "mcp_proxy_adapter"
            assert logger.level == logging.ERROR


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger(self):
        """Test get_logger function."""
        test_logger = get_logger("test_logger")
        
        assert test_logger.name == "test_logger"
        assert isinstance(test_logger, logging.Logger)


class TestGlobalLogger:
    """Tests for global logger."""

    def test_global_logger(self):
        """Test that global logger is properly configured."""
        assert logger.name == "mcp_proxy_adapter"
        assert isinstance(logger, logging.Logger)
        assert len(logger.handlers) > 0 