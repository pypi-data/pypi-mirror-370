"""Standardized event names for consistent logging."""


class Events:
    """Centralized event names following snake_case convention."""

    # Lifecycle events
    APP_STARTED = "app_started"
    APP_STOPPED = "app_stopped"

    # Paper operations
    PAPER_ADDED = "paper_added"
    PAPER_REMOVED = "paper_removed"
    PAPER_FETCHED = "paper_fetched"
    PAPER_SEARCH_STARTED = "paper_search_started"
    PAPER_SEARCH_COMPLETED = "paper_search_completed"

    # LLM operations
    LLM_REQUEST_STARTED = "llm_request_started"
    LLM_REQUEST_COMPLETED = "llm_request_completed"
    LLM_REQUEST_FAILED = "llm_request_failed"
    LLM_TOKEN_USAGE = "llm_token_usage"

    # Tool operations
    TOOL_EXECUTED = "tool_executed"
    TOOL_APPROVAL_REQUIRED = "tool_approval_required"
    TOOL_APPROVED = "tool_approved"
    TOOL_REJECTED = "tool_rejected"

    # Database operations
    DB_QUERY_EXECUTED = "db_query_executed"
    DB_TRANSACTION_STARTED = "db_transaction_started"
    DB_TRANSACTION_COMMITTED = "db_transaction_committed"
    DB_TRANSACTION_ROLLED_BACK = "db_transaction_rolled_back"

    # Error events
    UNEXPECTED_ERROR = "unexpected_error"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    PARSE_ERROR = "parse_error"
