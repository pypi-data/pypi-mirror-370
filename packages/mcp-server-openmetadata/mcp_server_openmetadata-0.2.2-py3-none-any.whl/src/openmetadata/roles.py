"""Roles management for OpenMetadata Role-Based Access Control.

This module provides comprehensive role management operations including
CRUD operations for roles, role assignments, and permissions management.
Roles define access permissions and are assigned to users and teams.
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
        (list_roles, "list_roles", "List roles with pagination and filtering"),
        (get_role, "get_role", "Get details of a specific role by ID"),
        (get_role_by_name, "get_role_by_name", "Get details of a specific role by name"),
        (create_role, "create_role", "Create a new role in OpenMetadata"),
        (update_role, "update_role", "Update an existing role"),
        (delete_role, "delete_role", "Delete a role from OpenMetadata"),
    ]


async def list_roles(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
    q: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List roles with pagination and filtering.

    Args:
        limit: Maximum number of roles to return (1 to 1000000)
        offset: Number of roles to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted roles
        q: Search query for role name or description

    Returns:
        List of MCP content types containing role list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"
    if q:
        params["q"] = q

    result = client.get("roles", params=params)

    # Add UI URLs for roles
    if "data" in result:
        for role in result["data"]:
            role_name = role.get("name", "")
            if role_name:
                role["ui_url"] = f"{client.host}/settings/access/roles/{role_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_role(
    role_id: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific role by ID.

    Args:
        role_id: ID of the role
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted roles

    Returns:
        List of MCP content types containing role details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"roles/{role_id}", params=params)

    # Add UI URL
    role_name = result.get("name", "")
    if role_name:
        result["ui_url"] = f"{client.host}/settings/access/roles/{role_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_role_by_name(
    name: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific role by name.

    Args:
        name: Name of the role
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted roles

    Returns:
        List of MCP content types containing role details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"roles/name/{name}", params=params)

    # Add UI URL
    role_name = result.get("name", "")
    if role_name:
        result["ui_url"] = f"{client.host}/settings/access/roles/{role_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_role(
    role_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new role.

    Args:
        role_data: Role data including name, description, policies, etc.

    Returns:
        List of MCP content types containing created role details
    """
    client = get_client()
    result = client.post("roles", json_data=role_data)

    # Add UI URL
    role_name = result.get("name", "")
    if role_name:
        result["ui_url"] = f"{client.host}/settings/access/roles/{role_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_role(
    role_id: str,
    role_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing role.

    Args:
        role_id: ID of the role to update
        role_data: Updated role data

    Returns:
        List of MCP content types containing updated role details
    """
    client = get_client()
    result = client.put(f"roles/{role_id}", json_data=role_data)

    # Add UI URL
    role_name = result.get("name", "")
    if role_name:
        result["ui_url"] = f"{client.host}/settings/access/roles/{role_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_role(
    role_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a role.

    Args:
        role_id: ID of the role to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"roles/{role_id}", params=params)

    return [types.TextContent(type="text", text=f"Role {role_id} deleted successfully")]
