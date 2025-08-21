# Tool Name: lightdash_edit_chart

## Description
Edit an existing Lightdash chart - **ONLY name and description can be updated**.

## When to Use
- Renaming charts for clarity
- Updating chart descriptions
- Fixing typos in chart metadata
- Improving chart documentation

## ⚠️ Important Limitation
**Only metadata (name/description) can be updated. To change queries, create a new chart.**

## Parameters

### Required:
- `chart_id` (string): The UUID of the chart to edit

### At least one of:
- `name` (string): New chart name
- `description` (string): New chart description

## JSON Examples

### Example 1: Update chart name
```json
{
  "chart_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Monthly Revenue Trend - 2024"
}
```

### Example 2: Update chart description
```json
{
  "chart_id": "7f4a2b8c-9e1d-4532-8abc-123456789def",
  "description": "Shows total revenue by month with year-over-year comparison. Updated for Q4 reporting."
}
```

### Example 3: Update both name and description
```json
{
  "chart_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Customer Lifetime Value by Segment",
  "description": "CLV breakdown by customer segment, filtered for active customers only"
}
```

## What This Tool CANNOT Do
❌ Change metrics or dimensions
❌ Modify filters or date ranges
❌ Update sort order
❌ Change visualization type
❌ Alter grouping or aggregations

## If You Need Query Changes
To modify the actual query, you must:
1. Use `lightdash_get_chart` to see current config
2. Use `lightdash_create_chart` with modified parameters
3. Use `lightdash_delete_chart` to remove the old one (optional)
4. Update any dashboards to use the new chart

## Common Mistakes to Avoid
- ❌ Trying to update query parameters
- ❌ Attempting to change metrics/dimensions
- ❌ Using chart names instead of UUIDs
- ✅ Only use for name/description updates
- ✅ Create new charts for query changes

## Related Tools
- `lightdash_get_chart` - View current configuration
- `lightdash_create_chart` - Create new chart with changes
- `lightdash_list_charts` - Find chart UUIDs
- `lightdash_delete_chart` - Remove old chart after creating new one

## Notes
- Lightdash API limitation, not a tool limitation
- Consider versioning in chart names (e.g., "Revenue v2")
- Update dashboards after creating replacement charts