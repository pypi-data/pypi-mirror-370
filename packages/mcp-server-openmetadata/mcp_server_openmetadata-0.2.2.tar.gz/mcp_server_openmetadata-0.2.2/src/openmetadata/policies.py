"""Policies management for OpenMetadata Access Control.

This module provides comprehensive policy management operations including
CRUD operations for access policies, data policies, and security configurations.
Policies control access to metadata entities and resources in OpenMetadata.
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
        (list_policies, "list_policies", "List policies with pagination and filtering"),
        (get_policy, "get_policy", "Get details of a specific policy by ID"),
        (get_policy_by_name, "get_policy_by_name", "Get details of a specific policy by name"),
        (create_policy, "create_policy", "Create a new policy in OpenMetadata"),
        (update_policy, "update_policy", "Update an existing policy"),
        (delete_policy, "delete_policy", "Delete a policy from OpenMetadata"),
        (validate_policy, "validate_policy", "Validate policy rules and conditions"),
        (list_policy_resources, "list_policy_resources", "List available resources for policy creation"),
    ]


async def list_policies(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    policy_type: Optional[str] = None,
    include_deleted: bool = False,
    q: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List policies with pagination and filtering.

    Args:
        limit: Maximum number of policies to return (1 to 1000000)
        offset: Number of policies to skip
        fields: Comma-separated list of fields to include
        policy_type: Filter by policy type (AccessControl, Privacy, Lifecycle)
        include_deleted: Whether to include deleted policies
        q: Search query for policy name or description

    Returns:
        List of MCP content types containing policy list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if policy_type:
        params["policyType"] = policy_type
    if include_deleted:
        params["include"] = "all"
    if q:
        params["q"] = q

    result = client.get("policies", params=params)

    # Add UI URLs for policies
    if "data" in result:
        for policy in result["data"]:
            policy_name = policy.get("name", "")
            if policy_name:
                policy["ui_url"] = f"{client.host}/settings/access/policies/{policy_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_policy(
    policy_id: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific policy by ID.

    Args:
        policy_id: ID of the policy
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted policies

    Returns:
        List of MCP content types containing policy details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"policies/{policy_id}", params=params)

    # Add UI URL
    policy_name = result.get("name", "")
    if policy_name:
        result["ui_url"] = f"{client.host}/settings/access/policies/{policy_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_policy_by_name(
    name: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific policy by name.

    Args:
        name: Name of the policy
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted policies

    Returns:
        List of MCP content types containing policy details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"policies/name/{name}", params=params)

    # Add UI URL
    policy_name = result.get("name", "")
    if policy_name:
        result["ui_url"] = f"{client.host}/settings/access/policies/{policy_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_policy(
    policy_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new policy.

    Args:
        policy_data: Policy data including name, description, rules, policy type, etc.

    Returns:
        List of MCP content types containing created policy details
    """
    client = get_client()
    result = client.post("policies", json_data=policy_data)

    # Add UI URL
    policy_name = result.get("name", "")
    if policy_name:
        result["ui_url"] = f"{client.host}/settings/access/policies/{policy_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_policy(
    policy_id: str,
    policy_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing policy.

    Args:
        policy_id: ID of the policy to update
        policy_data: Updated policy data

    Returns:
        List of MCP content types containing updated policy details
    """
    client = get_client()
    result = client.put(f"policies/{policy_id}", json_data=policy_data)

    # Add UI URL
    policy_name = result.get("name", "")
    if policy_name:
        result["ui_url"] = f"{client.host}/settings/access/policies/{policy_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_policy(
    policy_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a policy.

    Args:
        policy_id: ID of the policy to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"policies/{policy_id}", params=params)

    return [types.TextContent(type="text", text=f"Policy {policy_id} deleted successfully")]


async def validate_policy(
    policy_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Validate policy rules and conditions.

    Args:
        policy_data: Policy data to validate

    Returns:
        List of MCP content types containing validation results
    """
    client = get_client()
    result = client.post("policies/validation/condition", json_data=policy_data)

    return [types.TextContent(type="text", text=str(result))]


async def list_policy_resources() -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List available resources for policy creation.

    Returns:
        List of MCP content types containing available policy resources
    """
    client = get_client()
    result = client.get("policies/resources")

    return [types.TextContent(type="text", text=str(result))]
