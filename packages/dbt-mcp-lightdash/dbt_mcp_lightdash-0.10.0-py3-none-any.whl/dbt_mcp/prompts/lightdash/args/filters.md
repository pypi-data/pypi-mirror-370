List of filter conditions to apply to the query. Filters narrow down the results to specific subsets of data.

Format: `[{"field": "<field_name>", "operator": "<operator>", "value": <value>}]`

Common operators:
- `equals` / `notEquals` - Exact match
- `contains` / `notContains` - Text search
- `startsWith` / `endsWith` - Text patterns
- `greaterThan` / `lessThan` - Numeric comparison
- `greaterThanOrEqual` / `lessThanOrEqual` - Inclusive comparison
- `inThePast` / `inTheNext` - Relative date filters (requires `unit`)
- `between` - Range filter (requires array value)
- `isNull` / `notNull` - Null checks

Examples:
- Status filter: `{"field": "status", "operator": "equals", "value": "completed"}`
- Date range: `{"field": "created_date", "operator": "inThePast", "value": 30, "unit": "days"}`
- Revenue threshold: `{"field": "total_revenue", "operator": "greaterThan", "value": 1000}`
- Multiple values: `{"field": "region", "operator": "equals", "value": ["North", "South"]}`