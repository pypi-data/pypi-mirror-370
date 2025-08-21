"""Tool for listing available metrics from Lightdash explores"""

import logging
from typing import Dict, Any, List, Optional

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.argument_parser import parse_arguments

logger = logging.getLogger(__name__)


def get_lightdash_list_metrics_tool() -> Tool:
    """Get the Lightdash list metrics tool definition"""
    return Tool(
        name="lightdash_list_metrics",
        description="""List all metrics from Lightdash explores.

If the user is asking a data-related or business-related question,
this tool should be used as a first step to get a list of metrics
that can be used with other tools to answer the question.

Examples:
- "What are the top 5 products by revenue?" → First list metrics to find revenue metric
- "How many users did we have last month?" → First list metrics to find user metrics
- "What's our ROAS?" → First list metrics to find ROAS metric

Optional: Filter by explore name to see metrics from a specific data model.""",
        inputSchema={
            "type": "object",
            "properties": {
                "explore": {
                    "type": "string",
                    "description": "Optional: explore name to filter metrics (e.g., 'orders', 'pixel_joined')"
                }
            }
        }
    )


async def handle_lightdash_list_metrics(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the list metrics request"""
    
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
    
    explore_filter = arguments.get("explore")
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Get all explores
        explores = await client.list_explores()
        
        if not explores:
            return [
                TextContent(
                    type="text",
                    text="No explores found in the project."
                )
            ]
        
        # Filter explores if requested
        if explore_filter:
            explores = [e for e in explores if explore_filter.lower() in e['name'].lower()]
            if not explores:
                return [
                    TextContent(
                        type="text",
                        text=f"No explore found matching '{explore_filter}'"
                    )
                ]
        
        # Collect metrics from all explores
        all_metrics = []
        
        for explore in explores:
            explore_name = explore['name']
            logger.info(f"Getting metrics from explore: {explore_name}")
            
            try:
                # Get explore details
                explore_details = await client.get_explore(explore_name)
                
                # Extract metrics
                if 'tables' in explore_details:
                    for table_name, table_data in explore_details['tables'].items():
                        if 'metrics' in table_data:
                            for metric_name, metric_data in table_data['metrics'].items():
                                if not metric_data.get('hidden', False):
                                    all_metrics.append({
                                        'name': metric_name,
                                        'explore': explore_name,
                                        'table': table_name,
                                        'label': metric_data.get('label', metric_name),
                                        'type': metric_data.get('type', 'number'),
                                        'description': metric_data.get('description', ''),
                                        'full_name': f"{table_name}_{metric_name}"  # Use actual table name
                                    })
            except Exception as e:
                logger.warning(f"Failed to get metrics from explore {explore_name}: {e}")
                continue
        
        if not all_metrics:
            return [
                TextContent(
                    type="text",
                    text="No metrics found in any explores."
                )
            ]
        
        # Format the response
        result_text = f"Found {len(all_metrics)} metrics:\n\n"
        
        # Group by explore for readability
        metrics_by_explore = {}
        for metric in all_metrics:
            explore = metric['explore']
            if explore not in metrics_by_explore:
                metrics_by_explore[explore] = []
            metrics_by_explore[explore].append(metric)
        
        for explore, metrics in metrics_by_explore.items():
            result_text += f"**{explore}:**\n"
            # Show ROAS metrics first if they exist
            roas_metrics = [m for m in metrics if 'roas' in m['name'].lower()]
            other_metrics = [m for m in metrics if 'roas' not in m['name'].lower()]
            
            # Show ROAS metrics
            for metric in roas_metrics:
                result_text += f"  • {metric['name']} (use as: {metric['full_name']})"
                if metric['label'] != metric['name']:
                    result_text += f" - {metric['label']}"
                if metric['description']:
                    result_text += f" - {metric['description'][:50]}"
                result_text += "\n"
            
            # Show first few other metrics
            for metric in other_metrics[:10]:  # Limit to first 10 non-ROAS metrics
                result_text += f"  • {metric['name']} (use as: {metric['full_name']})"
                if metric['label'] != metric['name']:
                    result_text += f" - {metric['label']}"
                if metric['description']:
                    result_text += f" - {metric['description'][:50]}"
                result_text += "\n"
            if len(metrics) > 10:
                result_text += f"  ... and {len(metrics) - 10} more metrics\n"
            result_text += "\n"
        
        result_text += "\nUse lightdash_get_dimensions with metric names to see available dimensions."
        
        return [
            TextContent(
                type="text",
                text=result_text
            )
        ]
        
    except Exception as e:
        error_msg = f"Error listing metrics: {str(e)}"
        logger.error(error_msg)
        return [
            TextContent(
                type="text",
                text=error_msg
            )
        ]