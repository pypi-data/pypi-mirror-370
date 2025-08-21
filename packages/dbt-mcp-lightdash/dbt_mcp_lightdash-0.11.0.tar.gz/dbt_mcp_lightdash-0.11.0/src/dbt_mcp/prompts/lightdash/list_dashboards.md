# Tool Name: lightdash_list_dashboards

## Description
List all dashboards in the Lightdash project with metadata and optional space filtering.

## When to Use
- Discovering available dashboards
- Finding dashboards in a specific space
- Getting dashboard UUIDs for operations
- Understanding dashboard organization
- Preparing to embed dashboards

## Parameters

### Optional:
- `space_id` (string): Filter dashboards by space UUID

## JSON Examples

### Example 1: List all dashboards
```json
{}
```

### Example 2: List dashboards in a specific space
```json
{
  "space_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Example 3: Find executive dashboards
```json
{
  "space_id": "exec-space-uuid-here"
}
```

## Common Mistakes to Avoid
- ❌ Using space names instead of UUIDs
- ❌ Expecting dashboard content (use get_dashboard for details)
- ✅ Use `lightdash_list_spaces` to find space UUIDs
- ✅ Note dashboard UUIDs for embedding or editing

## Related Tools
- `lightdash_list_spaces` - Find space UUIDs for filtering
- `lightdash_get_dashboard` - Get full dashboard details
- `lightdash_edit_dashboard` - Modify dashboards
- `lightdash_get_embed_url` - Generate embed URLs

## Response Structure
Returns array of dashboards with:
- Dashboard UUID
- Name
- Description (if set)
- Space name and UUID
- Tile count
- View count
- Last updater
- Update timestamp

## Notes
- Returns metadata only, not full configurations
- Tile count shows number of charts/markdown blocks
- Dashboard UUIDs are required for all operations