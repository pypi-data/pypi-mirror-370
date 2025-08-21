"""Test Cases management for OpenMetadata Data Quality.

This module provides comprehensive test case management operations including
CRUD operations, test execution results, and data quality monitoring.
Test cases are data quality tests against tables, columns, and other data assets.
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
        (list_test_cases, "list_test_cases", "List test cases with pagination and filtering"),
        (get_test_case, "get_test_case", "Get details of a specific test case by ID"),
        (get_test_case_by_name, "get_test_case_by_name", "Get details of a specific test case by FQN"),
        (create_test_case, "create_test_case", "Create a new test case in OpenMetadata"),
        (update_test_case, "update_test_case", "Update an existing test case"),
        (delete_test_case, "delete_test_case", "Delete a test case from OpenMetadata"),
        (list_test_case_results, "list_test_case_results", "List test case execution results"),
        (get_test_case_results_by_name, "get_test_case_results_by_name", "Get test case results by FQN"),
    ]


async def list_test_cases(  # noqa: C901
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    entity_link: Optional[str] = None,
    test_suite_id: Optional[str] = None,
    include_all_tests: bool = False,
    test_case_status: Optional[str] = None,
    test_case_type: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List test cases with pagination and filtering.

    Args:
        limit: Maximum number of test cases to return (1 to 1000000)
        offset: Number of test cases to skip
        fields: Comma-separated list of fields to include
        entity_link: Filter by entity link pattern
        test_suite_id: Filter by test suite ID
        include_all_tests: Include all tests at entity level
        test_case_status: Filter by status (Success, Failed, Aborted, Queued)
        test_case_type: Filter by type (column, table, all)
        include_deleted: Whether to include deleted test cases

    Returns:
        List of MCP content types containing test case list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if entity_link:
        params["entityLink"] = entity_link
    if test_suite_id:
        params["testSuiteId"] = test_suite_id
    if include_all_tests:
        params["includeAllTests"] = include_all_tests
    if test_case_status:
        params["testCaseStatus"] = test_case_status
    if test_case_type:
        params["testCaseType"] = test_case_type
    if include_deleted:
        params["include"] = "all"

    result = client.get("dataQuality/testCases", params=params)

    # Add UI URLs for test cases
    if "data" in result:
        for test_case in result["data"]:
            test_case_fqn = test_case.get("fullyQualifiedName", "")
            if test_case_fqn:
                test_case["ui_url"] = f"{client.host}/data-quality/test-cases/{test_case_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_test_case(
    test_case_id: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific test case by ID.

    Args:
        test_case_id: ID of the test case
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted test cases

    Returns:
        List of MCP content types containing test case details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"dataQuality/testCases/{test_case_id}", params=params)

    # Add UI URL
    test_case_fqn = result.get("fullyQualifiedName", "")
    if test_case_fqn:
        result["ui_url"] = f"{client.host}/data-quality/test-cases/{test_case_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def get_test_case_by_name(
    fqn: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific test case by fully qualified name.

    Args:
        fqn: Fully qualified name of the test case
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted test cases

    Returns:
        List of MCP content types containing test case details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"dataQuality/testCases/name/{fqn}", params=params)

    # Add UI URL
    test_case_fqn = result.get("fullyQualifiedName", "")
    if test_case_fqn:
        result["ui_url"] = f"{client.host}/data-quality/test-cases/{test_case_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def create_test_case(
    test_case_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new test case.

    Args:
        test_case_data: Test case data including name, description, test definition, etc.

    Returns:
        List of MCP content types containing created test case details
    """
    client = get_client()
    result = client.post("dataQuality/testCases", json_data=test_case_data)

    # Add UI URL
    test_case_fqn = result.get("fullyQualifiedName", "")
    if test_case_fqn:
        result["ui_url"] = f"{client.host}/data-quality/test-cases/{test_case_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def update_test_case(
    test_case_id: str,
    test_case_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing test case.

    Args:
        test_case_id: ID of the test case to update
        test_case_data: Updated test case data

    Returns:
        List of MCP content types containing updated test case details
    """
    client = get_client()
    result = client.put(f"dataQuality/testCases/{test_case_id}", json_data=test_case_data)

    # Add UI URL
    test_case_fqn = result.get("fullyQualifiedName", "")
    if test_case_fqn:
        result["ui_url"] = f"{client.host}/data-quality/test-cases/{test_case_fqn}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_test_case(
    test_case_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a test case.

    Args:
        test_case_id: ID of the test case to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"dataQuality/testCases/{test_case_id}", params=params)

    return [types.TextContent(type="text", text=f"Test case {test_case_id} deleted successfully")]


async def list_test_case_results(
    fqn: str,
    start_ts: Optional[float] = None,
    end_ts: Optional[float] = None,
    limit: int = 10,
    offset: int = 0,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List test case execution results for a specific test case.

    Args:
        fqn: Fully qualified name of the test case
        start_ts: Filter results after this timestamp
        end_ts: Filter results before this timestamp
        limit: Maximum number of results to return
        offset: Number of results to skip

    Returns:
        List of MCP content types containing test case results
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if start_ts:
        params["startTs"] = start_ts
    if end_ts:
        params["endTs"] = end_ts

    result = client.get(f"dataQuality/testCases/{fqn}/testCaseResult", params=params)

    return [types.TextContent(type="text", text=str(result))]


async def get_test_case_results_by_name(
    fqn: str,
    start_ts: Optional[float] = None,
    end_ts: Optional[float] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get test case results by test case FQN.

    Args:
        fqn: Fully qualified name of the test case
        start_ts: Filter results after this timestamp
        end_ts: Filter results before this timestamp

    Returns:
        List of MCP content types containing test case results
    """
    client = get_client()
    params = {}

    if start_ts:
        params["startTs"] = start_ts
    if end_ts:
        params["endTs"] = end_ts

    result = client.get(f"dataQuality/testCases/testCaseResults/{fqn}", params=params)

    return [types.TextContent(type="text", text=str(result))]
