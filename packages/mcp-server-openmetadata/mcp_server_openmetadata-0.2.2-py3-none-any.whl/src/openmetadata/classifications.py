"""Classification entity management for OpenMetadata.

This module provides comprehensive classification management operations including
CRUD operations, field filtering, and tag relationship management.
Classifications contain hierarchical terms called Tags for categorizing data assets.
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
        (
            list_classifications,
            "list_classifications",
            "List classifications from OpenMetadata with pagination and filtering",
        ),
        (get_classification, "get_classification", "Get details of a specific classification by ID"),
        (get_classification_by_name, "get_classification_by_name", "Get details of a specific classification by name"),
        (create_classification, "create_classification", "Create a new classification in OpenMetadata"),
        (update_classification, "update_classification", "Update an existing classification in OpenMetadata"),
        (delete_classification, "delete_classification", "Delete a classification from OpenMetadata"),
    ]


async def list_classifications(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List classifications with pagination.

    Args:
        limit: Maximum number of classifications to return (1 to 1000000)
        offset: Number of classifications to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted classifications

    Returns:
        List of MCP content types containing classification list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get("classifications", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for classification in result["data"]:
            classification_name = classification.get("name", "")
            if classification_name:
                classification["ui_url"] = f"{client.host}/classification/{classification_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_classification(
    classification_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific classification by ID.

    Args:
        classification_id: ID of the classification
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing classification details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"classifications/{classification_id}", params=params)

    # Add UI URL for web interface integration
    classification_name = result.get("name", "")
    if classification_name:
        result["ui_url"] = f"{client.host}/classification/{classification_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_classification_by_name(
    name: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific classification by name.

    Args:
        name: Name of the classification
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing classification details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"classifications/name/{name}", params=params)

    # Add UI URL for web interface integration
    classification_name = result.get("name", "")
    if classification_name:
        result["ui_url"] = f"{client.host}/classification/{classification_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_classification(
    classification_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new classification.

    Args:
        classification_data: Classification data including name, description, tags, etc.

    Returns:
        List of MCP content types containing created classification details
    """
    client = get_client()
    result = client.post("classifications", json_data=classification_data)

    # Add UI URL for web interface integration
    classification_name = result.get("name", "")
    if classification_name:
        result["ui_url"] = f"{client.host}/classification/{classification_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_classification(
    classification_id: str,
    classification_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing classification.

    Args:
        classification_id: ID of the classification to update
        classification_data: Updated classification data

    Returns:
        List of MCP content types containing updated classification details
    """
    client = get_client()
    result = client.put(f"classifications/{classification_id}", json_data=classification_data)

    # Add UI URL for web interface integration
    classification_name = result.get("name", "")
    if classification_name:
        result["ui_url"] = f"{client.host}/classification/{classification_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_classification(
    classification_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a classification.

    Args:
        classification_id: ID of the classification to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"classifications/{classification_id}", params=params)

    return [types.TextContent(type="text", text=f"Classification {classification_id} deleted successfully")]
