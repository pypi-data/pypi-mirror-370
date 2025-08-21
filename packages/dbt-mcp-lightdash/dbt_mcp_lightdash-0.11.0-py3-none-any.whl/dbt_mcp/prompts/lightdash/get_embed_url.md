# Tool Name: lightdash_get_embed_url

## Description
Generate an embed URL for a Lightdash dashboard that can be displayed in an iframe (Note: Only dashboards can be embedded, not individual charts).

## When to Use
- Embedding Lightdash dashboards in other applications
- Creating shareable dashboard views with time-limited access
- Displaying dashboards in LibreChat using HTML artifacts
- Generating secure, JWT-based embed URLs

## Parameters

### Required:
- `resource_uuid` (string): The UUID of the dashboard to embed

### Optional:
- `resource_type` (string): Must be "dashboard" (charts cannot be embedded)
- `expires_in` (string): JWT expiration time (default: "8h")
- `dashboard_filters_interactivity` (object): Dashboard filter settings
- `can_export_csv` (boolean): Allow CSV export (default: false)
- `can_export_images` (boolean): Allow image export (default: false)
- `return_markdown` (boolean): Return markdown directive (default: true)
- `raw_directive` (boolean): Return only directive without text (default: false)
- `height` (integer): Height in pixels for the embed

## JSON Examples

### Example 1: Basic dashboard embed
```json
{
  "resource_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "resource_type": "dashboard"
}
```

### Example 2: Dashboard with custom expiration
```json
{
  "resource_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "resource_type": "dashboard",
  "expires_in": "24h"
}
```

### Example 3: Dashboard with export permissions
```json
{
  "resource_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "resource_type": "dashboard",
  "can_export_csv": true,
  "can_export_images": true
}
```

### Example 4: Dashboard with custom height
```json
{
  "resource_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "resource_type": "dashboard",
  "height": 800,
  "expires_in": "12h"
}
```

### Example 5: Get raw directive only
```json
{
  "resource_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "resource_type": "dashboard",
  "raw_directive": true,
  "return_markdown": true
}
```

## Common Mistakes to Avoid
- ❌ Trying to embed individual charts - only dashboards are supported
- ❌ Using chart UUIDs - the Lightdash API only supports dashboard embedding
- ❌ Setting resource_type to "chart" - this will cause an error
- ✅ Always use dashboard UUIDs from `lightdash_list_dashboards`
- ✅ Create a dashboard first if you want to embed charts

## Related Tools
- `lightdash_list_dashboards` - Find dashboard UUIDs to embed
- `lightdash_create_dashboard` - Create a dashboard to embed
- `lightdash_edit_dashboard` - Add charts to a dashboard before embedding

## Notes
- The tool returns instructions for creating an HTML artifact in LibreChat
- JWT tokens are generated server-side for security
- Embed URLs include the project UUID and JWT token
- Only dashboards can be embedded due to Lightdash API limitations
- Charts must be added to a dashboard first before they can be embedded