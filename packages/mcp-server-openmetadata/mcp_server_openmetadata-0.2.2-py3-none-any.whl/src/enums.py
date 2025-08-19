from enum import Enum


class APIType(str, Enum):
    """OpenMetadata API categories for modular server configuration."""

    # Core Entities
    TABLE = "table"
    DATABASE = "database"
    SCHEMA = "databaseschema"  # Maps to databaseSchemas endpoint

    # Data Assets
    DASHBOARD = "dashboard"
    CHART = "chart"
    PIPELINE = "pipeline"
    TOPIC = "topic"
    METRICS = "metrics"
    CONTAINER = "container"
    REPORT = "report"
    ML_MODEL = "mlmodel"

    # Users & Teams
    USER = "user"
    TEAM = "team"

    # Governance & Classification
    CLASSIFICATION = "classification"
    GLOSSARY = "glossary"
    TAG = "tag"

    # System & Operations
    BOT = "bot"
    SERVICES = "services"
    EVENT = "event"

    # Analytics & Monitoring
    LINEAGE = "lineage"
    USAGE = "usage"
    SEARCH = "search"

    # Data Quality
    TEST_CASE = "test_case"
    TEST_SUITE = "test_suite"

    # Access Control & Security
    POLICY = "policy"
    ROLE = "role"

    # Domain Management
    DOMAIN = "domain"

    # Not Yet Implemented - Future Expansion
    # These are placeholder values for future implementation
    # API_COLLECTION = "api_collection"
    # API_ENDPOINT = "api_endpoint"
    # APP = "app"
    # FEED = "feed"
    # PERSONA = "persona"
    # QUERY = "query"
    # SEARCH_INDEX = "search_index"
    # STORED_PROCEDURE = "stored_procedure"
    # SUGGESTION = "suggestion"
    # WEBHOOK = "webhook"
