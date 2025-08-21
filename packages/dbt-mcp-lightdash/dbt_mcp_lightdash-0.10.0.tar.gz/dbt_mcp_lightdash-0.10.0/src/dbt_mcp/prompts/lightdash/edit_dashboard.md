# Tool Name: lightdash_edit_dashboard

## Description
Edit an existing Lightdash dashboard by adding/removing charts, renaming, or reorganizing tiles.

## When to Use
- Adding one or more charts to an existing dashboard
- Removing unwanted tiles from a dashboard
- Renaming or updating dashboard metadata
- Reorganizing dashboard layout and tile positions
- Adding markdown tiles for documentation

## Parameters

### Required:
- `dashboard_id` (string): UUID of the dashboard to edit

### Optional:
- `name` (string): New name for the dashboard
- `description` (string): New description for the dashboard
- `add_chart_ids` (array): List of chart UUIDs to add to the dashboard
- `remove_tile_indices` (array): Indices of tiles to remove (0-based indexing)
- `reorder_tiles` (array): New positions/sizes for existing tiles
- `add_markdown` (object): Markdown tile to add with content and position

## JSON Examples

### Example 1: Add a single chart to dashboard
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000",
  "add_chart_ids": ["7c9e6679-7425-40de-944b-e07fc1f90ae7"]
}
```

### Example 2: Add multiple charts to dashboard
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000",
  "add_chart_ids": [
    "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "550e8400-e29b-41d4-a716-446655440001",
    "123e4567-e89b-12d3-a456-426614174000"
  ]
}
```

### Example 3: Rename dashboard and add charts
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q4 2024 Sales Performance Dashboard",
  "description": "Comprehensive view of Q4 sales metrics and KPIs",
  "add_chart_ids": ["7c9e6679-7425-40de-944b-e07fc1f90ae7"]
}
```

### Example 4: Remove specific tiles from dashboard
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000",
  "remove_tile_indices": [0, 2, 5]
}
```

### Example 5: Reorganize dashboard layout
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000",
  "reorder_tiles": [
    {"index": 0, "x": 0, "y": 0, "w": 12, "h": 4},
    {"index": 1, "x": 0, "y": 4, "w": 6, "h": 4},
    {"index": 2, "x": 6, "y": 4, "w": 6, "h": 4}
  ]
}
```

### Example 6: Add markdown documentation tile
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000",
  "add_markdown": {
    "content": "## Key Metrics\n- **Revenue**: Total sales for the period\n- **Orders**: Number of completed orders\n- **AOV**: Average order value",
    "x": 0,
    "y": 0,
    "w": 4,
    "h": 3
  }
}
```

### Example 7: Complex update - remove, add, and reorganize
```json
{
  "dashboard_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Reorganized Sales Dashboard",
  "remove_tile_indices": [3, 4],
  "add_chart_ids": [
    "new-revenue-chart-uuid",
    "new-customer-chart-uuid"
  ],
  "reorder_tiles": [
    {"index": 0, "x": 0, "y": 0, "w": 12, "h": 4}
  ]
}
```

## Common Mistakes to Avoid
- ❌ Using chart names instead of chart UUIDs - always use the UUID
- ❌ Using 1-based indexing for tiles - use 0-based indexing (first tile is index 0)
- ❌ Passing a single chart ID as a string - always use an array even for one chart
- ❌ Forgetting that remove operations happen before reorder operations
- ✅ Get chart UUIDs using `lightdash_list_charts` first
- ✅ Use `lightdash_get_dashboard` to see current tile indices before removing

## Related Tools
- `lightdash_list_charts` - Use this to find chart UUIDs before adding them
- `lightdash_get_dashboard` - Use this to see current dashboard structure and tile indices
- `lightdash_create_dashboard` - Use this for creating new dashboards instead of editing
- `lightdash_create_chart` - Create new charts before adding them to dashboards

## Notes
- New charts are automatically positioned in a 2-column layout below existing content
- The grid system uses 12 columns total width
- Standard tile sizes: charts (6x4), markdown (6x2), full-width (12x4)
- All operations are applied in order: remove tiles → add charts → reorder tiles