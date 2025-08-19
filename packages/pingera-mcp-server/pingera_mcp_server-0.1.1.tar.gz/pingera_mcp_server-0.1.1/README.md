# Pingera MCP Server

A Model Context Protocol (MCP) server for the Pingera monitoring service, providing seamless integration between AI models and monitoring data.

## Features

- **Modular Architecture**: Separate Pingera API client library with clean abstractions
- **Flexible Operation Modes**: Run in read-only or read-write mode
- **MCP Resources**: Access monitoring data as structured resources (`pingera://pages`, `pingera://status`)
- **MCP Tools**: Execute monitoring operations through tools (list_pages, get_page_details, test_connection)
- **Robust Error Handling**: Comprehensive error handling with custom exception hierarchy
- **Real-time Data**: Direct integration with Pingera API v1 for live monitoring data
- **Type Safety**: Pydantic models for data validation and serialization
- **Configurable**: Environment-based configuration management

## Quick Start

### Prerequisites
- Python 3.10+
- UV package manager
- Pingera API key

### Installation and Setup

```bash
# Install dependencies
uv sync

# Set up your API key (required)
# Add PINGERA_API_KEY to your environment or Replit secrets

# Run the server
python main.py
```

The server will start in read-only mode by default and connect to the Pingera API.

## Claude Desktop Integration

To use this MCP server with Claude Desktop, you need to configure it in your Claude Desktop settings.

### Installation

First, install the package globally using UV:

```bash
uv tool install pingera-mcp-server
```

### Configuration

Open the Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "pingera": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "pingera-mcp-server",
        "--python",
        "3.10",
        "pingera-mcp"
      ],
      "env": {
        "PINGERA_API_KEY": "your_api_key_here",
        "PINGERA_MODE": "read_only",
        "PINGERA_BASE_URL": "https://api.pingera.ru/v1",
        "PINGERA_TIMEOUT": "30",
        "PINGERA_MAX_RETRIES": "3",
        "PINGERA_DEBUG": "false",
        "PINGERA_SERVER_NAME": "Pingera MCP Server"
      }
    }
  }
}
```

### Required Environment Variables

- **`PINGERA_API_KEY`** - Your Pingera API key (required)

### Optional Environment Variables

- **`PINGERA_MODE`** - Operation mode: `read_only` (default) or `read_write`
- **`PINGERA_BASE_URL`** - API endpoint (default: `https://api.pingera.ru/v1`)
- **`PINGERA_TIMEOUT`** - Request timeout in seconds (default: `30`)
- **`PINGERA_MAX_RETRIES`** - Maximum retry attempts (default: `3`)
- **`PINGERA_DEBUG`** - Enable debug logging (default: `false`)
- **`PINGERA_SERVER_NAME`** - Server display name (default: `Pingera MCP Server`)

### Restart Claude Desktop

After updating the configuration file, restart Claude Desktop to load the new MCP server. You should now be able to access your Pingera monitoring data directly through Claude's interface.

### Verify Installation

Once configured, you can ask Claude to:
- "List my monitored status pages"
- "Show details for a specific page"
- "Test the Pingera API connection"
- "Get the current monitoring status"

## Configuration

Configure the server using environment variables:

```bash
# Required
PINGERA_API_KEY=your_api_key_here

# Optional
PINGERA_MODE=read_only                    # read_only or read_write
PINGERA_BASE_URL=https://api.pingera.ru/v1
PINGERA_TIMEOUT=30
PINGERA_MAX_RETRIES=3
PINGERA_DEBUG=false
PINGERA_SERVER_NAME=Pingera MCP Server
```

## MCP Tools

Available tools for AI agents:

### Pages Management
- **`list_pages`** - Get paginated list of monitored pages
  - Parameters: `page`, `per_page`, `status`
- **`get_page_details`** - Get detailed information about a specific page
  - Parameters: `page_id`

### Component Management
- **`list_component_groups`** - List all component groups for monitoring organization
- **`get_component_details`** - Get detailed information about a specific component
  - Parameters: `component_id`

### Monitoring Checks
- **`list_checks`** - List all monitoring checks (HTTP, TCP, ping, etc.)
  - Parameters: `page`, `page_size`, `status`, `check_type`
- **`get_check_details`** - Get detailed information about a specific check
  - Parameters: `check_id`

### Alert Rules
- **`list_alert_rules`** - List all alert rules and their trigger conditions

### Heartbeat Monitoring
- **`list_heartbeats`** - List all heartbeat monitors for cron jobs and scheduled tasks
  - Parameters: `page`, `page_size`, `status`

### Incident Management
- **`list_incidents`** - List all incidents and their current status
  - Parameters: `page`, `page_size`, `status`

### Connection Testing
- **`test_pingera_connection`** - Test API connectivity

### Write Operations
- **Write operations** - Available only in read-write mode (future implementation)

## Operation Modes

### Read-Only Mode (Default)
- Access monitoring data
- View status pages and their configurations
- Test API connectivity
- No modification capabilities

### Read-Write Mode
- All read-only features
- Create, update, and delete monitoring pages (future implementation)
- Manage incidents and notifications (future implementation)

Set `PINGERA_MODE=read_write` to enable write operations.

## Architecture

### Pingera API Client Library
Located in `pingera/`, this modular library provides:

- **PingeraClient**: Main API client with authentication and error handling
- **Models**: Pydantic data models for type-safe API responses
- **Exceptions**: Custom exception hierarchy for error handling

### MCP Server Implementation
- **FastMCP Framework**: Modern MCP server implementation
- **Resource Management**: Structured access to monitoring data
- **Tool Registration**: Executable operations for AI agents
- **Configuration**: Environment-based settings management

## Testing

### Running the Test Suite

Run all tests:
```bash
uv run pytest
```

Run tests with verbose output:
```bash
uv run pytest -v
```

Run specific test files:
```bash
uv run pytest tests/test_models.py
uv run pytest tests/test_config.py
uv run pytest tests/test_mcp_server.py
```

Run tests with coverage:
```bash
uv run pytest --cov=pingera --cov=config --cov=mcp_server
```

### Test Structure

The test suite includes:
- **Unit Tests**: Testing individual components (models, config, client)
- **Integration Tests**: Testing MCP server functionality 
- **Mock Tests**: Testing with simulated API responses

### Manual Testing

Test the client library directly:
```bash
python -c "from pingera import PingeraClient; import os; client = PingeraClient(os.getenv('PINGERA_API_KEY')); print(f'Pages: {len(client.get_pages().pages)}')"
```

Test MCP server functionality:
```bash
python test_mcp_server.py
```

## Error Handling

The system includes comprehensive error handling:
- `PingeraError`: Base exception for all client errors
- `PingeraAPIError`: API response errors with status codes
- `PingeraAuthError`: Authentication failures
- `PingeraConnectionError`: Network connectivity issues
- `PingeraTimeoutError`: Request timeout handling
