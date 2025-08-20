#!/bin/bash

# MCP Proxy Adapter - Docker Deployment Script
# This script runs the framework in Docker

# Function to extract value from JSON config
function get_json_value {
    local json_file=$1
    local json_path=$2
    
    python3 -c "
import json
with open('$json_file', 'r') as f:
    config = json.load(f)
path = '$json_path'.split('.')
result = config
for key in path:
    result = result.get(key, {})
print(result)
"
}

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/config.json"

# Check if config.json exists, copy from examples if not
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config file not found, copying from examples..."
    cp "$(dirname "${BASH_SOURCE[0]}")/config.json" "$CONFIG_FILE"
fi

# Create necessary directories
mkdir -p "$PROJECT_ROOT/logs" "$PROJECT_ROOT/data" "$PROJECT_ROOT/cache"

# Extract values from configuration
CONTAINER_NAME=$(get_json_value "$CONFIG_FILE" "docker.container_name")
SERVICE_PORT=$(get_json_value "$CONFIG_FILE" "server.port")
USER_ID=$(id -u)
GROUP_ID=$(id -g)

# Use default values if not defined in config
CONTAINER_NAME=${CONTAINER_NAME:-mcp-proxy-adapter}
SERVICE_PORT=${SERVICE_PORT:-8000}
HOST_PORT=${SERVICE_PORT}

echo "Using configuration:"
echo "  Container name: $CONTAINER_NAME"
echo "  Port mapping: 127.0.0.1:$HOST_PORT -> $SERVICE_PORT"
echo "  User/Group: $USER_ID:$GROUP_ID"

# Export variables for docker-compose
export CONTAINER_NAME=$CONTAINER_NAME
export SERVICE_PORT=$SERVICE_PORT
export HOST_PORT=$HOST_PORT
export USER_ID=$USER_ID
export GROUP_ID=$GROUP_ID

# Stop container if it already exists
docker-compose -f "$(dirname "${BASH_SOURCE[0]}")/docker-compose.yml" down

# Start container
docker-compose -f "$(dirname "${BASH_SOURCE[0]}")/docker-compose.yml" up -d

# Check if we need to connect to additional network
NETWORK=$(get_json_value "$CONFIG_FILE" "docker.network")
if [ ! -z "$NETWORK" ] && [ "$NETWORK" != "{}" ]; then
    echo "Connecting to network: $NETWORK"
    # Check if network exists
    if docker network inspect "$NETWORK" &>/dev/null; then
        # Connect container to network if not already connected
        if ! docker network inspect "$NETWORK" | grep -q "$CONTAINER_NAME"; then
            docker network connect "$NETWORK" "$CONTAINER_NAME"
            echo "Container connected to network: $NETWORK"
        else
            echo "Container already connected to network: $NETWORK"
        fi
    else
        echo "Warning: Network $NETWORK does not exist"
    fi
fi

echo "Container started. Use the following command to check logs:"
echo "  docker logs $CONTAINER_NAME" 