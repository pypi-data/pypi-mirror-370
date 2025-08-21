"""Tool for running metric queries through Lightdash instead of dbt Cloud"""

import json
import logging
from typing import Dict, Any, List, Optional

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.lightdash.validation import validate_query_parameters
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt
from dbt_mcp.tools.argument_parser import parse_arguments

logger = logging.getLogger(__name__)


def get_lightdash_run_metric_query_tool() -> Tool:
    """Get the Lightdash run metric query tool definition"""
    return Tool(
        name="lightdash_run_metric_query",
        description=get_prompt("lightdash/run_metric_query"),
        inputSchema={
            "type": "object",
            "properties": {
                "explore_id": {
                    "type": "string",
                    "description": "The explore (table) to query"
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of metrics to query (e.g., ['total_revenue', 'order_count'])"
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of dimensions to group by (e.g., ['event_date', 'customer_id'])",
                    "default": []
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "operator": {"type": "string", "enum": ["equals", "notEquals", "greaterThan", "lessThan", "greaterThanOrEqual", "lessThanOrEqual", "inThePast", "notInThePast", "in", "notIn"]},
                            "value": {"type": ["string", "number", "array", "null"]}
                        },
                        "required": ["field", "operator"]
                    },
                    "description": "Filters to apply to the query",
                    "default": []
                },
                "sort": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "descending": {"type": "boolean", "default": False}
                        },
                        "required": ["field"]
                    },
                    "description": "Sort order for results",
                    "default": []
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows to return",
                    "default": 500
                },
                "save_as_chart": {
                    "type": "boolean",
                    "description": "Whether to save the query results as a chart",
                    "default": False
                },
                "chart_name": {
                    "type": "string",
                    "description": "Name for the chart (required if save_as_chart is true)"
                },
                "chart_type": {
                    "type": "string",
                    "enum": ["table", "bar", "line", "scatter", "area", "pie", "donut"],
                    "description": "Type of chart to create",
                    "default": "table"
                },
                "space_id": {
                    "type": "string",
                    "description": get_prompt("lightdash/args/space_id")
                }
            },
            "required": ["explore_id", "metrics"]
        }
    )


