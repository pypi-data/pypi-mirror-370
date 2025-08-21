from enum import Enum


class ToolName(Enum):
    """Tool names available in the FastMCP server.

    This enum provides type safety and autocompletion for tool names.
    The validate_server_tools() function should be used to ensure
    this enum stays in sync with the actual server tools.
    """

    # dbt CLI tools
    BUILD = "build"
    COMPILE = "compile"
    DOCS = "docs"
    LIST = "list"
    PARSE = "parse"
    RUN = "run"
    TEST = "test"
    SHOW = "show"

    # Semantic Layer tools
    LIST_METRICS = "list_metrics"
    GET_DIMENSIONS = "get_dimensions"
    GET_ENTITIES = "get_entities"
    QUERY_METRICS = "query_metrics"

    # Discovery tools
    GET_MART_MODELS = "get_mart_models"
    GET_ALL_MODELS = "get_all_models"
    GET_MODEL_DETAILS = "get_model_details"
    GET_MODEL_PARENTS = "get_model_parents"
    GET_MODEL_CHILDREN = "get_model_children"

    # Remote tools
    TEXT_TO_SQL = "text_to_sql"
    EXECUTE_SQL = "execute_sql"
    
    # Lightdash tools
    LIGHTDASH_LIST_SPACES = "lightdash_list_spaces"
    LIGHTDASH_LIST_CHARTS = "lightdash_list_charts"
    LIGHTDASH_GET_CHART = "lightdash_get_chart"
    LIGHTDASH_CREATE_CHART = "lightdash_create_chart"
    LIGHTDASH_UPDATE_CHART = "lightdash_update_chart"
    LIGHTDASH_DELETE_CHART = "lightdash_delete_chart"
    
    # Progressive discovery tools (following dbt-mcp pattern)
    LIGHTDASH_LIST_EXPLORES = "lightdash_list_explores"
    LIGHTDASH_LIST_METRICS = "lightdash_list_metrics"
    LIGHTDASH_GET_DIMENSIONS = "lightdash_get_dimensions"
    LIGHTDASH_QUERY_METRICS = "lightdash_query_metrics"
    
    LIGHTDASH_GET_EMBED_URL = "lightdash_get_embed_url"
    LIGHTDASH_GET_USER = "lightdash_get_user"
    LIGHTDASH_SMART_QUERY = "lightdash_smart_query"  # Natural language helper tool
    
    # Dashboard tools
    LIGHTDASH_LIST_DASHBOARDS = "lightdash_list_dashboards"
    LIGHTDASH_GET_DASHBOARD = "lightdash_get_dashboard"
    LIGHTDASH_CREATE_DASHBOARD = "lightdash_create_dashboard"
    LIGHTDASH_UPDATE_DASHBOARD = "lightdash_update_dashboard"
    LIGHTDASH_DELETE_DASHBOARD = "lightdash_delete_dashboard"

    @classmethod
    def get_all_tool_names(cls) -> set[str]:
        """Returns a set of all tool names as strings."""
        return {member.value for member in cls}
