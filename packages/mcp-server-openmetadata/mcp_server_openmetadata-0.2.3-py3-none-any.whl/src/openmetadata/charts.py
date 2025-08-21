"""Chart entity management for OpenMetadata.

This module provides comprehensive chart management operations including
CRUD operations, field filtering, pagination support, and dashboard relationship management.
Charts are computed from data and present data visually as part of dashboards.
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
        (list_charts, "list_charts", "List charts from OpenMetadata with pagination and filtering"),
        (get_chart, "get_chart", "Get details of a specific chart by ID"),
        (get_chart_by_name, "get_chart_by_name", "Get details of a specific chart by fully qualified name"),
        (create_chart, "create_chart", "Create a new chart in OpenMetadata"),
        (update_chart, "update_chart", "Update an existing chart in OpenMetadata"),
        (delete_chart, "delete_chart", "Delete a chart from OpenMetadata"),
    ]


async def list_charts(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    service: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List charts with pagination.

    Args:
        limit: Maximum number of charts to return (1 to 1000000)
        offset: Number of charts to skip
        fields: Comma-separated list of fields to include
        service: Filter charts by service name
        include_deleted: Whether to include deleted charts

    Returns:
        List of MCP content types containing chart list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if service:
        params["service"] = service
    if include_deleted:
        params["include"] = "all"

    result = client.get("charts", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for chart in result["data"]:
            chart_fqn = chart.get("fullyQualifiedName", "")
            if chart_fqn:
                chart["ui_url"] = f"{client.host}/chart/{chart_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_chart(
    chart_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific chart by ID.

    Args:
        chart_id: ID of the chart
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing chart details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"charts/{chart_id}", params=params)

    # Add UI URL for web interface integration
    chart_fqn = result.get("fullyQualifiedName", "")
    if chart_fqn:
        result["ui_url"] = f"{client.host}/chart/{chart_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_chart_by_name(
    fqn: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific chart by fully qualified name.

    Args:
        fqn: Fully qualified name of the chart
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing chart details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"charts/name/{fqn}", params=params)

    # Add UI URL for web interface integration
    chart_fqn = result.get("fullyQualifiedName", "")
    if chart_fqn:
        result["ui_url"] = f"{client.host}/chart/{chart_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_chart(
    chart_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new chart.

    Args:
        chart_data: Chart data including name, description, chart type, etc.

    Returns:
        List of MCP content types containing created chart details
    """
    client = get_client()
    result = client.post("charts", json_data=chart_data)

    # Add UI URL for web interface integration
    chart_fqn = result.get("fullyQualifiedName", "")
    if chart_fqn:
        result["ui_url"] = f"{client.host}/chart/{chart_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_chart(
    chart_id: str,
    chart_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing chart.

    Args:
        chart_id: ID of the chart to update
        chart_data: Updated chart data

    Returns:
        List of MCP content types containing updated chart details
    """
    client = get_client()
    result = client.put(f"charts/{chart_id}", json_data=chart_data)

    # Add UI URL for web interface integration
    chart_fqn = result.get("fullyQualifiedName", "")
    if chart_fqn:
        result["ui_url"] = f"{client.host}/chart/{chart_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_chart(
    chart_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a chart.

    Args:
        chart_id: ID of the chart to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"charts/{chart_id}", params=params)

    return [types.TextContent(type="text", text=f"Chart {chart_id} deleted successfully")]
