"""
Tests for utility functions.
"""

import json
import os
import tempfile
import time
from datetime import datetime
from unittest.mock import patch

import pytest

from mcp_proxy_adapter.core.utils import (
    calculate_hash,
    ensure_directory,
    format_datetime,
    generate_id,
    get_timestamp,
    parse_datetime,
    safe_json_dumps,
    safe_json_loads,
)


class TestUtils:
    """Tests for utility functions."""

    def test_generate_id(self):
        """Test generate_id function."""
        # Test that it generates unique IDs
        id1 = generate_id()
        id2 = generate_id()
        
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0

    def test_get_timestamp(self):
        """Test get_timestamp function."""
        # Test that it returns current timestamp
        timestamp1 = get_timestamp()
        time.sleep(0.001)  # Small delay
        timestamp2 = get_timestamp()
        
        assert isinstance(timestamp1, int)
        assert isinstance(timestamp2, int)
        assert timestamp2 > timestamp1
        assert timestamp1 > 0
        assert timestamp2 > 0

    def test_format_datetime_default(self):
        """Test format_datetime with default parameters."""
        # Test with current time
        formatted = format_datetime()
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert "T" in formatted
        assert "Z" in formatted

    def test_format_datetime_custom(self):
        """Test format_datetime with custom datetime and format."""
        dt = datetime(2023, 1, 1, 12, 30, 45)
        formatted = format_datetime(dt, "%Y-%m-%d %H:%M:%S")
        
        assert formatted == "2023-01-01 12:30:45"

    def test_format_datetime_custom_format(self):
        """Test format_datetime with custom format string."""
        dt = datetime(2023, 1, 1, 12, 30, 45)
        formatted = format_datetime(dt, "%d/%m/%Y")
        
        assert formatted == "01/01/2023"

    def test_parse_datetime(self):
        """Test parse_datetime function."""
        dt_str = "2023-01-01T12:30:45.123456Z"
        dt = parse_datetime(dt_str)
        
        assert isinstance(dt, datetime)
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12
        assert dt.minute == 30
        assert dt.second == 45

    def test_parse_datetime_custom_format(self):
        """Test parse_datetime with custom format."""
        dt_str = "01/01/2023 12:30:45"
        dt = parse_datetime(dt_str, "%d/%m/%Y %H:%M:%S")
        
        assert isinstance(dt, datetime)
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 1

    def test_safe_json_loads_valid(self, caplog):
        """Test safe_json_loads with valid JSON."""
        json_str = '{"key": "value", "number": 42}'
        result = safe_json_loads(json_str)
        
        assert result == {"key": "value", "number": 42}
        # Verify no error was logged
        assert "Error parsing JSON" not in caplog.text

    def test_safe_json_loads_invalid(self, caplog):
        """Test safe_json_loads with invalid JSON."""
        invalid_json = '{"key": "value", "number": 42'  # Missing closing brace
        result = safe_json_loads(invalid_json)
        
        assert result is None
        # Verify that error was logged
        assert "Error parsing JSON" in caplog.text

    def test_safe_json_loads_with_default(self, caplog):
        """Test safe_json_loads with custom default."""
        invalid_json = '{"key": "value", "number": 42'
        default_value = {"error": "invalid"}
        result = safe_json_loads(invalid_json, default_value)
        
        assert result == default_value
        # Verify that error was logged
        assert "Error parsing JSON" in caplog.text

    def test_safe_json_dumps_valid(self, caplog):
        """Test safe_json_dumps with valid object."""
        obj = {"key": "value", "number": 42}
        result = safe_json_dumps(obj)
        
        assert result == '{"key": "value", "number": 42}'
        # Verify no error was logged
        assert "Error serializing to JSON" not in caplog.text

    def test_safe_json_dumps_with_indent(self, caplog):
        """Test safe_json_dumps with indentation."""
        obj = {"key": "value", "number": 42}
        result = safe_json_dumps(obj, indent=2)
        
        expected = '{\n  "key": "value",\n  "number": 42\n}'
        assert result == expected
        # Verify no error was logged
        assert "Error serializing to JSON" not in caplog.text

    def test_safe_json_dumps_invalid(self, caplog):
        """Test safe_json_dumps with non-serializable object."""
        # Create object that can't be serialized
        class NonSerializable:
            pass
        
        obj = NonSerializable()
        result = safe_json_dumps(obj)
        
        assert result == "{}"
        # Verify that error was logged
        assert "Error serializing to JSON" in caplog.text

    def test_safe_json_dumps_custom_default(self, caplog):
        """Test safe_json_dumps with custom default."""
        class NonSerializable:
            pass
        
        obj = NonSerializable()
        result = safe_json_dumps(obj, default='{"error": "serialization failed"}')
        
        assert result == '{"error": "serialization failed"}'
        # Verify that error was logged
        assert "Error serializing to JSON" in caplog.text

    def test_calculate_hash_string(self):
        """Test calculate_hash with string input."""
        data = "test string"
        result = calculate_hash(data)
        
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 produces 64 hex characters

    def test_calculate_hash_bytes(self):
        """Test calculate_hash with bytes input."""
        data = b"test bytes"
        result = calculate_hash(data)
        
        assert isinstance(result, str)
        assert len(result) == 64

    def test_calculate_hash_different_algorithms(self):
        """Test calculate_hash with different algorithms."""
        data = "test data"
        
        md5_hash = calculate_hash(data, "md5")
        sha1_hash = calculate_hash(data, "sha1")
        sha256_hash = calculate_hash(data, "sha256")
        
        assert len(md5_hash) == 32  # MD5 produces 32 hex characters
        assert len(sha1_hash) == 40  # SHA1 produces 40 hex characters
        assert len(sha256_hash) == 64  # SHA256 produces 64 hex characters
        assert md5_hash != sha1_hash
        assert sha1_hash != sha256_hash

    def test_calculate_hash_unicode(self):
        """Test calculate_hash with unicode string."""
        data = "тест с кириллицей"
        result = calculate_hash(data)
        
        assert isinstance(result, str)
        assert len(result) == 64

    def test_ensure_directory_new(self):
        """Test ensure_directory with new directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_test_dir")
            
            result = ensure_directory(new_dir)
            
            assert result is True
            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)

    def test_ensure_directory_existing(self):
        """Test ensure_directory with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = ensure_directory(temp_dir)
            
            assert result is True
            assert os.path.exists(temp_dir)

    def test_ensure_directory_nested(self):
        """Test ensure_directory with nested directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = os.path.join(temp_dir, "level1", "level2", "level3")
            
            result = ensure_directory(nested_dir)
            
            assert result is True
            assert os.path.exists(nested_dir)
            assert os.path.isdir(nested_dir)

    @patch('os.makedirs')
    def test_ensure_directory_permission_error(self, mock_makedirs, caplog):
        """Test ensure_directory with permission error."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        result = ensure_directory("/root/test_dir")
        
        assert result is False
        # Verify that error was logged
        assert "Error creating directory" in caplog.text

    @patch('os.makedirs')
    def test_ensure_directory_os_error(self, mock_makedirs, caplog):
        """Test ensure_directory with OS error."""
        mock_makedirs.side_effect = OSError("OS error")
        
        result = ensure_directory("/invalid/path")
        
        assert result is False
        # Verify that error was logged
        assert "Error creating directory" in caplog.text

    def test_format_datetime_edge_cases(self):
        """Test format_datetime with edge cases."""
        # Test with specific datetime
        dt = datetime(2023, 12, 31, 23, 59, 59, 999999)
        formatted = format_datetime(dt)
        
        assert "2023-12-31T23:59:59.999999Z" in formatted

    def test_parse_datetime_edge_cases(self):
        """Test parse_datetime with edge cases."""
        # Test with minimal datetime
        dt_str = "2023-01-01T00:00:00.000000Z"
        dt = parse_datetime(dt_str)
        
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 0
        assert dt.minute == 0
        assert dt.second == 0

    def test_safe_json_loads_complex_types(self, caplog):
        """Test safe_json_loads with complex JSON types."""
        complex_json = '''
        {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "boolean": true,
            "null": null,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }
        '''
        result = safe_json_loads(complex_json)
        
        assert result["string"] == "value"
        assert result["number"] == 42
        assert result["float"] == 3.14
        assert result["boolean"] is True
        assert result["null"] is None
        assert result["array"] == [1, 2, 3]
        assert result["object"]["nested"] == "value"
        # Verify no error was logged
        assert "Error parsing JSON" not in caplog.text

    def test_safe_json_dumps_complex_types(self, caplog):
        """Test safe_json_dumps with complex object types."""
        complex_obj = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "none": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }
        result = safe_json_dumps(complex_obj)
        
        # Parse back to verify
        parsed = json.loads(result)
        assert parsed == complex_obj
        # Verify no error was logged
        assert "Error serializing to JSON" not in caplog.text 