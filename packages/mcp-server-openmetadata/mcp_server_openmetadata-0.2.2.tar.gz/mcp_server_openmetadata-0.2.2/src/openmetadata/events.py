"""Events and Event Subscriptions management for OpenMetadata.

This module provides comprehensive event management operations including
event subscriptions, webhook configurations, event filtering, and notifications.
Events are changes to metadata sent when entities are created, modified, or updated.
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
        (list_events, "list_events", "List events with pagination and filtering"),
        (list_event_subscriptions, "list_event_subscriptions", "List event subscriptions"),
        (get_event_subscription, "get_event_subscription", "Get event subscription by ID"),
        (get_event_subscription_by_name, "get_event_subscription_by_name", "Get event subscription by name"),
        (create_event_subscription, "create_event_subscription", "Create a new event subscription"),
        (update_event_subscription, "update_event_subscription", "Update an existing event subscription"),
        (delete_event_subscription, "delete_event_subscription", "Delete an event subscription"),
        (test_destination, "test_event_destination", "Test event subscription destination"),
        (get_failed_events, "get_failed_events", "Get failed events for a subscription"),
        (get_subscription_status, "get_subscription_status", "Get status of event subscription destination"),
    ]


async def list_events(
    limit: int = 10,
    offset: int = 0,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    event_type: Optional[str] = None,
    timestamp_start: Optional[int] = None,
    timestamp_end: Optional[int] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List events with pagination and filtering.

    Args:
        limit: Maximum number of events to return (1 to 1000000)
        offset: Number of events to skip
        entity_type: Filter by entity type
        entity_id: Filter by entity ID
        event_type: Filter by event type
        timestamp_start: Filter events after this timestamp
        timestamp_end: Filter events before this timestamp

    Returns:
        List of MCP content types containing event list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if entity_type:
        params["entityType"] = entity_type
    if entity_id:
        params["entityId"] = entity_id
    if event_type:
        params["eventType"] = event_type
    if timestamp_start:
        params["timestampStart"] = timestamp_start
    if timestamp_end:
        params["timestampEnd"] = timestamp_end

    result = client.get("events", params=params)

    return [types.TextContent(type="text", text=str(result))]


async def list_event_subscriptions(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List event subscriptions with pagination.

    Args:
        limit: Maximum number of subscriptions to return (1 to 1000000)
        offset: Number of subscriptions to skip
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted subscriptions

    Returns:
        List of MCP content types containing subscription list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get("events/subscriptions", params=params)

    # Add UI URLs for subscriptions
    if "data" in result:
        for subscription in result["data"]:
            subscription_name = subscription.get("name", "")
            if subscription_name:
                subscription["ui_url"] = f"{client.host}/settings/members/teams/event-subscriptions/{subscription_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_event_subscription(
    subscription_id: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific event subscription by ID.

    Args:
        subscription_id: ID of the event subscription
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing subscription details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"events/subscriptions/id/{subscription_id}", params=params)

    # Add UI URL
    subscription_name = result.get("name", "")
    if subscription_name:
        result["ui_url"] = f"{client.host}/settings/members/teams/event-subscriptions/{subscription_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_event_subscription_by_name(
    name: str,
    fields: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific event subscription by name.

    Args:
        name: Name of the event subscription
        fields: Comma-separated list of fields to include

    Returns:
        List of MCP content types containing subscription details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields

    result = client.get(f"events/subscriptions/name/{name}", params=params)

    # Add UI URL
    subscription_name = result.get("name", "")
    if subscription_name:
        result["ui_url"] = f"{client.host}/settings/members/teams/event-subscriptions/{subscription_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_event_subscription(
    subscription_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new event subscription.

    Args:
        subscription_data: Subscription data including name, description, destinations, filters, etc.

    Returns:
        List of MCP content types containing created subscription details
    """
    client = get_client()
    result = client.post("events/subscriptions", json_data=subscription_data)

    # Add UI URL
    subscription_name = result.get("name", "")
    if subscription_name:
        result["ui_url"] = f"{client.host}/settings/members/teams/event-subscriptions/{subscription_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_event_subscription(
    subscription_id: str,
    subscription_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing event subscription.

    Args:
        subscription_id: ID of the subscription to update
        subscription_data: Updated subscription data

    Returns:
        List of MCP content types containing updated subscription details
    """
    client = get_client()
    result = client.put(f"events/subscriptions/{subscription_id}", json_data=subscription_data)

    # Add UI URL
    subscription_name = result.get("name", "")
    if subscription_name:
        result["ui_url"] = f"{client.host}/settings/members/teams/event-subscriptions/{subscription_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_event_subscription(
    subscription_id: str,
    hard_delete: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete an event subscription.

    Args:
        subscription_id: ID of the subscription to delete
        hard_delete: Whether to perform a hard delete

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete}
    client.delete(f"events/subscriptions/{subscription_id}", params=params)

    return [types.TextContent(type="text", text=f"Event subscription {subscription_id} deleted successfully")]


async def test_destination(
    destination_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Test event subscription destination configuration.

    Args:
        destination_data: Destination configuration to test

    Returns:
        List of MCP content types containing test results
    """
    client = get_client()
    result = client.post("events/subscriptions/testDestination", json_data=destination_data)

    return [types.TextContent(type="text", text=str(result))]


async def get_failed_events(
    subscription_id: str,
    limit: int = 10,
    offset: int = 0,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get failed events for a specific subscription.

    Args:
        subscription_id: ID of the event subscription
        limit: Maximum number of failed events to return
        offset: Number of failed events to skip

    Returns:
        List of MCP content types containing failed events
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    result = client.get(f"events/subscriptions/id/{subscription_id}/failedEvents", params=params)

    return [types.TextContent(type="text", text=str(result))]


async def get_subscription_status(
    subscription_name: str,
    destination_id: str,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get status of event subscription destination.

    Args:
        subscription_name: Name of the event subscription
        destination_id: ID of the destination

    Returns:
        List of MCP content types containing destination status
    """
    client = get_client()
    result = client.get(f"events/subscriptions/name/{subscription_name}/status/{destination_id}")

    return [types.TextContent(type="text", text=str(result))]
