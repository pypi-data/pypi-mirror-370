"""
Semantic catalog for Lightdash data model.
Maps business concepts to technical implementation details.
"""

from typing import Dict, List, Optional, Any
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Semantic mapping of business concepts to Lightdash explores
SEMANTIC_CATALOG = {
    "sales": {
        "explore": "orders",
        "primary_metrics": ["total_gross_revenue", "total_net_revenue"],
        "secondary_metrics": ["total_estimated_profit", "total_product_quantity_sold", "total_discount_amount"],
        "time_dimension": "event_date",
        "store_dimension": "write_key",  # For multi-store filtering
        "common_dimensions": [
            "customer_id", 
            "platform", 
            "source_name", 
            "fulfillment_status",
            "line_items_skus",  # Product SKUs
            "line_items_titles",  # Product names
            "line_items_vendors"  # Product vendors
        ],
        "product_dimensions": ["line_items_skus", "line_items_titles", "line_items_vendors"],
        "aliases": ["revenue", "income", "orders", "transactions", "earnings", "sales", "products", "sold", "items"],
        "questions": [
            "sales last X days",
            "revenue by month",
            "top customers",
            "profit margins",
            "order volume",
            "what did we sell",
            "products sold",
            "items sold",
            "what products",
            "which products"
        ]
    },
    
    "marketing": {
        "explore": "ads",
        "primary_metrics": ["total_cost", "total_impressions", "total_clicks"],
        "secondary_metrics": ["total_conversions", "avg_ctr", "avg_cost_per_click", "total_conversions_value"],
        "time_dimension": "event_date",
        "store_dimension": None,  # Ads might not have store dimension
        "common_dimensions": ["platform", "channel", "campaign_name", "ad_name", "campaign_status"],
        "aliases": ["advertising", "ads", "campaigns", "spend", "marketing spend", "ad spend"],
        "questions": [
            "ad spend last X days",
            "campaign performance",
            "cost per click",
            "impressions by channel"
        ]
    },
    
    "attribution": {
        "explore": "pixel_joined",
        "primary_metrics": ["total_attributed_revenue", "total_spend", "avg_pixel_roas"],
        "secondary_metrics": [
            "total_attributed_purchases", 
            "avg_pixel_conversion_rate",
            "total_sessions",
            "total_unique_visitors"
        ],
        "time_dimension": "event_date",
        "store_dimension": "write_key",  # Has store dimension
        "common_dimensions": ["channel", "campaign_name", "utm_source", "utm_medium", "device_type"],
        "aliases": ["roas", "attribution", "pixel", "tracking", "conversions", "performance"],
        "questions": [
            "ROAS by campaign",
            "attribution by channel",
            "conversion tracking",
            "pixel performance",
            "visitor metrics"
        ]
    },
    
    "leads": {
        "explore": "geo_reports_table",
        "primary_metrics": ["total_lead_count", "sum_total_spend", "cost_per_lead"],
        "secondary_metrics": ["total_revenue", "total_gross_profit"],
        "time_dimension": "date",
        "store_dimension": None,
        "common_dimensions": ["country", "state", "supplier_name", "buyer_name", "lead_status"],
        "aliases": ["leads", "lead gen", "geo", "geographic", "regional"],
        "questions": [
            "leads by region",
            "cost per lead",
            "lead quality",
            "geographic performance"
        ]
    }
}

# Time grain patterns
TIME_GRAINS = ["day", "week", "month", "quarter", "year"]

# Common time range patterns
TIME_PATTERNS = {
    r"last\s+(\d+)\s+(day|week|month|year)s?": "relative",
    r"yesterday": "yesterday",
    r"today": "today",
    r"this\s+(week|month|quarter|year)": "current_period",
    r"last\s+(week|month|quarter|year)": "last_period"
}


