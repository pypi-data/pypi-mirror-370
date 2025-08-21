"""Bot entity management for OpenMetadata.

This module provides comprehensive bot management operations including
CRUD operations, field filtering, and pagination support.
Bots are special users that automate tasks like ingesting metadata and running data quality checks.
"""

from typing import Any, Callable, Dict, List, Optional, Union

import mcp.types as types

from src.openmetadata.openmetadata_client import get_client


def get_all_functions() -> List[tuple[Callable, str, str]]:
    """Return list of (function, name, description) tuples for registration.

    Returns:
        List of tuples containing function reference, tool name, and description
    """
    return [
        (list_bots, "list_bots", "List bots from OpenMetadata with pagination and filtering"),
        (get_bot, "get_bot", "Get details of a specific bot by ID"),
        (get_bot_by_name, "get_bot_by_name", "Get details of a specific bot by name"),
        (create_bot, "create_bot", "Create a new bot in OpenMetadata"),
        (update_bot, "update_bot", "Update an existing bot in OpenMetadata"),
        (delete_bot, "delete_bot", "Delete a bot from OpenMetadata"),
    ]


async def list_bots(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List bots with pagination.

    Args:
        limit: Maximum number of bots to return (1 to 1000000)
        offset: Number of bots to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted bots

    Returns:
        List of MCP content types containing bot list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get("bots", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for bot in result["data"]:
            bot_name = bot.get("name", "")
            if bot_name:
                bot["ui_url"] = f"{client.host}/bot/{bot_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_bot(
    bot_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific bot by ID.

    Args:
        bot_id: ID of the bot
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing bot details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"bots/{bot_id}", params=params)

    # Add UI URL for web interface integration
    bot_name = result.get("name", "")
    if bot_name:
        result["ui_url"] = f"{client.host}/bot/{bot_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_bot_by_name(
    name: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific bot by name.

    Args:
        name: Name of the bot
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing bot details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"bots/name/{name}", params=params)

    # Add UI URL for web interface integration
    bot_name = result.get("name", "")
    if bot_name:
        result["ui_url"] = f"{client.host}/bot/{bot_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_bot(
    bot_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new bot.

    Args:
        bot_data: Bot data including name, description, bot type, etc.

    Returns:
        List of MCP content types containing created bot details
    """
    client = get_client()
    result = client.post("bots", json_data=bot_data)

    # Add UI URL for web interface integration
    bot_name = result.get("name", "")
    if bot_name:
        result["ui_url"] = f"{client.host}/bot/{bot_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_bot(
    bot_id: str,
    bot_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing bot.

    Args:
        bot_id: ID of the bot to update
        bot_data: Updated bot data

    Returns:
        List of MCP content types containing updated bot details
    """
    client = get_client()
    result = client.put(f"bots/{bot_id}", json_data=bot_data)

    # Add UI URL for web interface integration
    bot_name = result.get("name", "")
    if bot_name:
        result["ui_url"] = f"{client.host}/bot/{bot_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_bot(
    bot_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a bot.

    Args:
        bot_id: ID of the bot to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"bots/{bot_id}", params=params)

    return [types.TextContent(type="text", text=f"Bot {bot_id} deleted successfully")]
