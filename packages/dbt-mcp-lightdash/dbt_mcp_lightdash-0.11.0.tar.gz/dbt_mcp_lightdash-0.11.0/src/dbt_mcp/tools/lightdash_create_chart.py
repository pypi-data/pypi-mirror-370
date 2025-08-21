"""Tool for creating Lightdash charts from query results"""

import json
import logging
from typing import Dict, Any, List

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.lightdash.validation import ErrorHandler
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_create_chart_tool() -> Tool:
    """Get the Lightdash create chart tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_CREATE_CHART.value,
        description=get_prompt("lightdash/create_chart"),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": get_prompt("lightdash/args/chart_name")
                },
                "description": {
                    "type": "string",
                    "description": "Optional description for the chart"
                },
                "explore_id": {
                    "type": "string", 
                    "description": get_prompt("lightdash/args/explore_id")
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": get_prompt("lightdash/args/metrics")
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": get_prompt("lightdash/args/dimensions")
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "operator": {"type": "string"},
                            "value": {"type": ["string", "number", "array", "null"]}
                        }
                    },
                    "description": get_prompt("lightdash/args/filters")
                },
                "sort": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "descending": {"type": "boolean"}
                        }
                    },
                    "description": get_prompt("lightdash/args/sort")
                },
                "limit": {
                    "type": "integer",
                    "description": get_prompt("lightdash/args/limit"),
                    "default": 500
                },
                "chart_type": {
                    "type": "string",
                    "description": "Type of chart",
                    "enum": ["table", "bar", "line", "scatter", "area", "pie", "donut"],
                    "default": "table"
                },
                "space_id": {
                    "type": "string",
                    "description": get_prompt("lightdash/args/space_id")
                },
                "include_embed_url": {
                    "type": "boolean",
                    "description": "Include embed URL in response for rendering charts in LibreChat",
                    "default": True
                }
            },
            "required": ["name", "explore_id", "metrics"],
        },
    )


async def handle_lightdash_create_chart(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash create chart request"""
    
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
            logger.error(f"Failed to parse arguments JSON: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error parsing arguments: {str(e)}"
                )
            ]
    
    # Handle MCP argument wrapping
    # The MCP inspector sometimes sends arguments wrapped in an "arguments" string
    if isinstance(arguments, dict) and "arguments" in arguments and isinstance(arguments["arguments"], str):
        try:
            arguments = json.loads(arguments["arguments"])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse arguments JSON: {e}")
            logger.error(f"Raw arguments: {arguments}")
            return [
                TextContent(
                    type="text",
                    text="Error: Invalid JSON in arguments. Please check your input format."
                )
            ]
    
    # Extract arguments
    name = arguments.get("name")
    description = arguments.get("description", "")
    explore_id = arguments.get("explore_id")
    metrics = arguments.get("metrics", [])
    dimensions = arguments.get("dimensions", [])
    filters = arguments.get("filters", [])
    sort = arguments.get("sort", [])
    limit = arguments.get("limit", 500)
    chart_type = arguments.get("chart_type", config.lightdash_config.default_chart_type or "table")
    space_id = arguments.get("space_id", config.lightdash_config.default_space_id)
    include_embed_url = arguments.get("include_embed_url", True)
    
    # Validate required fields
    if not name:
        return [
            TextContent(
                type="text",
                text=ErrorHandler.handle_validation_error("Chart name is required")
            )
        ]
    
    if not explore_id:
        return [
            TextContent(
                type="text",
                text=ErrorHandler.handle_validation_error("Explore ID is required")
            )
        ]
    
    if not metrics:
        return [
            TextContent(
                type="text",
                text=ErrorHandler.handle_validation_error("At least one metric is required")
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Get user info for organizationUuid
        user_info = await client.get_user()
        organization_uuid = user_info.get("organizationUuid")
        
        # Process field names to add table prefix
        processed_metrics = []
        for metric in metrics:
            if metric.startswith(f"{explore_id}_"):
                field_id = metric
            elif '.' in metric:
                field_id = metric.replace('.', '_')
            else:
                field_id = f"{explore_id}_{metric}"
            processed_metrics.append(field_id)
        
        processed_dimensions = []
        for dimension in dimensions:
            if dimension.startswith(f"{explore_id}_"):
                field_id = dimension
            elif '.' in dimension:
                field_id = dimension.replace('.', '_')
            else:
                field_id = f"{explore_id}_{dimension}"
            processed_dimensions.append(field_id)
        
        # Process filters
        filter_rules = []
        for filter_spec in filters:
            field = filter_spec.get("field")
            operator = filter_spec.get("operator")
            value = filter_spec.get("value")
            
            if field and operator:
                if field.startswith(f"{explore_id}_"):
                    processed_field = field
                elif '.' in field:
                    processed_field = field.replace('.', '_')
                else:
                    processed_field = f"{explore_id}_{field}"
                
                filter_rules.append({
                    "id": processed_field,
                    "target": {
                        "fieldId": processed_field
                    },
                    "operator": operator,
                    "values": [value] if not isinstance(value, list) else value
                })
        
        # Process sorts
        sorts = []
        for sort_spec in sort:
            field = sort_spec.get("field")
            descending = sort_spec.get("descending", False)
            
            if field:
                if field.startswith(f"{explore_id}_"):
                    processed_field = field
                elif '.' in field:
                    processed_field = field.replace('.', '_')
                else:
                    processed_field = f"{explore_id}_{field}"
                
                sorts.append({
                    "fieldId": processed_field,
                    "descending": descending
                })
        
        # Build metric query
        metric_query = {
            "exploreName": explore_id,
            "dimensions": processed_dimensions,
            "metrics": processed_metrics,
            "filters": {},
            "sorts": sorts,
            "limit": limit,
            "tableCalculations": [],
            "additionalMetrics": [],
            "userAttributes": {
                "organizationUuid": organization_uuid
            }
        }
        
        # Add filters if provided
        if filter_rules:
            metric_query["filters"] = {
                "and": [{
                    "id": "root",
                    "and": filter_rules
                }]
            }
        
        # Create the chart
        created_chart = await client.create_chart(
            name=name,
            description=description,
            table_name=explore_id,
            metric_query=metric_query,
            chart_config={
                "type": chart_type,
                "config": {
                    "metricId": processed_metrics[0] if processed_metrics else None
                }
            },
            space_uuid=space_id
        )
        
        # Format success response
        result = f"✅ Chart created successfully!\n\n"
        result += f"Name: {name}\n"
        
        if "uuid" in created_chart:
            result += f"ID: {created_chart['uuid']}\n"
            
            # Construct URL
            base_url = config.lightdash_config.api_url.replace('/api/v1', '')
            chart_url = f"{base_url}/projects/{config.lightdash_config.project_id}/saved/{created_chart['uuid']}"
            result += f"URL: {chart_url}\n"
        
        result += f"Type: {chart_type}\n"
        result += f"Explore: {explore_id}\n"
        
        if metrics:
            result += f"Metrics: {', '.join(metrics)}\n"
        if dimensions:
            result += f"Dimensions: {', '.join(dimensions)}\n"
        
        # Note: Individual charts cannot be embedded, only dashboards
        # If embed URL is requested, we inform the user
        if include_embed_url and "uuid" in created_chart:
            result += "\n\n💡 Note: Individual charts cannot be embedded. To embed this visualization, add it to a dashboard first."
        
        return [TextContent(type="text", text=result.strip())]
        
    except Exception as e:
        logger.error(f"Error creating Lightdash chart: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=ErrorHandler.handle_api_error(e, "creating chart")
            )
        ]