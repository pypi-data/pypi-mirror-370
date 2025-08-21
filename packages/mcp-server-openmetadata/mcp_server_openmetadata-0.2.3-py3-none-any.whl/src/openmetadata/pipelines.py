"""Pipeline entity management for OpenMetadata.

This module provides comprehensive pipeline management operations including
CRUD operations, field filtering, pagination support, and task relationship management.
Pipelines enable the flow of data from source to destination through processing steps.
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
        (list_pipelines, "list_pipelines", "List pipelines from OpenMetadata with pagination and filtering"),
        (get_pipeline, "get_pipeline", "Get details of a specific pipeline by ID"),
        (get_pipeline_by_name, "get_pipeline_by_name", "Get details of a specific pipeline by fully qualified name"),
        (create_pipeline, "create_pipeline", "Create a new pipeline in OpenMetadata"),
        (update_pipeline, "update_pipeline", "Update an existing pipeline in OpenMetadata"),
        (delete_pipeline, "delete_pipeline", "Delete a pipeline from OpenMetadata"),
    ]


async def list_pipelines(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    service: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List pipelines with pagination.

    Args:
        limit: Maximum number of pipelines to return (1 to 1000000)
        offset: Number of pipelines to skip
        fields: Comma-separated list of fields to include
        service: Filter pipelines by service name
        include_deleted: Whether to include deleted pipelines

    Returns:
        List of MCP content types containing pipeline list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if service:
        params["service"] = service
    if include_deleted:
        params["include"] = "all"

    result = client.get("pipelines", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for pipeline in result["data"]:
            pipeline_fqn = pipeline.get("fullyQualifiedName", "")
            if pipeline_fqn:
                pipeline["ui_url"] = f"{client.host}/pipeline/{pipeline_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_pipeline(
    pipeline_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific pipeline by ID.

    Args:
        pipeline_id: ID of the pipeline
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing pipeline details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"pipelines/{pipeline_id}", params=params)

    # Add UI URL for web interface integration
    pipeline_fqn = result.get("fullyQualifiedName", "")
    if pipeline_fqn:
        result["ui_url"] = f"{client.host}/pipeline/{pipeline_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_pipeline_by_name(
    fqn: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific pipeline by fully qualified name.

    Args:
        fqn: Fully qualified name of the pipeline
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing pipeline details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"pipelines/name/{fqn}", params=params)

    # Add UI URL for web interface integration
    pipeline_fqn = result.get("fullyQualifiedName", "")
    if pipeline_fqn:
        result["ui_url"] = f"{client.host}/pipeline/{pipeline_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_pipeline(
    pipeline_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new pipeline.

    Args:
        pipeline_data: Pipeline data including name, description, tasks, etc.

    Returns:
        List of MCP content types containing created pipeline details
    """
    client = get_client()
    result = client.post("pipelines", json_data=pipeline_data)

    # Add UI URL for web interface integration
    pipeline_fqn = result.get("fullyQualifiedName", "")
    if pipeline_fqn:
        result["ui_url"] = f"{client.host}/pipeline/{pipeline_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_pipeline(
    pipeline_id: str,
    pipeline_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing pipeline.

    Args:
        pipeline_id: ID of the pipeline to update
        pipeline_data: Updated pipeline data

    Returns:
        List of MCP content types containing updated pipeline details
    """
    client = get_client()
    result = client.put(f"pipelines/{pipeline_id}", json_data=pipeline_data)

    # Add UI URL for web interface integration
    pipeline_fqn = result.get("fullyQualifiedName", "")
    if pipeline_fqn:
        result["ui_url"] = f"{client.host}/pipeline/{pipeline_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_pipeline(
    pipeline_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a pipeline.

    Args:
        pipeline_id: ID of the pipeline to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"pipelines/{pipeline_id}", params=params)

    return [types.TextContent(type="text", text=f"Pipeline {pipeline_id} deleted successfully")]