def identify_domain(question: str) -> Optional[str]:
    """
    Identify which business domain a question relates to.
    
    Args:
        question: Natural language question
        
    Returns:
        Domain key from SEMANTIC_CATALOG or None
    """
    question_lower = question.lower()
    
    # Check each domain's aliases and question patterns
    for domain, config in SEMANTIC_CATALOG.items():
        # Check aliases
        for alias in config["aliases"]:
            if alias in question_lower:
                return domain
        
        # Check question patterns
        for pattern in config.get("questions", []):
            # Remove placeholder X and check if pattern matches
            pattern_words = pattern.replace("X", "").lower().split()
            if all(word in question_lower for word in pattern_words if word not in ["by", "last"]):
                return domain
    
    # Fallback heuristics
    if any(word in question_lower for word in ["sales", "revenue", "orders", "profit", "customer"]):
        return "sales"
    elif any(word in question_lower for word in ["ad", "campaign", "marketing", "impression", "click"]):
        return "marketing"
    elif any(word in question_lower for word in ["roas", "attribution", "pixel", "conversion"]):
        return "attribution"
    elif any(word in question_lower for word in ["lead", "geo", "region", "state", "country"]):
        return "leads"
    
    return None


def parse_time_range(question: str) -> Optional[Dict[str, Any]]:
    """
    Parse time range from natural language.
    
    Args:
        question: Natural language question
        
    Returns:
        Dict with operator, value, and unit for time filtering
    """
    question_lower = question.lower()
    
    # Check for specific month/year patterns first
    month_year_pattern = r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})"
    month_match = re.search(month_year_pattern, question_lower)
    if month_match:
        month_name = month_match.group(1)
        year = month_match.group(2)
        month_map = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        month_num = month_map[month_name]
        return {
            "operator": "equals",
            "value": f"{year}-{month_num}",
            "is_month": True  # Special flag for month handling
        }
    
    # Check each time pattern
    for pattern, pattern_type in TIME_PATTERNS.items():
        match = re.search(pattern, question_lower)
        if match:
            if pattern_type == "relative":
                # "last X days/weeks/months"
                count = int(match.group(1))
                unit = match.group(2) + 's'  # Make plural
                return {
                    "operator": "inThePast",
                    "value": count,
                    "unit": unit
                }
            elif pattern_type == "yesterday":
                return {
                    "operator": "inThePast",
                    "value": 1,
                    "unit": "days"
                }
            elif pattern_type == "today":
                return {
                    "operator": "inThePast",
                    "value": 0,
                    "unit": "days"
                }
            elif pattern_type == "current_period":
                period = match.group(1)
                return {
                    "operator": f"inCurrent{period.capitalize()}",
                    "value": None
                }
            elif pattern_type == "last_period":
                period = match.group(1)
                return {
                    "operator": f"inLast{period.capitalize()}",
                    "value": None
                }
    
    # Default to last 30 days if no time specified
    return {
        "operator": "inThePast",
        "value": 30,
        "unit": "days"
    }


def determine_time_grain(question: str, time_dimension: str, time_range: Optional[Dict] = None) -> str:
    """
    Determine appropriate time grouping grain.
    
    Args:
        question: Natural language question
        time_dimension: Base time dimension field
        time_range: Parsed time range
        
    Returns:
        Time dimension with grain (e.g., "created_at_day")
    """
    question_lower = question.lower()
    
    # Explicit grain mentions
    if "daily" in question_lower or "by day" in question_lower:
        return f"{time_dimension}_day"
    elif "weekly" in question_lower or "by week" in question_lower:
        return f"{time_dimension}_week"
    elif "monthly" in question_lower or "by month" in question_lower:
        return f"{time_dimension}_month"
    elif "quarterly" in question_lower or "by quarter" in question_lower:
        return f"{time_dimension}_quarter"
    elif "yearly" in question_lower or "by year" in question_lower:
        return f"{time_dimension}_year"
    
    # Infer from time range
    if time_range and time_range.get("value"):
        value = time_range["value"]
        unit = time_range.get("unit", "days")
        
        if unit == "days":
            if value <= 7:
                return f"{time_dimension}_day"
            elif value <= 31:
                return f"{time_dimension}_day"  # Still daily for month view
            else:
                return f"{time_dimension}_week"
        elif unit == "weeks":
            if value <= 4:
                return f"{time_dimension}_week"
            else:
                return f"{time_dimension}_month"
        elif unit == "months":
            if value <= 3:
                return f"{time_dimension}_month"
            else:
                return f"{time_dimension}_month"
        else:
            return f"{time_dimension}_month"
    
    # Default to daily
    return f"{time_dimension}_day"


