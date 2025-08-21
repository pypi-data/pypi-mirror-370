"""Tool for getting Lightdash dashboard details"""

import logging
from typing import Dict, Any, List
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_get_dashboard_tool() -> Tool:
    """Get the Lightdash get dashboard tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_GET_DASHBOARD.value,
        description=get_prompt("lightdash/get_dashboard"),
        inputSchema={
            "type": "object",
            "properties": {
                "dashboard_id": {
                    "type": "string",
                    "description": "The UUID of the dashboard to retrieve"
                },
                "include_tiles": {
                    "type": "boolean",
                    "description": "Include detailed tile information (default: true)",
                    "default": True
                }
            },
            "required": ["dashboard_id"],
            "additionalProperties": False
        },
    )


async def handle_lightdash_get_dashboard(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash get dashboard request"""
    
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
    
    include_tiles = arguments.get("include_tiles", True)
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Get dashboard details
        dashboard = await client.get_dashboard(dashboard_id)
        
        # Format basic dashboard info
        response_parts = [
            f"Dashboard: {dashboard.get('name', 'Unnamed Dashboard')}",
            f"ID: {dashboard.get('uuid', dashboard_id)}",
            f"Space: {dashboard.get('spaceName', 'Unknown')}",
            f"Created: {dashboard.get('createdAt', 'Unknown')[:10] if dashboard.get('createdAt') else 'Unknown'}",
            f"Updated: {dashboard.get('updatedAt', 'Unknown')[:10] if dashboard.get('updatedAt') else 'Unknown'}",
        ]
        
        if dashboard.get('description'):
            response_parts.insert(1, f"Description: {dashboard['description']}")
        
        # Add creator/updater info if available
        if dashboard.get('createdByUser'):
            creator = dashboard['createdByUser']
            creator_name = f"{creator.get('firstName', '')} {creator.get('lastName', '')}".strip() or "Unknown"
            response_parts.append(f"Created by: {creator_name}")
        
        if dashboard.get('updatedByUser'):
            updater = dashboard['updatedByUser']
            updater_name = f"{updater.get('firstName', '')} {updater.get('lastName', '')}".strip() or "Unknown"
            response_parts.append(f"Updated by: {updater_name}")
        
        # Add tile information if requested
        if include_tiles and dashboard.get('tiles'):
            response_parts.extend(["", f"Tiles ({len(dashboard['tiles'])}):"])
            
            for i, tile in enumerate(dashboard['tiles'], 1):
                tile_type = tile.get('type', 'unknown')
                tile_info = [f"\n{i}. {tile_type.title()} Tile"]
                
                # Add tile properties based on type
                if tile_type == 'saved_chart':
                    properties = tile.get('properties', {})
                    if properties.get('savedChartUuid'):
                        tile_info.append(f"   Chart ID: {properties['savedChartUuid']}")
                    if properties.get('chartName'):
                        tile_info.append(f"   Chart: {properties['chartName']}")
                
                elif tile_type == 'markdown':
                    properties = tile.get('properties', {})
                    content = properties.get('content', '')
                    if content:
                        # Truncate long markdown content
                        preview = content[:100] + "..." if len(content) > 100 else content
                        tile_info.append(f"   Content: {preview}")
                
                # Add position info
                if tile.get('x') is not None and tile.get('y') is not None:
                    tile_info.append(f"   Position: ({tile['x']}, {tile['y']})")
                if tile.get('w') is not None and tile.get('h') is not None:
                    tile_info.append(f"   Size: {tile['w']}x{tile['h']}")
                
                response_parts.append("\n".join(tile_info))
        
        # Add dashboard URL
        base_url = config.lightdash_config.api_url.replace('/api/v1', '')
        dashboard_url = f"{base_url}/projects/{client.project_id}/dashboards/{dashboard['uuid']}"
        response_parts.extend(["", f"View dashboard: {dashboard_url}"])
        
        return [
            TextContent(
                type="text",
                text="\n".join(response_parts)
            )
        ]
        
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        
        # Check if it's a 404 error (dashboard not found)
        if "404" in str(e):
            return [
                TextContent(
                    type="text",
                    text=f"Error: Dashboard with ID '{dashboard_id}' not found."
                )
            ]
        
        return [
            TextContent(
                type="text",
                text=f"Error getting dashboard: {str(e)}"
            )
        ]