"""Tool for getting Lightdash chart details"""

import logging
from typing import Dict, Any, List
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_get_chart_tool() -> Tool:
    """Get the Lightdash get chart tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_GET_CHART.value,
        description=get_prompt("lightdash/get_chart"),
        inputSchema={
            "type": "object",
            "properties": {
                "chart_id": {
                    "type": "string",
                    "description": get_prompt("lightdash/args/chart_id")
                }
            },
            "required": ["chart_id"],
        },
    )


async def handle_lightdash_get_chart(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash get chart request"""
    
    # Parse arguments if they come as a string
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            # If it's just a plain string, assume it's the chart_id
            arguments = {"chart_id": arguments}
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
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
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        chart = await client.get_chart(chart_id)
        
        if not chart:
            return [
                TextContent(
                    type="text",
                    text=f"Chart with ID {chart_id} not found"
                )
            ]
        
        # Format chart details for display
        result = f"Chart Details:\n"
        result += f"{'=' * 50}\n\n"
        
        # Basic information
        result += f"Name: {chart.get('name', 'Unnamed')}\n"
        result += f"ID: {chart.get('uuid', 'N/A')}\n"
        
        description = chart.get('description')
        if description:
            result += f"Description: {description}\n"
        
        # Table and space information
        result += f"Table: {chart.get('tableName', 'N/A')}\n"
        result += f"Space ID: {chart.get('spaceUuid', 'N/A')}\n"
        
        # Chart configuration
        chart_config = chart.get('chartConfig', {})
        result += f"Chart Type: {chart_config.get('type', 'Unknown')}\n"
        
        # Metric query details
        metric_query = chart.get('metricQuery', {})
        if metric_query:
            result += "\nQuery Configuration:\n"
            result += f"  Dimensions: {', '.join(metric_query.get('dimensions', []))}\n"
            result += f"  Metrics: {', '.join(metric_query.get('metrics', []))}\n"
            result += f"  Limit: {metric_query.get('limit', 'Not set')}\n"
            
            filters = metric_query.get('filters', {})
            if filters:
                result += f"  Filters: {json.dumps(filters, indent=4)}\n"
            
            sorts = metric_query.get('sorts', [])
            if sorts:
                result += "  Sorts:\n"
                for sort in sorts:
                    result += f"    - {sort.get('fieldId', 'Unknown field')}: {sort.get('descending', False) and 'DESC' or 'ASC'}\n"
        
        # Table configuration
        table_config = chart.get('tableConfig', {})
        if table_config and table_config.get('columnOrder'):
            result += f"\nColumn Order: {', '.join(table_config.get('columnOrder', []))}\n"
        
        # Metadata
        result += "\nMetadata:\n"
        result += f"  Created At: {chart.get('createdAt', 'N/A')}\n"
        result += f"  Updated At: {chart.get('updatedAt', 'N/A')}\n"
        
        # Creator information
        created_by = chart.get('createdByUser', {})
        if created_by and created_by.get('firstName'):
            creator = f"{created_by.get('firstName', '')} {created_by.get('lastName', '')}".strip()
            result += f"  Created By: {creator}\n"
        
        updated_by = chart.get('updatedByUser', {})
        if updated_by and updated_by.get('firstName'):
            updater = f"{updated_by.get('firstName', '')} {updated_by.get('lastName', '')}".strip()
            result += f"  Updated By: {updater}\n"
        
        return [TextContent(type="text", text=result.strip())]
        
    except Exception as e:
        logger.error(f"Error getting Lightdash chart details: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error getting chart details: {str(e)}"
            )
        ]