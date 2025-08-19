"""Test Suites management for OpenMetadata Data Quality.

This module provides comprehensive test suite management operations including
CRUD operations for basic and executable test suites, execution monitoring,
and data quality reporting. Test suites group test cases for data quality validation.
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
        (list_test_suites, "list_test_suites", "List test suites with pagination and filtering"),
        (get_test_suite, "get_test_suite", "Get details of a specific test suite by ID"),
        (get_test_suite_by_name, "get_test_suite_by_name", "Get details of a specific test suite by name"),
        (create_basic_test_suite, "create_basic_test_suite", "Create a new basic test suite"),
        (create_executable_test_suite, "create_executable_test_suite", "Create a new executable test suite"),
        (update_test_suite, "update_test_suite", "Update an existing test suite"),
        (delete_test_suite, "delete_test_suite", "Delete a test suite from OpenMetadata"),
        (get_execution_summary, "get_test_suite_execution_summary", "Get execution summary of test suites"),
        (get_data_quality_report, "get_data_quality_report", "Get data quality report with aggregations"),
    ]


async def list_test_suites(
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    test_suite_type: Optional[str] = None,
    include_empty_test_suites: bool = True,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """List test suites with pagination and filtering.

    Args:
        limit: Maximum number of test suites to return (1 to 1000000)
        offset: Number of test suites to skip
        fields: Comma-separated list of fields to include
        test_suite_type: Filter by test suite type (basic, executable)
        include_empty_test_suites: Whether to include empty test suites
        include_deleted: Whether to include deleted test suites

    Returns:
        List of MCP content types containing test suite list and metadata
    """
    client = get_client()
    params = {"limit": min(max(1, limit), 1000000), "offset": max(0, offset)}

    if fields:
        params["fields"] = fields
    if test_suite_type:
        params["testSuiteType"] = test_suite_type
    if not include_empty_test_suites:
        params["includeEmptyTestSuites"] = False
    if include_deleted:
        params["include"] = "all"

    result = client.get("dataQuality/testSuites", params=params)

    # Add UI URLs for test suites
    if "data" in result:
        for test_suite in result["data"]:
            suite_name = test_suite.get("name", "")
            if suite_name:
                test_suite["ui_url"] = f"{client.host}/data-quality/test-suites/{suite_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_test_suite(
    test_suite_id: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific test suite by ID.

    Args:
        test_suite_id: ID of the test suite
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted test suites

    Returns:
        List of MCP content types containing test suite details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"dataQuality/testSuites/{test_suite_id}", params=params)

    # Add UI URL
    suite_name = result.get("name", "")
    if suite_name:
        result["ui_url"] = f"{client.host}/data-quality/test-suites/{suite_name}"

    return [types.TextContent(type="text", text=str(result))]


async def get_test_suite_by_name(
    name: str,
    fields: Optional[str] = None,
    include_deleted: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get details of a specific test suite by name.

    Args:
        name: Name of the test suite
        fields: Comma-separated list of fields to include
        include_deleted: Whether to include deleted test suites

    Returns:
        List of MCP content types containing test suite details
    """
    client = get_client()
    params = {}
    if fields:
        params["fields"] = fields
    if include_deleted:
        params["include"] = "all"

    result = client.get(f"dataQuality/testSuites/name/{name}", params=params)

    # Add UI URL
    suite_name = result.get("name", "")
    if suite_name:
        result["ui_url"] = f"{client.host}/data-quality/test-suites/{suite_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_basic_test_suite(
    test_suite_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new basic test suite.

    Args:
        test_suite_data: Test suite data including name, description, etc.

    Returns:
        List of MCP content types containing created test suite details
    """
    client = get_client()
    result = client.post("dataQuality/testSuites/basic", json_data=test_suite_data)

    # Add UI URL
    suite_name = result.get("name", "")
    if suite_name:
        result["ui_url"] = f"{client.host}/data-quality/test-suites/{suite_name}"

    return [types.TextContent(type="text", text=str(result))]


async def create_executable_test_suite(
    test_suite_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Create a new executable test suite.

    Args:
        test_suite_data: Test suite data including name, description, pipeline config, etc.

    Returns:
        List of MCP content types containing created test suite details
    """
    client = get_client()
    result = client.post("dataQuality/testSuites/executable", json_data=test_suite_data)

    # Add UI URL
    suite_name = result.get("name", "")
    if suite_name:
        result["ui_url"] = f"{client.host}/data-quality/test-suites/{suite_name}"

    return [types.TextContent(type="text", text=str(result))]


async def update_test_suite(
    test_suite_id: str,
    test_suite_data: Dict[str, Any],
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Update an existing test suite.

    Args:
        test_suite_id: ID of the test suite to update
        test_suite_data: Updated test suite data

    Returns:
        List of MCP content types containing updated test suite details
    """
    client = get_client()
    result = client.put(f"dataQuality/testSuites/{test_suite_id}", json_data=test_suite_data)

    # Add UI URL
    suite_name = result.get("name", "")
    if suite_name:
        result["ui_url"] = f"{client.host}/data-quality/test-suites/{suite_name}"

    return [types.TextContent(type="text", text=str(result))]


async def delete_test_suite(
    test_suite_id: str,
    hard_delete: bool = False,
    recursive: bool = False,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Delete a test suite.

    Args:
        test_suite_id: ID of the test suite to delete
        hard_delete: Whether to perform a hard delete
        recursive: Whether to recursively delete children

    Returns:
        List of MCP content types confirming deletion
    """
    client = get_client()
    params = {"hardDelete": hard_delete, "recursive": recursive}
    client.delete(f"dataQuality/testSuites/{test_suite_id}", params=params)

    return [types.TextContent(type="text", text=f"Test suite {test_suite_id} deleted successfully")]


async def get_execution_summary(
    test_suite_id: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get execution summary of test suites.

    Args:
        test_suite_id: Optional test suite ID to get summary for specific suite

    Returns:
        List of MCP content types containing execution summary
    """
    client = get_client()
    params = {}
    if test_suite_id:
        params["testSuiteId"] = test_suite_id

    result = client.get("dataQuality/testSuites/executionSummary", params=params)

    return [types.TextContent(type="text", text=str(result))]


async def get_data_quality_report(
    q: Optional[str] = None,
    aggregation_query: Optional[str] = None,
    index: Optional[str] = None,
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Get data quality report with aggregations.

    Args:
        q: Search query to filter aggregation results
        aggregation_query: Aggregation query for search results
        index: Index to perform aggregation against

    Returns:
        List of MCP content types containing data quality report
    """
    client = get_client()
    params = {}

    if q:
        params["q"] = q
    if aggregation_query:
        params["aggregationQuery"] = aggregation_query
    if index:
        params["index"] = index

    result = client.get("dataQuality/testSuites/dataQualityReport", params=params)

    return [types.TextContent(type="text", text=str(result))]
