# Azure MCP Server Examples

This directory contains example configurations and usage patterns for the Azure MCP Python Server.

## Example: Claude Desktop Configuration

To use the Azure MCP server with Claude Desktop:

1. Install the Azure MCP server:
   ```bash
   pip install -e /path/to/azure-mcp-python
   ```

2. Authenticate with Azure:
   ```bash
   az login
   ```

3. Configure Claude Desktop by editing the MCP settings file:

   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   
   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

4. Add the following configuration:

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

5. Restart Claude Desktop

## Example Prompts

Once configured, you can interact with Azure through Claude Desktop:

### List Subscriptions
```
Please list my Azure subscriptions using the azure MCP server.
```

### Get Subscription Details
```
Get detailed information about subscription 12345678-1234-1234-1234-123456789012
```

### List Resource Groups
```
Show me all resource groups in my subscription 12345678-1234-1234-1234-123456789012
```

### List Resources
```
List all resources in subscription 12345678-1234-1234-1234-123456789012 and resource group my-rg
```

### List Storage Accounts
```
What storage accounts do I have in subscription 12345678-1234-1234-1234-123456789012?
```

## Testing the Server

You can test the server manually by running it and sending JSON-RPC messages via stdin:

```bash
python -m azure_mcp.server
```

Then send a JSON-RPC request (note: this is for testing only, normally an MCP client handles this):

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
```

The server will respond with the list of available tools.

## Environment Variables

If you need to use specific Azure credentials, you can set these environment variables:

```bash
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

Then run the server:

```bash
python -m azure_mcp.server
```

## Troubleshooting

### Server not responding
- Check that Python 3.10+ is installed
- Verify all dependencies are installed: `pip list | grep -E "mcp|azure"`
- Check stderr for error messages

### Authentication errors
- Verify Azure login: `az account show`
- Check Azure permissions: `az role assignment list --assignee your-user@domain.com`
- Ensure you have at least Reader role on the subscription

### MCP client can't connect
- Verify the command in your MCP client configuration matches your Python installation
- Check that the azure_mcp module is in Python's path
- Try running the command manually to see any error messages
