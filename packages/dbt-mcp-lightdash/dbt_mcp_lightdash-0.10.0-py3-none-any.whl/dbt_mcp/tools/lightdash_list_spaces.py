"""Tool for listing Lightdash spaces"""

import logging
from typing import Dict, Any, List
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_list_spaces_tool() -> Tool:
    """Get the Lightdash list spaces tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_LIST_SPACES.value,
        description=get_prompt("lightdash/list_spaces"),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )


async def handle_lightdash_list_spaces(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash list spaces request"""
    
    # Parse arguments if they come as a string
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            # This tool doesn't require arguments, so just use empty dict
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
        spaces = await client.list_spaces()
        
        if not spaces:
            return [
                TextContent(
                    type="text",
                    text="No spaces found in the Lightdash project"
                )
            ]
        
        # Format spaces for display
        result = f"Found {len(spaces)} space(s) in Lightdash:\n\n"
        
        for space in spaces:
            result += f"• {space.get('name', 'Unnamed')}\n"
            result += f"  ID: {space.get('uuid', 'N/A')}\n"
            result += f"  Private: {space.get('isPrivate', False)}\n"
            
            # Show access information if available
            access = space.get('access', [])
            if access:
                result += f"  Access: {', '.join(access)}\n"
            
            result += "\n"
        
        return [TextContent(type="text", text=result.strip())]
        
    except Exception as e:
        logger.error(f"Error listing Lightdash spaces: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error listing Lightdash spaces: {str(e)}"
            )
        ]