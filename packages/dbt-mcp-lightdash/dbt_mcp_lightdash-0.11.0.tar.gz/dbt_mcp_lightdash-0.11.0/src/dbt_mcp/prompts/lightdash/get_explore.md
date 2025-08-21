# Tool Name: lightdash_get_explore

## Description
Get detailed information about a specific Lightdash explore including all available fields, metrics, and dimensions.

## When to Use
- Before building queries to understand available fields
- To discover what metrics and dimensions are in a specific explore
- To check field types and descriptions
- To understand table relationships and joins

## Parameters

### Required:
- `explore_id` (string): The name/ID of the explore (e.g., "orders", "customers")

### Optional:
None

## JSON Examples

### Example 1: Get details for orders explore
```json
{
  "explore_id": "orders"
}
```

### Example 2: Get details for customers explore
```json
{
  "explore_id": "customers"
}
```

### Example 3: Get details for a specific explore name
```json
{
  "explore_id": "revenue_analysis"
}
```

## Common Mistakes to Avoid
- ❌ Using display names instead of explore IDs - use the actual explore identifier
- ❌ Including table prefixes - just use the explore name
- ❌ Passing multiple explores - this tool handles one explore at a time
- ✅ Use `lightdash_list_explores` first to find available explore IDs
- ✅ The explore_id is typically the dbt model name

## Related Tools
- `lightdash_list_explores` - Use this first to see all available explores
- `lightdash_run_metric_query` - Use after this to query the explore
- `list_metrics_enhanced` - Alternative way to see metrics across all explores

## Notes
- This tool returns all dimensions and metrics with their types and descriptions
- Hidden fields are excluded from the results
- The response shows the base table and any joined tables
- Field names in the response include the table prefix (e.g., "orders.total_revenue")