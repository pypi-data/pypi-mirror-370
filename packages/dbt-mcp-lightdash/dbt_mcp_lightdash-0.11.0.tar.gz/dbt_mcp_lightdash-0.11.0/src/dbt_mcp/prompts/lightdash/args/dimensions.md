List of dimension field names available for grouping, filtering, or display. Dimensions are categorical or time-based attributes that provide context to metrics.

Common dimension types:
- **Time dimensions**: `created_date`, `order_date`, `updated_at`
- **Geographic**: `region`, `country`, `city`, `store_location`
- **Categories**: `product_category`, `customer_segment`, `channel`
- **Identifiers**: `customer_name`, `product_id`, `order_status`

Dimensions are used to:
- Break down metrics (group by)
- Filter results (where conditions)
- Add context to the data

Note: Provide dimension names without the table prefix. Use `get_explore` to see all available dimensions for a specific explore.