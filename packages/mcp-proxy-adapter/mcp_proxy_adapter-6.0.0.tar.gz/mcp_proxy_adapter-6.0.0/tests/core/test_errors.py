"""
Tests for error classes and functions.
"""

import pytest

from mcp_proxy_adapter.core.errors import (
    AuthenticationError,
    AuthorizationError,
    CommandError,
    ConfigurationError,
    InternalError,
    InvalidParamsError,
    InvalidRequestError,
    MethodNotFoundError,
    MicroserviceError,
    NotFoundError,
    ParseError,
    TimeoutError,
    ValidationError,
    format_validation_errors,
)


class TestMicroserviceError:
    """Tests for base MicroserviceError class."""

    def test_init_default_values(self):
        """Test MicroserviceError initialization with default values."""
        error = MicroserviceError("Test error")
        
        assert error.message == "Test error"
        assert error.code == -32000
        assert error.data == {}

    def test_init_custom_values(self):
        """Test MicroserviceError initialization with custom values."""
        data = {"field": "value"}
        error = MicroserviceError("Test error", code=-32600, data=data)
        
        assert error.message == "Test error"
        assert error.code == -32600
        assert error.data == data

    def test_init_with_none_data(self):
        """Test MicroserviceError initialization with None data."""
        error = MicroserviceError("Test error", data=None)
        
        assert error.message == "Test error"
        assert error.code == -32000
        assert error.data == {}

    def test_to_dict_without_data(self):
        """Test to_dict method without data."""
        error = MicroserviceError("Test error", code=-32600)
        result = error.to_dict()
        
        assert result == {
            "code": -32600,
            "message": "Test error"
        }

    def test_to_dict_with_data(self):
        """Test to_dict method with data."""
        data = {"field": "value", "details": "test"}
        error = MicroserviceError("Test error", code=-32600, data=data)
        result = error.to_dict()
        
        assert result == {
            "code": -32600,
            "message": "Test error",
            "data": data
        }

    def test_str_representation(self):
        """Test string representation of error."""
        error = MicroserviceError("Test error")
        
        assert str(error) == "Test error"


class TestParseError:
    """Tests for ParseError class."""

    def test_init_default_values(self):
        """Test ParseError initialization with default values."""
        error = ParseError()
        
        assert error.message == "Parse error"
        assert error.code == -32700
        assert error.data == {}

    def test_init_custom_values(self):
        """Test ParseError initialization with custom values."""
        data = {"line": 10, "column": 5}
        error = ParseError("Custom parse error", data=data)
        
        assert error.message == "Custom parse error"
        assert error.code == -32700
        assert error.data == data


class TestInvalidRequestError:
    """Tests for InvalidRequestError class."""

    def test_init_default_values(self):
        """Test InvalidRequestError initialization with default values."""
        error = InvalidRequestError()
        
        assert error.message == "Invalid Request"
        assert error.code == -32600
        assert error.data == {}

    def test_init_custom_values(self):
        """Test InvalidRequestError initialization with custom values."""
        data = {"received": "invalid_format"}
        error = InvalidRequestError("Custom invalid request", data=data)
        
        assert error.message == "Custom invalid request"
        assert error.code == -32600
        assert error.data == data


class TestMethodNotFoundError:
    """Tests for MethodNotFoundError class."""

    def test_init_default_values(self):
        """Test MethodNotFoundError initialization with default values."""
        error = MethodNotFoundError()
        
        assert error.message == "Method not found"
        assert error.code == -32601
        assert error.data == {}

    def test_init_custom_values(self):
        """Test MethodNotFoundError initialization with custom values."""
        data = {"method": "nonexistent_method"}
        error = MethodNotFoundError("Custom method not found", data=data)
        
        assert error.message == "Custom method not found"
        assert error.code == -32601
        assert error.data == data


class TestInvalidParamsError:
    """Tests for InvalidParamsError class."""

    def test_init_default_values(self):
        """Test InvalidParamsError initialization with default values."""
        error = InvalidParamsError()
        
        assert error.message == "Invalid params"
        assert error.code == -32602
        assert error.data == {}

    def test_init_custom_values(self):
        """Test InvalidParamsError initialization with custom values."""
        data = {"param": "value", "expected": "string"}
        error = InvalidParamsError("Custom invalid params", data=data)
        
        assert error.message == "Custom invalid params"
        assert error.code == -32602
        assert error.data == data


class TestInternalError:
    """Tests for InternalError class."""

    def test_init_default_values(self):
        """Test InternalError initialization with default values."""
        error = InternalError()
        
        assert error.message == "Internal error"
        assert error.code == -32603
        assert error.data == {}

    def test_init_custom_values(self):
        """Test InternalError initialization with custom values."""
        data = {"traceback": "stack_trace"}
        error = InternalError("Custom internal error", data=data)
        
        assert error.message == "Custom internal error"
        assert error.code == -32603
        assert error.data == data


class TestValidationError:
    """Tests for ValidationError class."""

    def test_init_default_values(self):
        """Test ValidationError initialization with default values."""
        error = ValidationError()
        
        assert error.message == "Validation error"
        assert error.code == -32602
        assert error.data == {}

    def test_init_custom_values(self):
        """Test ValidationError initialization with custom values."""
        data = {"field": "email", "value": "invalid_email"}
        error = ValidationError("Custom validation error", data=data)
        
        assert error.message == "Custom validation error"
        assert error.code == -32602
        assert error.data == data


