"""
Data Transform Command Example

A command that demonstrates advanced hooks with data transformation.
"""

from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult


class DataTransformResult(CommandResult):
    """
    Result of the data transform command execution.
    """
    
    def __init__(self, original_data: Dict[str, Any], transformed_data: Dict[str, Any], 
                 processing_info: Dict[str, Any]):
        """
        Initialize data transform command result.
        
        Args:
            original_data: Original input data
            transformed_data: Transformed output data
            processing_info: Information about processing steps
        """
        self.original_data = original_data
        self.transformed_data = transformed_data
        self.processing_info = processing_info
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        return {
            "original_data": self.original_data,
            "transformed_data": self.transformed_data,
            "processing_info": self.processing_info,
            "command_type": "data_transform"
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for the result.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "original_data": {"type": "object"},
                "transformed_data": {"type": "object"},
                "processing_info": {"type": "object"},
                "command_type": {"type": "string"}
            }
        }


class DataTransformCommand(Command):
    """
    Data transform command for demonstrating advanced hooks.
    """
    
    name = "data_transform"
    result_class = DataTransformResult
    
    async def execute(self, data: Optional[Dict[str, Any]] = None, 
                     transform_type: Optional[str] = None, **kwargs) -> DataTransformResult:
        """
        Execute data transform command.
        
        Args:
            data: Input data to transform
            transform_type: Type of transformation to apply
            **kwargs: Additional parameters
            
        Returns:
            DataTransformResult: Data transform command result
        """
        # Get original data (may be modified by hooks)
        original_data = data or {}
        transform_type = transform_type or "default"
        
        # Apply transformation based on type
        if transform_type == "uppercase":
            transformed_data = {k: str(v).upper() for k, v in original_data.items()}
        elif transform_type == "lowercase":
            transformed_data = {k: str(v).lower() for k, v in original_data.items()}
        elif transform_type == "reverse":
            transformed_data = {k: str(v)[::-1] for k, v in original_data.items()}
        else:
            transformed_data = original_data.copy()
        
        # Add processing info
        processing_info = {
            "transform_type": transform_type,
            "input_keys": list(original_data.keys()),
            "output_keys": list(transformed_data.keys()),
            "hook_enhanced": kwargs.get("hook_enhanced", False),
            "data_modified": kwargs.get("data_modified", False)
        }
        
        return DataTransformResult(
            original_data=original_data,
            transformed_data=transformed_data,
            processing_info=processing_info
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Input data to transform"
                },
                "transform_type": {
                    "type": "string",
                    "enum": ["uppercase", "lowercase", "reverse", "default"],
                    "description": "Type of transformation to apply"
                }
            }
        } 