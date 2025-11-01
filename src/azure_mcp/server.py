"""Azure MCP Server implementation."""

import logging
import sys
from typing import Any

import anyio
import click
import mcp.types as types
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

# Configure logging to stderr (not stdout, which is used for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class AzureMcpServer:
    """Azure MCP Server with Azure management tools."""

    def __init__(self):
        """Initialize the Azure MCP Server."""
        self.server = Server("azure-mcp-server")
        self.credential = None
        self._setup_handlers()

    def _get_credential(self):
        """Get or create Azure credential."""
        if self.credential is None:
            logger.info("Initializing Azure DefaultAzureCredential")
            self.credential = DefaultAzureCredential()
        return self.credential

    def _setup_handlers(self):
        """Set up MCP request handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available Azure tools."""
            return [
                types.Tool(
                    name="list_subscriptions",
                    description="List all Azure subscriptions accessible to the authenticated user",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="get_subscription_info",
                    description="Get detailed information about a specific Azure subscription",
                    inputSchema={
                        "type": "object",
                        "required": ["subscription_id"],
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="list_resource_groups",
                    description="List all resource groups in an Azure subscription",
                    inputSchema={
                        "type": "object",
                        "required": ["subscription_id"],
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="list_resources",
                    description="List all resources in an Azure subscription or resource group",
                    inputSchema={
                        "type": "object",
                        "required": ["subscription_id"],
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID",
                            },
                            "resource_group": {
                                "type": "string",
                                "description": "Optional: Filter by resource group name",
                            },
                        },
                    },
                ),
                types.Tool(
                    name="list_storage_accounts",
                    description="List all storage accounts in an Azure subscription",
                    inputSchema={
                        "type": "object",
                        "required": ["subscription_id"],
                        "properties": {
                            "subscription_id": {
                                "type": "string",
                                "description": "Azure subscription ID",
                            },
                            "resource_group": {
                                "type": "string",
                                "description": "Optional: Filter by resource group name",
                            },
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: dict[str, Any]
        ) -> list[types.ContentBlock]:
            """Handle tool calls."""
            logger.info(f"Tool called: {name} with arguments: {arguments}")

            try:
                if name == "list_subscriptions":
                    return await self._list_subscriptions()
                elif name == "get_subscription_info":
                    subscription_id = arguments.get("subscription_id")
                    if not subscription_id:
                        raise ValueError("subscription_id is required")
                    return await self._get_subscription_info(subscription_id)
                elif name == "list_resource_groups":
                    subscription_id = arguments.get("subscription_id")
                    if not subscription_id:
                        raise ValueError("subscription_id is required")
                    return await self._list_resource_groups(subscription_id)
                elif name == "list_resources":
                    subscription_id = arguments.get("subscription_id")
                    if not subscription_id:
                        raise ValueError("subscription_id is required")
                    resource_group = arguments.get("resource_group")
                    return await self._list_resources(subscription_id, resource_group)
                elif name == "list_storage_accounts":
                    subscription_id = arguments.get("subscription_id")
                    if not subscription_id:
                        raise ValueError("subscription_id is required")
                    resource_group = arguments.get("resource_group")
                    return await self._list_storage_accounts(
                        subscription_id, resource_group
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

    async def _list_subscriptions(self) -> list[types.ContentBlock]:
        """List all Azure subscriptions."""
        credential = self._get_credential()
        subscription_client = SubscriptionClient(credential)

        subscriptions = []
        for sub in subscription_client.subscriptions.list():
            subscriptions.append(
                {
                    "id": sub.id,
                    "subscription_id": sub.subscription_id,
                    "display_name": sub.display_name,
                    "state": sub.state,
                }
            )

        return [
            types.TextContent(
                type="text",
                text=f"Found {len(subscriptions)} subscription(s):\n\n"
                + "\n".join(
                    [
                        f"- {sub['display_name']} ({sub['subscription_id']}) - {sub['state']}"
                        for sub in subscriptions
                    ]
                ),
            )
        ]

    async def _get_subscription_info(
        self, subscription_id: str
    ) -> list[types.ContentBlock]:
        """Get information about a specific subscription."""
        credential = self._get_credential()
        subscription_client = SubscriptionClient(credential)

        try:
            sub = subscription_client.subscriptions.get(subscription_id)
            info = {
                "subscription_id": sub.subscription_id,
                "display_name": sub.display_name,
                "state": sub.state,
                "subscription_policies": {
                    "location_placement_id": sub.subscription_policies.location_placement_id
                    if sub.subscription_policies
                    else None,
                    "quota_id": sub.subscription_policies.quota_id
                    if sub.subscription_policies
                    else None,
                },
            }

            return [
                types.TextContent(
                    type="text",
                    text=f"Subscription Information:\n\n"
                    f"Display Name: {info['display_name']}\n"
                    f"Subscription ID: {info['subscription_id']}\n"
                    f"State: {info['state']}\n"
                    f"Quota ID: {info['subscription_policies']['quota_id']}\n",
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error getting subscription info: {str(e)}",
                )
            ]

    async def _list_resource_groups(
        self, subscription_id: str
    ) -> list[types.ContentBlock]:
        """List resource groups in a subscription."""
        credential = self._get_credential()
        resource_client = ResourceManagementClient(credential, subscription_id)

        resource_groups = []
        for rg in resource_client.resource_groups.list():
            resource_groups.append(
                {
                    "name": rg.name,
                    "location": rg.location,
                    "id": rg.id,
                }
            )

        return [
            types.TextContent(
                type="text",
                text=f"Found {len(resource_groups)} resource group(s):\n\n"
                + "\n".join(
                    [
                        f"- {rg['name']} (Location: {rg['location']})"
                        for rg in resource_groups
                    ]
                ),
            )
        ]

    async def _list_resources(
        self, subscription_id: str, resource_group: str | None = None
    ) -> list[types.ContentBlock]:
        """List resources in a subscription or resource group."""
        credential = self._get_credential()
        resource_client = ResourceManagementClient(credential, subscription_id)

        resources = []
        if resource_group:
            resource_list = resource_client.resources.list_by_resource_group(
                resource_group
            )
        else:
            resource_list = resource_client.resources.list()

        for resource in resource_list:
            resources.append(
                {
                    "name": resource.name,
                    "type": resource.type,
                    "location": resource.location,
                    "id": resource.id,
                }
            )

        scope = (
            f"resource group '{resource_group}'"
            if resource_group
            else "subscription"
        )
        return [
            types.TextContent(
                type="text",
                text=f"Found {len(resources)} resource(s) in {scope}:\n\n"
                + "\n".join(
                    [
                        f"- {res['name']} ({res['type']}) in {res['location']}"
                        for res in resources
                    ]
                ),
            )
        ]

    async def _list_storage_accounts(
        self, subscription_id: str, resource_group: str | None = None
    ) -> list[types.ContentBlock]:
        """List storage accounts in a subscription or resource group."""
        credential = self._get_credential()
        storage_client = StorageManagementClient(credential, subscription_id)

        storage_accounts = []
        if resource_group:
            account_list = storage_client.storage_accounts.list_by_resource_group(
                resource_group
            )
        else:
            account_list = storage_client.storage_accounts.list()

        for account in account_list:
            storage_accounts.append(
                {
                    "name": account.name,
                    "location": account.location,
                    "sku": account.sku.name if account.sku else None,
                    "kind": account.kind,
                    "id": account.id,
                }
            )

        scope = (
            f"resource group '{resource_group}'"
            if resource_group
            else "subscription"
        )
        return [
            types.TextContent(
                type="text",
                text=f"Found {len(storage_accounts)} storage account(s) in {scope}:\n\n"
                + "\n".join(
                    [
                        f"- {acc['name']} ({acc['sku']}, {acc['kind']}) in {acc['location']}"
                        for acc in storage_accounts
                    ]
                ),
            )
        ]

    async def run(self):
        """Run the server with stdio transport."""
        logger.info("Starting Azure MCP Server with stdio transport")
        async with stdio_server() as streams:
            await self.server.run(
                streams[0], streams[1], self.server.create_initialization_options()
            )


@click.command()
def main() -> int:
    """
    Azure MCP Server - Provides Azure management tools via Model Context Protocol.

    Usage:
        python -m azure_mcp.server start
        azure-mcp start
    """
    server = AzureMcpServer()
    anyio.run(server.run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
