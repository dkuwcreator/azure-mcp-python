# Azure MCP Python Server

A Python-based implementation of the Azure Model Context Protocol (MCP) server. Provides Azure resource access and management tools through a lightweight, async JSON-RPC interface compatible with the MCP specification — no Node.js or npm required.

## Features

- ✅ **Pure Python Implementation**: Built with asyncio and the official MCP Python SDK
- ✅ **Azure Authentication**: Uses `azure.identity.DefaultAzureCredential` for flexible authentication
- ✅ **JSON-RPC over stdio**: Standard MCP stdio transport for maximum compatibility
- ✅ **Azure Management Tools**: Access Azure subscriptions, resources, and storage accounts
- ✅ **Async/Await**: Modern async Python for efficient I/O operations

## Installation

### Prerequisites

- Python 3.10 or higher
- Azure subscription and appropriate credentials

### Install from source

```bash
git clone https://github.com/dkuwcreator/azure-mcp-python.git
cd azure-mcp-python
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Authentication

The server uses Azure's `DefaultAzureCredential`, which supports multiple authentication methods in this order:

1. **Environment Variables**: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`
2. **Managed Identity**: When running in Azure (VM, App Service, etc.)
3. **Azure CLI**: `az login` credentials
4. **Azure PowerShell**: `Connect-AzAccount` credentials
5. **Interactive Browser**: As a fallback

For local development, the easiest method is:

```bash
az login
```

## Usage

### Running the Server

Start the MCP server with stdio transport:

```bash
python -m azure_mcp.server
```

Or using the installed script:

```bash
azure-mcp
```

### Available Tools

The server exposes the following Azure management tools:

#### 1. `list_subscriptions`
List all Azure subscriptions accessible to the authenticated user.

**Parameters**: None

**Example Response**:
```
Found 2 subscription(s):

- My Dev Subscription (12345678-1234-1234-1234-123456789012) - Enabled
- My Prod Subscription (87654321-4321-4321-4321-210987654321) - Enabled
```

#### 2. `get_subscription_info`
Get detailed information about a specific Azure subscription.

**Parameters**:
- `subscription_id` (required): Azure subscription ID

**Example**:
```json
{
  "subscription_id": "12345678-1234-1234-1234-123456789012"
}
```

#### 3. `list_resource_groups`
List all resource groups in an Azure subscription.

**Parameters**:
- `subscription_id` (required): Azure subscription ID

**Example Response**:
```
Found 3 resource group(s):

- rg-webapp-dev (Location: eastus)
- rg-storage-prod (Location: westus2)
- rg-networking (Location: centralus)
```

#### 4. `list_resources`
List all resources in an Azure subscription or resource group.

**Parameters**:
- `subscription_id` (required): Azure subscription ID
- `resource_group` (optional): Filter by resource group name

**Example**:
```json
{
  "subscription_id": "12345678-1234-1234-1234-123456789012",
  "resource_group": "rg-webapp-dev"
}
```

#### 5. `list_storage_accounts`
List all storage accounts in an Azure subscription.

**Parameters**:
- `subscription_id` (required): Azure subscription ID
- `resource_group` (optional): Filter by resource group name

**Example Response**:
```
Found 2 storage account(s) in subscription:

- mystorageaccount (Standard_LRS, StorageV2) in eastus
- backupstorage (Standard_GRS, StorageV2) in westus2
```

## MCP Configuration

To use this server with an MCP client (like Claude Desktop), add it to your MCP settings configuration:

### Claude Desktop Configuration

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the server configuration:

```json
{
  "mcpServers": {
    "azure": {
      "command": "python",
      "args": ["-m", "azure_mcp.server"]
    }
  }
}
```

## Architecture

The server follows the MCP specification and implements:

- **JSON-RPC 2.0**: All messages are JSON-RPC compliant
- **stdio Transport**: Communicates via standard input/output
- **Async Operations**: Built on asyncio for efficient Azure API calls
- **Error Handling**: Graceful error handling with informative messages

### Project Structure

```
azure-mcp-python/
├── src/
│   └── azure_mcp/
│       ├── __init__.py       # Package initialization
│       ├── __main__.py       # Module entry point
│       └── server.py         # Main MCP server implementation
├── pyproject.toml            # Project configuration and dependencies
├── README.md                 # This file
└── .gitignore               # Git ignore rules
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
ruff check src/
```

## Dependencies

- **mcp**: Official Model Context Protocol SDK
- **azure-identity**: Azure authentication library
- **azure-mgmt-resource**: Azure Resource Management client
- **azure-mgmt-storage**: Azure Storage Management client
- **azure-mgmt-subscription**: Azure Subscription Management client
- **click**: Command-line interface framework
- **anyio**: Async I/O library

## Comparison with @azure/mcp

This Python implementation follows the same design principles as the official Azure MCP server (`@azure/mcp`):

- ✅ Uses Azure SDK for authentication and resource management
- ✅ Implements MCP specification with stdio transport
- ✅ Provides similar Azure management tools
- ✅ Supports the same authentication methods via DefaultAzureCredential

**Key Differences**:
- Written in Python instead of TypeScript/Node.js
- Uses Python's async/await instead of JavaScript Promises
- No npm or Node.js runtime required
- Lighter weight and easier to embed in Python applications

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

1. Verify you're logged in: `az login`
2. Check your subscription access: `az account list`
3. Ensure proper RBAC permissions (Reader role minimum)

### MCP Client Connection Issues

1. Verify the server starts correctly: `python -m azure_mcp.server start`
2. Check stderr for log messages (stdout is reserved for MCP protocol)
3. Ensure your MCP client configuration is correct

### Import Errors

If you get module import errors:

```bash
pip install -e .
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is provided as-is for educational and development purposes.

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification)
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
- [Official Azure MCP Server](https://github.com/Azure/azure-mcp)
