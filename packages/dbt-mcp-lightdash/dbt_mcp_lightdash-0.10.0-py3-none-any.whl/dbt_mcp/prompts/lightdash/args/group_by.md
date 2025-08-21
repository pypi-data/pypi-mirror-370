List of dimensions to group results by. Each group by item should specify the field and optionally a time grain for date dimensions.

Format: `[{"field": "<dimension_name>", "grain": "<time_grain>"}]`

Time grains for date dimensions:
- `day` - Daily grouping
- `week` - Weekly grouping  
- `month` - Monthly grouping
- `quarter` - Quarterly grouping
- `year` - Yearly grouping

Examples:
- Group by category: `[{"field": "product_category"}]`
- Group by month: `[{"field": "created_date", "grain": "month"}]`
- Group by multiple: `[{"field": "region"}, {"field": "created_date", "grain": "quarter"}]`

Note: You can only group by dimensions that exist in the selected explore.