def select_metrics(question: str, domain: str) -> List[str]:
    """
    Select appropriate metrics based on question and domain.
    
    Args:
        question: Natural language question
        domain: Identified domain
        
    Returns:
        List of metric names
    """
    question_lower = question.lower()
    catalog_entry = SEMANTIC_CATALOG[domain]
    
    # Check for product-related questions FIRST
    product_keywords = ["what did we sell", "what sold", "which products", "what products", 
                       "products sold", "items sold", "what items", "which items"]
    
    if any(keyword in question_lower for keyword in product_keywords):
        # For product questions, focus on quantity and revenue
        available_metrics = catalog_entry["primary_metrics"] + catalog_entry.get("secondary_metrics", [])
        product_metrics = []
        
        # Add quantity sold as primary metric for product questions
        if "total_product_quantity_sold" in available_metrics:
            product_metrics.append("total_product_quantity_sold")
        
        # Add revenue if mentioned or implied
        if any(word in question_lower for word in ["revenue", "sales", "value", "amount"]):
            if "total_net_revenue" in available_metrics:
                product_metrics.append("total_net_revenue")
        
        # Return quantity sold if we have it, otherwise fall back to revenue
        if product_metrics:
            return product_metrics
        else:
            return ["total_net_revenue"] if "total_net_revenue" in available_metrics else catalog_entry["primary_metrics"][:1]
    
    # Check for specific metric keywords
    metric_keywords = {
        "profit": ["total_estimated_profit", "total_gross_profit"],
        "revenue": ["total_gross_revenue", "total_net_revenue"],
        "sales": ["total_gross_revenue", "total_net_revenue"],
        "cost": ["total_cost", "sum_total_spend"],
        "spend": ["total_cost", "total_spend", "sum_total_spend"],
        "roas": ["avg_pixel_roas", "total_attributed_revenue", "total_spend"],
        "conversion": ["total_conversions", "avg_conversion_rate", "avg_pixel_conversion_rate"],
        "clicks": ["total_clicks"],
        "impressions": ["total_impressions"],
        "leads": ["total_lead_count", "cost_per_lead"],
        "visitors": ["total_unique_visitors", "total_sessions"],
        "orders": ["total_product_quantity_sold"],
        "quantity": ["total_product_quantity_sold"],
        "units": ["total_product_quantity_sold"]
    }
    
    # Check for keyword matches
    for keyword, metrics in metric_keywords.items():
        if keyword in question_lower:
            # Filter to metrics that exist in this domain
            available_metrics = catalog_entry["primary_metrics"] + catalog_entry.get("secondary_metrics", [])
            matching_metrics = [m for m in metrics if m in available_metrics]
            if matching_metrics:
                return matching_metrics[:2]  # Return up to 2 matching metrics
    
    # Default to primary metrics
    return catalog_entry["primary_metrics"][:2]


def select_dimensions(question: str, domain: str, time_grain: Optional[str] = None) -> List[str]:
    """
    Select dimensions based on question context.
    
    Args:
        question: Natural language question
        domain: Identified domain
        time_grain: Time dimension with grain
        
    Returns:
        List of dimension names
    """
    question_lower = question.lower()
    catalog_entry = SEMANTIC_CATALOG[domain]
    dimensions = []
    
    # Check for product-related questions FIRST
    product_keywords = ["what did we sell", "what sold", "which products", "what products", 
                       "products sold", "items sold", "what items", "which items", "product sales"]
    
    if any(keyword in question_lower for keyword in product_keywords):
        # Add product dimensions
        product_dims = catalog_entry.get("product_dimensions", [])
        if product_dims:
            # Use line_items_titles as the primary product dimension
            if "line_items_titles" in product_dims:
                dimensions.append("line_items_titles")
            # Optionally add SKUs if explicitly mentioned
            if "sku" in question_lower and "line_items_skus" in product_dims:
                dimensions.append("line_items_skus")
        # Add time dimension if time period is mentioned
        if any(word in question_lower for word in ["today", "yesterday", "last", "this", "days", "week", "month"]):
            if time_grain:
                dimensions.append(time_grain)
        return dimensions
    
    # Always add time dimension if provided for non-product queries
    if time_grain:
        dimensions.append(time_grain)
    
    # Check for specific dimension requests
    dimension_keywords = {
        "by campaign": "campaign_name",
        "by channel": "channel",
        "by platform": "platform",
        "by customer": "customer_id",
        "by state": "state",
        "by region": "state",
        "by country": "country",
        "by supplier": "supplier_name",
        "by buyer": "buyer_name",
        "by source": "source_name",
        "by utm": "utm_source",
        "by device": "device_type",
        "by status": "campaign_status" if domain == "marketing" else "fulfillment_status" if domain == "sales" else "lead_status",
        "by product": "line_items_titles",
        "by sku": "line_items_skus",
        "by vendor": "line_items_vendors"
    }
    
    for keyword, dimension in dimension_keywords.items():
        if keyword in question_lower:
            # Check if dimension exists in this domain
            if dimension in catalog_entry.get("common_dimensions", []):
                dimensions.append(dimension)
            elif dimension == catalog_entry.get("store_dimension"):
                dimensions.append(dimension)
    
    return dimensions


