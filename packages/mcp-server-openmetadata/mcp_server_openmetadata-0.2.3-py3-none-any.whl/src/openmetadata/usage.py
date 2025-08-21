"""Usage analytics management for OpenMetadata.

This module provides comprehensive usage analytics operations including
retrieving usage data, access patterns, and analytics for data assets.
Usage APIs help track how data assets are being utilized across the organization.
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
        (get_usage_by_entity, "get_usage_by_entity", "Get usage analytics for a specific entity"),
        (add_usage_data, "add_usage_data", "Add usage data for entities"),
        (get_entity_usage_summary, "get_entity_usage_summary", "Get usage summary for entity types"),
    ]


async def get_usage_by_entity(
    entity_type: str,
    entity_id: str,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get usage analytics for a specific entity.

    Args:
        entity_type: Type of entity (table, dashboard, pipeline, etc.)
        entity_id: ID of the entity
        start_ts: Start timestamp for usage period
        end_ts: End timestamp for usage period

    Returns:
        List of MCP content types containing usage analytics
    """
    client = get_client()
    params = {}
    if start_ts:
        params["startTs"] = start_ts
    if end_ts:
        params["endTs"] = end_ts

    result = client.get(f"usage/{entity_type}/{entity_id}", params=params)

    return [types.TextContent(type="text", text=str(result))]


async def add_usage_data(
    usage_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Add usage data for entities.

    Args:
        usage_data: Usage data including entity references, usage metrics, etc.

    Returns:
        List of MCP content types containing usage data submission result
    """
    client = get_client()
    result = client.post("usage", json_data=usage_data)

    return [types.TextContent(type="text", text=str(result))]


async def get_entity_usage_summary(
    entity_type: str,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get usage summary for entity types.

    Args:
        entity_type: Type of entity to get summary for
        start_ts: Start timestamp for usage period
        end_ts: End timestamp for usage period

    Returns:
        List of MCP content types containing usage summary
    """
    client = get_client()
    params = {"entityType": entity_type}
    if start_ts:
        params["startTs"] = start_ts
    if end_ts:
        params["endTs"] = end_ts

    result = client.get("usage/summary", params=params)

    return [types.TextContent(type="text", text=str(result))]
