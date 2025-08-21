# Tool Name: lightdash_create_dashboard

## Description
Create a new dashboard in Lightdash with charts and markdown tiles in a grid layout.

## When to Use
- Creating new dashboards from scratch
- Organizing multiple charts together
- Building executive or team dashboards
- Creating presentation-ready views
- Setting up monitoring dashboards

## Parameters

### Required:
- `name` (string): Dashboard name
- `space_id` (string): Space UUID where dashboard will be created

### Optional:
- `description` (string): Dashboard description
- `tiles` (array): Array of tile configurations
- `layout` (string): Layout preset: "auto", "single_column", "two_column"

## JSON Examples

### Example 1: Empty dashboard
```json
{
  "name": "Sales Dashboard",
  "space_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "Monthly sales performance metrics"
}
```

### Example 2: Dashboard with single chart
```json
{
  "name": "Revenue Overview",
  "space_id": "550e8400-e29b-41d4-a716-446655440000",
  "tiles": [
    {
      "type": "saved_chart",
      "saved_chart_uuid": "abc123-chart-uuid",
      "properties": {
        "title": "Monthly Revenue"
      }
    }
  ]
}
```

### Example 3: Dashboard with multiple charts (auto layout)
```json
{
  "name": "Executive Dashboard",
  "space_id": "exec-space-uuid",
  "description": "Key metrics for leadership team",
  "layout": "auto",
  "tiles": [
    {
      "type": "saved_chart",
      "saved_chart_uuid": "revenue-chart-uuid"
    },
    {
      "type": "saved_chart", 
      "saved_chart_uuid": "customer-chart-uuid"
    },
    {
      "type": "saved_chart",
      "saved_chart_uuid": "growth-chart-uuid"
    }
  ]
}
```

### Example 4: Dashboard with markdown and charts
```json
{
  "name": "Team Performance",
  "space_id": "team-space-uuid",
  "tiles": [
    {
      "type": "markdown",
      "properties": {
        "title": "Overview",
        "content": "## Q4 Performance\n\nKey metrics for the quarter."
      }
    },
    {
      "type": "saved_chart",
      "saved_chart_uuid": "sales-by-rep-uuid"
    },
    {
      "type": "saved_chart",
      "saved_chart_uuid": "pipeline-uuid"
    }
  ],
  "layout": "single_column"
}
```

### Example 5: Dashboard with custom positioning
```json
{
  "name": "Custom Layout Dashboard",
  "space_id": "550e8400-e29b-41d4-a716-446655440000",
  "tiles": [
    {
      "type": "saved_chart",
      "saved_chart_uuid": "main-kpi-uuid",
      "x": 0,
      "y": 0,
      "w": 12,
      "h": 4
    },
    {
      "type": "saved_chart",
      "saved_chart_uuid": "trend-chart-uuid",
      "x": 0,
      "y": 4,
      "w": 6,
      "h": 6
    },
    {
      "type": "saved_chart",
      "saved_chart_uuid": "breakdown-chart-uuid",
      "x": 6,
      "y": 4,
      "w": 6,
      "h": 6
    }
  ]
}
```

## Tile Structure
- `type`: "saved_chart" or "markdown"
- `saved_chart_uuid`: Required for chart tiles
- `properties`: Optional title/content overrides
- `x`, `y`, `w`, `h`: Grid position (0-11 for x, any for y, 1-12 for width)

## Layout Options
- `auto`: Automatic tile arrangement
- `single_column`: Stack tiles vertically
- `two_column`: Two-column grid
- Custom: Specify x, y, w, h for each tile

## Common Mistakes to Avoid
- ❌ Using chart names instead of UUIDs
- ❌ Creating charts within dashboard creation
- ❌ Using non-existent space IDs
- ✅ Create charts first, then add to dashboard
- ✅ Use `lightdash_list_charts` to find UUIDs

## Related Tools
- `lightdash_list_spaces` - Find space UUIDs
- `lightdash_list_charts` - Get chart UUIDs
- `lightdash_create_chart` - Create charts first
- `lightdash_edit_dashboard` - Modify after creation
- `lightdash_get_embed_url` - Embed the dashboard

## Notes
- Charts must exist before adding to dashboards
- Grid is 12 columns wide
- Use layout presets for quick setup
- Markdown tiles support full markdown syntax