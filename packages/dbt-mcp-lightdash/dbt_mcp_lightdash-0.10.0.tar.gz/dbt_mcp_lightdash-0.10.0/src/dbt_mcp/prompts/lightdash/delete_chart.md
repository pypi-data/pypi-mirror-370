# Tool Name: lightdash_delete_chart

## Description
Delete a Lightdash chart permanently - this action cannot be undone.

## When to Use
- Removing obsolete or unused charts
- Cleaning up test charts
- Replacing charts with newer versions
- Removing duplicate charts
- Chart housekeeping and cleanup

## ⚠️ Warning
- **This action is permanent and cannot be undone**
- Charts on dashboards will be removed automatically
- No recovery option after deletion

## Parameters

### Required:
- `chart_id` (string): The UUID of the chart to delete
- `confirm` (boolean): Must be true to confirm deletion

## JSON Examples

### Example 1: Delete a specific chart
```json
{
  "chart_id": "550e8400-e29b-41d4-a716-446655440000",
  "confirm": true
}
```

### Example 2: Attempt without confirmation (will fail)
```json
{
  "chart_id": "7f4a2b8c-9e1d-4532-8abc-123456789def",
  "confirm": false
}
```

### Example 3: Delete obsolete chart
```json
{
  "chart_id": "old-revenue-chart-uuid-here",
  "confirm": true
}
```

## Common Mistakes to Avoid
- ❌ Forgetting to set confirm to true
- ❌ Using chart names instead of UUIDs
- ❌ Deleting without checking dashboard usage
- ✅ Always verify chart ID before deletion
- ✅ Check if chart is used in dashboards first

## Best Practices
1. Use `lightdash_get_chart` to verify before deleting
2. Check dashboards with `lightdash_list_dashboards`
3. Consider renaming instead of deleting if unsure
4. Create replacement chart before deleting old one

## Related Tools
- `lightdash_list_charts` - Find charts to delete
- `lightdash_get_chart` - Verify chart details
- `lightdash_get_dashboard` - Check dashboard usage
- `lightdash_edit_chart` - Rename instead of delete

## Notes
- Deletion removes chart from all dashboards
- No undo or recovery mechanism
- Confirm parameter prevents accidents