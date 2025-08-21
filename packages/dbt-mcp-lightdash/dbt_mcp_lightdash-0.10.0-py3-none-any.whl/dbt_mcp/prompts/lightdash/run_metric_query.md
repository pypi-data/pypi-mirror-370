# Tool Name: lightdash_run_metric_query

## Description
Execute queries against Lightdash explores to analyze data and optionally save results as charts.

## When to Use
- Running data analysis queries to answer business questions
- Exploring metrics and dimensions before creating charts
- Creating and saving charts from query results
- Building queries for dashboards

## Parameters

### Required:
- `explore_id` (string): The explore/model to query (e.g., "orders", "customers")
- `metrics` (array): List of metric names to include
- `dimensions` (array): List of dimension names available for grouping

### Optional:
- `group_by` (array): Dimensions to group results by, with optional time grain
- `filters` (array): Filter conditions to apply
- `sort` (array): Fields to sort by with order
- `limit` (integer): Maximum number of results to return
- `save_as_chart` (boolean): Whether to save results as a chart
- `chart_name` (string): Name for saved chart (required if save_as_chart=true)
- `chart_description` (string): Description for saved chart
- `space_id` (string): Space UUID to save chart in

## JSON Examples

### Example 1: Simple metric query
```json
{
  "explore_id": "orders",
  "metrics": ["total_revenue", "order_count"],
  "dimensions": ["status"]
}
```

### Example 2: Query with grouping and time grain
```json
{
  "explore_id": "orders",
  "metrics": ["total_revenue"],
  "dimensions": ["created_date"],
  "group_by": [
    {"field": "created_date", "grain": "month"}
  ],
  "sort": [
    {"field": "created_date", "order": "asc"}
  ],
  "limit": 12
}
```

### Example 3: Query with filters
```json
{
  "explore_id": "customers",
  "metrics": ["customer_lifetime_value", "order_count"],
  "dimensions": ["customer_segment", "customer_name"],
  "group_by": [
    {"field": "customer_segment"},
    {"field": "customer_name"}
  ],
  "filters": [
    {"field": "customer_segment", "operator": "equals", "value": "Enterprise"},
    {"field": "created_date", "operator": "inThePast", "value": 90, "unit": "days"}
  ],
  "sort": [
    {"field": "customer_lifetime_value", "order": "desc"}
  ],
  "limit": 20
}
```

### Example 4: Save query as chart
```json
{
  "explore_id": "orders",
  "metrics": ["total_revenue", "order_count"],
  "dimensions": ["product_category"],
  "group_by": [
    {"field": "product_category"}
  ],
  "sort": [
    {"field": "total_revenue", "order": "desc"}
  ],
  "save_as_chart": true,
  "chart_name": "Revenue by Product Category",
  "chart_description": "Product category performance analysis showing revenue and order volume"
}
```

### Example 5: Complex query with multiple filters and groupings
```json
{
  "explore_id": "orders",
  "metrics": ["total_revenue", "average_order_value", "order_count"],
  "dimensions": ["region", "created_date", "status"],
  "group_by": [
    {"field": "region"},
    {"field": "created_date", "grain": "week"},
    {"field": "status"}
  ],
  "filters": [
    {"field": "created_date", "operator": "inThePast", "value": 30, "unit": "days"},
    {"field": "status", "operator": "equals", "value": "completed"},
    {"field": "region", "operator": "notEquals", "value": "Test"}
  ],
  "sort": [
    {"field": "created_date", "order": "desc"},
    {"field": "total_revenue", "order": "desc"}
  ],
  "limit": 100,
  "save_as_chart": true,
  "chart_name": "Regional Sales Performance - Last 30 Days",
  "space_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Filter Operators
- `equals`: Exact match
- `notEquals`: Not equal to value
- `isNull`: Field is null
- `isNotNull`: Field has a value
- `greaterThan`: Greater than value
- `greaterThanOrEqual`: Greater than or equal
- `lessThan`: Less than value
- `lessThanOrEqual`: Less than or equal
- `inThePast`: Time period in the past (requires `value` and `unit`)
- `inCurrentQuarter`: Current quarter
- `inLastQuarter`: Previous quarter

## Time Grains for Date Grouping
- `day`, `week`, `month`, `quarter`, `year`

## Common Mistakes to Avoid
- ❌ Using field names with table prefixes - use just the field name
- ❌ Forgetting to include dimensions in the dimensions array before grouping
- ❌ Missing required chart_name when save_as_chart is true
- ❌ Using incorrect filter operators or missing required filter properties
- ✅ Use `lightdash_get_explore` first to see available fields
- ✅ Start with a small limit to test queries before saving

## Related Tools
- `lightdash_list_explores` - Find available explores
- `lightdash_get_explore` - See fields in an explore
- `lightdash_create_chart` - Alternative way to create charts
- `list_metrics_enhanced` - Discover available metrics

## Notes
- Metrics and dimensions must exist in the specified explore
- Charts default to table visualization when saved
- The tool handles field name mapping automatically
- Results include both the query data and metadata about the query