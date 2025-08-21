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
# Use lightdash_run_metric_query or lightdash_create_chart instead
# Removed: lightdash_list_explores, lightdash_get_explore, enhanced_list_metrics
# Use lightdash_smart_query instead for natural language queries
from dbt_mcp.tools.lightdash_run_metric_query import (
    get_lightdash_run_metric_query_tool,
    handle_lightdash_run_metric_query,
)
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
    # Use lightdash_run_metric_query or lightdash_create_chart instead
    
    # Note: lightdash_list_explores, lightdash_get_explore, enhanced_list_metrics removed
    # Use lightdash_smart_query for natural language queries instead
    
    # Run Metric Query tool (Lightdash-based semantic layer)
    if ToolName.LIGHTDASH_RUN_METRIC_QUERY not in disable_tools:
        tool_def = get_lightdash_run_metric_query_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def run_metric_query_handler(arguments):
            return await handle_lightdash_run_metric_query(arguments, config)
        logger.info("Registered lightdash_run_metric_query tool")
    
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