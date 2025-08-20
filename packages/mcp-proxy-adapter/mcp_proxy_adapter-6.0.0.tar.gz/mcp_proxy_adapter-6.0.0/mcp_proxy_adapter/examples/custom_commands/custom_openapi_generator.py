"""
Custom OpenAPI generator example for the extended server.

This demonstrates how to create a custom OpenAPI schema generator
that can be registered with the framework.
"""

from typing import Dict, Any
from fastapi import FastAPI

from mcp_proxy_adapter.custom_openapi import register_openapi_generator, CustomOpenAPIGenerator
from mcp_proxy_adapter.core.logging import logger


def custom_openapi_generator(app: FastAPI) -> Dict[str, Any]:
    """
    Custom OpenAPI generator for the extended server example.
    
    This generator extends the default generator with additional
    information specific to the extended server.
    
    Args:
        app: FastAPI application instance.
        
    Returns:
        Custom OpenAPI schema.
    """
    # Use the default generator as base
    default_generator = CustomOpenAPIGenerator()
    schema = default_generator.generate(
        title=getattr(app, 'title', None),
        description=getattr(app, 'description', None),
        version=getattr(app, 'version', None)
    )
    
    # Add custom information to the schema
    schema["info"]["description"] += "\n\n## Extended Server Features:\n"
    schema["info"]["description"] += "- Custom commands with hooks\n"
    schema["info"]["description"] += "- Data transformation hooks\n"
    schema["info"]["description"] += "- Command interception hooks\n"
    schema["info"]["description"] += "- Auto-registration and manual registration examples\n"
    
    # Add custom tags
    if "tags" not in schema:
        schema["tags"] = []
    
    schema["tags"].extend([
        {
            "name": "custom-commands",
            "description": "Custom commands with advanced features"
        },
        {
            "name": "hooks",
            "description": "Command hooks for data transformation and interception"
        },
        {
            "name": "registration",
            "description": "Command registration examples"
        }
    ])
    
    # Add custom server information
    if "servers" not in schema:
        schema["servers"] = []
    
    schema["servers"].append({
        "url": "http://localhost:8000",
        "description": "Extended server with custom features"
    })
    
    logger.info("Generated custom OpenAPI schema for extended server")
    return schema


# Register the custom generator
register_openapi_generator("extended_server", custom_openapi_generator) 