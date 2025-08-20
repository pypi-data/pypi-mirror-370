#!/usr/bin/env python3
"""
Simple test server to get OpenAPI schema.
"""

import uvicorn
from fastapi import FastAPI
from mcp_proxy_adapter.custom_openapi import custom_openapi_with_fallback

# Create FastAPI app
app = FastAPI(
    title="Test MCP Proxy Server",
    description="Test server for OpenAPI schema",
    version="1.0.0"
)

# Set custom OpenAPI generator
app.openapi = lambda: custom_openapi_with_fallback(app)

# Add OpenAPI endpoint
@app.get("/openapi.json")
async def get_openapi_schema():
    """Returns OpenAPI schema."""
    return custom_openapi_with_fallback(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 