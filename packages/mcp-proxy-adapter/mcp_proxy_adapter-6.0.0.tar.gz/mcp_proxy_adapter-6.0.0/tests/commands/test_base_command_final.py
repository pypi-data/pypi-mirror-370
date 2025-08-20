"""
Final tests for base command to achieve 90%+ coverage.

This module contains additional tests for commands/base.py to achieve 90%+ coverage.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any, List

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.core.errors import (
    ValidationError, InvalidParamsError, NotFoundError, 
    TimeoutError, CommandError, InternalError
)


class TestCommandFinal:
    """Final tests for Command base class to improve coverage."""

    def test_validate_params_with_none_values(self):
        """Test validate_params with None values."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        params = {"param1": None, "param2": "value", "param3": ""}
        validated = TestCommand.validate_params(params)
        
        # None values should be removed
        assert "param1" not in validated
        assert "param2" in validated
        assert "param3" not in validated
        assert validated["param2"] == "value"

    def test_validate_params_with_null_strings(self):
        """Test validate_params with null-like strings."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        params = {"param1": "null", "param2": "None", "param3": "NONE", "param4": "value"}
        validated = TestCommand.validate_params(params)
        
        # null-like strings should be removed
        assert "param1" not in validated
        assert "param2" not in validated
        assert "param3" not in validated
        assert "param4" in validated
        assert validated["param4"] == "value"

    def test_validate_params_with_cmdname_none(self):
        """Test validate_params with cmdname as None."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        params = {"cmdname": None, "other_param": "value"}
        validated = TestCommand.validate_params(params)
        
        # cmdname should be preserved as None
        assert "cmdname" in validated
        assert validated["cmdname"] is None
        assert "other_param" in validated

    def test_get_param_info_with_kwargs(self):
        """Test get_param_info with **kwargs parameter."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        param_info = TestCommand.get_param_info()
        
        # Should handle **kwargs parameter
        assert "kwargs" in param_info  # **kwargs is treated as a parameter

    def test_get_param_info_with_complex_annotations(self):
        """Test get_param_info with complex type annotations."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, 
                            simple_param: str,
                            optional_param: str = "default",
                            typed_param: Dict[str, Any] = None,
                            union_param: str | int = "default",
                            **kwargs):
                return SuccessResult()
        
        param_info = TestCommand.get_param_info()
        
        assert "simple_param" in param_info
        assert "optional_param" in param_info
        assert "typed_param" in param_info
        assert "union_param" in param_info
        assert param_info["optional_param"]["default"] == "default"
        assert param_info["typed_param"]["default"] is None

    def test_get_metadata_without_docstring(self):
        """Test get_metadata without docstring."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self):
                return SuccessResult()
        
        metadata = TestCommand.get_metadata()
        
        assert metadata["name"] == "test"
        assert metadata["summary"] == ""
        assert metadata["description"] == ""

    def test_get_metadata_with_docstring(self):
        """Test get_metadata with docstring."""
        class TestCommand(Command):
            """Test command with docstring.
            
            This is a test command for testing metadata generation.
            """
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, param1: str = "default"):
                """Execute the test command."""
                return SuccessResult()
        
        metadata = TestCommand.get_metadata()
        
        assert metadata["name"] == "test"
        assert "Test command with docstring" in metadata["summary"]
        assert "This is a test command" in metadata["description"]
        assert "param1" in metadata["params"]
        assert "examples" in metadata
        assert "schema" in metadata
        assert "result_schema" in metadata
        assert metadata["result_class"] == "SuccessResult"

    def test_generate_examples_with_no_params(self):
        """Test _generate_examples with no parameters."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self):
                return SuccessResult()
        
        params = {}
        examples = TestCommand._generate_examples(params)
        
        assert len(examples) == 1
        assert examples[0]["command"] == "test"
        assert "without parameters" in examples[0]["description"]

    def test_generate_examples_with_mixed_params(self):
        """Test _generate_examples with mixed required and optional parameters."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, required_param: str, optional_param: int = 42):
                return SuccessResult()
        
        params = {
            "required_param": {"type": "str", "required": True},
            "optional_param": {"type": "int", "required": False, "default": 42}
        }
        
        examples = TestCommand._generate_examples(params)
        
        assert len(examples) == 2
        
        # Check required params example
        required_example = next((ex for ex in examples if "required parameters" in ex["description"]), None)
        assert required_example is not None
        assert required_example["params"]["required_param"] == "sample_required_param"
        
        # Check all params example
        all_params_example = next((ex for ex in examples if "all parameters" in ex["description"]), None)
        assert all_params_example is not None
        assert all_params_example["params"]["optional_param"] == 42

    def test_generate_examples_with_complex_types(self):
        """Test _generate_examples with complex type parameters."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, list_param: list, dict_param: dict, unknown_param):
                return SuccessResult()
        
        params = {
            "list_param": {"type": "list", "required": True},
            "dict_param": {"type": "dict", "required": True},
            "unknown_param": {"type": "CustomType", "required": True}
        }
        
        examples = TestCommand._generate_examples(params)
        
        required_example = next((ex for ex in examples if "params" in ex), None)
        assert required_example is not None
        assert required_example["params"]["list_param"] == []
        assert required_example["params"]["dict_param"] == {}
        assert required_example["params"]["unknown_param"] == "..."

    def test_generate_examples_with_optional_params(self):
        """Test _generate_examples with optional parameters."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, optional_param: str = "default"):
                return SuccessResult()
        
        params = {
            "optional_param": {"type": "str", "required": False, "default": "default"}
        }
        
        examples = TestCommand._generate_examples(params)
        
        # Should have multiple examples (without params and with all params)
        assert len(examples) >= 1
        assert examples[0]["command"] == "test"
        assert "without parameters" in examples[0]["description"]

    def test_generate_examples_with_all_optional_no_defaults(self):
        """Test _generate_examples with all optional parameters without defaults."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, param1: str = None, param2: int = None):
                return SuccessResult()
        
        params = {
            "param1": {"type": "str", "required": False},
            "param2": {"type": "int", "required": False}
        }
        
        examples = TestCommand._generate_examples(params)
        
        # Should have multiple examples (without params and with all params)
        assert len(examples) >= 1
        assert examples[0]["command"] == "test"
        assert "without parameters" in examples[0]["description"] 

