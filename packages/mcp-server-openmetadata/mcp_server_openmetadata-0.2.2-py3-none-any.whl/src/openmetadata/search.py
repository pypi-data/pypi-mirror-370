"""Search functionality for OpenMetadata.

This module provides comprehensive search operations including
full-text search, entity suggestions, and advanced search filtering.
Search APIs help discover and explore data assets across the organization.
"""

from typing import Callable, List, Optional, Union

import mcp.types as types

from src.openmetadata.openmetadata_client import get_client


def get_all_functions() -> List[tuple[Callable, str, str]]:
    """Return list of (function, name, description) tuples for registration.

    Returns:
        List of tuples containing function reference, tool name, and description
    """
    return [
        (search_entities, "search_entities", "Search entities using query text"),
        (suggest_entities, "suggest_entities", "Get suggested entities for auto-completion"),
        (search_aggregate, "search_aggregate", "Get aggregated search results with facets"),
        (search_field_query, "search_field_query", "Search entities with specific field and value"),
    ]


async def search_entities(
    q: str,
    index: Optional[str] = None,
    from_: int = 0,
    size: int = 10,
    sort: Optional[str] = None,
    service_name: Optional[str] = None,
    classification: Optional[str] = None,
    entity_type: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Search entities using query text.

    Args:
        q: Search query text
        index: Elasticsearch index to search in
        from_: Starting offset for pagination
        size: Number of results to return
        sort: Sort order (e.g., 'name.keyword:asc')
        service_name: Filter by service name
        classification: Filter by classification
        entity_type: Filter by entity type (table, dashboard, etc.)

    Returns:
        List of MCP content types containing search results
    """
    client = get_client()
    params = {
        "q": q,
        "from": from_,
        "size": min(max(1, size), 100),
    }

    if index:
        params["index"] = index
    if sort:
        params["sort"] = sort
    if service_name:
        params["serviceName"] = service_name
    if classification:
        params["classification"] = classification
    if entity_type:
        params["entityType"] = entity_type

    result = client.get("search/query", params=params)

    # Add UI URLs for search results
    if "hits" in result and "hits" in result["hits"]:
        for hit in result["hits"]["hits"]:
            source = hit.get("_source", {})
            entity_type_hit = source.get("entityType", "")
            fqn = source.get("fullyQualifiedName", "")
            if entity_type_hit and fqn:
                source["ui_url"] = f"{client.host}/{entity_type_hit.lower()}/{fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def suggest_entities(
    q: str,
    index: Optional[str] = None,
    field: Optional[str] = None,
    size: int = 10,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get suggested entities for auto-completion.

    Args:
        q: Query text for suggestions
        index: Elasticsearch index to search in
        field: Field to get suggestions for
        size: Number of suggestions to return

    Returns:
        List of MCP content types containing suggestion results
    """
    client = get_client()
    params = {
        "q": q,
        "size": min(max(1, size), 25),
    }

    if index:
        params["index"] = index
    if field:
        params["field"] = field

    result = client.get("search/suggest", params=params)

    return [types.TextContent(type="text", text=str(result))]


async def search_aggregate(
    q: str,
    index: Optional[str] = None,
    from_: int = 0,
    size: int = 10,
    facets: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get aggregated search results with facets.

    Args:
        q: Search query text
        index: Elasticsearch index to search in
        from_: Starting offset for pagination
        size: Number of results to return
        facets: Comma-separated list of facet fields

    Returns:
        List of MCP content types containing aggregated search results
    """
    client = get_client()
    params = {
        "q": q,
        "from": from_,
        "size": min(max(1, size), 100),
    }

    if index:
        params["index"] = index
    if facets:
        params["facets"] = facets

    result = client.get("search/aggregate", params=params)

    return [types.TextContent(type="text", text=str(result))]


async def search_field_query(
    field_name: str,
    field_value: str,
    index: Optional[str] = None,
    size: int = 10,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Search entities with specific field and value.

    Args:
        field_name: Name of the field to search
        field_value: Value to search for in the field
        index: Elasticsearch index to search in
        size: Number of results to return

    Returns:
        List of MCP content types containing search results
    """
    client = get_client()
    params = {
        "fieldName": field_name,
        "fieldValue": field_value,
        "size": min(max(1, size), 100),
    }

    if index:
        params["index"] = index

    result = client.get("search/fieldQuery", params=params)

    return [types.TextContent(type="text", text=str(result))]
