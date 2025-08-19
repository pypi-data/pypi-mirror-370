"""Dashboard entity management for OpenMetadata.

This module provides comprehensive dashboard management operations including
CRUD operations, field filtering, pagination support, and chart relationship management.
Dashboards are computed from data and visually present data, metrics, and KPIs.
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
        (list_dashboards, "list_dashboards", "List dashboards from OpenMetadata with pagination and filtering"),
        (get_dashboard, "get_dashboard", "Get details of a specific dashboard by ID"),
        (get_dashboard_by_name, "get_dashboard_by_name", "Get details of a specific dashboard by fully qualified name"),
        (create_dashboard, "create_dashboard", "Create a new dashboard in OpenMetadata"),
        (update_dashboard, "update_dashboard", "Update an existing dashboard in OpenMetadata"),
        (delete_dashboard, "delete_dashboard", "Delete a dashboard from OpenMetadata"),
    ]


async def list_dashboards(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    service: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List dashboards with pagination.

    Args:
        limit: Maximum number of dashboards to return (1 to 1000000)
        offset: Number of dashboards to skip
        fields: Comma-separated list of fields to include
        service: Filter dashboards by service name
        include_deleted: Whether to include deleted dashboards

    Returns:
        List of MCP content types containing dashboard list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if service:
        params["service"] = service
    if include_deleted:
        params["include"] = "all"

    result = client.get("dashboards", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for dashboard in result["data"]:
            dashboard_fqn = dashboard.get("fullyQualifiedName", "")
            if dashboard_fqn:
                dashboard["ui_url"] = f"{client.host}/dashboard/{dashboard_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_dashboard(
    dashboard_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific dashboard by ID.

    Args:
        dashboard_id: ID of the dashboard
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing dashboard details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"dashboards/{dashboard_id}", params=params)

    # Add UI URL for web interface integration
    dashboard_fqn = result.get("fullyQualifiedName", "")
    if dashboard_fqn:
        result["ui_url"] = f"{client.host}/dashboard/{dashboard_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_dashboard_by_name(
    fqn: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific dashboard by fully qualified name.

    Args:
        fqn: Fully qualified name of the dashboard
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing dashboard details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"dashboards/name/{fqn}", params=params)

    # Add UI URL for web interface integration
    dashboard_fqn = result.get("fullyQualifiedName", "")
    if dashboard_fqn:
        result["ui_url"] = f"{client.host}/dashboard/{dashboard_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_dashboard(
    dashboard_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new dashboard.

    Args:
        dashboard_data: Dashboard data including name, description, charts, etc.

    Returns:
        List of MCP content types containing created dashboard details
    """
    client = get_client()
    result = client.post("dashboards", json_data=dashboard_data)

    # Add UI URL for web interface integration
    dashboard_fqn = result.get("fullyQualifiedName", "")
    if dashboard_fqn:
        result["ui_url"] = f"{client.host}/dashboard/{dashboard_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_dashboard(
    dashboard_id: str,
    dashboard_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing dashboard.

    Args:
        dashboard_id: ID of the dashboard to update
        dashboard_data: Updated dashboard data

    Returns:
        List of MCP content types containing updated dashboard details
    """
    client = get_client()
    result = client.put(f"dashboards/{dashboard_id}", json_data=dashboard_data)

    # Add UI URL for web interface integration
    dashboard_fqn = result.get("fullyQualifiedName", "")
    if dashboard_fqn:
        result["ui_url"] = f"{client.host}/dashboard/{dashboard_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_dashboard(
    dashboard_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a dashboard.

    Args:
        dashboard_id: ID of the dashboard to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"dashboards/{dashboard_id}", params=params)

    return [types.TextContent(type="text", text=f"Dashboard {dashboard_id} deleted successfully")]
