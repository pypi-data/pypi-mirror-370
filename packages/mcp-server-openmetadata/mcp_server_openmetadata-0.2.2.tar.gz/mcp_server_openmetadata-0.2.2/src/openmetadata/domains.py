"""Domains and Data Products management for OpenMetadata.

This module provides comprehensive domain management operations including
CRUD operations for domains, data products, and domain organization.
Domains help organize data assets by business context and ownership.
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
        (list_domains, "list_domains", "List domains with pagination and filtering"),
        (get_domain, "get_domain", "Get details of a specific domain by ID"),
        (get_domain_by_name, "get_domain_by_name", "Get details of a specific domain by name"),
        (create_domain, "create_domain", "Create a new domain in OpenMetadata"),
        (update_domain, "update_domain", "Update an existing domain"),
        (delete_domain, "delete_domain", "Delete a domain from OpenMetadata"),
        (list_data_products, "list_data_products", "List data products with pagination"),
        (get_data_product, "get_data_product", "Get details of a specific data product by ID"),
        (get_data_product_by_name, "get_data_product_by_name", "Get details of a data product by name"),
        (create_data_product, "create_data_product", "Create a new data product"),
        (update_data_product, "update_data_product", "Update an existing data product"),
        (delete_data_product, "delete_data_product", "Delete a data product"),
    ]


async def list_domains(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
    q: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List domains with pagination and filtering.

    Args:
        limit: Maximum number of domains to return (1 to 1000000)
        offset: Number of domains to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted domains
        q: Search query for domain name or description

    Returns:
        List of MCP content types containing domain list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"
    if q:
        params["q"] = q

    result = client.get("domains", params=params)

    # Add UI URLs for domains
    if "data" in result:
        for domain in result["data"]:
            domain_name = domain.get("name", "")
            if domain_name:
                domain["ui_url"] = f"{client.host}/domain/{domain_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_domain(
    domain_id: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific domain by ID.

    Args:
        domain_id: ID of the domain
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted domains

    Returns:
        List of MCP content types containing domain details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"domains/{domain_id}", params=params)

    # Add UI URL
    domain_name = result.get("name", "")
    if domain_name:
        result["ui_url"] = f"{client.host}/domain/{domain_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_domain_by_name(
    name: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific domain by name.

    Args:
        name: Name of the domain
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted domains

    Returns:
        List of MCP content types containing domain details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"domains/name/{name}", params=params)

    # Add UI URL
    domain_name = result.get("name", "")
    if domain_name:
        result["ui_url"] = f"{client.host}/domain/{domain_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_domain(
    domain_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new domain.

    Args:
        domain_data: Domain data including name, description, domain type, experts, etc.

    Returns:
        List of MCP content types containing created domain details
    """
    client = get_client()
    result = client.post("domains", json_data=domain_data)

    # Add UI URL
    domain_name = result.get("name", "")
    if domain_name:
        result["ui_url"] = f"{client.host}/domain/{domain_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_domain(
    domain_id: str,
    domain_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing domain.

    Args:
        domain_id: ID of the domain to update
        domain_data: Updated domain data

    Returns:
        List of MCP content types containing updated domain details
    """
    client = get_client()
    result = client.put(f"domains/{domain_id}", json_data=domain_data)

    # Add UI URL
    domain_name = result.get("name", "")
    if domain_name:
        result["ui_url"] = f"{client.host}/domain/{domain_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_domain(
    domain_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a domain.

    Args:
        domain_id: ID of the domain to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"domains/{domain_id}", params=params)

    return [types.TextContent(type="text", text=f"Domain {domain_id} deleted successfully")]


async def list_data_products(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    domain: Optional[str] = None,
    include_deleted: bool = False,
    q: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List data products with pagination and filtering.

    Args:
        limit: Maximum number of data products to return (1 to 1000000)
        offset: Number of data products to skip
        fields: Comma-separated list of fields to include
        domain: Filter by domain name
        include_deleted: Whether to include deleted data products
        q: Search query for data product name or description

    Returns:
        List of MCP content types containing data product list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if domain:
        params["domain"] = domain
    if include_deleted:
        params["include"] = "all"
    if q:
        params["q"] = q

    result = client.get("dataProducts", params=params)

    # Add UI URLs for data products
    if "data" in result:
        for data_product in result["data"]:
            product_fqn = data_product.get("fullyQualifiedName", "")
            if product_fqn:
                data_product["ui_url"] = f"{client.host}/data-product/{product_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_data_product(
    data_product_id: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific data product by ID.

    Args:
        data_product_id: ID of the data product
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted data products

    Returns:
        List of MCP content types containing data product details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"dataProducts/{data_product_id}", params=params)

    # Add UI URL
    product_fqn = result.get("fullyQualifiedName", "")
    if product_fqn:
        result["ui_url"] = f"{client.host}/data-product/{product_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_data_product_by_name(
    name: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific data product by fully qualified name.

    Args:
        name: Fully qualified name of the data product
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted data products

    Returns:
        List of MCP content types containing data product details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"dataProducts/name/{name}", params=params)

    # Add UI URL
    product_fqn = result.get("fullyQualifiedName", "")
    if product_fqn:
        result["ui_url"] = f"{client.host}/data-product/{product_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_data_product(
    data_product_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new data product.

    Args:
        data_product_data: Data product data including name, description, domain, assets, etc.

    Returns:
        List of MCP content types containing created data product details
    """
    client = get_client()
    result = client.post("dataProducts", json_data=data_product_data)

    # Add UI URL
    product_fqn = result.get("fullyQualifiedName", "")
    if product_fqn:
        result["ui_url"] = f"{client.host}/data-product/{product_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_data_product(
    data_product_id: str,
    data_product_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing data product.

    Args:
        data_product_id: ID of the data product to update
        data_product_data: Updated data product data

    Returns:
        List of MCP content types containing updated data product details
    """
    client = get_client()
    result = client.put(f"dataProducts/{data_product_id}", json_data=data_product_data)

    # Add UI URL
    product_fqn = result.get("fullyQualifiedName", "")
    if product_fqn:
        result["ui_url"] = f"{client.host}/data-product/{product_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_data_product(
    data_product_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a data product.

    Args:
        data_product_id: ID of the data product to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"dataProducts/{data_product_id}", params=params)

    return [types.TextContent(type="text", text=f"Data product {data_product_id} deleted successfully")]
