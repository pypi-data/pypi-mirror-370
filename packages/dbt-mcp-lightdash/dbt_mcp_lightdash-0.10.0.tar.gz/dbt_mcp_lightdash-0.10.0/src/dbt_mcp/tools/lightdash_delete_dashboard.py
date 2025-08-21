"""Tool for deleting Lightdash dashboards"""

import logging
from typing import Dict, Any, List
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_delete_dashboard_tool() -> Tool:
    """Get the Lightdash delete dashboard tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_DELETE_DASHBOARD.value,
        description=get_prompt("lightdash/delete_dashboard"),
        inputSchema={
            "type": "object",
            "properties": {
                "dashboard_id": {
                    "type": "string",
                    "description": "The UUID of the dashboard to delete"
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Confirmation flag - must be true to delete the dashboard"
                }
            },
            "required": ["dashboard_id", "confirm"],
            "additionalProperties": False
        },
    )


async def handle_lightdash_delete_dashboard(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash delete dashboard request"""
    
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
    
    dashboard_id = arguments.get("dashboard_id")
    if not dashboard_id:
        return [
            TextContent(
                type="text",
                text="Error: dashboard_id is required"
            )
        ]
    
    confirm = arguments.get("confirm", False)
    if not confirm:
        return [
            TextContent(
                type="text",
                text="Error: Deletion not confirmed. Set 'confirm' to true to delete the dashboard."
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # First get the dashboard details for confirmation message
        try:
            dashboard_details = await client.get_dashboard(dashboard_id)
            dashboard_name = dashboard_details.get("name", "Unnamed Dashboard")
            space_name = dashboard_details.get("spaceName", "Unknown Space")
            tile_count = len(dashboard_details.get("tiles", []))
        except Exception:
            # If we can't get dashboard details, proceed with generic info
            dashboard_name = f"Dashboard {dashboard_id}"
            space_name = "Unknown Space"
            tile_count = 0
        
        # Delete the dashboard
        await client.delete_dashboard(dashboard_id)
        
        # Format success response
        response_parts = [
            f"✅ Successfully deleted dashboard: {dashboard_name}",
            f"Dashboard ID: {dashboard_id}",
            f"Space: {space_name}",
        ]
        
        if tile_count > 0:
            response_parts.append(f"Removed dashboard with {tile_count} tile(s)")
        
        response_parts.extend([
            "",
            "⚠️  This action cannot be undone.",
            "Note: Charts referenced by this dashboard were NOT deleted and remain available."
        ])
        
        return [
            TextContent(
                type="text",
                text="\n".join(response_parts)
            )
        ]
        
    except Exception as e:
        logger.error(f"Error deleting dashboard: {str(e)}")
        
        # Check if it's a 404 error (dashboard not found)
        if "404" in str(e):
            return [
                TextContent(
                    type="text",
                    text=f"Error: Dashboard with ID '{dashboard_id}' not found. It may have already been deleted."
                )
            ]
        
        return [
            TextContent(
                type="text",
                text=f"Error deleting dashboard: {str(e)}"
            )
        ]