#!/usr/bin/env python3
"""
Simple server with fixed OpenAPI generator.
"""

import uvicorn
import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

from fastapi import FastAPI
from mcp_proxy_adapter.custom_openapi import CustomOpenAPIGenerator
from mcp_proxy_adapter.commands.command_registry import registry

# Create FastAPI app
app = FastAPI(
    title="Extended MCP Proxy Server",
    description="Advanced MCP Proxy Adapter server with custom commands and hooks",
    version="2.1.0"
)

async def generate_openapi_schema():
    """Generate OpenAPI schema with custom commands."""
    # Initialize commands
    await registry.reload_system()
    
    # Load custom commands
    custom_commands = [
        "echo_command",
        "custom_help_command", 
        "custom_health_command",
        "manual_echo_command"
    ]
    
    for cmd_name in custom_commands:
        try:
            module = __import__(cmd_name)
            if hasattr(module, 'EchoCommand'):
                registry.register_custom(module.EchoCommand())
            elif hasattr(module, 'CustomHelpCommand'):
                registry.register_custom(module.CustomHelpCommand())
            elif hasattr(module, 'CustomHealthCommand'):
                registry.register_custom(module.CustomHealthCommand())
            elif hasattr(module, 'ManualEchoCommand'):
                registry.register_custom(module.ManualEchoCommand())
        except Exception as e:
            print(f"Warning: Failed to load {cmd_name}: {e}")
    
    # Generate schema
    generator = CustomOpenAPIGenerator()
    return generator.generate(
        title="Extended MCP Proxy Server",
        description="Advanced MCP Proxy Adapter server with custom commands and hooks",
        version="2.1.0"
    )

# Set custom OpenAPI generator
@app.on_event("startup")
async def startup_event():
    """Initialize OpenAPI schema on startup."""
    app.openapi_schema = await generate_openapi_schema()

@app.get("/openapi.json")
async def get_openapi_schema():
    """Returns OpenAPI schema."""
    if not hasattr(app, 'openapi_schema'):
        app.openapi_schema = await generate_openapi_schema()
    return app.openapi_schema

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 