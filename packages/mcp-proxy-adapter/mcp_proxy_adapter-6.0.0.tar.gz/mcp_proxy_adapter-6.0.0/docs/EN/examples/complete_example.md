# Complete Example

The complete example demonstrates a production-ready microservice with Docker support, environment-specific configurations, and advanced features.

## Structure

```
complete_example/
├── __init__.py           # Package initialization
├── cache/                # Cache directory
├── commands/             # Commands directory
│   ├── __init__.py
│   ├── health_command.py # Health check command
│   ├── config_command.py # Configuration management command
│   ├── file_command.py   # File operations command
│   └── system_command.py # System information command
├── configs/              # Configuration files
│   ├── development.yaml  # Development environment config
│   ├── production.yaml   # Production environment config
│   └── testing.yaml      # Testing environment config
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── logs/                 # Logs directory
├── README.md             # Documentation
├── requirements.txt      # Python dependencies
├── server.py             # Server initialization
└── tests/                # Tests directory
    ├── conftest.py       # Test configuration
    └── ...               # Command tests
```

## Key Components

### Docker Support

The example includes Docker configuration for containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV MCP_ENV=production
ENV CONFIG_PATH=/app/configs/production.yaml

CMD ["python", "server.py"]
```

And Docker Compose for orchestration:

```yaml
version: '3'

services:
  microservice:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./configs:/app/configs
      - ./logs:/app/logs
      - ./cache:/app/cache
    environment:
      - MCP_ENV=production
      - CONFIG_PATH=/app/configs/production.yaml
    networks:
      - mcp-network

networks:
  mcp-network:
    external: true
```

### Environment-Specific Configuration

The example demonstrates using different configuration files for various environments:

```
configs/
├── development.yaml  # Local development settings
├── production.yaml   # Production settings
└── testing.yaml      # Test environment settings
```

Configuration loading:

```python
# Load configuration based on environment
env = os.getenv("MCP_ENV", "development")
config_path = os.getenv("CONFIG_PATH", f"configs/{env}.yaml")

service = mcp.MicroService(
    title="Complete Example Microservice",
    description="Complete example with Docker and advanced features",
    version="1.0.0",
    config_path=config_path
)
```

### Advanced Commands

#### Health Check Command

```python
class HealthCommand(Command):
    """Command for checking service health."""
    
    name = "health"
    result_class = HealthResult
    
    async def execute(self, check_type: str = "basic") -> HealthResult:
        """
        Check service health.
        
        Args:
            check_type: Type of health check (basic or detailed)
            
        Returns:
            Health check result
        """
        # Get basic system information
        system_info = {
            "hostname": socket.gethostname(),
            "pid": os.getpid(),
            "uptime": time.time() - psutil.Process(os.getpid()).create_time(),
            "memory_usage": psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024),
        }
        
        # Add detailed metrics for detailed check
        if check_type == "detailed":
            system_info.update({
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "open_files": len(psutil.Process(os.getpid()).open_files()),
                "connections": len(psutil.Process(os.getpid()).connections()),
            })
            
        return HealthResult(
            status="ok",
            timestamp=datetime.datetime.now().isoformat(),
            system_info=system_info
        )
```

## Running the Example

### With Docker

```bash
# Navigate to the project directory
cd examples/complete_example

# Build and run the Docker container
docker-compose up --build
```

### Without Docker

```bash
# Navigate to the project directory
cd examples/complete_example

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

The server will be available at http://localhost:8000.

## Key Concepts Demonstrated

1. Containerization with Docker
2. Environment-specific configuration
3. Volume mounting for logs and cache
4. Health checks and monitoring
5. System information commands
6. Configuration management
7. Production-ready setup
8. Externalized configuration
9. Resource isolation and management 