"""Tool for listing available explores in Lightdash"""

import logging
from typing import Dict, Any, List

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.lightdash.explore_selector import EXPLORE_METADATA
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.tools.argument_parser import parse_arguments

logger = logging.getLogger(__name__)


def get_lightdash_list_explores_tool() -> Tool:
    """Get the Lightdash list explores tool definition"""
    return Tool(
        name="lightdash_list_explores",
        description="""
# Tool Name: lightdash_list_explores

## Description
List all available data models (explores) in Lightdash with descriptions of what each contains.

## When to Use
- To discover what data sources are available
- Before running queries to understand options
- To choose the right explore for your analysis

## Returns
List of explores with:
- Name
- Description of what data it contains
- Best use cases

## Parameters
None - this tool takes no parameters

## JSON Examples

### Example 1: List all explores
```json
{}
```

## Notes
- orders: Sales and revenue data with products
- ads: Advertising campaign performance
- pixel_joined: ROAS and attribution data
- geo_reports_table: Geographic and lead data
""",
        inputSchema={
            "type": "object",
            "properties": {},
        }
    )


async def handle_lightdash_list_explores(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the list explores request"""
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Get explores from Lightdash
        explores = await client.list_explores()
        
        if not explores:
            return [
                TextContent(
                    type="text",
                    text="No explores found in the project."
                )
            ]
        
        # Format the response with descriptions
        result_text = f"Found {len(explores)} explores:\n\n"
        
        for explore in explores:
            explore_name = explore['name']
            result_text += f"**{explore_name}**\n"
            
            # Add description from metadata if available
            if explore_name in EXPLORE_METADATA:
                metadata = EXPLORE_METADATA[explore_name]
                result_text += f"  Description: {metadata['description']}\n"
                result_text += f"  Use for: {', '.join(metadata['use_for'])}\n"
                result_text += f"  Key metrics: {', '.join(metadata['metrics'][:3])}\n"
                
                # Show required filters if any
                if 'required_filters' in metadata:
                    req_filters = metadata['required_filters']
                    if 'note' in req_filters:
                        result_text += f"  ⚠️ {req_filters['note']}\n"
                    result_text += f"  Required filters:\n"
                    for filter_name, values in req_filters.items():
                        if filter_name != 'note':
                            result_text += f"    - {filter_name}: {', '.join(values) if isinstance(values, list) else values}\n"
            else:
                result_text += f"  Description: Data from {explore_name}\n"
            
            result_text += "\n"
        
        result_text += "\nUse lightdash_smart_query with your question to query these explores."
        
        return [
            TextContent(
                type="text",
                text=result_text
            )
        ]
        
    except Exception as e:
        error_msg = f"Error listing explores: {str(e)}"
        logger.error(error_msg)
        return [
            TextContent(
                type="text",
                text=error_msg
            )
        ]