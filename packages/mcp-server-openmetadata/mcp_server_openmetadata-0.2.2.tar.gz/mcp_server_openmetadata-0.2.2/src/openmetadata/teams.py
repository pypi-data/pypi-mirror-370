"""Team entity management for OpenMetadata.

This module provides comprehensive team management operations including
CRUD operations, field filtering, pagination support, and user relationship management.
Teams are groups of users that can own data assets and follow hierarchical structures.
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
        (list_teams, "list_teams", "List teams from OpenMetadata with pagination and filtering"),
        (get_team, "get_team", "Get details of a specific team by ID"),
        (get_team_by_name, "get_team_by_name", "Get details of a specific team by name"),
        (create_team, "create_team", "Create a new team in OpenMetadata"),
        (update_team, "update_team", "Update an existing team in OpenMetadata"),
        (delete_team, "delete_team", "Delete a team from OpenMetadata"),
    ]


async def list_teams(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    parent_team: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List teams with pagination.

    Args:
        limit: Maximum number of teams to return (1 to 1000000)
        offset: Number of teams to skip
        fields: Comma-separated list of fields to include
        parent_team: Filter teams by parent team name
        include_deleted: Whether to include deleted teams

    Returns:
        List of MCP content types containing team list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}
    if fields:
        params["fields"] = fields
    if parent_team:
        params["parentTeam"] = parent_team
    if include_deleted:
        params["include"] = "all"

    result = client.get("teams", params=params)

    # Add UI URL for web interface integration
    if "data" in result:
        for team in result["data"]:
            team_name = team.get("name", "")
            if team_name:
                team["ui_url"] = f"{client.host}/team/{team_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_team(
    team_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific team by ID.

    Args:
        team_id: ID of the team
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing team details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"teams/{team_id}", params=params)

    # Add UI URL for web interface integration
    team_name = result.get("name", "")
    if team_name:
        result["ui_url"] = f"{client.host}/team/{team_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_team_by_name(
    name: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific team by name.

    Args:
        name: Name of the team
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing team details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"teams/name/{name}", params=params)

    # Add UI URL for web interface integration
    team_name = result.get("name", "")
    if team_name:
        result["ui_url"] = f"{client.host}/team/{team_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_team(
    team_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new team.

    Args:
        team_data: Team data including name, description, users, etc.

    Returns:
        List of MCP content types containing created team details
    """
    client = get_client()
    result = client.post("teams", json_data=team_data)

    # Add UI URL for web interface integration
    team_name = result.get("name", "")
    if team_name:
        result["ui_url"] = f"{client.host}/team/{team_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_team(
    team_id: str,
    team_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing team.

    Args:
        team_id: ID of the team to update
        team_data: Updated team data

    Returns:
        List of MCP content types containing updated team details
    """
    client = get_client()
    result = client.put(f"teams/{team_id}", json_data=team_data)

    # Add UI URL for web interface integration
    team_name = result.get("name", "")
    if team_name:
        result["ui_url"] = f"{client.host}/team/{team_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_team(
    team_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a team.

    Args:
        team_id: ID of the team to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"teams/{team_id}", params=params)

    return [types.TextContent(type="text", text=f"Team {team_id} deleted successfully")]
