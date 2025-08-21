"""Register Lightdash tools with the MCP server"""

import logging
from typing import List, TYPE_CHECKING, Any

from dbt_mcp.config.config import LightdashConfig
from dbt_mcp.tools.tool_names import ToolName

if TYPE_CHECKING:
    from dbt_mcp.mcp.server import DbtMCP

from dbt_mcp.tools.lightdash_list_spaces import (
    get_lightdash_list_spaces_tool,
    handle_lightdash_list_spaces,
)
from dbt_mcp.tools.lightdash_list_charts import (
    get_lightdash_list_charts_tool,
    handle_lightdash_list_charts,
)
from dbt_mcp.tools.lightdash_get_chart import (
    get_lightdash_get_chart_tool,
    handle_lightdash_get_chart,
)
from dbt_mcp.tools.lightdash_create_chart import (
    get_lightdash_create_chart_tool,
    handle_lightdash_create_chart,
)
from dbt_mcp.tools.lightdash_edit_chart import (
    get_lightdash_edit_chart_tool,
    handle_lightdash_edit_chart,
)
from dbt_mcp.tools.lightdash_delete_chart import (
    get_lightdash_delete_chart_tool,
    handle_lightdash_delete_chart,
)
# Removed: lightdash_save_query_as_chart (semantic layer tool)
# Removed: lightdash_run_metric_query (redundant with smart_query)
# Removed: lightdash_list_explores, lightdash_get_explore, enhanced_list_metrics
# Use lightdash_smart_query for all natural language queries
from dbt_mcp.tools.lightdash_get_user import (
    get_lightdash_get_user_tool,
    handle_lightdash_get_user,
)
from dbt_mcp.tools.lightdash_get_embed_url import (
    get_lightdash_get_embed_url_tool,
    handle_lightdash_get_embed_url,
)
# Dashboard tools
from dbt_mcp.tools.lightdash_list_dashboards import (
    get_lightdash_list_dashboards_tool,
    handle_lightdash_list_dashboards,
)
from dbt_mcp.tools.lightdash_get_dashboard import (
    get_lightdash_get_dashboard_tool,
    handle_lightdash_get_dashboard,
)
from dbt_mcp.tools.lightdash_create_dashboard import (
    get_lightdash_create_dashboard_tool,
    handle_lightdash_create_dashboard,
)
from dbt_mcp.tools.lightdash_edit_dashboard import (
    get_lightdash_edit_dashboard_tool,
    handle_lightdash_edit_dashboard,
)
from dbt_mcp.tools.lightdash_delete_dashboard import (
    get_lightdash_delete_dashboard_tool,
    handle_lightdash_delete_dashboard,
)
# Smart query tool for natural language
from dbt_mcp.tools.lightdash_smart_query import (
    get_lightdash_smart_query_tool,
    handle_lightdash_smart_query,
)
# Progressive discovery tools (following dbt-mcp pattern)
from dbt_mcp.tools.lightdash_list_explores import (
    get_lightdash_list_explores_tool,
    handle_lightdash_list_explores,
)
from dbt_mcp.tools.lightdash_list_metrics import (
    get_lightdash_list_metrics_tool,
    handle_lightdash_list_metrics,
)
from dbt_mcp.tools.lightdash_get_dimensions import (
    get_lightdash_get_dimensions_tool,
    handle_lightdash_get_dimensions,
)
from dbt_mcp.tools.lightdash_query_metrics import (
    get_lightdash_query_metrics_tool,
    handle_lightdash_query_metrics,
)

logger = logging.getLogger(__name__)


