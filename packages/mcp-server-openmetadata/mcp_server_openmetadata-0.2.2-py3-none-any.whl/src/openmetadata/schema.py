"""Schema-level metadata management for OpenMetadata.

This module provides schema CRUD operations, table relationship management,
and namespace organization functionality.
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
        (list_schemas, "list_schemas", "List database schemas from OpenMetadata with pagination and filtering"),
        (get_schema, "get_schema", "Get details of a specific schema by ID"),
        (get_schema_by_name, "get_schema_by_name", "Get details of a specific schema by fully qualified name"),
        (create_schema, "create_schema", "Create a new database schema in OpenMetadata"),
        (update_schema, "update_schema", "Update an existing database schema in OpenMetadata"),
        (delete_schema, "delete_schema", "Delete a database schema from OpenMetadata"),
    ]


async def list_schemas(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    database: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List database schemas with pagination.

    Args:
        limit: Maximum number of schemas to return
        offset: Number of schemas to skip
        fields: Comma-separated list of fields to include
        database: Filter schemas by database fully qualified name
        include_deleted: Whether to include deleted schemas

    Returns:
        List of MCP content types containing schema list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if database:
        params["database"] = database
    if include_deleted:
        params["include"] = "all"

    result = client.get("databaseSchemas", params=params)

    # Add UI URLs for web interface integration
    if "data" in result:
        for schema in result["data"]:
            schema_fqn = schema.get("fullyQualifiedName", "")
            if schema_fqn:
                schema["ui_url"] = f"{client.host}/schema/{schema_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_schema(
    schema_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific schema by ID.

    Args:
        schema_id: ID of the schema
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing schema details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"databaseSchemas/{schema_id}", params=params)

    # Add UI URL for web interface integration
    schema_fqn = result.get("fullyQualifiedName", "")
    if schema_fqn:
        result["ui_url"] = f"{client.host}/schema/{schema_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_schema_by_name(
    fqn: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific schema by fully qualified name.

    Args:
        fqn: Fully qualified name of the schema
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing schema details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"databaseSchemas/name/{fqn}", params=params)

    # Add UI URL for web interface integration
    schema_fqn = result.get("fullyQualifiedName", "")
    if schema_fqn:
        result["ui_url"] = f"{client.host}/schema/{schema_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_schema(
    schema_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new database schema.

    Args:
        schema_data: Schema data including name, description, database, etc.

    Returns:
        List of MCP content types containing created schema details
    """
    client = get_client()
    result = client.post("databaseSchemas", json_data=schema_data)

    # Add UI URL for web interface integration
    schema_fqn = result.get("fullyQualifiedName", "")
    if schema_fqn:
        result["ui_url"] = f"{client.host}/schema/{schema_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_schema(
    schema_id: str,
    schema_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing database schema.

    Args:
        schema_id: ID of the schema to update
        schema_data: Updated schema data

    Returns:
        List of MCP content types containing updated schema details
    """
    client = get_client()
    result = client.put(f"databaseSchemas/{schema_id}", json_data=schema_data)

    # Add UI URL for web interface integration
    schema_fqn = result.get("fullyQualifiedName", "")
    if schema_fqn:
        result["ui_url"] = f"{client.host}/schema/{schema_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_schema(
    schema_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a database schema.

    Args:
        schema_id: ID of the schema to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"databaseSchemas/{schema_id}", params=params)

    return [types.TextContent(type="text", text=f"Schema {schema_id} deleted successfully")]
