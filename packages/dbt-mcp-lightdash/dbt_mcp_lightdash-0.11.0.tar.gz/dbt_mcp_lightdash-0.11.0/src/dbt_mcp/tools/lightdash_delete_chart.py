"""Tool for deleting Lightdash charts"""

import logging
from typing import Dict, Any, List
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_delete_chart_tool() -> Tool:
    """Get the Lightdash delete chart tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_DELETE_CHART.value,
        description=get_prompt("lightdash/delete_chart"),
        inputSchema={
            "type": "object",
            "properties": {
                "chart_id": {
                    "type": "string",
                    "description": "The UUID of the chart to delete"
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Confirmation flag - must be true to delete the chart"
                }
            },
            "required": ["chart_id", "confirm"],
            "additionalProperties": False
        },
    )


async def handle_lightdash_delete_chart(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash delete chart request"""
    
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
    
    chart_id = arguments.get("chart_id")
    if not chart_id:
        return [
            TextContent(
                type="text",
                text="Error: chart_id is required"
            )
        ]
    
    confirm = arguments.get("confirm", False)
    if not confirm:
        return [
            TextContent(
                type="text",
                text="Error: Deletion not confirmed. Set 'confirm' to true to delete the chart."
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # First get the chart details for confirmation message
        try:
            chart_details = await client.get_chart(chart_id)
            chart_name = chart_details.get("name", "Unnamed Chart")
            space_name = chart_details.get("space", {}).get("name", "Unknown Space")
        except Exception:
            # If we can't get chart details, proceed with generic info
            chart_name = f"Chart {chart_id}"
            space_name = "Unknown Space"
        
        # Delete the chart
        await client.delete_chart(chart_id)
        
        # Format success response
        response_parts = [
            f"✅ Successfully deleted chart: {chart_name}",
            f"Chart ID: {chart_id}",
            f"Space: {space_name}",
            "",
            "⚠️  This action cannot be undone."
        ]
        
        return [
            TextContent(
                type="text",
                text="\n".join(response_parts)
            )
        ]
        
    except Exception as e:
        logger.error(f"Error deleting chart: {str(e)}")
        
        # Check if it's a 404 error (chart not found)
        if "404" in str(e):
            return [
                TextContent(
                    type="text",
                    text=f"Error: Chart with ID '{chart_id}' not found. It may have already been deleted."
                )
            ]
        
        return [
            TextContent(
                type="text",
                text=f"Error deleting chart: {str(e)}"
            )
        ]