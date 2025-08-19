"""Report entity management for OpenMetadata.

This module provides comprehensive report management operations including
CRUD operations, field filtering, pagination support, and report scheduling metadata.
Reports are static information computed from data periodically that includes data in text, table, and visual form.
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
        (list_reports, "list_reports", "List reports from OpenMetadata with pagination and filtering"),
        (get_report, "get_report", "Get details of a specific report by ID"),
        (get_report_by_name, "get_report_by_name", "Get details of a specific report by fully qualified name"),
        (create_report, "create_report", "Create a new report in OpenMetadata"),
        (update_report, "update_report", "Update an existing report in OpenMetadata"),
        (delete_report, "delete_report", "Delete a report from OpenMetadata"),
    ]


async def list_reports(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    service: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List reports with pagination.

    Args:
        limit: Maximum number of reports to return (1 to 1000000)
        offset: Number of reports to skip
        fields: Comma-separated list of fields to include
        service: Filter reports by service name
        include_deleted: Whether to include deleted reports

    Returns:
        List of MCP content types containing report list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if service:
        params["service"] = service
    if include_deleted:
        params["include"] = "all"

    result = client.get("reports", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for report in result["data"]:
            report_fqn = report.get("fullyQualifiedName", "")
            if report_fqn:
                report["ui_url"] = f"{client.host}/report/{report_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_report(
    report_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific report by ID.

    Args:
        report_id: ID of the report
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing report details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"reports/{report_id}", params=params)

    # Add UI URL for web interface integration
    report_fqn = result.get("fullyQualifiedName", "")
    if report_fqn:
        result["ui_url"] = f"{client.host}/report/{report_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_report_by_name(
    fqn: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific report by fully qualified name.

    Args:
        fqn: Fully qualified name of the report
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing report details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"reports/name/{fqn}", params=params)

    # Add UI URL for web interface integration
    report_fqn = result.get("fullyQualifiedName", "")
    if report_fqn:
        result["ui_url"] = f"{client.host}/report/{report_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_report(
    report_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new report.

    Args:
        report_data: Report data including name, description, content, schedule, etc.

    Returns:
        List of MCP content types containing created report details
    """
    client = get_client()
    result = client.post("reports", json_data=report_data)

    # Add UI URL for web interface integration
    report_fqn = result.get("fullyQualifiedName", "")
    if report_fqn:
        result["ui_url"] = f"{client.host}/report/{report_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_report(
    report_id: str,
    report_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing report.

    Args:
        report_id: ID of the report to update
        report_data: Updated report data

    Returns:
        List of MCP content types containing updated report details
    """
    client = get_client()
    result = client.put(f"reports/{report_id}", json_data=report_data)

    # Add UI URL for web interface integration
    report_fqn = result.get("fullyQualifiedName", "")
    if report_fqn:
        result["ui_url"] = f"{client.host}/report/{report_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_report(
    report_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a report.

    Args:
        report_id: ID of the report to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"reports/{report_id}", params=params)

    return [types.TextContent(type="text", text=f"Report {report_id} deleted successfully")]
