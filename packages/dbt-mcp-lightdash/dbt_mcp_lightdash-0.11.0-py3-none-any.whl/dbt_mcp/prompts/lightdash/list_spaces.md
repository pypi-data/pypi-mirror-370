# Tool Name: lightdash_list_spaces

## Description
List all available spaces in the Lightdash project for organizing charts and dashboards.

## When to Use
- Discovering available spaces
- Finding where to save new charts/dashboards
- Getting space UUIDs for filtering
- Understanding project organization
- Choosing spaces for chart creation

## Parameters
None - this tool takes no parameters

## JSON Examples

### Example 1: List all spaces
```json
{}
```

### Example 2: Get spaces for chart creation
```json
{}
```

### Example 3: Find available spaces
```json
{}
```

## Common Mistakes to Avoid
- ❌ Passing any parameters - this tool takes none
- ❌ Expecting detailed permissions info
- ✅ Note space UUIDs for use in other tools
- ✅ Use "Shared" space as default if unsure

## Related Tools
- `lightdash_list_charts` - Filter charts by space
- `lightdash_list_dashboards` - Filter dashboards by space
- `lightdash_create_chart` - Specify space for new charts
- `lightdash_create_dashboard` - Specify space for dashboards

## Response Structure
Returns array of spaces with:
- Space UUID
- Name
- Is private flag
- Dashboard count
- Chart count
- Access count

## Notes
- Space UUIDs are required for filtering and creation
- "Shared" space is typically available to all users
- Private spaces may have restricted access