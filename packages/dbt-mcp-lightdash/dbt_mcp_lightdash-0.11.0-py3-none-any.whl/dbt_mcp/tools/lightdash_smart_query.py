"""Smart query tool that uses progressive discovery for natural language queries"""

import logging
from typing import Dict, Any, List, Optional

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.lightdash.query_builder import (
    build_query_from_question,
    validate_and_suggest_fields
)
from dbt_mcp.lightdash.explore_selector import (
    select_best_explore,
    get_explore_description
)
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.tools.argument_parser import parse_arguments

logger = logging.getLogger(__name__)


def get_lightdash_smart_query_tool() -> Tool:
    """Get the smart query tool definition"""
    return Tool(
        name="lightdash_smart_query",
        description="""
# Tool Name: lightdash_smart_query

## Description
Answer business questions using natural language with progressive field discovery.
This tool dynamically discovers available metrics and dimensions from your data model.

## When to Use
- Any business metric question
- Sales/revenue analysis (orders, products sold)
- Marketing performance (ad spend, CTR, impressions)
- ROAS and attribution analysis (return on ad spend, last-click attribution)
- Product analytics (what products were sold)
- Customer insights
- Geographic/lead analysis
- Time-based trends

## Important Notes
- For ROAS/attribution questions, the tool automatically uses attribution data
- For "what did we sell" questions, the tool finds product information
- The tool automatically selects the right data source based on your question

## Progressive Discovery Flow
1. Lists available explores/models
2. Discovers metrics and dimensions
3. Suggests best fields based on your question
4. Builds and executes the query

## Examples
- "what did we sell last week"
- "revenue by product category"
- "top customers by order count"
- "ad spend by campaign this month"
- "conversion rate trend"
- "products sold yesterday"

## Parameters

### Required:
- `question` (string): Natural language business question

### Optional:
- `explore_hint` (string): Specific explore to use (auto-detected if not provided)
- `verbose` (boolean): Show field discovery details (default: false)
- `limit` (integer): Max rows to return (default: 100)

## JSON Examples

### Example 1: Product analysis
```json
{
  "question": "what products did we sell this month"
}
```

### Example 2: Revenue with specific explore
```json
{
  "question": "revenue by customer segment",
  "explore_hint": "orders"
}
```

### Example 3: Verbose discovery
```json
{
  "question": "top selling items last week",
  "verbose": true,
  "limit": 20
}
```

## Features
- No hardcoded field mappings
- Fuzzy matching for typos
- Automatic time parsing
- Smart metric/dimension selection
- Works with any dbt model

## Notes
- Adapts to your actual schema
- Suggests alternatives for invalid fields
- Shows available options when unclear
""",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Natural language business question"
                },
                "explore_hint": {
                    "type": "string",
                    "description": "Optional: specific explore/model to query"
                },
                "verbose": {
                    "type": "boolean",
                    "description": "Show field discovery process",
                    "default": False
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum rows to return",
                    "default": 100
                }
            },
            "required": ["question"]
        }
    )


