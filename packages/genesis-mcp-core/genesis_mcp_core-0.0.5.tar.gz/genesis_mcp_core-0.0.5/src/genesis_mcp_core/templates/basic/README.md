# {{ project_name | title }}

**🏥 Healthcare-focused Model Context Protocol server built with Genesis MCP Core SDK**

[![MCP Protocol](https://img.shields.io/badge/MCP-2025--06--18-blue.svg)](https://modelcontextprotocol.io)
[![Genesis SDK](https://img.shields.io/badge/Built%20with-Genesis%20MCP%20Core-green.svg)](../genesis-mcp-core/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Poetry](https://img.shields.io/badge/Poetry-dependency%20management-blue.svg)](https://python-poetry.org)

This MCP server provides seamless integration with healthcare APIs, enabling AI applications to access medical data and workflows through a standardized MCP 2025-06-18 interface.

## ✨ What Makes It Special

- 🚀 **Built with Genesis MCP Core SDK** - Leverages the power of the Genesis ecosystem
- 🏥 **Healthcare-Optimized** - Pre-configured for medical API integration patterns
- 📋 **MCP 2025-06-18 Compliant** - Full support for the latest MCP protocol
- 🔌 **Easy Connector Integration** - Drop JSON files to add new API integrations
- 🛠️ **Developer-Friendly** - Comprehensive tooling and testing framework
- 📊 **Production-Ready** - Health monitoring, structured logging, and error handling

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Poetry for dependency management

### Installation

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your API credentials
   ```

3. **Add your connector configurations:**
   ```bash
   # Place your JSON connector files in connectors/
   # See connectors/README.md for examples
   ```

4. **Run the service:**
   ```bash
   # Development mode
   make dev
   
   # Or manually
   poetry run python main.py
   ```

The service will start on **http://localhost:8002**

### Verify Installation

```bash
# Check server health
make health

# List available tools
make tools

# Run comprehensive tests
make client
```

## 🌐 API Endpoints

| Endpoint | Method | Description | Protocol |
|----------|--------|-------------|----------|
| `/health` | GET | Server health and status | REST |
| `/tools` | GET | List available MCP tools | REST |
| `/mcp` | POST | MCP 2025-06-18 JSON-RPC endpoint | MCP |
| `/sse` | GET | Server-Sent Events streaming | Legacy |
| `/messages` | POST | Legacy message handling | Legacy |

### Example API Usage

```bash
# Health check
curl http://localhost:8002/health

# List tools
curl http://localhost:8002/tools

# MCP initialization
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "id": 1,
    "params": {}
  }'
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=8002
SERVER_DEBUG=false

# Logging Configuration
LOGGING_LEVEL=INFO

# Add your connector-specific variables here
```

### Connector Configuration

Place your healthcare API connector JSON files in the `connectors/` directory:

```
{{ project_name }}/
├── connectors/
│   ├── my_healthcare_api.json    # Your API configuration
│   ├── another_api.json          # Another API configuration
│   └── README.md                 # Configuration guide
├── main.py
└── ...
```

See `connectors/README.md` for detailed configuration examples.

## 🛠️ Development

### Available Commands

```bash
# Development server
make dev

# Production server  
make start

# Health checks
make ping          # Quick check
make health        # Detailed check

# Testing
make client        # Run MCP client tests
make test          # Run unit tests

# Code quality
make lint          # Check code style
make format        # Format code

# Utilities
make tools         # List available tools
make clean         # Clean temporary files
make help          # Show all commands
```

### Project Structure

```
{{ project_name }}/
├── main.py                    # Server entry point
├── pyproject.toml            # Poetry configuration
├── Makefile                  # Development commands
├── test_mcp_client.py        # MCP client test suite
├── .env                      # Environment variables
├── connectors/               # API connector configurations
│   ├── README.md            # Connector guide
│   └── *.json               # Your connector files
└── README.md                # This file
```

## 🧪 Testing

### Run Tests

```bash
# Comprehensive MCP client tests
make client

# Or run directly
poetry run python test_mcp_client.py

# Test specific server URL
poetry run python test_mcp_client.py http://localhost:8002
```

### Test Results

Tests validate:
- ✅ Server health and status
- ✅ MCP protocol initialization
- ✅ Tool discovery and listing
- ✅ Tool execution and responses
- ✅ Error handling and edge cases

## 🚀 Deployment

### Local Development
```bash
make dev
```

### Production Deployment
```bash
make start
```

### Docker (if available)
```bash
docker build -t {{ project_name_normalized }} .
docker run -p 8002:8002 {{ project_name_normalized }}
```

## 📊 Monitoring

### Health Monitoring
```bash
# Quick health check
curl http://localhost:8002/health

# Detailed status
make health
```

### Logging

The server uses structured logging with configurable levels:
- `DEBUG` - Detailed debugging information
- `INFO` - General operational messages
- `WARNING` - Warning conditions
- `ERROR` - Error conditions

Configure logging level in `.env`:
```bash
LOGGING_LEVEL=INFO
```

## 🤝 Integration

### Langflow Integration

Connect this MCP server to Langflow:

1. In Langflow, add an MCP Tool component
2. Set the MCP server URL: `http://localhost:8002`
3. The component will automatically discover available tools
4. Use natural language prompts to invoke healthcare tools

### Custom MCP Client

```python
import httpx

async def call_mcp_tool(tool_name: str, arguments: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8002/mcp", json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        })
        return response.json()
```

## 🆘 Troubleshooting

### Common Issues

1. **Server won't start**
   ```bash
   # Check if port is in use
   lsof -i :8002
   
   # Check logs for errors
   make dev
   ```

2. **No tools available**
   ```bash
   # Verify connectors directory
   ls -la connectors/
   
   # Check connector JSON files are valid
   python -m json.tool connectors/your_connector.json
   ```

3. **API authentication errors**
   ```bash
   # Verify environment variables
   cat .env
   
   # Check connector configuration
   ```

### Getting Help

- 📖 Check the `connectors/README.md` for configuration help
- 🧪 Run `make client` to test your setup
- 🔍 Use `make health` to check server status
- 📋 Review logs for detailed error messages

## 📄 License

This project is generated from the Genesis MCP Core SDK template.

## 🙏 Acknowledgments

- Built with [Genesis MCP Core SDK](../genesis-mcp-core/)
- Implements [Model Context Protocol 2025-06-18](https://modelcontextprotocol.io)
- Powered by [FastAPI](https://fastapi.tiangolo.com/) and [Poetry](https://python-poetry.org)
