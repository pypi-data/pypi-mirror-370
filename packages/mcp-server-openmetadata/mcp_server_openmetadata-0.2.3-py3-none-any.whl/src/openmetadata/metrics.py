"""Metric entity management for OpenMetadata.

This module provides comprehensive metric management operations including
CRUD operations, field filtering, pagination support, and KPI management.
Metrics are measurements computed from data including Monthly Active Users and KPIs.
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
        (list_metrics, "list_metrics", "List metrics from OpenMetadata with pagination and filtering"),
        (get_metric, "get_metric", "Get details of a specific metric by ID"),
        (get_metric_by_name, "get_metric_by_name", "Get details of a specific metric by fully qualified name"),
        (create_metric, "create_metric", "Create a new metric in OpenMetadata"),
        (update_metric, "update_metric", "Update an existing metric in OpenMetadata"),
        (delete_metric, "delete_metric", "Delete a metric from OpenMetadata"),
    ]


async def list_metrics(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    service: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List metrics with pagination.

    Args:
        limit: Maximum number of metrics to return (1 to 1000000)
        offset: Number of metrics to skip
        fields: Comma-separated list of fields to include
        service: Filter metrics by service name
        include_deleted: Whether to include deleted metrics

    Returns:
        List of MCP content types containing metric list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if service:
        params["service"] = service
    if include_deleted:
        params["include"] = "all"

    result = client.get("metrics", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for metric in result["data"]:
            metric_fqn = metric.get("fullyQualifiedName", "")
            if metric_fqn:
                metric["ui_url"] = f"{client.host}/metric/{metric_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_metric(
    metric_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific metric by ID.

    Args:
        metric_id: ID of the metric
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing metric details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"metrics/{metric_id}", params=params)

    # Add UI URL for web interface integration
    metric_fqn = result.get("fullyQualifiedName", "")
    if metric_fqn:
        result["ui_url"] = f"{client.host}/metric/{metric_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_metric_by_name(
    fqn: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific metric by fully qualified name.

    Args:
        fqn: Fully qualified name of the metric
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing metric details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"metrics/name/{fqn}", params=params)

    # Add UI URL for web interface integration
    metric_fqn = result.get("fullyQualifiedName", "")
    if metric_fqn:
        result["ui_url"] = f"{client.host}/metric/{metric_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_metric(
    metric_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new metric.

    Args:
        metric_data: Metric data including name, description, formula, etc.

    Returns:
        List of MCP content types containing created metric details
    """
    client = get_client()
    result = client.post("metrics", json_data=metric_data)

    # Add UI URL for web interface integration
    metric_fqn = result.get("fullyQualifiedName", "")
    if metric_fqn:
        result["ui_url"] = f"{client.host}/metric/{metric_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_metric(
    metric_id: str,
    metric_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing metric.

    Args:
        metric_id: ID of the metric to update
        metric_data: Updated metric data

    Returns:
        List of MCP content types containing updated metric details
    """
    client = get_client()
    result = client.put(f"metrics/{metric_id}", json_data=metric_data)

    # Add UI URL for web interface integration
    metric_fqn = result.get("fullyQualifiedName", "")
    if metric_fqn:
        result["ui_url"] = f"{client.host}/metric/{metric_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_metric(
    metric_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a metric.

    Args:
        metric_id: ID of the metric to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"metrics/{metric_id}", params=params)

    return [types.TextContent(type="text", text=f"Metric {metric_id} deleted successfully")]
