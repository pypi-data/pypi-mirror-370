"""
Custom Help Command Example

A custom help command that provides enhanced help information.
"""

from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import NotFoundError


class CustomHelpResult(CommandResult):
    """
    Result of the custom help command execution.
    """
    
    def __init__(self, commands_info: Optional[Dict[str, Any]] = None, 
                 command_info: Optional[Dict[str, Any]] = None,
                 custom_info: Optional[Dict[str, Any]] = None):
        """
        Initialize custom help command result.
        
        Args:
            commands_info: Information about all commands
            command_info: Information about a specific command
            custom_info: Additional custom information
        """
        self.commands_info = commands_info
        self.command_info = command_info
        self.custom_info = custom_info or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        if self.command_info is not None:
            return {
                "cmdname": self.command_info.get("name", "unknown"),
                "info": {
                    "description": self.command_info.get("description", ""),
                    "summary": self.command_info.get("summary", ""),
                    "params": self.command_info.get("params", {}),
                    "examples": self.command_info.get("examples", []),
                    "custom_help": True
                }
            }
        
        if self.commands_info is None:
            return {
                "tool_info": {
                    "name": "Custom MCP-Proxy API Service",
                    "description": "Enhanced JSON-RPC API with custom commands",
                    "version": "2.0.0",
                    "custom_help": True
                },
                "help_usage": {
                    "description": "Get enhanced information about commands",
                    "examples": [
                        {"command": "help", "description": "List of all available commands"},
                        {"command": "help", "params": {"cmdname": "command_name"}, "description": "Get detailed information about a specific command"}
                    ]
                },
                "commands": {},
                "total": 0,
                "custom_features": self.custom_info
            }
        
        result = self.commands_info.copy()
        commands = result.get("commands", {})
        result["total"] = len(commands)
        result["custom_help"] = True
        result["custom_features"] = self.custom_info
        
        return result
    
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
                "cmdname": {
                    "type": "string",
                    "description": "Name of the command"
                },
                "info": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "summary": {"type": "string"},
                        "params": {"type": "object"},
                        "examples": {"type": "array"},
                        "custom_help": {"type": "boolean"}
                    }
                },
                "tool_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "version": {"type": "string"},
                        "custom_help": {"type": "boolean"}
                    }
                },
                "help_usage": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "examples": {"type": "array"}
                    }
                },
                "commands": {"type": "object"},
                "total": {"type": "integer"},
                "custom_features": {"type": "object"}
            }
        }


class CustomHelpCommand(Command):
    """
    Custom help command with enhanced functionality.
    """
    
    name = "help"
    result_class = CustomHelpResult
    
    async def execute(self, cmdname: Optional[str] = None, **kwargs) -> CustomHelpResult:
        """
        Execute custom help command.
        
        Args:
            cmdname: Name of specific command to get help for
            **kwargs: Additional parameters
            
        Returns:
            CustomHelpResult: Custom help command result
        """
        try:
            # Check if hook processed this request
            request_id = kwargs.get("request_id")
            hook_processed = kwargs.get("hook_processed", False)
            
            if cmdname is not None:
                # Get specific command info
                command_info = registry.get_command_info(cmdname)
                if command_info is None:
                    raise NotFoundError(f"Command '{cmdname}' not found")
                
                custom_info = {
                    "enhanced": True, 
                    "command_specific": True,
                    "request_id": request_id,
                    "hook_processed": hook_processed
                }
                
                return CustomHelpResult(
                    command_info=command_info,
                    custom_info=custom_info
                )
            else:
                # Get all commands info
                commands_info = registry.get_all_commands_info()
                
                custom_info = {
                    "enhanced": True,
                    "total_commands": len(commands_info.get("commands", {})),
                    "custom_commands": ["echo", "help", "health"],
                    "request_id": request_id,
                    "hook_processed": hook_processed
                }
                
                return CustomHelpResult(
                    commands_info=commands_info,
                    custom_info=custom_info
                )
                
        except Exception as e:
            # Return error result
            return CustomHelpResult(
                custom_info={
                    "error": str(e),
                    "enhanced": True,
                    "error_handling": True,
                    "request_id": request_id,
                    "hook_processed": hook_processed
                }
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
                "cmdname": {
                    "type": "string",
                    "description": "Name of specific command to get help for"
                }
            }
        } 