def register_lightdash_tools(
    mcp: Any,  # Using Any to avoid circular import
    lightdash_config: LightdashConfig,
    disable_tools: List[ToolName]
) -> None:
    """Register Lightdash tools with the MCP server"""
    
    config = mcp.config
    
    # List Spaces tool
    if ToolName.LIGHTDASH_LIST_SPACES not in disable_tools:
        tool_def = get_lightdash_list_spaces_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def list_spaces_handler(arguments):
            return await handle_lightdash_list_spaces(arguments, config)
        logger.info("Registered lightdash_list_spaces tool")
    
    # List Charts tool
    if ToolName.LIGHTDASH_LIST_CHARTS not in disable_tools:
        tool_def = get_lightdash_list_charts_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_list_charts_handler(arguments):
            return await handle_lightdash_list_charts(arguments, config)
        logger.info("Registered lightdash_list_charts tool")
    
    # Get Chart tool
    if ToolName.LIGHTDASH_GET_CHART not in disable_tools:
        tool_def = get_lightdash_get_chart_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_get_chart_handler(arguments):
            return await handle_lightdash_get_chart(arguments, config)
        logger.info("Registered lightdash_get_chart tool")
    
    # Create Chart tool
    if ToolName.LIGHTDASH_CREATE_CHART not in disable_tools:
        tool_def = get_lightdash_create_chart_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_create_chart_handler(arguments):
            return await handle_lightdash_create_chart(arguments, config)
        logger.info("Registered lightdash_create_chart tool")
    
    # Edit Chart tool
    if ToolName.LIGHTDASH_UPDATE_CHART not in disable_tools:
        tool_def = get_lightdash_edit_chart_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_edit_chart_handler(arguments):
            return await handle_lightdash_edit_chart(arguments, config)
        logger.info("Registered lightdash_update_chart tool")
    
    # Delete Chart tool
    if ToolName.LIGHTDASH_DELETE_CHART not in disable_tools:
        tool_def = get_lightdash_delete_chart_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_delete_chart_handler(arguments):
            return await handle_lightdash_delete_chart(arguments, config)
        logger.info("Registered lightdash_delete_chart tool")
    
    # Note: lightdash_run_query (semantic layer tool) has been removed
    # Note: lightdash_run_metric_query has been removed (redundant with smart_query)
    # Note: lightdash_list_explores, lightdash_get_explore, enhanced_list_metrics removed
    # Use lightdash_smart_query for all natural language queries
    
    # Get User tool
    if ToolName.LIGHTDASH_GET_USER not in disable_tools:
        tool_def = get_lightdash_get_user_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def get_user_handler(arguments):
            return await handle_lightdash_get_user(arguments, config)
        logger.info("Registered lightdash_get_user tool")
    
    # Get Embed URL tool
    if ToolName.LIGHTDASH_GET_EMBED_URL not in disable_tools:
        tool_def = get_lightdash_get_embed_url_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def get_embed_url_handler(arguments):
            return await handle_lightdash_get_embed_url(arguments, config)
        logger.info("Registered lightdash_get_embed_url tool")
    
    # Dashboard Tools
    
    # List Dashboards tool
    if ToolName.LIGHTDASH_LIST_DASHBOARDS not in disable_tools:
        tool_def = get_lightdash_list_dashboards_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_list_dashboards_handler(arguments):
            return await handle_lightdash_list_dashboards(arguments, config)
        logger.info("Registered lightdash_list_dashboards tool")
    
    # Get Dashboard tool
    if ToolName.LIGHTDASH_GET_DASHBOARD not in disable_tools:
        tool_def = get_lightdash_get_dashboard_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_get_dashboard_handler(arguments):
            return await handle_lightdash_get_dashboard(arguments, config)
        logger.info("Registered lightdash_get_dashboard tool")
    
    # Create Dashboard tool
    if ToolName.LIGHTDASH_CREATE_DASHBOARD not in disable_tools:
        tool_def = get_lightdash_create_dashboard_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_create_dashboard_handler(arguments):
            return await handle_lightdash_create_dashboard(arguments, config)
        logger.info("Registered lightdash_create_dashboard tool")
    
    # Edit Dashboard tool
    if ToolName.LIGHTDASH_UPDATE_DASHBOARD not in disable_tools:
        tool_def = get_lightdash_edit_dashboard_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_edit_dashboard_handler(arguments):
            return await handle_lightdash_edit_dashboard(arguments, config)
        logger.info("Registered lightdash_update_dashboard tool")
    
    # Delete Dashboard tool
    if ToolName.LIGHTDASH_DELETE_DASHBOARD not in disable_tools:
        tool_def = get_lightdash_delete_dashboard_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_delete_dashboard_handler(arguments):
            return await handle_lightdash_delete_dashboard(arguments, config)
        logger.info("Registered lightdash_delete_dashboard tool")
    
    # Smart Query tool - Natural language queries
    if ToolName.LIGHTDASH_SMART_QUERY not in disable_tools:
        tool_def = get_lightdash_smart_query_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_smart_query_handler(arguments):
            return await handle_lightdash_smart_query(arguments, config)
        logger.info("Registered lightdash_smart_query tool")
    
    # Progressive discovery tools (following dbt-mcp pattern)
    # List Explores tool
    if ToolName.LIGHTDASH_LIST_EXPLORES not in disable_tools:
        tool_def = get_lightdash_list_explores_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_list_explores_handler(arguments):
            return await handle_lightdash_list_explores(arguments, config)
        logger.info("Registered lightdash_list_explores tool")
    
    # List Metrics tool
    if ToolName.LIGHTDASH_LIST_METRICS not in disable_tools:
        tool_def = get_lightdash_list_metrics_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_list_metrics_handler(arguments):
            return await handle_lightdash_list_metrics(arguments, config)
        logger.info("Registered lightdash_list_metrics tool")
    
    # Get Dimensions tool
    if ToolName.LIGHTDASH_GET_DIMENSIONS not in disable_tools:
        tool_def = get_lightdash_get_dimensions_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_get_dimensions_handler(arguments):
            return await handle_lightdash_get_dimensions(arguments, config)
        logger.info("Registered lightdash_get_dimensions tool")
    
    # Query Metrics tool
    if ToolName.LIGHTDASH_QUERY_METRICS not in disable_tools:
        tool_def = get_lightdash_query_metrics_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_query_metrics_handler(arguments):
            return await handle_lightdash_query_metrics(arguments, config)
        logger.info("Registered lightdash_query_metrics tool")