# Protocols.io MCP Server

A Model Context Protocol (MCP) server that enables MCP clients like Claude Desktop to interact with [protocols.io](https://www.protocols.io), a popular platform for sharing scientific protocols and methods.

## Available Tools

The server provides the following tools that can be used by MCP clients:

### Search and Retrieval
- `search_public_protocols` - Search for public protocols by keyword
- `get_protocol` - Get basic protocol information by ID
- `get_protocol_steps` - Get detailed steps for a specific protocol
- `get_my_protocols` - Retrieve all protocols from your account

### Protocol Creation and Management
- `create_protocol` - Create a new protocol with title and description
- `update_protocol_title` - Update the title of an existing protocol
- `update_protocol_description` - Update the description of an existing protocol

### Step Management
- `set_protocol_steps` - Replace all steps in a protocol
- `add_protocol_step` - Add a single step to the end of a protocol
- `delete_protocol_step` - Delete a specific step from a protocol

## Requirements

- Python 3.10 or higher
- protocols.io account with API access token
- MCP client (such as Claude Desktop)

## Installation

Install the package using pip:

```bash
pip install protocols-io-mcp
```

## Configuration

### Environment Variables

Before running the server or tests, you must set your protocols.io API access token:

```bash
export PROTOCOLS_IO_CLIENT_ACCESS_TOKEN="your_client_access_token"
```

To obtain an API token:
1. Visit [protocols.io/developer](https://www.protocols.io/developers)
2. Sign in to your account
3. Go to API clients section and add a new client
4. Copy the generated client access token and set it in your environment

## Usage

### Command Line Interface

Run the MCP server with various transport options:

```bash
# Default: stdio transport (recommended for MCP clients)
protocols-io-mcp

# HTTP transport
protocols-io-mcp --transport http --host 127.0.0.1 --port 8000

# Server-Sent Events transport
protocols-io-mcp --transport sse --host 127.0.0.1 --port 8000
```

#### CLI Options

```
Usage: protocols-io-mcp [OPTIONS]

  Run the protocols.io MCP server.
    
Options:
  --transport [stdio|http|sse]  Transport protocol to use [default: stdio]
  --host TEXT                   Host to bind to when using http and sse
                                transport [default: 127.0.0.1]
  --port INTEGER                Port to bind to when using http and sse
                                transport [default: 8000]
  --help                        Show this message and exit.
```

### Integration with Claude Desktop

To use this server with Claude Desktop, add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "protocols-io": {
      "command": "protocols-io-mcp",
      "env": {
        "PROTOCOLS_IO_CLIENT_ACCESS_TOKEN": "your_client_access_token"
      }
    }
  }
}
```

## Development

### Running Tests

Ensure you have set the `PROTOCOLS_IO_CLIENT_ACCESS_TOKEN` environment variable, then run:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.