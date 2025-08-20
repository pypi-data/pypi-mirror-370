# Deployment Guide

This guide describes various methods for deploying the MCP Proxy Adapter.

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for containerized deployment)
- Access to the target deployment environment

## Deployment Methods

### 1. Direct Python Installation

For simple deployments or development environments:

1. Install the package:
   ```bash
   pip install mcp-proxy-adapter
   ```

2. Create a configuration file:
   ```bash
   cat > config.json << EOF
   {
     "host": "0.0.0.0",
     "port": 8000,
     "log_level": "INFO",
     "log_file": "logs/mcp_proxy.log",
     "cors_origins": ["*"],
     "api_keys": ["your-api-key-here"]
   }
   EOF
   ```

3. Start the service:
   ```bash
   mcp-proxy-adapter --config config.json
   ```

### 2. Docker Container

For containerized deployment:

1. Pull the Docker image:
   ```bash
   docker pull organization/mcp-proxy-adapter:latest
   ```

2. Create a configuration file:
   ```bash
   cat > config.json << EOF
   {
     "host": "0.0.0.0",
     "port": 8000,
     "log_level": "INFO",
     "log_file": "logs/mcp_proxy.log",
     "cors_origins": ["*"],
     "api_keys": ["your-api-key-here"]
   }
   EOF
   ```

3. Run the container:
   ```bash
   docker run -p 8000:8000 -v $(pwd)/config.json:/app/config.json -v $(pwd)/logs:/app/logs organization/mcp-proxy-adapter:latest
   ```

### 3. Docker Compose

For more complex deployments:

1. Create a docker-compose.yml file:
   ```yaml
   version: '3'

   services:
     mcp-proxy-adapter:
       image: organization/mcp-proxy-adapter:latest
       ports:
         - "8000:8000"
       volumes:
         - ./config.json:/app/config.json
         - ./logs:/app/logs
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 5s
   ```

2. Create a configuration file:
   ```bash
   cat > config.json << EOF
   {
     "host": "0.0.0.0",
     "port": 8000,
     "log_level": "INFO",
     "log_file": "logs/mcp_proxy.log",
     "cors_origins": ["*"],
     "api_keys": ["your-api-key-here"]
   }
   EOF
   ```

3. Start the service:
   ```bash
   docker-compose up -d
   ```

### 4. Automated Deployment

For continuous deployment:

1. Set up a deployment server with SSH access
2. Configure environment variables for secrets
3. Use the included deployment script:
   ```bash
   ./scripts/deploy.sh production
   ```

4. Or integrate with CI/CD systems like GitHub Actions or Jenkins

## Environment-Specific Configurations

We provide sample configurations for different environments:

- `config.development.json`: For local development
- `config.staging.json`: For the staging environment
- `config.production.json`: For the production environment

Choose the appropriate configuration for your deployment environment.

## Post-Deployment Verification

After deployment, verify that the service is running correctly:

1. Check the health endpoint:
   ```bash
   curl http://your-server:8000/api/health
   ```

2. Test a simple command:
   ```bash
   curl -X POST http://your-server:8000/api/v1/execute \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -d '{"jsonrpc": "2.0", "method": "hello_world", "params": {"name": "User"}, "id": 1}'
   ```

3. Check the logs for any errors:
   ```bash
   tail -f logs/mcp_proxy.log
   ```

## Troubleshooting

If you encounter issues during deployment:

1. Check the logs for error messages
2. Verify that the configuration file is valid JSON
3. Ensure that the environment variables are set correctly
4. Check that the ports are not already in use
5. Verify that the API keys are correctly configured 