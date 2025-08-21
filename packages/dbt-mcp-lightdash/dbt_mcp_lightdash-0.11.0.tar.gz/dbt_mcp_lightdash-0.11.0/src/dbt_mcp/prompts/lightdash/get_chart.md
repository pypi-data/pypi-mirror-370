# Tool Name: lightdash_get_chart

## Description
Get detailed information about a specific Lightdash chart including its configuration, query, and metadata.

## When to Use
- Retrieving the configuration of an existing chart
- Understanding how a chart is built (metrics, dimensions, filters)
- Getting chart details before editing
- Checking chart visualization settings
- Finding the explore used by a chart

## Parameters

### Required:
- `chart_id` (string): The UUID of the chart to retrieve

## JSON Examples

### Example 1: Basic chart retrieval
```json
{
  "chart_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Example 2: Get chart for editing
```json
{
  "chart_id": "7f4a2b8c-9e1d-4532-8abc-123456789def"
}
```

### Example 3: Check chart configuration
```json
{
  "chart_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## Common Mistakes to Avoid
- ❌ Using chart names instead of UUIDs
- ❌ Using partial IDs or short codes
- ✅ Use `lightdash_list_charts` to find the correct UUID
- ✅ Always use the full UUID from list results

## Related Tools
- `lightdash_list_charts` - Find chart UUIDs
- `lightdash_edit_chart` - Modify chart after getting details
- `lightdash_delete_chart` - Remove chart if needed
- `lightdash_edit_dashboard` - Add chart to dashboards

## Response Structure
The tool returns:
- Chart name and description
- Explore used
- Metrics and dimensions
- Filters and sorts
- Visualization type and config
- Space location
- Creator and update info

## Notes
- Chart IDs are UUIDs, not names
- Use this before editing to understand current state
- Shows the full query configuration