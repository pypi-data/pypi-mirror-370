# Protocol Configuration Examples

This directory contains example configuration files for different protocol setups in the MCP Proxy Adapter.

## Overview

The protocol management system allows you to configure which protocols (HTTP, HTTPS, MTLS) are allowed and enabled for your server. Each protocol can be configured with its own port and settings.

## Configuration Structure

All configuration files follow this structure:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": true,
    "log_level": "INFO"
  },
  "logging": {
    "level": "INFO",
    "log_dir": "./logs",
    "console_output": true
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "mcp_proxy_adapter.commands"
  },
  "ssl": {
    "enabled": false,
    "mode": "https_only",
    "cert_file": "path/to/cert.pem",
    "key_file": "path/to/key.pem",
    "ca_cert": "path/to/ca.pem",
    "verify_client": false,
    "client_cert_required": false
  },
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["http"],
    "http": {
      "enabled": true,
      "port": 8000
    },
    "https": {
      "enabled": false,
      "port": 8443
    },
    "mtls": {
      "enabled": false,
      "port": 9443
    }
  }
}
```

## Available Configurations

### 1. HTTP Only (`http_only_config.json`)

**Purpose:** Basic HTTP server without SSL/TLS encryption.

**Features:**
- Only HTTP protocol enabled
- No SSL/TLS encryption
- Port 8000 for HTTP traffic
- Suitable for development and internal networks

**Use Cases:**
- Development environments
- Internal network services
- Testing and debugging
- Local development servers

### 2. HTTPS Only (`https_only_config.json`)

**Purpose:** Secure HTTPS server with SSL/TLS encryption.

**Features:**
- Only HTTPS protocol enabled
- SSL/TLS encryption required
- Port 8443 for HTTPS traffic
- Server certificate authentication

**Use Cases:**
- Production web services
- Public-facing APIs
- Secure data transmission
- E-commerce applications

### 3. MTLS Only (`mtls_only_config.json`)

**Purpose:** Mutual TLS server with client certificate authentication.

**Features:**
- Only MTLS protocol enabled
- SSL/TLS encryption required
- Client certificate authentication
- Port 9443 for MTLS traffic
- Highest security level

**Use Cases:**
- High-security environments
- API-to-API communication
- Financial services
- Government systems
- Enterprise internal services

## Protocol Configuration Options

### Protocols Section

```json
"protocols": {
  "enabled": true,                    // Enable/disable protocol management
  "allowed_protocols": ["http"],      // List of allowed protocols
  "http": {
    "enabled": true,                  // Enable HTTP protocol
    "port": 8000                      // HTTP port
  },
  "https": {
    "enabled": false,                 // Enable HTTPS protocol
    "port": 8443                      // HTTPS port
  },
  "mtls": {
    "enabled": false,                 // Enable MTLS protocol
    "port": 9443                      // MTLS port
  }
}
```

### SSL Section

```json
"ssl": {
  "enabled": true,                    // Enable SSL/TLS
  "mode": "https_only",               // SSL mode: "https_only" or "mtls"
  "cert_file": "path/to/cert.pem",    // Server certificate file
  "key_file": "path/to/key.pem",      // Server private key file
  "ca_cert": "path/to/ca.pem",        // CA certificate file (for MTLS)
  "verify_client": true,              // Verify client certificates (MTLS)
  "client_cert_required": true        // Require client certificates (MTLS)
}
```

## Usage Examples

### Starting Server with HTTP Only

```bash
cd mcp_proxy_adapter/examples/basic_server
cp ../protocol_configs/http_only_config.json config.json
python server.py
```

### Starting Server with HTTPS Only

```bash
cd mcp_proxy_adapter/examples/basic_server
cp ../protocol_configs/https_only_config.json config.json
python server.py
```

### Starting Server with MTLS Only

```bash
cd mcp_proxy_adapter/examples/basic_server
cp ../protocol_configs/mtls_only_config.json config.json
python server.py
```

## Testing Configurations

Use the protocol testing utility to validate your configurations:

```bash
python scripts/test_protocol_configs.py
```

This will test all configuration files and provide detailed feedback about:
- Protocol validation
- SSL configuration
- Port assignments
- Certificate requirements

## Security Considerations

### HTTP Only
- **Security Level:** Low
- **Use:** Development, internal networks only
- **Risks:** No encryption, data transmitted in plain text

### HTTPS Only
- **Security Level:** Medium
- **Use:** Production environments
- **Benefits:** Encrypted communication, server authentication
- **Requirements:** Valid SSL certificates

### MTLS Only
- **Security Level:** High
- **Use:** High-security environments
- **Benefits:** Encrypted communication, mutual authentication
- **Requirements:** Valid SSL certificates for both server and clients

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**
   - Ensure certificate files exist and are readable
   - Check certificate validity and expiration
   - Verify certificate chain is complete

2. **Port Conflicts**
   - Ensure ports are not already in use
   - Check firewall settings
   - Verify port permissions

3. **Protocol Validation Errors**
   - Check that enabled protocols are in allowed_protocols list
   - Ensure SSL is enabled for HTTPS/MTLS protocols
   - Verify certificate files are configured for SSL protocols

### Validation Commands

```bash
# Test protocol configuration
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "protocol_management",
    "params": {"action": "validate_config"},
    "id": 1
  }'

# Get protocol information
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "protocol_management",
    "params": {"action": "get_info"},
    "id": 1
  }'
```

## Related Documentation

- [Protocol Management Command](../docs/EN/commands/protocol_management_command.md)
- [SSL/TLS Configuration](../docs/EN/user/configuration.md)
- [Security Best Practices](../docs/EN/user/deployment.md) 