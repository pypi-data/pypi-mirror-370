List of fields to sort results by. Sorting helps highlight important patterns and makes data easier to interpret.

Format: `[{"field": "<field_name>", "order": "asc|desc"}]`

Sort order:
- `asc` - Ascending order (smallest to largest, A to Z, oldest to newest)
- `desc` - Descending order (largest to smallest, Z to A, newest to oldest)

Examples:
- Highest revenue first: `[{"field": "total_revenue", "order": "desc"}]`
- Chronological order: `[{"field": "created_date", "order": "asc"}]`
- Multiple sorts: `[{"field": "region", "order": "asc"}, {"field": "revenue", "order": "desc"}]`

Best practices:
- For "top N" queries, sort the metric descending
- For time series, sort the date ascending
- For rankings, consider secondary sort for tie-breaking