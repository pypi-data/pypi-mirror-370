"""Lineage entity management for OpenMetadata.

This module provides comprehensive lineage management operations including
retrieving upstream and downstream relationships, managing data flow, and
analyzing impact across data assets.
"""

from typing import Any, Callable, Dict, List, Union

import mcp.types as types

from src.openmetadata.openmetadata_client import get_client


def get_all_functions() -> List[tuple[Callable, str, str]]:
    """Return list of (function, name, description) tuples for registration.

    Returns:
        List of tuples containing function reference, tool name, and description
    """
    return [
        (get_lineage, "get_lineage", "Get lineage information for a specific entity"),
        (get_lineage_by_name, "get_lineage_by_name", "Get lineage information by entity name"),
        (add_lineage, "add_lineage", "Add or update lineage between entities"),
        (delete_lineage, "delete_lineage", "Delete lineage between entities"),
    ]


async def get_lineage(
    entity_id: str,
    entity_type: str = "table",
    upstream_depth: int = 1,
    downstream_depth: int = 1,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get lineage information for a specific entity.

    Args:
        entity_id: ID of the entity
        entity_type: Type of entity (table, pipeline, dashboard, etc.)
        upstream_depth: Depth of upstream lineage to retrieve
        downstream_depth: Depth of downstream lineage to retrieve

    Returns:
        List of MCP content types containing lineage information
    """
    client = get_client()
    params = {
        "upstreamDepth": upstream_depth,
        "downstreamDepth": downstream_depth,
    }

    result = client.get(f"lineage/{entity_type}/{entity_id}", params=params)

    # Add UI URL for web interface integration
    result["ui_url"] = f"{client.host}/lineage/{entity_type}/{entity_id}"

    return [types.TextContent(type="text", text=str(result))]


async def get_lineage_by_name(
    entity_fqn: str,
    entity_type: str = "table",
    upstream_depth: int = 1,
    downstream_depth: int = 1,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get lineage information by entity fully qualified name.

    Args:
        entity_fqn: Fully qualified name of the entity
        entity_type: Type of entity (table, pipeline, dashboard, etc.)
        upstream_depth: Depth of upstream lineage to retrieve
        downstream_depth: Depth of downstream lineage to retrieve

    Returns:
        List of MCP content types containing lineage information
    """
    client = get_client()
    params = {
        "upstreamDepth": upstream_depth,
        "downstreamDepth": downstream_depth,
    }

    result = client.get(f"lineage/{entity_type}/name/{entity_fqn}", params=params)

    # Add UI URL for web interface integration
    result["ui_url"] = f"{client.host}/lineage/{entity_type}/{entity_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def add_lineage(
    lineage_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Add or update lineage between entities.

    Args:
        lineage_data: Lineage data including source, target, and relationship details

    Returns:
        List of MCP content types containing lineage update result
    """
    client = get_client()
    result = client.put("lineage", json_data=lineage_data)

    return [types.TextContent(type="text", text=str(result))]


async def delete_lineage(
    source_fqn: str,
    target_fqn: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete lineage between entities.

    Args:
        source_fqn: Fully qualified name of source entity
        target_fqn: Fully qualified name of target entity

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {
        "source": source_fqn,
        "target": target_fqn,
    }

    client.delete("lineage", params=params)

    return [types.TextContent(type="text", text=f"Lineage between {source_fqn} and {target_fqn} deleted successfully")]
