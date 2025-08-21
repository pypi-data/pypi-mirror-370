# Tool Name: lightdash_list_charts

## Description
List all charts/saved queries in Lightdash, optionally filtered by space.

## When to Use
- Discovering available charts in the project
- Finding charts in a specific space
- Getting chart UUIDs for other operations
- Auditing saved queries
- Understanding what visualizations exist

## Parameters

### Optional:
- `space_id` (string): Filter charts by space UUID

## JSON Examples

### Example 1: List all charts
```json
{}
```

### Example 2: List charts in a specific space
```json
{
  "space_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Example 3: Find charts for dashboard creation
```json
{
  "space_id": "marketing-space-uuid-here"
}
```

## Common Mistakes to Avoid
- ❌ Using space names instead of UUIDs
- ❌ Expecting chart content (use get_chart for details)
- ✅ Use `lightdash_list_spaces` to find space UUIDs
- ✅ Note the chart UUIDs for subsequent operations

## Related Tools
- `lightdash_list_spaces` - Find space UUIDs for filtering
- `lightdash_get_chart` - Get full chart details
- `lightdash_edit_chart` - Modify charts
- `lightdash_create_dashboard` - Use charts in dashboards

## Response Structure
Returns array of charts with:
- Chart UUID
- Name
- Description (if set)
- Space name and UUID
- Chart type
- Last updater
- Update timestamp

## Notes
- Returns metadata only, not full chart configs
- Use space_id to filter large chart lists
- Chart UUIDs are needed for all chart operations