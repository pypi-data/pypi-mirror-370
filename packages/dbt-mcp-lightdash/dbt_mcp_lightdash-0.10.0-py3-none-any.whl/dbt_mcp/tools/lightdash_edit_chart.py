"""Tool for editing Lightdash charts"""

import logging
from typing import Dict, Any, List, Optional
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_edit_chart_tool() -> Tool:
    """Get the Lightdash edit chart tool definition
    
    Note: Currently only supports updating chart metadata (name, description).
    To update queries (metrics, dimensions, filters), you need to create a new chart.
    """
    return Tool(
        name=ToolName.LIGHTDASH_UPDATE_CHART.value,
        description=get_prompt("lightdash/edit_chart"),
        inputSchema={
            "type": "object",
            "properties": {
                "chart_id": {
                    "type": "string",
                    "description": "The UUID of the chart to edit"
                },
                "name": {
                    "type": "string",
                    "description": "New name for the chart (optional)"
                },
                "description": {
                    "type": ["string", "null"],
                    "description": "New description for the chart (optional)"
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New list of metrics to include (optional, replaces existing)"
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New list of dimensions to group by (optional, replaces existing)"
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "operator": {"type": "string"},
                            "value": {}
                        },
                        "required": ["field", "operator"]
                    },
                    "description": "New filters to apply (optional, replaces existing)"
                },
                "sorts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "order": {"type": "string", "enum": ["asc", "desc"]}
                        },
                        "required": ["field", "order"]
                    },
                    "description": "New sort configuration (optional, replaces existing)"
                },
                "limit": {
                    "type": ["integer", "null"],
                    "description": "New result limit (optional)"
                }
            },
            "required": ["chart_id"],
            "additionalProperties": False
        },
    )


async def handle_lightdash_edit_chart(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash edit chart request"""
    
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
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # First get the existing chart to understand its structure
        existing_chart = await client.get_chart(chart_id)
        
        # Build the update payload - only include fields that were provided
        updates = {}
        
        # Basic metadata updates
        if "name" in arguments:
            updates["name"] = arguments["name"]
        
        if "description" in arguments:
            updates["description"] = arguments["description"]
        
        # Check if user is trying to update query fields
        query_fields = ["metrics", "dimensions", "filters", "sorts", "limit"]
        query_updates_requested = [field for field in query_fields if field in arguments]
        
        if query_updates_requested:
            # Lightdash API doesn't support updating queries through PATCH
            # Provide helpful guidance
            return [
                TextContent(
                    type="text",
                    text=f"⚠️ Chart query updates are not supported by the Lightdash API.\n\n"
                         f"You attempted to update: {', '.join(query_updates_requested)}\n\n"
                         f"To modify chart queries, you need to:\n"
                         f"1. Create a new chart with the desired query using 'lightdash_create_chart'\n"
                         f"2. Delete the old chart using 'lightdash_delete_chart' (if needed)\n\n"
                         f"Current chart details:\n"
                         f"- Name: {existing_chart.get('name', 'Unnamed Chart')}\n"
                         f"- ID: {chart_id}\n"
                         f"- Table: {existing_chart.get('tableName', 'Unknown')}\n\n"
                         f"Only chart metadata (name, description) can be updated."
                )
            ]
        
        # Only proceed if there are updates to make
        if not updates:
            return [
                TextContent(
                    type="text",
                    text="No updates to perform. Only name and description can be updated."
                )
            ]
        
        # Log the update payload for debugging
        logger.info(f"Sending update payload: {json.dumps(updates, indent=2)}")
        
        # Perform the update
        updated_chart = await client.update_chart(chart_id, updates)
        
        # Format the response
        response_parts = [
            f"Successfully updated chart: {updated_chart.get('name', 'Unnamed Chart')}",
            f"Chart ID: {updated_chart.get('uuid', chart_id)}"
        ]
        
        # Show what was updated
        if "name" in arguments:
            response_parts.append(f"✓ Updated name to: {arguments['name']}")
        if "description" in arguments:
            response_parts.append(f"✓ Updated description")
        if "metrics" in arguments:
            response_parts.append(f"✓ Updated metrics: {', '.join(arguments['metrics'])}")
        if "dimensions" in arguments:
            response_parts.append(f"✓ Updated dimensions: {', '.join(arguments['dimensions'])}")
        if "filters" in arguments:
            response_parts.append(f"✓ Updated {len(arguments['filters'])} filter(s)")
        if "sorts" in arguments:
            response_parts.append(f"✓ Updated {len(arguments['sorts'])} sort(s)")
        if "limit" in arguments:
            response_parts.append(f"✓ Updated limit to: {arguments['limit']}")
        
        # Add chart URL
        if updated_chart.get('uuid'):
            base_url = config.lightdash_config.api_url.replace('/api/v1', '')
            chart_url = f"{base_url}/projects/{client.project_id}/saved/{updated_chart['uuid']}"
            response_parts.append(f"\nView chart: {chart_url}")
        
        return [
            TextContent(
                type="text",
                text="\n".join(response_parts)
            )
        ]
        
    except Exception as e:
        logger.error(f"Error editing chart: {str(e)}")
        return [
            TextContent(
                type="text",
                text=f"Error editing chart: {str(e)}"
            )
        ]