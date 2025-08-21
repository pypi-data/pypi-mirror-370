"""Central orchestration module for MCP OpenMetadata server.

This module configures the CLI interface with Click for transport selection,
dynamically loads and registers API modules based on user selection,
and manages server lifecycle with chosen transport protocol.
"""

import logging
from typing import List

import click

from src.enums import APIType

# Import API modules with explicit aliases
from src.openmetadata.bots import get_all_functions as get_bots_functions
from src.openmetadata.charts import get_all_functions as get_charts_functions
from src.openmetadata.classifications import get_all_functions as get_classifications_functions
from src.openmetadata.containers import get_all_functions as get_containers_functions
from src.openmetadata.dashboards import get_all_functions as get_dashboards_functions
from src.openmetadata.database import get_all_functions as get_database_functions
from src.openmetadata.domains import get_all_functions as get_domains_functions
from src.openmetadata.events import get_all_functions as get_events_functions
from src.openmetadata.glossary import get_all_functions as get_glossary_functions
from src.openmetadata.lineage import get_all_functions as get_lineage_functions
from src.openmetadata.metrics import get_all_functions as get_metrics_functions
from src.openmetadata.mlmodels import get_all_functions as get_mlmodels_functions
from src.openmetadata.pipelines import get_all_functions as get_pipelines_functions
from src.openmetadata.policies import get_all_functions as get_policies_functions
from src.openmetadata.reports import get_all_functions as get_reports_functions
from src.openmetadata.roles import get_all_functions as get_roles_functions
from src.openmetadata.schema import get_all_functions as get_schema_functions
from src.openmetadata.search import get_all_functions as get_search_functions
from src.openmetadata.services import get_all_functions as get_services_functions
from src.openmetadata.table import get_all_functions as get_table_functions
from src.openmetadata.tags import get_all_functions as get_tags_functions
from src.openmetadata.teams import get_all_functions as get_teams_functions
from src.openmetadata.test_cases import get_all_functions as get_test_cases_functions
from src.openmetadata.test_suites import get_all_functions as get_test_suites_functions
from src.openmetadata.topics import get_all_functions as get_topics_functions
from src.openmetadata.usage import get_all_functions as get_usage_functions
from src.openmetadata.users import get_all_functions as get_users_functions

# Map API types to their respective function collections
APITYPE_TO_FUNCTIONS = {
    # Core Data Entities
    APIType.TABLE: get_table_functions,
    APIType.DATABASE: get_database_functions,
    APIType.SCHEMA: get_schema_functions,
    # Data Assets
    APIType.DASHBOARD: get_dashboards_functions,
    APIType.CHART: get_charts_functions,
    APIType.PIPELINE: get_pipelines_functions,
    APIType.TOPIC: get_topics_functions,
    APIType.METRICS: get_metrics_functions,
    APIType.CONTAINER: get_containers_functions,
    APIType.REPORT: get_reports_functions,
    APIType.ML_MODEL: get_mlmodels_functions,
    # Users & Teams
    APIType.USER: get_users_functions,
    APIType.TEAM: get_teams_functions,
    # Governance & Classification
    APIType.CLASSIFICATION: get_classifications_functions,
    APIType.GLOSSARY: get_glossary_functions,
    APIType.TAG: get_tags_functions,
    # System & Operations
    APIType.BOT: get_bots_functions,
    APIType.SERVICES: get_services_functions,
    APIType.EVENT: get_events_functions,
    # Analytics & Monitoring
    APIType.LINEAGE: get_lineage_functions,
    APIType.USAGE: get_usage_functions,
    APIType.SEARCH: get_search_functions,
    # Data Quality
    APIType.TEST_CASE: get_test_cases_functions,
    APIType.TEST_SUITE: get_test_suites_functions,
    # Access Control & Security
    APIType.POLICY: get_policies_functions,
    APIType.ROLE: get_roles_functions,
    # Domain Management
    APIType.DOMAIN: get_domains_functions,
}


def filter_functions_for_read_only(functions: list[tuple]) -> list[tuple]:
    """
    Filter functions to only include read-only operations.

    Args:
        functions: List of (func, name, description, is_read_only) tuples

    Returns:
        List of (func, name, description, is_read_only) tuples with only read-only functions
    """
    return [
        (func, name, description, is_read_only) for func, name, description, is_read_only in functions if is_read_only
    ]


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type for MCP communication",
)
@click.option(
    "--apis",
    type=click.Choice([api.value for api in APIType]),
    default=[api.value for api in APIType],
    multiple=True,
    help="API groups to enable (default: core entities and common assets)",
)
@click.option(
    "--read-only",
    is_flag=True,
    help="Only expose read-only tools (GET operations, no CREATE/UPDATE/DELETE)",
)
def main(transport: str, apis: List[str], read_only: bool) -> None:
    """Start the MCP OpenMetadata server with selected API groups."""
    from src.config import Config
    from src.openmetadata.openmetadata_client import initialize_client
    from src.server import app

    # Get OpenMetadata credentials from environment
    config = Config.from_env()

    # Initialize global OpenMetadata client
    initialize_client(
        host=config.OPENMETADATA_HOST,
        api_token=config.OPENMETADATA_JWT_TOKEN,
        username=config.OPENMETADATA_USERNAME,
        password=config.OPENMETADATA_PASSWORD,
    )

    registered_count = 0
    for api in apis:
        logging.debug(f"Adding API: {api}")
        get_function = APITYPE_TO_FUNCTIONS[APIType(api)]
        try:
            functions = get_function()
        except NotImplementedError:
            logging.warning(f"API type '{api}' not implemented yet")
            continue

        # Filter functions for read-only mode if requested
        if read_only:
            functions = filter_functions_for_read_only(functions)

        for func, name, description, *_ in functions:
            app.add_tool(func, name=name, description=description)
            registered_count += 1

        logging.info(f"Registered {len(functions)} tools from {api} API")

    logging.info(f"Total registered tools: {registered_count}")

    if transport == "sse":
        logging.debug("Starting MCP server for OpenMetadata with SSE transport")
        app.run(transport="sse")
    else:
        logging.debug("Starting MCP server for OpenMetadata with stdio transport")
        app.run(transport="stdio")


if __name__ == "__main__":
    main()
