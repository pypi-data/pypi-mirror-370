"""Tool for listing Lightdash charts"""

import logging
from typing import Dict, Any, List
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_list_charts_tool() -> Tool:
    """Get the Lightdash list charts tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_LIST_CHARTS.value,
        description=get_prompt("lightdash/list_charts"),
        inputSchema={
            "type": "object",
            "properties": {
                "space_id": {
                    "type": "string",
                    "description": "Optional space UUID to filter charts"
                }
            },
            "required": [],
        },
    )


async def handle_lightdash_list_charts(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash list charts request"""
    
    # Parse arguments if they come as a string
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            # This tool has optional arguments, so just use empty dict
            arguments = {}
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        space_id = arguments.get("space_id")
        
        charts = await client.list_charts(space_id=space_id)
        
        if not charts:
            message = "No charts found"
            if space_id:
                message += f" in space {space_id}"
            return [
                TextContent(
                    type="text",
                    text=message
                )
            ]
        
        # Format charts for display
        result = f"Found {len(charts)} chart(s)"
        if space_id:
            result += f" in space {space_id}"
        result += ":\n\n"
        
        for chart in charts:
            result += f"• {chart.get('name', 'Unnamed')}\n"
            result += f"  ID: {chart.get('uuid', 'N/A')}\n"
            
            # Add description if available
            description = chart.get('description')
            if description:
                result += f"  Description: {description}\n"
            
            # Add table name if available
            table_name = chart.get('tableName')
            if table_name:
                result += f"  Table: {table_name}\n"
            
            # Add chart type if available
            chart_type = chart.get('chartType', chart.get('chartConfig', {}).get('type', 'Unknown'))
            result += f"  Type: {chart_type}\n"
            
            # Add last updated info if available
            updated_at = chart.get('updatedAt')
            if updated_at:
                result += f"  Updated: {updated_at}\n"
            
            # Add creator info if available
            updated_by = chart.get('updatedByUser', {})
            if updated_by and updated_by.get('firstName'):
                creator = f"{updated_by.get('firstName', '')} {updated_by.get('lastName', '')}".strip()
                if creator:
                    result += f"  Updated by: {creator}\n"
            
            result += "\n"
        
        return [TextContent(type="text", text=result.strip())]
        
    except Exception as e:
        logger.error(f"Error listing Lightdash charts: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error listing Lightdash charts: {str(e)}"
            )
        ]