def parse_store_context(question: str, domain: str) -> Dict[str, Any]:
    """
    Parse store/write_key requirements from question.
    
    Args:
        question: Natural language question
        domain: Identified domain
        
    Returns:
        Dict with store filtering requirements
    """
    question_lower = question.lower()
    catalog_entry = SEMANTIC_CATALOG.get(domain, {})
    store_dimension = catalog_entry.get("store_dimension")
    
    if not store_dimension:
        return {"has_stores": False}
    
    store_context = {
        "has_stores": True,
        "dimension": store_dimension,
        "filter_stores": False,
        "show_stores": False,
        "stores": []
    }
    
    # Check for store-related keywords
    if any(phrase in question_lower for phrase in ["by store", "each store", "per store", "all stores"]):
        store_context["show_stores"] = True
        
    # Check for comparison keywords
    if any(word in question_lower for word in ["compare", "versus", "vs", "between"]):
        store_context["show_stores"] = True
    
    # Note: We don't filter by specific stores as we don't have the mapping
    # The write_key values would need to be provided by configuration
    
    return store_context


def build_smart_query(question: str, config: Optional[Any] = None) -> Dict[str, Any]:
    """
    Build a complete Lightdash query from a natural language question.
    
    Args:
        question: Natural language business question
        
    Returns:
        Query configuration dict ready for lightdash_run_metric_query
    """
    # Identify domain
    domain = identify_domain(question)
    if not domain:
        raise ValueError("Could not identify data domain. Please specify: sales, marketing, attribution, or leads.")
    
    catalog_entry = SEMANTIC_CATALOG[domain]
    
    # Parse time range
    time_range = parse_time_range(question)
    
    # Determine time grain
    time_grain = determine_time_grain(question, catalog_entry["time_dimension"], time_range)
    
    # Select metrics
    metrics = select_metrics(question, domain)
    
    # Select dimensions (including time if needed)
    dimensions = select_dimensions(question, domain, time_grain)
    
    # Parse store context
    store_context = parse_store_context(question, domain)
    if store_context.get("show_stores") and store_context.get("dimension"):
        if store_context["dimension"] not in dimensions:
            dimensions.append(store_context["dimension"])
    
    # Build query - add table prefix to metrics and dimensions
    explore = catalog_entry["explore"]
    prefixed_metrics = [f"{explore}.{m}" for m in metrics]
    prefixed_dimensions = [f"{explore}.{d}" for d in dimensions]
    
    query = {
        "explore_id": explore,
        "metrics": prefixed_metrics,
        "dimensions": prefixed_dimensions,
        "filters": [],
        "sort": [],
        "limit": 500  # Need more rows to see all product combinations
    }
    
    # Add time filter
    if time_range:
        # Add table prefix to time dimension for filter
        filter_field = f"{catalog_entry['explore']}.{catalog_entry['time_dimension']}"
        filter_config = {
            "field": filter_field,
            "operator": time_range["operator"],
            "value": time_range.get("value")
        }
        # Only add unit if it exists
        if time_range.get("unit"):
            filter_config["unit"] = time_range["unit"]
        query["filters"].append(filter_config)
    
    # Add sorting
    if prefixed_dimensions:
        # Sort by time dimension first if present
        for dim in prefixed_dimensions:
            if catalog_entry["time_dimension"] in dim:
                query["sort"].append({
                    "field": dim,
                    "order": "desc"  # Most recent first
                })
                break
        
        # If no time dimension, sort by first metric
        if not query["sort"] and prefixed_metrics:
            query["sort"].append({
                "field": prefixed_metrics[0],
                "order": "desc"
            })
    
    return query