The explore (dbt model) to query data from. An explore in Lightdash represents a dbt model that has been configured for querying and visualization.

Common explores include:
- `orders` - Order transactions and revenue data
- `customers` - Customer profiles and lifetime value
- `products` - Product catalog and performance
- `events` - User behavior and activity tracking

To find available explores, use the `list_explores` tool first. The explore_id should match the explore name exactly as returned by that tool.