class TestCommandError:
    """Tests for CommandError class."""

    def test_init_default_values(self):
        """Test CommandError initialization with default values."""
        error = CommandError()
        
        assert error.message == "Command execution error"
        assert error.code == -32000
        assert error.data == {}

    def test_init_custom_values(self):
        """Test CommandError initialization with custom values."""
        data = {"command": "test_command", "args": ["arg1", "arg2"]}
        error = CommandError("Custom command error", data=data)
        
        assert error.message == "Custom command error"
        assert error.code == -32000
        assert error.data == data


class TestNotFoundError:
    """Tests for NotFoundError class."""

    def test_init_default_values(self):
        """Test NotFoundError initialization with default values."""
        error = NotFoundError()
        
        assert error.message == "Resource not found"
        assert error.code == -32601
        assert error.data == {}

    def test_init_custom_values(self):
        """Test NotFoundError initialization with custom values."""
        data = {"resource": "user", "id": "123"}
        error = NotFoundError("Custom not found error", data=data)
        
        assert error.message == "Custom not found error"
        assert error.code == -32601
        assert error.data == data


class TestConfigurationError:
    """Tests for ConfigurationError class."""

    def test_init_default_values(self):
        """Test ConfigurationError initialization with default values."""
        error = ConfigurationError()
        
        assert error.message == "Configuration error"
        assert error.code == -32603
        assert error.data == {}

    def test_init_custom_values(self):
        """Test ConfigurationError initialization with custom values."""
        data = {"config_file": "config.json", "missing": "database_url"}
        error = ConfigurationError("Custom configuration error", data=data)
        
        assert error.message == "Custom configuration error"
        assert error.code == -32603
        assert error.data == data


class TestAuthenticationError:
    """Tests for AuthenticationError class."""

    def test_init_default_values(self):
        """Test AuthenticationError initialization with default values."""
        error = AuthenticationError()
        
        assert error.message == "Authentication error"
        assert error.code == -32001
        assert error.data == {}

    def test_init_custom_values(self):
        """Test AuthenticationError initialization with custom values."""
        data = {"user": "test_user", "reason": "invalid_token"}
        error = AuthenticationError("Custom authentication error", data=data)
        
        assert error.message == "Custom authentication error"
        assert error.code == -32001
        assert error.data == data


class TestAuthorizationError:
    """Tests for AuthorizationError class."""

    def test_init_default_values(self):
        """Test AuthorizationError initialization with default values."""
        error = AuthorizationError()
        
        assert error.message == "Authorization error"
        assert error.code == -32002
        assert error.data == {}

    def test_init_custom_values(self):
        """Test AuthorizationError initialization with custom values."""
        data = {"user": "test_user", "resource": "admin_panel", "permission": "read"}
        error = AuthorizationError("Custom authorization error", data=data)
        
        assert error.message == "Custom authorization error"
        assert error.code == -32002
        assert error.data == data


class TestTimeoutError:
    """Tests for TimeoutError class."""

    def test_init_default_values(self):
        """Test TimeoutError initialization with default values."""
        error = TimeoutError()
        
        assert error.message == "Timeout error"
        assert error.code == -32003
        assert error.data == {}

    def test_init_custom_values(self):
        """Test TimeoutError initialization with custom values."""
        data = {"timeout": 30, "operation": "database_query"}
        error = TimeoutError("Custom timeout error", data=data)
        
        assert error.message == "Custom timeout error"
        assert error.code == -32003
        assert error.data == data


class TestFormatValidationErrors:
    """Tests for format_validation_errors function."""

    def test_format_validation_errors_empty_list(self):
        """Test format_validation_errors with empty list."""
        result = format_validation_errors([])
        
        assert result == {}

    def test_format_validation_errors_single_error(self):
        """Test format_validation_errors with single error."""
        errors = [
            {
                "loc": ["field", "email"],
                "msg": "Invalid email format"
            }
        ]
        
        result = format_validation_errors(errors)
        
        assert result == {
            "field.email": "Invalid email format"
        }

    def test_format_validation_errors_multiple_errors(self):
        """Test format_validation_errors with multiple errors."""
        errors = [
            {
                "loc": ["user", "name"],
                "msg": "Name is required"
            },
            {
                "loc": ["user", "age"],
                "msg": "Age must be positive"
            },
            {
                "loc": ["settings", "theme"],
                "msg": "Invalid theme value"
            }
        ]
        
        result = format_validation_errors(errors)
        
        assert result == {
            "user.name": "Name is required",
            "user.age": "Age must be positive",
            "settings.theme": "Invalid theme value"
        }

    def test_format_validation_errors_without_loc(self):
        """Test format_validation_errors with error without loc."""
        errors = [
            {
                "msg": "General validation error"
            }
        ]
        
        result = format_validation_errors(errors)
        
        assert result == {
            "": "General validation error"
        }

    def test_format_validation_errors_without_msg(self):
        """Test format_validation_errors with error without msg."""
        errors = [
            {
                "loc": ["field"]
            }
        ]
        
        result = format_validation_errors(errors)
        
        assert result == {
            "field": "Validation error"
        }

    def test_format_validation_errors_complex_loc(self):
        """Test format_validation_errors with complex location."""
        errors = [
            {
                "loc": ["users", 0, "profile", "settings"],
                "msg": "Invalid settings"
            }
        ]
        
        result = format_validation_errors(errors)
        
        assert result == {
            "users.0.profile.settings": "Invalid settings"
        }

    def test_format_validation_errors_mixed_types(self):
        """Test format_validation_errors with mixed location types."""
        errors = [
            {
                "loc": ["config", "items", 1, "name"],
                "msg": "Name is required"
            }
        ]
        
        result = format_validation_errors(errors)
        
        assert result == {
            "config.items.1.name": "Name is required"
        } 