"""Tool for listing Lightdash dashboards"""

import logging
from typing import Dict, Any, List, Optional
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_list_dashboards_tool() -> Tool:
    """Get the Lightdash list dashboards tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_LIST_DASHBOARDS.value,
        description=get_prompt("lightdash/list_dashboards"),
        inputSchema={
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "Optional space UUID to filter dashboards by"
                }
            },
            "additionalProperties": False
        },
    )


async def handle_lightdash_list_dashboards(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash list dashboards request"""
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
            )
        ]
    
    # Parse arguments if they come as a string
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error parsing arguments: {str(e)}"
                )
            ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Get optional space filter
        space_id = arguments.get("space_id")
        
        # List dashboards
        dashboards = await client.list_dashboards(space_id=space_id)
        
        if not dashboards:
            return [
                TextContent(
                    type="text",
                    text="No dashboards found" + (f" in space {space_id}" if space_id else "")
                )
            ]
        
        # Format dashboard list
        dashboard_info = []
        for dashboard in dashboards:
            info_parts = [
                f"• {dashboard.get('name', 'Unnamed Dashboard')}",
                f"  ID: {dashboard.get('uuid', 'N/A')}",
                f"  Space: {dashboard.get('spaceName', 'Unknown')}",
                f"  Tiles: {dashboard.get('tileCount', 0)}",
                f"  Updated: {dashboard.get('updatedAt', 'Unknown')[:10] if dashboard.get('updatedAt') else 'Unknown'}",
                f"  Updated by: {dashboard.get('updatedByUser', {}).get('firstName', '')} {dashboard.get('updatedByUser', {}).get('lastName', '')}".strip() or "Unknown"
            ]
            
            if dashboard.get('description'):
                info_parts.insert(1, f"  Description: {dashboard['description']}")
            
            dashboard_info.append("\n".join(info_parts))
        
        # Build response
        response_parts = [
            f"Found {len(dashboards)} dashboard{'s' if len(dashboards) != 1 else ''}:",
            "",
            "\n\n".join(dashboard_info)
        ]
        
        return [
            TextContent(
                type="text",
                text="\n".join(response_parts)
            )
        ]
        
    except Exception as e:
        logger.error(f"Error listing dashboards: {str(e)}")
        return [
            TextContent(
                type="text",
                text=f"Error listing dashboards: {str(e)}"
            )
        ]