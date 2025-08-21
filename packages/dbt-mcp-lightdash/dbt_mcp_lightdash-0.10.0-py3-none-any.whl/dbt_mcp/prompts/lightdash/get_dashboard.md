# Tool Name: lightdash_get_dashboard

## Description
Get detailed information about a specific Lightdash dashboard including tiles, layout, and metadata.

## When to Use
- Viewing dashboard contents and structure
- Understanding which charts are on a dashboard
- Getting dashboard details before editing
- Checking dashboard layout configuration
- Finding markdown tiles and their content

## Parameters

### Required:
- `dashboard_id` (string): The UUID of the dashboard to retrieve

## JSON Examples

### Example 1: Basic dashboard retrieval
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Example 2: Get dashboard for editing
```json
{
  "dashboard_id": "9f8e7d6c-5a4b-3210-fedc-ba0987654321"
}
```

### Example 3: Check dashboard contents
```json
{
  "dashboard_id": "11223344-5566-7788-99aa-bbccddeeff00"
}
```

## Common Mistakes to Avoid
- ❌ Using dashboard names instead of UUIDs
- ❌ Confusing dashboard IDs with chart IDs
- ✅ Use `lightdash_list_dashboards` to find the correct UUID
- ✅ Note which tiles contain charts vs markdown

## Related Tools
- `lightdash_list_dashboards` - Find dashboard UUIDs
- `lightdash_edit_dashboard` - Modify dashboard after viewing
- `lightdash_delete_dashboard` - Remove dashboard if needed
- `lightdash_get_embed_url` - Generate embed URL for dashboard

## Response Structure
The tool returns:
- Dashboard name and description
- Space location
- Tiles array with:
  - Chart tiles (UUID, position, size)
  - Markdown tiles (content, position, size)
- Layout configuration
- Creator and update info
- Dashboard-level filters

## Notes
- Dashboard IDs are UUIDs, not names
- Tiles have x, y, h, w properties for grid layout
- Each tile can be either a chart or markdown