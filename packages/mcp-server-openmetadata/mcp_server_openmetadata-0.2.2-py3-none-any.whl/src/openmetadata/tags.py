"""Tags management for OpenMetadata Tagging System.

This module provides comprehensive tag management operations including
CRUD operations for tags, tag categories, and tag assignments.
Tags provide a way to categorize and organize metadata entities.
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
        (list_tags, "list_tags", "List tags with pagination and filtering"),
        (get_tag, "get_tag", "Get details of a specific tag by ID"),
        (get_tag_by_name, "get_tag_by_name", "Get details of a specific tag by name"),
        (create_tag, "create_tag", "Create a new tag in OpenMetadata"),
        (update_tag, "update_tag", "Update an existing tag"),
        (delete_tag, "delete_tag", "Delete a tag from OpenMetadata"),
        (list_tag_categories, "list_tag_categories", "List tag categories"),
        (get_tag_category, "get_tag_category", "Get tag category by name"),
        (create_tag_category, "create_tag_category", "Create a new tag category"),
        (update_tag_category, "update_tag_category", "Update a tag category"),
        (delete_tag_category, "delete_tag_category", "Delete a tag category"),
    ]


async def list_tags(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    parent: Optional[str] = None,
    include_deleted: bool = False,
    q: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List tags with pagination and filtering.

    Args:
        limit: Maximum number of tags to return (1 to 1000000)
        offset: Number of tags to skip
        fields: Comma-separated list of fields to include
        parent: Filter by parent tag category
        include_deleted: Whether to include deleted tags
        q: Search query for tag name or description

    Returns:
        List of MCP content types containing tag list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if parent:
        params["parent"] = parent
    if include_deleted:
        params["include"] = "all"
    if q:
        params["q"] = q

    result = client.get("tags", params=params)

    # Add UI URLs for tags
    if "data" in result:
        for tag in result["data"]:
            tag_fqn = tag.get("fullyQualifiedName", "")
            if tag_fqn:
                tag["ui_url"] = f"{client.host}/tags/{tag_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_tag(
    tag_id: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific tag by ID.

    Args:
        tag_id: ID of the tag
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted tags

    Returns:
        List of MCP content types containing tag details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"tags/{tag_id}", params=params)

    # Add UI URL
    tag_fqn = result.get("fullyQualifiedName", "")
    if tag_fqn:
        result["ui_url"] = f"{client.host}/tags/{tag_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_tag_by_name(
    name: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific tag by name.

    Args:
        name: Fully qualified name of the tag
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted tags

    Returns:
        List of MCP content types containing tag details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"tags/name/{name}", params=params)

    # Add UI URL
    tag_fqn = result.get("fullyQualifiedName", "")
    if tag_fqn:
        result["ui_url"] = f"{client.host}/tags/{tag_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_tag(
    tag_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new tag.

    Args:
        tag_data: Tag data including name, description, parent classification, etc.

    Returns:
        List of MCP content types containing created tag details
    """
    client = get_client()
    result = client.post("tags", json_data=tag_data)

    # Add UI URL
    tag_fqn = result.get("fullyQualifiedName", "")
    if tag_fqn:
        result["ui_url"] = f"{client.host}/tags/{tag_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_tag(
    tag_id: str,
    tag_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing tag.

    Args:
        tag_id: ID of the tag to update
        tag_data: Updated tag data

    Returns:
        List of MCP content types containing updated tag details
    """
    client = get_client()
    result = client.put(f"tags/{tag_id}", json_data=tag_data)

    # Add UI URL
    tag_fqn = result.get("fullyQualifiedName", "")
    if tag_fqn:
        result["ui_url"] = f"{client.host}/tags/{tag_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_tag(
    tag_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a tag.

    Args:
        tag_id: ID of the tag to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"tags/{tag_id}", params=params)

    return [types.TextContent(type="text", text=f"Tag {tag_id} deleted successfully")]


async def list_tag_categories(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List tag categories (classifications) with pagination.

    Args:
        limit: Maximum number of categories to return (1 to 1000000)
        offset: Number of categories to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted categories

    Returns:
        List of MCP content types containing tag category list
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get("classifications", params=params)

    # Add UI URLs for classifications
    if "data" in result:
        for classification in result["data"]:
            class_name = classification.get("name", "")
            if class_name:
                classification["ui_url"] = f"{client.host}/tags/{class_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_tag_category(
    name: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get tag category (classification) by name.

    Args:
        name: Name of the classification
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted categories

    Returns:
        List of MCP content types containing tag category details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"classifications/name/{name}", params=params)

    # Add UI URL
    class_name = result.get("name", "")
    if class_name:
        result["ui_url"] = f"{client.host}/tags/{class_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_tag_category(
    category_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new tag category (classification).

    Args:
        category_data: Category data including name, description, etc.

    Returns:
        List of MCP content types containing created category details
    """
    client = get_client()
    result = client.post("classifications", json_data=category_data)

    # Add UI URL
    class_name = result.get("name", "")
    if class_name:
        result["ui_url"] = f"{client.host}/tags/{class_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_tag_category(
    category_id: str,
    category_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update a tag category (classification).

    Args:
        category_id: ID of the category to update
        category_data: Updated category data

    Returns:
        List of MCP content types containing updated category details
    """
    client = get_client()
    result = client.put(f"classifications/{category_id}", json_data=category_data)

    # Add UI URL
    class_name = result.get("name", "")
    if class_name:
        result["ui_url"] = f"{client.host}/tags/{class_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_tag_category(
    category_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a tag category (classification).

    Args:
        category_id: ID of the category to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"classifications/{category_id}", params=params)

    return [types.TextContent(type="text", text=f"Tag category {category_id} deleted successfully")]
