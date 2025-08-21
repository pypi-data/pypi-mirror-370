"""Container entity management for OpenMetadata.

This module provides comprehensive container management operations including
CRUD operations, field filtering, pagination support, and object store management.
Containers are abstractions for paths storing data in object stores like S3, GCP, Azure.
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
        (list_containers, "list_containers", "List containers from OpenMetadata with pagination and filtering"),
        (get_container, "get_container", "Get details of a specific container by ID"),
        (get_container_by_name, "get_container_by_name", "Get details of a specific container by fully qualified name"),
        (create_container, "create_container", "Create a new container in OpenMetadata"),
        (update_container, "update_container", "Update an existing container in OpenMetadata"),
        (delete_container, "delete_container", "Delete a container from OpenMetadata"),
    ]


async def list_containers(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    service: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List containers with pagination.

    Args:
        limit: Maximum number of containers to return (1 to 1000000)
        offset: Number of containers to skip
        fields: Comma-separated list of fields to include
        service: Filter containers by service name
        include_deleted: Whether to include deleted containers

    Returns:
        List of MCP content types containing container list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if service:
        params["service"] = service
    if include_deleted:
        params["include"] = "all"

    result = client.get("containers", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for container in result["data"]:
            container_fqn = container.get("fullyQualifiedName", "")
            if container_fqn:
                container["ui_url"] = f"{client.host}/container/{container_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_container(
    container_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific container by ID.

    Args:
        container_id: ID of the container
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing container details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"containers/{container_id}", params=params)

    # Add UI URL for web interface integration
    container_fqn = result.get("fullyQualifiedName", "")
    if container_fqn:
        result["ui_url"] = f"{client.host}/container/{container_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_container_by_name(
    fqn: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific container by fully qualified name.

    Args:
        fqn: Fully qualified name of the container
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing container details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"containers/name/{fqn}", params=params)

    # Add UI URL for web interface integration
    container_fqn = result.get("fullyQualifiedName", "")
    if container_fqn:
        result["ui_url"] = f"{client.host}/container/{container_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_container(
    container_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new container.

    Args:
        container_data: Container data including name, description, prefix, etc.

    Returns:
        List of MCP content types containing created container details
    """
    client = get_client()
    result = client.post("containers", json_data=container_data)

    # Add UI URL for web interface integration
    container_fqn = result.get("fullyQualifiedName", "")
    if container_fqn:
        result["ui_url"] = f"{client.host}/container/{container_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_container(
    container_id: str,
    container_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing container.

    Args:
        container_id: ID of the container to update
        container_data: Updated container data

    Returns:
        List of MCP content types containing updated container details
    """
    client = get_client()
    result = client.put(f"containers/{container_id}", json_data=container_data)

    # Add UI URL for web interface integration
    container_fqn = result.get("fullyQualifiedName", "")
    if container_fqn:
        result["ui_url"] = f"{client.host}/container/{container_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_container(
    container_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a container.

    Args:
        container_id: ID of the container to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"containers/{container_id}", params=params)

    return [types.TextContent(type="text", text=f"Container {container_id} deleted successfully")]
