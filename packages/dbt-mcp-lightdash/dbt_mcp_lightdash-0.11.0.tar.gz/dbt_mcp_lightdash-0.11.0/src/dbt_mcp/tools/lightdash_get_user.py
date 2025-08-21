"""Tool for getting current Lightdash user information"""

import logging
from typing import Dict, Any, List
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_get_user_tool() -> Tool:
    """Get the Lightdash get user tool definition"""
    return Tool(
        name="lightdash_get_user",
        description=get_prompt("lightdash/get_user"),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )


async def handle_lightdash_get_user(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the get user request"""
    
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
        # Create a custom client that can call the user endpoint
        client = LightdashAPIClient(config.lightdash_config)
        
        # Get user info
        user_endpoint = "/user"
        user_info = await client._make_request("GET", user_endpoint)
        
        # Format the response
        result = "Current Lightdash User Information:\n"
        result += "=" * 50 + "\n\n"
        
        if "results" in user_info:
            user = user_info["results"]
            result += f"User ID: {user.get('userUuid', 'N/A')}\n"
            result += f"Email: {user.get('email', 'N/A')}\n"
            result += f"First Name: {user.get('firstName', 'N/A')}\n"
            result += f"Last Name: {user.get('lastName', 'N/A')}\n"
            result += f"Organization ID: {user.get('organizationUuid', 'N/A')}\n"
            result += f"Organization Name: {user.get('organizationName', 'N/A')}\n"
            result += f"Role: {user.get('role', 'N/A')}\n"
            result += f"Is Active: {user.get('isActive', 'N/A')}\n"
            
            # Check for user attributes
            if "userAttributes" in user:
                result += f"\nUser Attributes:\n"
                for attr in user["userAttributes"]:
                    result += f"  - {attr.get('name', 'N/A')}: {attr.get('value', 'N/A')}\n"
        else:
            result += "No user information available\n"
        
        return [TextContent(type="text", text=result.strip())]
        
    except Exception as e:
        logger.error(f"Error getting user information: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]