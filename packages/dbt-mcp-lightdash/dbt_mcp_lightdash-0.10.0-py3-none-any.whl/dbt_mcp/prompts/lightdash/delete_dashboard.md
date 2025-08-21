# Tool Name: lightdash_delete_dashboard

## Description
Delete a Lightdash dashboard permanently - this action cannot be undone.

## When to Use
- Removing obsolete dashboards
- Cleaning up test dashboards
- Removing duplicate dashboards
- Dashboard housekeeping
- Space cleanup and organization

## ⚠️ Warning
- **This action is permanent and cannot be undone**
- Dashboard layout and configuration will be lost
- Charts remain available (not deleted)

## Parameters

### Required:
- `dashboard_id` (string): The UUID of the dashboard to delete
- `confirm` (boolean): Must be true to confirm deletion

## JSON Examples

### Example 1: Delete a specific dashboard
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000",
  "confirm": true
}
```

### Example 2: Attempt without confirmation (will fail)
```json
{
  "dashboard_id": "9f8e7d6c-5a4b-3210-fedc-ba0987654321",
  "confirm": false
}
```

### Example 3: Delete test dashboard
```json
{
  "dashboard_id": "test-dashboard-uuid-here",
  "confirm": true
}
```

## What Gets Deleted vs Preserved
### ✅ Deleted:
- Dashboard configuration
- Tile layout and positioning
- Dashboard-level filters
- Dashboard metadata

### ✅ Preserved:
- All charts (remain in their spaces)
- Chart configurations
- Markdown content (if saved elsewhere)

## Common Mistakes to Avoid
- ❌ Forgetting to set confirm to true
- ❌ Using dashboard names instead of UUIDs
- ❌ Worrying about losing charts (they're safe)
- ✅ Always verify dashboard ID first
- ✅ Export important layouts before deletion

## Best Practices
1. Use `lightdash_get_dashboard` to verify
2. Document tile layout if needed later
3. Check view count to see usage
4. Consider renaming instead of deleting
5. Notify users before deletion

## Related Tools
- `lightdash_list_dashboards` - Find dashboards
- `lightdash_get_dashboard` - Verify details
- `lightdash_edit_dashboard` - Modify instead
- `lightdash_create_dashboard` - Recreate if needed

## Notes
- Charts are NOT deleted, only unlinked
- No recovery for dashboard layout
- Confirm parameter prevents accidents
- Consider exporting configuration first