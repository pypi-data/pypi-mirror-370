"""Glossary entity management for OpenMetadata.

This module provides comprehensive glossary management operations including
CRUD operations, field filtering, and glossary term relationship management.
Glossaries are collections of hierarchical glossary terms for business vocabulary.
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
        (list_glossaries, "list_glossaries", "List glossaries from OpenMetadata with pagination and filtering"),
        (get_glossary, "get_glossary", "Get details of a specific glossary by ID"),
        (get_glossary_by_name, "get_glossary_by_name", "Get details of a specific glossary by name"),
        (create_glossary, "create_glossary", "Create a new glossary in OpenMetadata"),
        (update_glossary, "update_glossary", "Update an existing glossary in OpenMetadata"),
        (delete_glossary, "delete_glossary", "Delete a glossary from OpenMetadata"),
        (list_glossary_terms, "list_glossary_terms", "List glossary terms with pagination and filtering"),
        (get_glossary_term, "get_glossary_term", "Get details of a specific glossary term by ID"),
    ]


async def list_glossaries(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List glossaries with pagination.

    Args:
        limit: Maximum number of glossaries to return (1 to 1000000)
        offset: Number of glossaries to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted glossaries

    Returns:
        List of MCP content types containing glossary list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get("glossaries", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for glossary in result["data"]:
            glossary_name = glossary.get("name", "")
            if glossary_name:
                glossary["ui_url"] = f"{client.host}/glossary/{glossary_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_glossary(
    glossary_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific glossary by ID.

    Args:
        glossary_id: ID of the glossary
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing glossary details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"glossaries/{glossary_id}", params=params)

    # Add UI URL for web interface integration
    glossary_name = result.get("name", "")
    if glossary_name:
        result["ui_url"] = f"{client.host}/glossary/{glossary_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_glossary_by_name(
    name: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific glossary by name.

    Args:
        name: Name of the glossary
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing glossary details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"glossaries/name/{name}", params=params)

    # Add UI URL for web interface integration
    glossary_name = result.get("name", "")
    if glossary_name:
        result["ui_url"] = f"{client.host}/glossary/{glossary_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_glossary(
    glossary_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new glossary.

    Args:
        glossary_data: Glossary data including name, description, terms, etc.

    Returns:
        List of MCP content types containing created glossary details
    """
    client = get_client()
    result = client.post("glossaries", json_data=glossary_data)

    # Add UI URL for web interface integration
    glossary_name = result.get("name", "")
    if glossary_name:
        result["ui_url"] = f"{client.host}/glossary/{glossary_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_glossary(
    glossary_id: str,
    glossary_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing glossary.

    Args:
        glossary_id: ID of the glossary to update
        glossary_data: Updated glossary data

    Returns:
        List of MCP content types containing updated glossary details
    """
    client = get_client()
    result = client.put(f"glossaries/{glossary_id}", json_data=glossary_data)

    # Add UI URL for web interface integration
    glossary_name = result.get("name", "")
    if glossary_name:
        result["ui_url"] = f"{client.host}/glossary/{glossary_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_glossary(
    glossary_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a glossary.

    Args:
        glossary_id: ID of the glossary to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"glossaries/{glossary_id}", params=params)

    return [types.TextContent(type="text", text=f"Glossary {glossary_id} deleted successfully")]


async def list_glossary_terms(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    glossary: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List glossary terms with pagination.

    Args:
        limit: Maximum number of glossary terms to return (1 to 1000000)
        offset: Number of glossary terms to skip
        fields: Comma-separated list of fields to include
        glossary: Filter terms by glossary name
        include_deleted: Whether to include deleted terms

    Returns:
        List of MCP content types containing glossary term list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if glossary:
        params["glossary"] = glossary
    if include_deleted:
        params["include"] = "all"

    result = client.get("glossaryTerms", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for term in result["data"]:
            term_fqn = term.get("fullyQualifiedName", "")
            if term_fqn:
                term["ui_url"] = f"{client.host}/glossaryTerm/{term_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_glossary_term(
    term_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific glossary term by ID.

    Args:
        term_id: ID of the glossary term
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing glossary term details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"glossaryTerms/{term_id}", params=params)

    # Add UI URL for web interface integration
    term_fqn = result.get("fullyQualifiedName", "")
    if term_fqn:
        result["ui_url"] = f"{client.host}/glossaryTerm/{term_fqn}"

    return [types.TextContent(type="text", text=str(result))]
