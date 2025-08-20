#!/bin/bash

# MCP Proxy Adapter - Local Development Script
# This script runs the framework locally for development

# Variables
HOST_PORT=${HOST_PORT:-8000}
CONFIG_PATH=${CONFIG_PATH:-"config.json"}
LOG_LEVEL=${LOG_LEVEL:-"INFO"}

# Get the project root directory (3 levels up from this script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

echo "Starting MCP Proxy Adapter locally..."
echo "Project root: $PROJECT_ROOT"
echo "Config path: $CONFIG_PATH"
echo "Port: $HOST_PORT"

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Install dependencies if needed
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
    source "$PROJECT_ROOT/.venv/bin/activate"
    pip install -r "$PROJECT_ROOT/requirements.txt"
fi

# Copy config file if it doesn't exist
if [ ! -f "$PROJECT_ROOT/config.json" ]; then
    echo "Copying default config..."
    cp "$(dirname "${BASH_SOURCE[0]}")/config.json" "$PROJECT_ROOT/config.json"
fi

# Run the application
cd "$PROJECT_ROOT"
python -m uvicorn mcp_proxy_adapter.api.app:create_app --host 0.0.0.0 --port $HOST_PORT --reload

echo "MCP Proxy Adapter started on http://localhost:$HOST_PORT" 