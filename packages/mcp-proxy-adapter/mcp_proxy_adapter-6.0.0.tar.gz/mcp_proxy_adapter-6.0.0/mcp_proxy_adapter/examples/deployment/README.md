# Deployment Examples

This directory contains deployment examples for the MCP Proxy Adapter framework.

## Files

### Docker Deployment
- `Dockerfile` - Docker image configuration for the framework
- `docker-compose.yml` - Docker Compose configuration for easy deployment
- `run_docker.sh` - Script to run the application in Docker

### Local Deployment
- `run.sh` - Script to run the application locally

### Configuration Files
- `config.json` - Default configuration file
- `config.development.json` - Development environment configuration
- `config.staging.json` - Staging environment configuration  
- `config.production.json` - Production environment configuration

## Usage

### Local Development
```bash
./run.sh
```

### Docker Deployment
```bash
./run_docker.sh
```

### Docker Compose
```bash
docker-compose up -d
```

## Configuration

Copy the appropriate configuration file to your project root:
```bash
cp config.development.json config.json
```

## Notes

- These are example configurations and should be customized for your specific use case
- The framework itself is designed to be used as a library, not as a standalone application
- Modify the configuration files according to your deployment requirements 