# Tool Name: lightdash_list_explores

## Description
List all available explores (dbt models) in the Lightdash project for querying and visualization.

## When to Use
- Discovering available data models
- Finding explores for chart creation
- Understanding what data is queryable
- Choosing explores for analysis
- Mapping dbt models to Lightdash

## Parameters
None - this tool takes no parameters

## JSON Examples

### Example 1: List all explores
```json
{}
```

### Example 2: Discover data models
```json
{}
```

### Example 3: Find queryable models
```json
{}
```

## Common Mistakes to Avoid
- ❌ Passing any parameters - this tool takes none
- ❌ Expecting field details (use get_explore for that)
- ✅ Note explore names for use in queries
- ✅ Use get_explore to see available fields

## Related Tools
- `lightdash_get_explore` - Get fields within an explore
- `lightdash_create_chart` - Use explores in charts
- `lightdash_run_metric_query` - Query explores directly
- `list_metrics_enhanced` - See metrics by explore

## Response Structure
Returns array of explores with:
- Explore name (ID)
- Label (display name)
- Tags (if any)
- Schema name
- Database name
- Description

## Notes
- Explore names are used as explore_id in other tools
- Each explore represents a dbt model
- Use get_explore to see metrics and dimensions