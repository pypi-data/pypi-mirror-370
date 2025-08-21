List of metric field names to include in the query. Metrics are quantitative measures that can be aggregated (summed, averaged, counted, etc.).

Examples:
- `total_revenue` - Sum of order amounts
- `order_count` - Number of orders
- `average_order_value` - Average revenue per order
- `customer_lifetime_value` - Total spend per customer

Note: Provide metric names without the table prefix. The tool will automatically handle the correct field naming for Lightdash.

To discover available metrics for an explore, use:
1. `list_metrics_enhanced` - Shows all metrics across explores
2. `get_explore` - Shows metrics for a specific explore