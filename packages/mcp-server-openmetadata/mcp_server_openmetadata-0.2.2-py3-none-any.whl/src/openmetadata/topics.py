"""Topic entity management for OpenMetadata.

This module provides comprehensive topic management operations including
CRUD operations, field filtering, pagination support, and messaging service management.
Topics are feeds or event streams in messaging services for publishers and consumers.
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
        (list_topics, "list_topics", "List topics from OpenMetadata with pagination and filtering"),
        (get_topic, "get_topic", "Get details of a specific topic by ID"),
        (get_topic_by_name, "get_topic_by_name", "Get details of a specific topic by fully qualified name"),
        (create_topic, "create_topic", "Create a new topic in OpenMetadata"),
        (update_topic, "update_topic", "Update an existing topic in OpenMetadata"),
        (delete_topic, "delete_topic", "Delete a topic from OpenMetadata"),
    ]


async def list_topics(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    service: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List topics with pagination.

    Args:
        limit: Maximum number of topics to return (1 to 1000000)
        offset: Number of topics to skip
        fields: Comma-separated list of fields to include
        service: Filter topics by service name
        include_deleted: Whether to include deleted topics

    Returns:
        List of MCP content types containing topic list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if service:
        params["service"] = service
    if include_deleted:
        params["include"] = "all"

    result = client.get("topics", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for topic in result["data"]:
            topic_fqn = topic.get("fullyQualifiedName", "")
            if topic_fqn:
                topic["ui_url"] = f"{client.host}/topic/{topic_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_topic(
    topic_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific topic by ID.

    Args:
        topic_id: ID of the topic
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing topic details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"topics/{topic_id}", params=params)

    # Add UI URL for web interface integration
    topic_fqn = result.get("fullyQualifiedName", "")
    if topic_fqn:
        result["ui_url"] = f"{client.host}/topic/{topic_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_topic_by_name(
    fqn: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific topic by fully qualified name.

    Args:
        fqn: Fully qualified name of the topic
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing topic details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"topics/name/{fqn}", params=params)

    # Add UI URL for web interface integration
    topic_fqn = result.get("fullyQualifiedName", "")
    if topic_fqn:
        result["ui_url"] = f"{client.host}/topic/{topic_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_topic(
    topic_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new topic.

    Args:
        topic_data: Topic data including name, description, schema, etc.

    Returns:
        List of MCP content types containing created topic details
    """
    client = get_client()
    result = client.post("topics", json_data=topic_data)

    # Add UI URL for web interface integration
    topic_fqn = result.get("fullyQualifiedName", "")
    if topic_fqn:
        result["ui_url"] = f"{client.host}/topic/{topic_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_topic(
    topic_id: str,
    topic_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing topic.

    Args:
        topic_id: ID of the topic to update
        topic_data: Updated topic data

    Returns:
        List of MCP content types containing updated topic details
    """
    client = get_client()
    result = client.put(f"topics/{topic_id}", json_data=topic_data)

    # Add UI URL for web interface integration
    topic_fqn = result.get("fullyQualifiedName", "")
    if topic_fqn:
        result["ui_url"] = f"{client.host}/topic/{topic_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_topic(
    topic_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a topic.

    Args:
        topic_id: ID of the topic to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"topics/{topic_id}", params=params)

    return [types.TextContent(type="text", text=f"Topic {topic_id} deleted successfully")]