async def handle_lightdash_smart_query(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle smart query requests with progressive discovery"""
    
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
    
    question = arguments.get("question")
    explore_hint = arguments.get("explore_hint")
    verbose = arguments.get("verbose", False)
    limit = arguments.get("limit", 100)
    
    if not question:
        return [
            TextContent(
                type="text",
                text="Error: question is required"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        # Step 1: List available explores if no hint provided
        if not explore_hint:
            logger.info("Discovering available explores...")
            explores = await client.list_explores()
            
            if verbose:
                logger.info(f"Found {len(explores)} explores: {[e['name'] for e in explores]}")
            
            if not explores:
                return [
                    TextContent(
                        type="text",
                        text="No explores available in the project. Please check your Lightdash configuration."
                    )
                ]
            
            # Use intelligent explore selection
            explore_hint = select_best_explore(explores, question)
            
            if verbose:
                logger.info(f"Selected explore: {explore_hint}")
                explore_desc = get_explore_description(explore_hint)
                logger.info(f"Explore description: {explore_desc}")
        
        # Step 2: Get explore details (metrics and dimensions)
        logger.info(f"Getting fields for explore '{explore_hint}'...")
        explore_details = await client.get_explore(explore_hint)
        
        # Extract available metrics and dimensions
        available_metrics = []
        available_dimensions = []
        
        # Parse the explore structure
        if 'tables' in explore_details:
            for table_name, table_data in explore_details['tables'].items():
                # Get metrics
                if 'metrics' in table_data:
                    for metric_name, metric_data in table_data['metrics'].items():
                        if not metric_data.get('hidden', False):
                            available_metrics.append({
                                'name': metric_name,
                                'label': metric_data.get('label', metric_name),
                                'type': metric_data.get('type', 'number'),
                                'description': metric_data.get('description', '')
                            })
                
                # Get dimensions
                if 'dimensions' in table_data:
                    for dim_name, dim_data in table_data['dimensions'].items():
                        if not dim_data.get('hidden', False):
                            available_dimensions.append({
                                'name': dim_name,
                                'label': dim_data.get('label', dim_name),
                                'type': dim_data.get('type', 'string'),
                                'description': dim_data.get('description', '')
                            })
        
        if verbose:
            logger.info(f"Found {len(available_metrics)} metrics, {len(available_dimensions)} dimensions")
        
        # Step 3: Build query using dynamic discovery
        from dbt_mcp.lightdash.query_builder import build_query_from_question
        
        query = build_query_from_question(
            question=question,
            explore_name=explore_hint,
            available_metrics=available_metrics,
            available_dimensions=available_dimensions
        )
        
        # Add limit
        query['limit'] = limit
        
        if verbose:
            logger.info(f"Built query: {query}")
        
        # Step 4: Execute the query
        logger.info("Executing query...")
        
        # Build the metric query in Lightdash format
        metric_query = {
            "exploreName": query['explore_id'],
            "dimensions": query['dimensions'],
            "metrics": query['metrics'],
            "sorts": [],
            "limit": query['limit'],
            "filters": {},
            "tableCalculations": [],
            "additionalMetrics": []
        }
        
        # Add filters if present
        if query.get('filters'):
            filter_rules = []
            for filter_spec in query['filters']:
                filter_rule = {
                    "id": filter_spec['field'],
                    "target": {"fieldId": filter_spec['field']},
                    "operator": filter_spec['operator'],
                    "values": [filter_spec.get('value')] if filter_spec.get('value') is not None else []
                }
                
                # Add settings for time filters
                if filter_spec.get('unit'):
                    filter_rule["settings"] = {
                        "unitOfTime": filter_spec['unit'],
                        "completed": False
                    }
                
                filter_rules.append(filter_rule)
            
            if filter_rules:
                metric_query["filters"] = {
                    "and": [{
                        "id": "root",
                        "and": filter_rules
                    }]
                }
        
        # Add sorts
        for sort_spec in query.get('sort', []):
            metric_query["sorts"].append({
                "fieldId": sort_spec['field'],
                "descending": sort_spec.get('order', 'asc') == 'desc'
            })
        
        # Execute using compile + SQL approach
        compile_endpoint = f"/projects/{client.project_id}/explores/{query['explore_id']}/compileQuery"
        compile_result = await client._make_request("POST", compile_endpoint, data=metric_query)
        
        if "results" in compile_result:
            sql = compile_result["results"]
            
            # Execute SQL
            v2_sql_endpoint = f"/projects/{client.project_id}/query/sql"
            sql_payload = {"sql": sql}
            
            sql_result = await client._make_request("POST", v2_sql_endpoint, data=sql_payload, use_v2=True)
            
            if "results" in sql_result and "queryUuid" in sql_result["results"]:
                query_uuid = sql_result["results"]["queryUuid"]
                
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
                            query_result = status_data
                            break
                        elif status == "error":
                            error_msg = status_data.get("error", "Unknown error")
                            raise Exception(f"Query failed: {error_msg}")
                    
                    await asyncio.sleep(1)
                else:
                    raise Exception("Query timed out after 30 seconds")
        
        # Format results
        result_text = f"Query Results for: \"{question}\"\n"
        result_text += f"Explore: {query['explore_id']}\n\n"
        
        if verbose:
            result_text += f"Discovery Details:\n"
            result_text += f"- Selected metrics: {', '.join(m.split('_', 1)[-1] if '_' in m else m for m in query['metrics'])}\n"
            result_text += f"- Selected dimensions: {', '.join(d.split('_', 1)[-1] if '_' in d else d for d in query['dimensions']) if query['dimensions'] else 'None'}\n"
            result_text += f"- Filters applied: {len(query.get('filters', []))}\n\n"
        
        if "rows" in query_result:
            row_count = len(query_result["rows"])
            result_text += f"Found {row_count} rows\n\n"
            
            if row_count > 0:
                # Format as table-like output
                for i, row in enumerate(query_result["rows"][:20], 1):
                    result_text += f"{i}. "
                    # Format each field
                    formatted_fields = []
                    for key, value in row.items():
                        # Clean up field names (remove table prefix)
                        clean_key = key.split('_', 1)[-1] if '_' in key else key
                        formatted_fields.append(f"{clean_key}: {value}")
                    result_text += " | ".join(formatted_fields) + "\n"
                
                if row_count > 20:
                    result_text += f"\n... and {row_count - 20} more rows"
        else:
            result_text += "No results found"
        
        return [
            TextContent(
                type="text",
                text=result_text
            )
        ]
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        logger.error(error_msg)
        
        return [
            TextContent(
                type="text",
                text=f"""{error_msg}

Try rephrasing your question or use the explore_hint parameter to specify which data model to query.

Available explores can be found using the lightdash_list_explores tool.
"""
            )
        ]