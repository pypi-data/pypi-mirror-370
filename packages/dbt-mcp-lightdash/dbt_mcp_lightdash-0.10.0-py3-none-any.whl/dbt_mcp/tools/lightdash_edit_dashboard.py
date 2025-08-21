"""Tool for editing Lightdash dashboards"""

import logging
from typing import Dict, Any, List, Optional
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_edit_dashboard_tool() -> Tool:
    """Get the Lightdash edit dashboard tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_UPDATE_DASHBOARD.value,
        description=get_prompt("lightdash/edit_dashboard"),
        inputSchema={
            "type": "object",
            "properties": {
                "dashboard_id": {
                    "type": "string",
                    "description": "The UUID of the dashboard to edit"
                },
                "name": {
                    "type": "string",
                    "description": "New name for the dashboard (optional)"
                },
                "description": {
                    "type": ["string", "null"],
                    "description": "New description for the dashboard (optional)"
                },
                "add_chart_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Chart UUIDs to add to the dashboard"
                },
                "remove_tile_indices": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Indices of tiles to remove (0-based)"
                },
                "reorder_tiles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "integer"},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "w": {"type": "integer"},
                            "h": {"type": "integer"}
                        },
                        "required": ["index"]
                    },
                    "description": "New positions/sizes for existing tiles"
                },
                "add_markdown": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "x": {"type": "integer"},
                        "y": {"type": "integer"},
                        "w": {"type": "integer", "default": 6},
                        "h": {"type": "integer", "default": 2}
                    },
                    "required": ["content"],
                    "description": "Add a markdown tile with content"
                }
            },
            "required": ["dashboard_id"],
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


async def handle_lightdash_edit_dashboard(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash edit dashboard request"""
    
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
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # First get the existing dashboard
        existing_dashboard = await client.get_dashboard(dashboard_id)
        
        # Build update payload
        updates = {}
        changes_made = []
        
        # Update basic metadata
        if "name" in arguments:
            updates["name"] = arguments["name"]
            changes_made.append(f"✓ Updated name to: {arguments['name']}")
        
        if "description" in arguments:
            updates["description"] = arguments["description"]
            changes_made.append(f"✓ Updated description")
        
        # Handle tile modifications
        tiles = existing_dashboard.get("tiles", []).copy()
        
        # Remove tiles by index (do this first to avoid index shifting issues)
        remove_indices = arguments.get("remove_tile_indices", [])
        if remove_indices:
            # Sort in reverse order to avoid index shifting
            for idx in sorted(remove_indices, reverse=True):
                if 0 <= idx < len(tiles):
                    removed_tile = tiles.pop(idx)
                    tile_type = removed_tile.get('type', 'unknown')
                    changes_made.append(f"✓ Removed tile {idx} ({tile_type})")
        
        # Reorder/resize existing tiles
        reorder_tiles = arguments.get("reorder_tiles", [])
        for reorder in reorder_tiles:
            idx = reorder.get("index")
            if idx is not None and 0 <= idx < len(tiles):
                tile = tiles[idx]
                if "x" in reorder:
                    tile["x"] = reorder["x"]
                if "y" in reorder:
                    tile["y"] = reorder["y"]
                if "w" in reorder:
                    tile["w"] = reorder["w"]
                if "h" in reorder:
                    tile["h"] = reorder["h"]
                changes_made.append(f"✓ Repositioned/resized tile {idx}")
        
        # Add new chart tiles
        add_chart_ids = arguments.get("add_chart_ids", [])
        if add_chart_ids:
            # Find the next available position
            max_y = max((t.get("y", 0) + t.get("h", 4) for t in tiles), default=0)
            
            for i, chart_id in enumerate(add_chart_ids):
                # Try to place new charts in a 2-column layout
                col = i % 2
                row = i // 2
                tiles.append(create_chart_tile(
                    chart_id,
                    x=col * 6,
                    y=max_y + row * 4,
                    w=6,
                    h=4
                ))
            changes_made.append(f"✓ Added {len(add_chart_ids)} chart(s)")
        
        # Add markdown tile
        add_markdown = arguments.get("add_markdown")
        if add_markdown:
            # Find the next available position
            max_y = max((t.get("y", 0) + t.get("h", 4) for t in tiles), default=0)
            
            tiles.append(create_markdown_tile(
                add_markdown["content"],
                x=add_markdown.get("x", 0),
                y=add_markdown.get("y", max_y),
                w=add_markdown.get("w", 6),
                h=add_markdown.get("h", 2)
            ))
            changes_made.append("✓ Added markdown tile")
        
        # Update tiles if any tile-related changes were made
        if any(k in arguments for k in ["remove_tile_indices", "reorder_tiles", "add_chart_ids", "add_markdown"]):
            updates["tiles"] = tiles
        
        # Perform the update if there are any changes
        if updates:
            updated_dashboard = await client.update_dashboard(dashboard_id, updates)
            
            # Format response
            response_parts = [
                f"Successfully updated dashboard: {updated_dashboard.get('name', 'Unnamed Dashboard')}",
                f"Dashboard ID: {updated_dashboard.get('uuid', dashboard_id)}",
                "",
                "Changes made:"
            ]
            response_parts.extend(changes_made)
            
            # Add dashboard URL
            base_url = config.lightdash_config.api_url.replace('/api/v1', '')
            dashboard_url = f"{base_url}/projects/{client.project_id}/dashboards/{dashboard_id}"
            response_parts.append(f"\nView dashboard: {dashboard_url}")
            
            return [
                TextContent(
                    type="text",
                    text="\n".join(response_parts)
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text="No changes were specified. Dashboard remains unchanged."
                )
            ]
        
    except Exception as e:
        logger.error(f"Error editing dashboard: {str(e)}")
        return [
            TextContent(
                type="text",
                text=f"Error editing dashboard: {str(e)}"
            )
        ]