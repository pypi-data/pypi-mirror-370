"""Tool for getting dimensions for specified metrics"""

import logging
from typing import Dict, Any, List

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.argument_parser import parse_arguments

logger = logging.getLogger(__name__)


def get_lightdash_get_dimensions_tool() -> Tool:
    """Get the Lightdash get dimensions tool definition"""
    return Tool(
        name="lightdash_get_dimensions",
        description="""Get the dimensions for specified metrics.

Dimensions are the attributes, features, or characteristics
that describe or categorize data (e.g., date, customer_name, product_category).

This tool shows what dimensions can be used to group or filter the metrics.

Parameters:
- metrics: List of metric names (e.g., ["total_revenue", "order_count"])
- explore: The explore containing these metrics (e.g., "orders")""",
        inputSchema={
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of metric names to get dimensions for"
                },
                "explore": {
                    "type": "string",
                    "description": "The explore containing these metrics"
                }
            },
            "required": ["metrics", "explore"]
        }
    )


async def handle_lightdash_get_dimensions(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the get dimensions request"""
    
    # Parse arguments
    try:
        arguments = parse_arguments(arguments)
    except Exception as e:
        logger.error(f"Failed to parse arguments: {e}")
        return [
            TextContent(
                type="text",
                text=f"Error parsing arguments: {str(e)}"
            )
        ]
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
            )
        ]
    
    metrics = arguments.get("metrics", [])
    explore = arguments.get("explore")
    
    if not metrics:
        return [
            TextContent(
                type="text",
                text="Error: metrics list is required"
            )
        ]
    
    if not explore:
        return [
            TextContent(
                type="text",
                text="Error: explore name is required"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Get explore details
        logger.info(f"Getting dimensions for metrics {metrics} in explore '{explore}'")
        explore_details = await client.get_explore(explore)
        
        # Extract available dimensions
        available_dimensions = []
        
        if 'tables' in explore_details:
            for table_name, table_data in explore_details['tables'].items():
                if 'dimensions' in table_data:
                    for dim_name, dim_data in table_data['dimensions'].items():
                        if not dim_data.get('hidden', False):
                            available_dimensions.append({
                                'name': dim_name,
                                'table': table_name,
                                'label': dim_data.get('label', dim_name),
                                'type': dim_data.get('type', 'string'),
                                'description': dim_data.get('description', ''),
                                'full_name': f"{table_name}_{dim_name}"  # Use actual table name
                            })
        
        if not available_dimensions:
            return [
                TextContent(
                    type="text",
                    text=f"No dimensions found in explore '{explore}'"
                )
            ]
        
        # Format the response
        result_text = f"Found {len(available_dimensions)} dimensions for metrics {metrics}:\n\n"
        
        # Group by type for readability
        dims_by_type = {}
        for dim in available_dimensions:
            dim_type = dim['type']
            if dim_type not in dims_by_type:
                dims_by_type[dim_type] = []
            dims_by_type[dim_type].append(dim)
        
        # Show date/time dimensions first (most commonly used)
        for dim_type in ['date', 'timestamp', 'time']:
            if dim_type in dims_by_type:
                result_text += f"**{dim_type.title()} dimensions:**\n"
                for dim in dims_by_type[dim_type]:
                    result_text += f"  • {dim['name']} (use as: {dim['full_name']})"
                    if dim['label'] != dim['name']:
                        result_text += f" - {dim['label']}"
                    if dim['description']:
                        result_text += f" - {dim['description'][:50]}"
                    result_text += "\n"
                result_text += "\n"
                del dims_by_type[dim_type]
        
        # Show other dimensions
        for dim_type, dims in dims_by_type.items():
            result_text += f"**{dim_type.title()} dimensions:**\n"
            for dim in dims[:15]:  # Limit to first 15 per type
                result_text += f"  • {dim['name']} (use as: {dim['full_name']})"
                if dim['label'] != dim['name']:
                    result_text += f" - {dim['label']}"
                if dim['description']:
                    result_text += f" - {dim['description'][:50]}"
                result_text += "\n"
            if len(dims) > 15:
                result_text += f"  ... and {len(dims) - 15} more {dim_type} dimensions\n"
            result_text += "\n"
        
        result_text += f"\nUse lightdash_query_metrics with these metrics and dimensions to run the analysis."
        
        return [
            TextContent(
                type="text",
                text=result_text
            )
        ]
        
    except Exception as e:
        error_msg = f"Error getting dimensions: {str(e)}"
        logger.error(error_msg)
        return [
            TextContent(
                type="text",
                text=error_msg
            )
        ]