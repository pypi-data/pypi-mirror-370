"""Smart query tool that uses semantic catalog for natural language queries"""

import logging
from typing import Dict, Any, List

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.lightdash.semantic_catalog import build_smart_query, build_smart_query_with_dspy, identify_domain
from dbt_mcp.tools.lightdash_run_metric_query import handle_lightdash_run_metric_query

logger = logging.getLogger(__name__)


def get_lightdash_smart_query_tool() -> Tool:
    """Get the smart query tool definition"""
    return Tool(
        name="lightdash_smart_query",
        description="""
# Tool Name: lightdash_smart_query

## Description
Answer business questions directly using natural language, without manual exploration.

## When to Use
- Getting sales/revenue data quickly
- Checking marketing performance
- Analyzing attribution/ROAS
- Reviewing lead generation metrics
- Any business metric question

## Examples
- "last 7 days of sales"
- "monthly revenue trend"
- "ad spend by campaign this month"
- "ROAS last quarter"
- "leads by state"
- "yesterday's profit"
- "conversion rate by channel"

## Automatic Intelligence
- Determines the right table automatically
- Selects appropriate metrics
- Handles time ranges naturally
- Adds proper dimensions
- No need to know field names

## Parameters

### Required:
- `question` (string): Natural language business question

### Optional:
- `verbose` (boolean): Include query details in response (default: false)

## JSON Examples

### Example 1: Simple sales query
```json
{
  "question": "last 7 days of sales"
}
```

### Example 2: Marketing performance
```json
{
  "question": "ad spend by campaign this month"
}
```

### Example 3: Attribution analysis
```json
{
  "question": "ROAS by channel last 30 days"
}
```

### Example 4: Lead metrics
```json
{
  "question": "cost per lead by state"
}
```

### Example 5: Profit analysis
```json
{
  "question": "monthly profit trend"
}
```

## Common Patterns
- Time: "last X days/weeks/months", "yesterday", "today", "this month/quarter/year"
- Grouping: "by campaign", "by channel", "by customer", "by state"
- Metrics: automatically selected based on context

## Notes
- No need to specify explore/table names
- Time ranges understood naturally
- Automatic metric selection
- Store filtering handled via write_key dimension
""",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Natural language business question"
                },
                "verbose": {
                    "type": "boolean",
                    "description": "Include query details in response",
                    "default": False
                }
            },
            "required": ["question"]
        }
    )


async def handle_lightdash_smart_query(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle smart query requests"""
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
            )
        ]
    
    question = arguments.get("question")
    verbose = arguments.get("verbose", False)
    
    if not question:
        return [
            TextContent(
                type="text",
                text="Error: question is required"
            )
        ]
    
    try:
        # Build query using semantic catalog
        logger.info(f"Processing natural language question: {question}")
        
        # Try to use DSPy-enhanced version first
        use_dspy = config and hasattr(config, 'lightdash_config')
        
        if use_dspy:
            try:
                logger.info("Attempting to use DSPy-enhanced field selection")
                query = await build_smart_query_with_dspy(question, config)
                logger.info(f"DSPy query built successfully: explore={query['explore_id']}")
            except Exception as e:
                logger.warning(f"DSPy query building failed, falling back to static: {e}")
                query = build_smart_query(question)
        else:
            # First identify the domain for better error messages
            domain = identify_domain(question)
            if not domain:
                return [
                    TextContent(
                        type="text",
                        text="""I couldn't understand what type of data you're looking for.

Please specify one of:
- **Sales/Revenue**: orders, revenue, profit, customers
- **Marketing**: ad spend, campaigns, impressions, clicks
- **Attribution**: ROAS, pixel tracking, conversions
- **Leads**: lead generation, geographic data, cost per lead

Example: "last 7 days of sales" or "ad spend by campaign"
"""
                    )
                ]
            
            # Build the query with static catalog
            query = build_smart_query(question)
            logger.info(f"Generated query for domain '{domain}': explore={query['explore_id']}")
        
        logger.info(f"Final query: metrics={query['metrics']}, dimensions={query['dimensions']}")
        
        # Execute the query using existing handler
        result = await handle_lightdash_run_metric_query(query, config)
        
        # If verbose, prepend query details
        if verbose and result:
            query_details = f"""Query Details:
- Domain: {domain}
- Explore: {query['explore_id']}
- Metrics: {', '.join(query['metrics'])}
- Dimensions: {', '.join(query['dimensions']) if query['dimensions'] else 'None'}
- Filters: {len(query.get('filters', []))} applied

---

"""
            result[0].text = query_details + result[0].text
        
        return result
        
    except ValueError as e:
        # User-friendly error from semantic catalog
        return [
            TextContent(
                type="text",
                text=str(e)
            )
        ]
    except Exception as e:
        error_msg = f"Error processing smart query: {str(e)}"
        logger.error(error_msg)
        
        # Provide helpful error message
        return [
            TextContent(
                type="text",
                text=f"""{error_msg}

Try rephrasing your question with:
- Clear time range: "last 7 days", "this month", "yesterday"
- Specific metrics: "revenue", "profit", "ad spend", "leads"
- Optional grouping: "by campaign", "by channel", "by state"

Example: "revenue by channel last 30 days"
"""
            )
        ]