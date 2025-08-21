# Tool Name: list_metrics_enhanced

## Description
List all available metrics with enriched metadata from both dbt semantic layer and Lightdash explores.

## When to Use
- Starting a new analysis and discovering metrics
- Planning which system to use (dbt vs Lightdash)
- Building charts and need metric context
- Understanding metric availability by explore
- Finding metrics across multiple explores

## Metric Sources
- **[SL]** - Available in dbt semantic layer
- **[LD]** - Available in Lightdash only
- **[SL+LD]** - Available in both systems

## Parameters

### Optional:
- `explore_filter` (string): Filter metrics to specific explore/model
- `include_lightdash_only` (boolean): Include Lightdash-only metrics (default: true)

## JSON Examples

### Example 1: List all metrics across all explores
```json
{}
```

### Example 2: Filter metrics to specific explore
```json
{
  "explore_filter": "orders",
  "include_lightdash_only": true
}
```

### Example 3: Show only cross-platform metrics
```json
{
  "include_lightdash_only": false
}
```

### Example 4: Find customer-related metrics
```json
{
  "explore_filter": "customer",
  "include_lightdash_only": true
}
```

### Example 5: Product explore metrics only
```json
{
  "explore_filter": "products",
  "include_lightdash_only": true
}
```

## Response Structure
Groups metrics by explore showing:
- Metric name with source indicator
- Description
- Data type (number, currency, percent)
- Associated dimensions
- Labels and tags

Example output format:
```
orders:
  - total_revenue [SL+LD] - Sum of all order amounts
  - order_count [LD] - Number of orders  
  - average_order_value [SL+LD] - Revenue per order
  Dimensions: created_date, status, customer_name
```

## Common Mistakes to Avoid
- ❌ Using exact explore names (use partial match)
- ❌ Expecting metric details (use get_explore)
- ✅ Use explore_filter for fuzzy matching
- ✅ Check both systems for full coverage

## Usage Patterns
1. **Dashboard Planning**: List all metrics, note explores
2. **Cross-System Work**: Set include_lightdash_only=false
3. **Explore Discovery**: Filter by business area
4. **Migration Status**: Compare [SL] vs [LD] metrics

## Related Tools
- `lightdash_list_explores` - See all available explores
- `lightdash_get_explore` - Get detailed field info
- `lightdash_create_chart` - Use discovered metrics
- `dbt_list_semantic_models` - dbt-only metrics

## Notes
- Partial explore names work (e.g., "cust" matches "customers")
- Enriched metadata helps understand metric relationships
- Use for metric discovery before creating charts