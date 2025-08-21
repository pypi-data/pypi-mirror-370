"""User entity management for OpenMetadata.

This module provides comprehensive user management operations including
CRUD operations, field filtering, pagination support, and team relationship management.
Users represent individuals in OpenMetadata who can own and follow data assets.
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
        (list_users, "list_users", "List users from OpenMetadata with pagination and filtering"),
        (get_user, "get_user", "Get details of a specific user by ID"),
        (get_user_by_name, "get_user_by_name", "Get details of a specific user by name"),
        (create_user, "create_user", "Create a new user in OpenMetadata"),
        (update_user, "update_user", "Update an existing user in OpenMetadata"),
        (delete_user, "delete_user", "Delete a user from OpenMetadata"),
    ]


async def list_users(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    team: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List users with pagination.

    Args:
        limit: Maximum number of users to return (1 to 1000000)
        offset: Number of users to skip
        fields: Comma-separated list of fields to include
        team: Filter users by team name
        include_deleted: Whether to include deleted users

    Returns:
        List of MCP content types containing user list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if team:
        params["team"] = team
    if include_deleted:
        params["include"] = "all"

    result = client.get("users", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for user in result["data"]:
            user_name = user.get("name", "")
            if user_name:
                user["ui_url"] = f"{client.host}/user/{user_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_user(
    user_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific user by ID.

    Args:
        user_id: ID of the user
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing user details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"users/{user_id}", params=params)

    # Add UI URL for web interface integration
    user_name = result.get("name", "")
    if user_name:
        result["ui_url"] = f"{client.host}/user/{user_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_user_by_name(
    name: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific user by name.

    Args:
        name: Name of the user
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing user details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"users/name/{name}", params=params)

    # Add UI URL for web interface integration
    user_name = result.get("name", "")
    if user_name:
        result["ui_url"] = f"{client.host}/user/{user_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_user(
    user_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new user.

    Args:
        user_data: User data including name, email, roles, etc.

    Returns:
        List of MCP content types containing created user details
    """
    client = get_client()
    result = client.post("users", json_data=user_data)

    # Add UI URL for web interface integration
    user_name = result.get("name", "")
    if user_name:
        result["ui_url"] = f"{client.host}/user/{user_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_user(
    user_id: str,
    user_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing user.

    Args:
        user_id: ID of the user to update
        user_data: Updated user data

    Returns:
        List of MCP content types containing updated user details
    """
    client = get_client()
    result = client.put(f"users/{user_id}", json_data=user_data)

    # Add UI URL for web interface integration
    user_name = result.get("name", "")
    if user_name:
        result["ui_url"] = f"{client.host}/user/{user_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_user(
    user_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a user.

    Args:
        user_id: ID of the user to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"users/{user_id}", params=params)

    return [types.TextContent(type="text", text=f"User {user_id} deleted successfully")]
