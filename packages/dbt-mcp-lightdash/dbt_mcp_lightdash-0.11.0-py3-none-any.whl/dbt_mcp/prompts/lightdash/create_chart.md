# Tool Name: lightdash_create_chart

## Description
Create a new chart in Lightdash by defining metrics, dimensions, and query parameters.

## When to Use
- Creating a new chart from scratch with specific metrics
- Saving a predefined query as a permanent chart
- Building charts for dashboards
- Creating reusable charts for team analysis

## Parameters

### Required:
- `name` (string): Clear, descriptive name for the chart
- `explore_id` (string): The explore (dbt model) containing the data
- `metrics` (array): List of metrics to include
- `dimensions` (array): List of dimensions available for grouping

### Optional:
- `description` (string): Explanation of what the chart shows
- `group_by` (array): Dimensions to group by with optional grain
- `filters` (array): Filter conditions to apply
- `sort` (array): Sorting configuration
- `limit` (integer): Result limit
- `chart_type` (string): Visualization type (default: "table")
- `space_id` (string): Space UUID to save the chart in

## JSON Examples

### Example 1: Simple metric chart
```json
{
  "name": "Total Revenue",
  "explore_id": "orders",
  "metrics": ["total_revenue"],
  "dimensions": ["created_date"]
}
```

### Example 2: Chart with grouping and filters
```json
{
  "name": "Monthly Revenue Trend",
  "description": "Monthly revenue for the last 12 months showing growth trend",
  "explore_id": "orders",
  "metrics": ["total_revenue"],
  "dimensions": ["created_date"],
  "group_by": [{"field": "created_date", "grain": "month"}],
  "filters": [
    {"field": "created_date", "operator": "inThePast", "value": 12, "unit": "months"}
  ],
  "sort": [{"field": "created_date", "order": "asc"}]
}
```

### Example 3: Multi-metric comparison chart
```json
{
  "name": "Revenue vs Orders by Category",
  "explore_id": "orders",
  "metrics": ["total_revenue", "order_count", "average_order_value"],
  "dimensions": ["product_category"],
  "group_by": [{"field": "product_category"}],
  "sort": [{"field": "total_revenue", "order": "desc"}],
  "limit": 10,
  "chart_type": "bar"
}
```

### Example 4: Customer analysis with multiple dimensions
```json
{
  "name": "Top Enterprise Customers - Current Quarter",
  "description": "Highest spending enterprise customers for executive review",
  "explore_id": "customers",
  "metrics": ["total_spend", "order_count"],
  "dimensions": ["customer_name", "customer_segment", "region"],
  "group_by": [
    {"field": "customer_name"},
    {"field": "customer_segment"},
    {"field": "region"}
  ],
  "filters": [
    {"field": "customer_segment", "operator": "equals", "value": "Enterprise"},
    {"field": "order_date", "operator": "inCurrentQuarter"}
  ],
  "sort": [{"field": "total_spend", "order": "desc"}],
  "limit": 20,
  "space_id": "exec-space-uuid"
}
```

### Example 5: Time-series analysis with complex filters
```json
{
  "name": "Weekly Sales Performance by Region",
  "explore_id": "orders",
  "metrics": ["total_revenue", "order_count"],
  "dimensions": ["created_date", "region"],
  "group_by": [
    {"field": "created_date", "grain": "week"},
    {"field": "region"}
  ],
  "filters": [
    {"field": "created_date", "operator": "inThePast", "value": 8, "unit": "weeks"},
    {"field": "status", "operator": "equals", "value": "completed"},
    {"field": "total_revenue", "operator": "greaterThan", "value": 0}
  ],
  "sort": [
    {"field": "created_date", "order": "desc"},
    {"field": "total_revenue", "order": "desc"}
  ],
  "chart_type": "line"
}
```

## Chart Types
- `table` (default)
- `bar`
- `line`
- `area`
- `scatter`
- `pie`
- `donut`

## Common Mistakes to Avoid
- ❌ Using metric/dimension names with table prefixes
- ❌ Creating overly generic chart names
- ❌ Forgetting to include dimensions before grouping by them
- ❌ Using non-existent fields from wrong explores
- ✅ Use `lightdash_get_explore` first to verify available fields
- ✅ Give charts descriptive, business-friendly names

## Related Tools
- `lightdash_get_explore` - Check available fields before creating
- `lightdash_run_metric_query` - Test queries before saving as charts
- `lightdash_list_spaces` - Find appropriate space for the chart
- `lightdash_edit_dashboard` - Add created charts to dashboards

## Notes
- Charts default to table visualization if not specified
- The tool handles field name mapping automatically
- Charts can be edited later in the Lightdash UI
- Consider reusability when choosing filters