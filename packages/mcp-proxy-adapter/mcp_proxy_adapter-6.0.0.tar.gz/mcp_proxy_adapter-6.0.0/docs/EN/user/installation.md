# Installation

This guide describes how to install and deploy the MCP Proxy service.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) Docker for containerized deployment

## Installation from PyPI

The simplest way to install the package is from PyPI:

```bash
pip install mcp-proxy
```

## Installation from Source

To install from source, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/organization/mcp-proxy.git
   cd mcp-proxy
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

## Docker Installation

To use the Docker image:

1. Pull the image:
   ```bash
   docker pull organization/mcp-proxy:latest
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 -v /path/to/config.json:/app/config.json organization/mcp-proxy:latest
   ```

## Verifying the Installation

To verify that the installation was successful, run:

```bash
mcp-proxy --version
```

This should display the current version of the MCP Proxy service. 