"""
Additional tests for Command base class to achieve 90%+ coverage.

This module contains specific tests to cover uncovered lines in base.py.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.core.errors import (
    ValidationError, InvalidParamsError, NotFoundError, 
    TimeoutError, CommandError, InternalError
)


class TestCommandWithoutResultClass:
    """Test Command class without result_class attribute."""
    
    class CommandWithoutResult(Command):
        """Test command without result_class."""
        name = "test_without_result"
        
        async def execute(self, **kwargs):
            return SuccessResult(data={"test": "data"})
    
    def test_get_result_schema_without_result_class(self):
        """Test get_result_schema when result_class is not defined."""
        schema = self.CommandWithoutResult.get_result_schema()
        assert schema == {}


class TestCommandNameExtraction:
    """Test command name extraction logic."""
    
    class TestCommand(Command):
        """Test command with default name extraction."""
        # No name attribute defined
        
        async def execute(self, **kwargs):
            return SuccessResult(data={"test": "data"})
    
    class EchoCommand(Command):
        """Test command ending with 'Command'."""
        # No name attribute defined
        
        async def execute(self, **kwargs):
            return SuccessResult(data={"test": "data"})
    
    class CustomCommand(Command):
        """Test command with explicit name."""
        name = "custom"
        
        async def execute(self, **kwargs):
            return SuccessResult(data={"test": "data"})
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_run_with_none_kwargs_creates_empty_dict(self, mock_registry):
        """Test that run method creates empty dict when kwargs is None."""
        mock_registry.get_command.return_value = self.TestCommand
        mock_registry.has_instance.return_value = False
        
        result = await self.TestCommand.run(**{})
        
        # Verify that kwargs was converted to empty dict
        assert isinstance(result, SuccessResult)
        mock_registry.get_command.assert_called_once_with("test")
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_command_name_extraction_from_class_name(self, mock_registry):
        """Test command name extraction from class name."""
        mock_registry.get_command.return_value = self.TestCommand
        mock_registry.has_instance.return_value = False
        
        result = await self.TestCommand.run()
        
        # Should extract "test" from "TestCommand"
        mock_registry.get_command.assert_called_once_with("test")
        assert isinstance(result, SuccessResult)
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_command_name_extraction_removes_command_suffix(self, mock_registry):
        """Test command name extraction removes 'Command' suffix."""
        mock_registry.get_command.return_value = self.EchoCommand
        mock_registry.has_instance.return_value = False
        
        result = await self.EchoCommand.run()
        
        # Should extract "echo" from "EchoCommand"
        mock_registry.get_command.assert_called_once_with("echo")
        assert isinstance(result, SuccessResult)
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_command_name_extraction_uses_explicit_name(self, mock_registry):
        """Test command name extraction uses explicit name attribute."""
        mock_registry.get_command.return_value = self.CustomCommand
        mock_registry.has_instance.return_value = False
        
        result = await self.CustomCommand.run()
        
        # Should use explicit name "custom"
        mock_registry.get_command.assert_called_once_with("custom")
        assert isinstance(result, SuccessResult)


class TestTimeoutErrorHandling:
    """Test TimeoutError handling with code and data attributes."""
    
    class TestCommand(Command):
        """Test command that raises TimeoutError."""
        name = "test_timeout"
        
        async def execute(self, **kwargs):
            error = TimeoutError("Operation timed out")
            error.code = 408
            error.data = {"timeout": 30}
            raise error
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_run_timeout_error_with_code_and_data(self, mock_registry):
        """Test run method handles TimeoutError with code and data attributes."""
        class ErrorCommand(self.TestCommand):
            async def execute(self, **kwargs):
                error = TimeoutError("Operation timed out")
                error.code = 408
                error.data = {"timeout": 30}
                raise error
        
        mock_registry.get_command.return_value = ErrorCommand
        mock_registry.has_instance.return_value = False
        
        result = await ErrorCommand.run()
        
        assert isinstance(result, ErrorResult)
        assert "Operation timed out" in result.message
        assert result.code == -32603  # InternalError code
        assert "Operation timed out" in result.details["original_error"]


class TestGenerateExamplesEdgeCases:
    """Test _generate_examples method edge cases."""
    
    class TestCommand(Command):
        """Test command for examples generation."""
        name = "test_examples"
        
        async def execute(self, **kwargs):
            return SuccessResult(data={"test": "data"})
    
    def test_generate_examples_with_all_optional_params(self):
        """Test _generate_examples with all optional parameters."""
        # Mock get_param_info to return all optional parameters
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "param1": {"required": False, "type": "str", "default": "default1"},
                "param2": {"required": False, "type": "int", "default": 10},
                "param3": {"required": False, "type": "bool", "default": True}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples: one without params, one with all params
            assert len(examples) == 2
            
            # First example should be without parameters
            assert examples[0]["command"] == "test_examples"
            assert "params" not in examples[0]
            
            # Second example should have all parameters with their default values
            assert examples[1]["command"] == "test_examples"
            assert examples[1]["params"]["param1"] == "default1"
            assert examples[1]["params"]["param2"] == 10
            assert examples[1]["params"]["param3"] is True
    
    def test_generate_examples_with_optional_params_no_defaults(self):
        """Test _generate_examples with optional parameters without default values."""
        # Mock get_param_info to return optional parameters without defaults
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "param1": {"required": False, "type": "str"},
                "param2": {"required": False, "type": "int"},
                "param3": {"required": False, "type": "bool"},
                "param4": {"required": False, "type": "List[str]"},
                "param5": {"required": False, "type": "Dict[str, Any]"},
                "param6": {"required": False, "type": "float"},
                "param7": {"required": False, "type": "unknown_type"}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples
            assert len(examples) == 2
            
            # Second example should have all parameters with sample values
            all_params_example = examples[1]
            assert all_params_example["command"] == "test_examples"
            assert all_params_example["params"]["param1"] == "optional_param1"
            assert all_params_example["params"]["param2"] == 0
            assert all_params_example["params"]["param3"] is False
            assert all_params_example["params"]["param4"] == "optional_param4"  # List[str] becomes str due to "str" check first
            assert all_params_example["params"]["param5"] == "optional_param5"  # Dict[str, Any] becomes str due to "str" check first
            assert all_params_example["params"]["param6"] == 0.0
            assert all_params_example["params"]["param7"] is None
    
    def test_generate_examples_with_mixed_required_and_optional(self):
        """Test _generate_examples with mixed required and optional parameters."""
        # Mock get_param_info to return mixed parameters
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "required_param": {"required": True, "type": "str"},
                "optional_param1": {"required": False, "type": "int", "default": 5},
                "optional_param2": {"required": False, "type": "bool"},
                "optional_param3": {"required": False, "type": "List[str]", "default": ["a", "b"]}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples: one with required params, one with all params
            assert len(examples) == 2
            
            # First example should have only required parameters
            required_example = examples[0]
            assert required_example["command"] == "test_examples"
            assert required_example["params"]["required_param"] == "sample_required_param"
            
            # Second example should have all parameters
            all_params_example = examples[1]
            assert all_params_example["command"] == "test_examples"
            assert all_params_example["params"]["required_param"] == "sample_required_param"
            assert all_params_example["params"]["optional_param1"] == 5  # default value
            assert all_params_example["params"]["optional_param2"] == 0  # sample value
            assert all_params_example["params"]["optional_param3"] == ["a", "b"]  # default value 

class TestAdditionalCoverage:
    """Additional tests to achieve 90%+ coverage."""
    
    class TestCommand(Command):
        """Test command for additional coverage."""
        name = "test_additional"
        
        async def execute(self, **kwargs):
            return SuccessResult(data={"test": "data"})
    
    def test_validate_params_with_none_params(self):
        """Test validate_params with None params."""
        result = self.TestCommand.validate_params(None)
        assert result == {}
    
    def test_validate_params_with_empty_string_values(self):
        """Test validate_params with empty string values."""
        params = {
            "param1": "",
            "param2": "null",
            "param3": "NONE",
            "cmdname": None,
            "normal_param": "value"
        }
        result = self.TestCommand.validate_params(params)
        
        # Empty strings should be removed
        assert "param1" not in result
        assert "param2" not in result
        assert "param3" not in result
        # cmdname should be kept as None
        assert result["cmdname"] is None
        # normal_param should be kept
        assert result["normal_param"] == "value"
    
    def test_generate_examples_with_unknown_type(self):
        """Test _generate_examples with unknown parameter type."""
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "param1": {"required": True, "type": "unknown_type"},
                "param2": {"required": False, "type": "another_unknown"}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples
            assert len(examples) == 2
            
            # First example should have required parameters with "..." for unknown type
            required_example = examples[0]
            assert required_example["params"]["param1"] == "..."
            
            # Second example should have all parameters
            all_params_example = examples[1]
            assert all_params_example["params"]["param1"] == "..."
            assert all_params_example["params"]["param2"] is None  # optional unknown type
    
    def test_generate_examples_with_list_and_dict_types(self):
        """Test _generate_examples with List and Dict types."""
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "list_param": {"required": True, "type": "List[str]"},
                "dict_param": {"required": True, "type": "Dict[str, Any]"},
                "optional_list": {"required": False, "type": "List[int]"},
                "optional_dict": {"required": False, "type": "Dict[str, str]"}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples
            assert len(examples) == 2
            
            # First example should have required parameters
            required_example = examples[0]
            assert required_example["params"]["list_param"] == "sample_list_param"  # str check first
            assert required_example["params"]["dict_param"] == "sample_dict_param"  # str check first
            
            # Second example should have all parameters
            all_params_example = examples[1]
            assert all_params_example["params"]["list_param"] == "sample_list_param"
            assert all_params_example["params"]["dict_param"] == "sample_dict_param"
            assert all_params_example["params"]["optional_list"] == 0  # List[int] becomes 0 for optional (int check first)
            assert all_params_example["params"]["optional_dict"] == "optional_optional_dict"  # Dict[str, str] becomes str for optional
    
    def test_generate_examples_with_float_types(self):
        """Test _generate_examples with float types."""
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "float_param": {"required": True, "type": "float"},
                "optional_float": {"required": False, "type": "float"}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples
            assert len(examples) == 2
            
            # First example should have required parameters
            required_example = examples[0]
            assert required_example["params"]["float_param"] == 1.0
            
            # Second example should have all parameters
            all_params_example = examples[1]
            assert all_params_example["params"]["float_param"] == 1.0
            assert all_params_example["params"]["optional_float"] == 0.0
    
    def test_generate_examples_with_bool_types(self):
        """Test _generate_examples with bool types."""
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "bool_param": {"required": True, "type": "bool"},
                "optional_bool": {"required": False, "type": "bool"}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples
            assert len(examples) == 2
            
            # First example should have required parameters
            required_example = examples[0]
            assert required_example["params"]["bool_param"] is True
            
            # Second example should have all parameters
            all_params_example = examples[1]
            assert all_params_example["params"]["bool_param"] is True
            assert all_params_example["params"]["optional_bool"] is False
    
    def test_generate_examples_with_int_types(self):
        """Test _generate_examples with int types."""
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "int_param": {"required": True, "type": "int"},
                "optional_int": {"required": False, "type": "int"}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples
            assert len(examples) == 2
            
            # First example should have required parameters
            required_example = examples[0]
            assert required_example["params"]["int_param"] == 1
            
            # Second example should have all parameters
            all_params_example = examples[1]
            assert all_params_example["params"]["int_param"] == 1
            assert all_params_example["params"]["optional_int"] == 0 

    def test_generate_examples_with_list_and_dict_types_for_required(self):
        """Test _generate_examples with List and Dict types for required parameters."""
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "list_param": {"required": True, "type": "List[str]"},
                "dict_param": {"required": True, "type": "Dict[str, Any]"},
                "optional_param": {"required": False, "type": "str"}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples
            assert len(examples) == 2
            
            # First example should have required parameters with actual list/dict values
            required_example = examples[0]
            assert required_example["params"]["list_param"] == "sample_list_param"  # List[str] becomes str
            assert required_example["params"]["dict_param"] == "sample_dict_param"  # Dict[str, Any] becomes str
            
            # Second example should have all parameters
            all_params_example = examples[1]
            assert all_params_example["params"]["list_param"] == "sample_list_param"  # List[str] becomes str
            assert all_params_example["params"]["dict_param"] == "sample_dict_param"  # Dict[str, Any] becomes str
            assert all_params_example["params"]["optional_param"] == "optional_optional_param"
    
    def test_generate_examples_with_list_and_dict_types_for_optional(self):
        """Test _generate_examples with List and Dict types for optional parameters."""
        with patch.object(self.TestCommand, 'get_param_info') as mock_get_param_info:
            mock_get_param_info.return_value = {
                "required_param": {"required": True, "type": "str"},
                "optional_list": {"required": False, "type": "List[int]"},
                "optional_dict": {"required": False, "type": "Dict[str, str]"}
            }
            
            examples = self.TestCommand._generate_examples(mock_get_param_info.return_value)
            
            # Should generate 2 examples
            assert len(examples) == 2
            
            # First example should have required parameters
            required_example = examples[0]
            assert required_example["params"]["required_param"] == "sample_required_param"
            
            # Second example should have all parameters
            all_params_example = examples[1]
            assert all_params_example["params"]["required_param"] == "sample_required_param"
            assert all_params_example["params"]["optional_list"] == 0  # List[int] becomes 0 for optional (int check first)
            assert all_params_example["params"]["optional_dict"] == "optional_optional_dict"  # Dict[str, str] becomes str for optional 

class TestErrorHandlingCoverage:
    """Tests for error handling coverage."""
    
    class TestCommand(Command):
        """Test command for error handling."""
        name = "test_errors"
        
        async def execute(self, **kwargs):
            return SuccessResult(data={"test": "data"})
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_run_validation_error_with_code_and_data(self, mock_registry):
        """Test run method handles ValidationError with code and data attributes."""
        class ErrorCommand(self.TestCommand):
            async def execute(self, **kwargs):
                error = ValidationError("Validation failed")
                error.code = 400
                error.data = {"field": "value"}
                raise error
        
        mock_registry.get_command.return_value = ErrorCommand
        mock_registry.has_instance.return_value = False
        
        result = await ErrorCommand.run()
        
        assert isinstance(result, ErrorResult)
        assert result.message == "Validation failed"
        assert result.code == 400
        assert result.details == {"field": "value"}
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_run_invalid_params_error_with_code_and_data(self, mock_registry):
        """Test run method handles InvalidParamsError with code and data attributes."""
        class ErrorCommand(self.TestCommand):
            async def execute(self, **kwargs):
                error = InvalidParamsError("Invalid parameters")
                error.code = 400
                error.data = {"param": "invalid"}
                raise error
        
        mock_registry.get_command.return_value = ErrorCommand
        mock_registry.has_instance.return_value = False
        
        result = await ErrorCommand.run()
        
        assert isinstance(result, ErrorResult)
        assert result.message == "Invalid parameters"
        assert result.code == 400
        assert result.details == {"param": "invalid"}
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_run_not_found_error_with_code_and_data(self, mock_registry):
        """Test run method handles NotFoundError with code and data attributes."""
        class ErrorCommand(self.TestCommand):
            async def execute(self, **kwargs):
                error = NotFoundError("Resource not found")
                error.code = 404
                error.data = {"resource": "missing"}
                raise error
        
        mock_registry.get_command.return_value = ErrorCommand
        mock_registry.has_instance.return_value = False
        
        result = await ErrorCommand.run()
        
        assert isinstance(result, ErrorResult)
        assert result.message == "Resource not found"
        assert result.code == 404
        assert result.details == {"resource": "missing"}
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_run_command_error_with_code_and_data(self, mock_registry):
        """Test run method handles CommandError with code and data attributes."""
        class ErrorCommand(self.TestCommand):
            async def execute(self, **kwargs):
                error = CommandError("Command execution failed")
                error.code = 500
                error.data = {"command": "failed"}
                raise error
        
        mock_registry.get_command.return_value = ErrorCommand
        mock_registry.has_instance.return_value = False
        
        result = await ErrorCommand.run()
        
        assert isinstance(result, ErrorResult)
        assert result.message == "Command execution failed"
        assert result.code == 500
        assert result.details == {"command": "failed"}
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_run_with_existing_instance(self, mock_registry):
        """Test run method creates new instance."""
        mock_registry.get_command.return_value = self.TestCommand
        mock_registry.has_instance.return_value = True
        
        result = await self.TestCommand.run()
        
        assert isinstance(result, SuccessResult)
        mock_registry.get_command.assert_called_once_with("test_errors")
    
    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    async def test_run_with_priority_command_not_found(self, mock_registry):
        """Test run method when priority command is not found."""
        mock_registry.get_command.side_effect = NotFoundError("Command 'test_errors' not found")
        
        result = await self.TestCommand.run()
        
        assert isinstance(result, ErrorResult)
        assert "not found" in result.message
        assert result.code == -32601  # Method not found 