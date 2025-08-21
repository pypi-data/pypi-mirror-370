"""Tool for creating Lightdash dashboards"""

import logging
from typing import Dict, Any, List, Optional
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_create_dashboard_tool() -> Tool:
    """Get the Lightdash create dashboard tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_CREATE_DASHBOARD.value,
        description=get_prompt("lightdash/create_dashboard"),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the dashboard"
                },
                "description": {
                    "type": ["string", "null"],
                    "description": "Description of the dashboard (optional)"
                },
                "space_id": {
                    "type": "string",
                    "description": "Space UUID to create the dashboard in (optional, uses default if not specified)"
                },
                "chart_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of chart UUIDs to add to the dashboard"
                },
                "layout": {
                    "type": "string",
                    "enum": ["auto", "single_column", "two_column", "custom"],
                    "description": "Layout preset for arranging charts (default: auto)",
                    "default": "auto"
                },
                "tiles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["saved_chart", "markdown"]},
                            "properties": {"type": "object"},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "w": {"type": "integer"},
                            "h": {"type": "integer"}
                        }
                    },
                    "description": "Custom tile configuration (advanced usage)"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
    )


def create_chart_tile(chart_id: str, x: int, y: int, w: int = 6, h: int = 4) -> Dict[str, Any]:
    """Create a chart tile configuration"""
    return {
        "type": "saved_chart",
        "properties": {
            "savedChartUuid": chart_id
        },
        "x": x,
        "y": y,
        "w": w,
        "h": h
    }


def create_markdown_tile(content: str, x: int, y: int, w: int = 6, h: int = 2) -> Dict[str, Any]:
    """Create a markdown tile configuration"""
    return {
        "type": "markdown",
        "properties": {
            "content": content
        },
        "x": x,
        "y": y,
        "w": w,
        "h": h
    }


async def handle_lightdash_create_dashboard(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash create dashboard request"""
    
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
    
    name = arguments.get("name")
    if not name:
        return [
            TextContent(
                type="text",
                text="Error: name is required"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Get parameters
        description = arguments.get("description")
        space_id = arguments.get("space_id")
        chart_ids = arguments.get("chart_ids", [])
        layout = arguments.get("layout", "auto")
        custom_tiles = arguments.get("tiles")
        
        # Create tiles configuration
        tiles = []
        
        if custom_tiles:
            # Use custom tile configuration if provided
            tiles = custom_tiles
        elif chart_ids:
            # Auto-generate tile layout based on layout preset
            if layout == "single_column":
                # Single column layout
                for i, chart_id in enumerate(chart_ids):
                    tiles.append(create_chart_tile(chart_id, x=0, y=i*4, w=12, h=4))
            
            elif layout == "two_column":
                # Two column layout
                for i, chart_id in enumerate(chart_ids):
                    col = i % 2
                    row = i // 2
                    tiles.append(create_chart_tile(chart_id, x=col*6, y=row*4, w=6, h=4))
            
            else:  # auto or custom
                # Auto layout - try to fit nicely
                charts_per_row = 2 if len(chart_ids) > 1 else 1
                chart_width = 12 // charts_per_row
                
                for i, chart_id in enumerate(chart_ids):
                    col = i % charts_per_row
                    row = i // charts_per_row
                    tiles.append(create_chart_tile(
                        chart_id,
                        x=col * chart_width,
                        y=row * 4,
                        w=chart_width,
                        h=4
                    ))
        
        # Create the dashboard
        dashboard = await client.create_dashboard(
            name=name,
            description=description,
            tiles=tiles,
            space_uuid=space_id
        )
        
        # Format response
        response_parts = [
            f"✅ Successfully created dashboard: {dashboard.get('name', name)}",
            f"Dashboard ID: {dashboard.get('uuid', 'N/A')}",
            f"Space: {dashboard.get('spaceName', 'Default')}",
        ]
        
        if description:
            response_parts.insert(1, f"Description: {description}")
        
        if tiles:
            response_parts.append(f"Added {len(tiles)} tile(s) to the dashboard")
        
        # Add dashboard URL
        if dashboard.get('uuid'):
            base_url = config.lightdash_config.api_url.replace('/api/v1', '')
            dashboard_url = f"{base_url}/projects/{client.project_id}/dashboards/{dashboard['uuid']}"
            response_parts.append(f"\nView dashboard: {dashboard_url}")
        
        # Suggest next steps
        if not tiles:
            response_parts.extend([
                "",
                "💡 Next steps:",
                "- Add charts using the edit dashboard tool",
                "- Create charts using the create chart tool",
                "- View available charts with the list charts tool"
            ])
        
        return [
            TextContent(
                type="text",
                text="\n".join(response_parts)
            )
        ]
        
    except Exception as e:
        logger.error(f"Error creating dashboard: {str(e)}")
        return [
            TextContent(
                type="text",
                text=f"Error creating dashboard: {str(e)}"
            )
        ]