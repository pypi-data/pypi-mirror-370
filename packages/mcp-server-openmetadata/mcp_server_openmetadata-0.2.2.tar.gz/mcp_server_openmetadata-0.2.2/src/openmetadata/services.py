"""Service management for OpenMetadata.

This module provides comprehensive service management operations including
database services, dashboard services, messaging services, and other service types.
Services are the connections to external systems from which metadata is collected.
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
        (list_database_services, "list_database_services", "List database services"),
        (get_database_service, "get_database_service", "Get database service by ID"),
        (get_database_service_by_name, "get_database_service_by_name", "Get database service by name"),
        (create_database_service, "create_database_service", "Create a new database service"),
        (update_database_service, "update_database_service", "Update a database service"),
        (delete_database_service, "delete_database_service", "Delete a database service"),
        (list_dashboard_services, "list_dashboard_services", "List dashboard services"),
        (get_dashboard_service, "get_dashboard_service", "Get dashboard service by ID"),
        (create_dashboard_service, "create_dashboard_service", "Create a new dashboard service"),
        (list_messaging_services, "list_messaging_services", "List messaging services"),
        (get_messaging_service, "get_messaging_service", "Get messaging service by ID"),
        (create_messaging_service, "create_messaging_service", "Create a new messaging service"),
        (test_connection, "test_service_connection", "Test connection to a service"),
    ]


# Database Services
async def list_database_services(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List database services with pagination.

    Args:
        limit: Maximum number of services to return (1 to 1000000)
        offset: Number of services to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted services

    Returns:
        List of MCP content types containing service list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get("services/databaseServices", params=params)

    # Add UI URLs for services
    if "data" in result:
        for service in result["data"]:
            service_name = service.get("name", "")
            if service_name:
                service["ui_url"] = f"{client.host}/services/database/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_database_service(
    service_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific database service by ID.

    Args:
        service_id: ID of the service
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing service details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"services/databaseServices/{service_id}", params=params)

    # Add UI URL
    service_name = result.get("name", "")
    if service_name:
        result["ui_url"] = f"{client.host}/services/database/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_database_service_by_name(
    service_name: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific database service by name.

    Args:
        service_name: Name of the service
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing service details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"services/databaseServices/name/{service_name}", params=params)

    # Add UI URL
    service_name_result = result.get("name", "")
    if service_name_result:
        result["ui_url"] = f"{client.host}/services/database/{service_name_result}"

    return [types.TextContent(type="text", text=str(result))]


async def create_database_service(
    service_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new database service.

    Args:
        service_data: Service data including name, description, connection, etc.

    Returns:
        List of MCP content types containing created service details
    """
    client = get_client()
    result = client.post("services/databaseServices", json_data=service_data)

    # Add UI URL
    service_name = result.get("name", "")
    if service_name:
        result["ui_url"] = f"{client.host}/services/database/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_database_service(
    service_id: str,
    service_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing database service.

    Args:
        service_id: ID of the service to update
        service_data: Updated service data

    Returns:
        List of MCP content types containing updated service details
    """
    client = get_client()
    result = client.put(f"services/databaseServices/{service_id}", json_data=service_data)

    # Add UI URL
    service_name = result.get("name", "")
    if service_name:
        result["ui_url"] = f"{client.host}/services/database/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_database_service(
    service_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a database service.

    Args:
        service_id: ID of the service to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"services/databaseServices/{service_id}", params=params)

    return [types.TextContent(type="text", text=f"Database service {service_id} deleted successfully")]


# Dashboard Services
async def list_dashboard_services(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List dashboard services with pagination.

    Args:
        limit: Maximum number of services to return (1 to 1000000)
        offset: Number of services to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted services

    Returns:
        List of MCP content types containing service list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get("services/dashboardServices", params=params)

    # Add UI URLs for services
    if "data" in result:
        for service in result["data"]:
            service_name = service.get("name", "")
            if service_name:
                service["ui_url"] = f"{client.host}/services/dashboard/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_dashboard_service(
    service_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific dashboard service by ID.

    Args:
        service_id: ID of the service
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing service details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"services/dashboardServices/{service_id}", params=params)

    # Add UI URL
    service_name = result.get("name", "")
    if service_name:
        result["ui_url"] = f"{client.host}/services/dashboard/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_dashboard_service(
    service_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new dashboard service.

    Args:
        service_data: Service data including name, description, connection, etc.

    Returns:
        List of MCP content types containing created service details
    """
    client = get_client()
    result = client.post("services/dashboardServices", json_data=service_data)

    # Add UI URL
    service_name = result.get("name", "")
    if service_name:
        result["ui_url"] = f"{client.host}/services/dashboard/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


# Messaging Services
async def list_messaging_services(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List messaging services with pagination.

    Args:
        limit: Maximum number of services to return (1 to 1000000)
        offset: Number of services to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted services

    Returns:
        List of MCP content types containing service list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get("services/messagingServices", params=params)

    # Add UI URLs for services
    if "data" in result:
        for service in result["data"]:
            service_name = service.get("name", "")
            if service_name:
                service["ui_url"] = f"{client.host}/services/messaging/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_messaging_service(
    service_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific messaging service by ID.

    Args:
        service_id: ID of the service
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing service details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"services/messagingServices/{service_id}", params=params)

    # Add UI URL
    service_name = result.get("name", "")
    if service_name:
        result["ui_url"] = f"{client.host}/services/messaging/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_messaging_service(
    service_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new messaging service.

    Args:
        service_data: Service data including name, description, connection, etc.

    Returns:
        List of MCP content types containing created service details
    """
    client = get_client()
    result = client.post("services/messagingServices", json_data=service_data)

    # Add UI URL
    service_name = result.get("name", "")
    if service_name:
        result["ui_url"] = f"{client.host}/services/messaging/{service_name}"

    return [types.TextContent(type="text", text=str(result))]


# Utility Functions
async def test_connection(
    connection_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Test connection to a service.

    Args:
        connection_data: Connection configuration to test

    Returns:
        List of MCP content types containing connection test results
    """
    client = get_client()
    result = client.post("services/testConnection", json_data=connection_data)

    return [types.TextContent(type="text", text=str(result))]