async def handle_lightdash_run_metric_query(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash run metric query request"""
    
    # Parse arguments using the universal parser
    try:
        arguments = parse_arguments(arguments)
    except Exception as e:
        logger.error(f"Failed to parse arguments: {e}")
        logger.error(f"Raw arguments: {arguments}")
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
    
    # Extract parameters
    explore_id = arguments.get("explore_id")
    metrics = arguments.get("metrics", [])
    dimensions = arguments.get("dimensions", [])
    filters = arguments.get("filters", [])
    sort = arguments.get("sort", [])
    limit = arguments.get("limit", 500)
    save_as_chart = arguments.get("save_as_chart", False)
    chart_name = arguments.get("chart_name")
    chart_type = arguments.get("chart_type", config.lightdash_config.default_chart_type or "table")
    space_id = arguments.get("space_id", config.lightdash_config.default_space_id)
    
    # Validate required fields
    if not explore_id:
        return [
            TextContent(
                type="text",
                text="Error: explore_id is required"
            )
        ]
    
    if not metrics:
        return [
            TextContent(
                type="text",
                text="Error: at least one metric is required"
            )
        ]
    
    # Validate save as chart parameters
    if save_as_chart and not chart_name:
        return [
            TextContent(
                type="text",
                text="Error: chart_name is required when save_as_chart is true"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Build the metric query in Lightdash format
        # The v1 API expects field names with table prefix
        metric_query = {
            "exploreName": explore_id,
            "dimensions": dimensions,
            "metrics": metrics,
            "sorts": [],
            "limit": limit,
            "tableCalculations": [],
            "additionalMetrics": []
        }
        
        # Build filters
        filter_rules = []
        if filters:
            for filter_spec in filters:
                field = filter_spec.get("field")
                operator = filter_spec.get("operator")
                value = filter_spec.get("value")
                
                if field and operator:
                    # Process field name same as metrics/dimensions
                    if field.startswith(f"{explore_id}_"):
                        processed_field = field
                    elif '.' in field:
                        processed_field = field.replace('.', '_')
                    else:
                        processed_field = f"{explore_id}_{field}"
                    
                    filter_rule = {
                        "id": processed_field,
                        "target": {
                            "fieldId": processed_field
                        },
                        "operator": operator,
                        "values": [value] if not isinstance(value, list) else value
                    }
                    
                    # Add settings for time-based filters
                    if operator == "inThePast" and filter_spec.get("unit"):
                        filter_rule["settings"] = {
                            "unitOfTime": filter_spec["unit"],
                            "completed": False
                        }
                    
                    filter_rules.append(filter_rule)
        
        # Set filters in the query
        if filter_rules:
            metric_query["filters"] = {
                "and": [{
                    "id": "root",
                    "and": filter_rules
                }]
            }
        else:
            # Based on our debug script, empty object works with compileQuery
            metric_query["filters"] = {}
        
        logger.info(f"Applied filters: {filter_rules if filter_rules else 'none'}")
        
        # Add sorts if provided
        for sort_spec in sort:
            field = sort_spec.get("field")
            order = sort_spec.get("order", "asc")  # Changed from descending to order
            if field:
                # Process field name same as metrics/dimensions
                if field.startswith(f"{explore_id}_"):
                    processed_field = field
                elif '.' in field:
                    processed_field = field.replace('.', '_')
                else:
                    processed_field = f"{explore_id}_{field}"
                    
                metric_query["sorts"].append({
                    "fieldId": processed_field,
                    "descending": order == "desc"  # Convert order to descending boolean
                })
        
        # Execute the query using v2 API endpoint with async query
        logger.info(f"Executing metric query on explore '{explore_id}'")
        logger.info(f"Original metrics requested: {metrics}")
        logger.info(f"Original dimensions requested: {dimensions}")
        
        # Lightdash uses underscore notation for field names, not dots
        # Always add table prefix unless it's already there
        processed_metrics = []
        for metric in metrics:
            # Check if it already has the table prefix
            if metric.startswith(f"{explore_id}_"):
                field_id = metric
            elif '.' in metric:
                # Convert dot notation to underscore
                field_id = metric.replace('.', '_')
            else:
                # Add table prefix with underscore
                field_id = f"{explore_id}_{metric}"
            processed_metrics.append(field_id)
        
        processed_dimensions = []
        for dimension in dimensions:
            # Check if it already has the table prefix
            if dimension.startswith(f"{explore_id}_"):
                field_id = dimension
            elif '.' in dimension:
                # Convert dot notation to underscore
                field_id = dimension.replace('.', '_')
            else:
                # Add table prefix with underscore
                field_id = f"{explore_id}_{dimension}"
            processed_dimensions.append(field_id)
        
        # Update the query with processed field names
        metric_query['metrics'] = processed_metrics
        metric_query['dimensions'] = processed_dimensions
        
        logger.info(f"Processed metrics: {processed_metrics}")
        logger.info(f"Processed dimensions: {processed_dimensions}")
        
        # First, get the user's organizationUuid
        try:
            user_info = await client.get_user()
            organization_uuid = user_info.get("organizationUuid")
            logger.info(f"Got organizationUuid: {organization_uuid}")
        except Exception as e:
            logger.warning(f"Failed to get user info: {e}")
            organization_uuid = None
        
        # Use a workaround: compile the query first, then execute the SQL directly
        compile_endpoint = f"/projects/{client.project_id}/explores/{explore_id}/compileQuery"
        
        # Inject the organizationUuid into the metric query
        if organization_uuid:
            # Add user attributes to the query
            metric_query["userAttributes"] = {
                "organizationUuid": organization_uuid,
                "organizationuuid": organization_uuid  # Try lowercase too
            }
            logger.info("Injected organizationUuid into query")
        
        try:
            # Step 1: Compile the query to get SQL
            logger.info("Compiling query to get SQL...")
            compile_result = await client._make_request("POST", compile_endpoint, data=metric_query)
            
            if "results" in compile_result:
                sql = compile_result["results"]
                logger.info(f"Compiled SQL: {sql}")
                
                # Step 2: Execute the SQL using v2 API endpoint
                v2_sql_endpoint = f"/projects/{client.project_id}/query/sql"
                sql_payload = {
                    "sql": sql
                }
                
                logger.info("Executing SQL via v2 API...")
                sql_result = await client._make_request("POST", v2_sql_endpoint, data=sql_payload, use_v2=True)
                
                if "results" in sql_result and "queryUuid" in sql_result["results"]:
                    query_uuid = sql_result["results"]["queryUuid"]
                    logger.info(f"SQL query started with UUID: {query_uuid}")
                    
                    # Poll for results
                    import asyncio
                    max_attempts = 30
                    for attempt in range(max_attempts):
                        status_endpoint = f"/projects/{client.project_id}/query/{query_uuid}"
                        status_result = await client._make_request("GET", status_endpoint, use_v2=True)
                        
                        if "results" in status_result:
                            status_data = status_result["results"]
                            status = status_data.get("status")
                            
                            if status in ["completed", "ready"]:
                                # Results are in the status response for v2 API
                                query_result = status_data
                                logger.info("SQL query completed successfully")
                                break
                            elif status == "error":
                                error_msg = status_data.get("error", "Unknown error")
                                raise Exception(f"SQL query failed: {error_msg}")
                        
                        await asyncio.sleep(1)
                    else:
                        raise Exception("SQL query timed out after 30 seconds")
                else:
                    raise Exception("SQL query didn't return queryUuid")
            else:
                raise Exception("Failed to compile query")
                
        except Exception as e:
            # If all else fails, try the original v1 endpoint
            logger.error(f"Workaround failed: {str(e)}, attempting v1 endpoint...")
            endpoint = f"/projects/{client.project_id}/explores/{explore_id}/runQuery"
            
            # Make sure user attributes are in the query for v1 endpoint too
            if organization_uuid and "userAttributes" not in metric_query:
                metric_query["userAttributes"] = {
                    "organizationUuid": organization_uuid,
                    "organizationuuid": organization_uuid
                }
            
            query_result = await client._make_request("POST", endpoint, data=metric_query)
        
        # For v2 API, query_result is already the status_data which contains rows directly
        # No need to extract results again
        
        # Format the results
        result_text = f"Query executed successfully on explore '{explore_id}'\n\n"
        
        # Check if we have results
        if "rows" in query_result:
            row_count = len(query_result["rows"])
            result_text += f"Returned {row_count} rows\n\n"
            
            # Show sample of results (first 10 rows)
            if row_count > 0:
                result_text += "Sample results (first 10 rows):\n"
                for i, row in enumerate(query_result["rows"][:10]):
                    result_text += f"{i+1}. {row}\n"
                
                if row_count > 10:
                    result_text += f"\n... and {row_count - 10} more rows\n"
        
        # Save as chart if requested
        if save_as_chart and chart_name:
            # Create chart configuration
            chart_config = {
                "name": chart_name,
                "description": f"Created from metric query: {', '.join(metrics)}",
                "tableName": explore_id,
                "metricQuery": metric_query,
                "chartConfig": {
                    "type": chart_type,
                    "config": {
                        "metricId": metrics[0] if metrics else None
                    }
                },
                "tableConfig": {
                    "columnOrder": dimensions + metrics
                },
                "pivotConfig": None,
                "updatedAt": None,
                "spaceUuid": space_id
            }
            
            # Create the chart
            chart_result = await client.create_chart(
                name=chart_name,
                description=f"Created from metric query: {', '.join(metrics)}",
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
            
            if "savedQueryUuid" in chart_result:
                result_text += f"\n\n✅ Chart saved successfully!\n"
                result_text += f"Chart ID: {chart_result['savedQueryUuid']}\n"
                result_text += f"Chart Name: {chart_name}\n"
                result_text += f"Space ID: {space_id}"
            else:
                result_text += f"\n\n⚠️ Chart creation returned unexpected result: {chart_result}"
        
        return [
            TextContent(
                type="text",
                text=result_text
            )
        ]
        
    except Exception as e:
        error_msg = f"Error executing metric query: {str(e)}"
        logger.error(error_msg)
        return [
            TextContent(
                type="text",
                text=error_msg
            )
        ]