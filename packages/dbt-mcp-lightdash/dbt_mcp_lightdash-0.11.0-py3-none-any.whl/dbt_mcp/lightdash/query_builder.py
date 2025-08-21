"""
Dynamic query builder for Lightdash.
Uses progressive discovery pattern - no hardcoded mappings.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

from dbt_mcp.semantic_layer.levenshtein import get_closest_words, get_misspellings

logger = logging.getLogger(__name__)


def parse_time_filter(question: str) -> Optional[Dict[str, Any]]:
    """
    Parse time-related phrases from natural language.
    Returns filter configuration for Lightdash.
    """
    question_lower = question.lower()
    
    # Common time patterns
    patterns = [
        (r"last (\d+) days?", lambda m: {"operator": "inThePast", "value": int(m.group(1)), "unit": "days"}),
        (r"last (\d+) weeks?", lambda m: {"operator": "inThePast", "value": int(m.group(1)), "unit": "weeks"}),
        (r"last (\d+) months?", lambda m: {"operator": "inThePast", "value": int(m.group(1)), "unit": "months"}),
        (r"last (\d+) years?", lambda m: {"operator": "inThePast", "value": int(m.group(1)), "unit": "years"}),
        (r"yesterday", lambda m: {"operator": "inThePast", "value": 1, "unit": "days"}),
        (r"today", lambda m: {"operator": "inThePast", "value": 0, "unit": "days"}),
        (r"this week", lambda m: {"operator": "inCurrentWeek"}),
        (r"this month", lambda m: {"operator": "inCurrentMonth"}),
        (r"this quarter", lambda m: {"operator": "inCurrentQuarter"}),
        (r"this year", lambda m: {"operator": "inCurrentYear"}),
        (r"last week", lambda m: {"operator": "inLastWeek"}),
        (r"last month", lambda m: {"operator": "inLastMonth"}),
        (r"last quarter", lambda m: {"operator": "inLastQuarter"}),
        (r"last year", lambda m: {"operator": "inLastYear"}),
    ]
    
    for pattern, builder in patterns:
        match = re.search(pattern, question_lower)
        if match:
            return builder(match)
    
    return None


def find_time_dimension(dimensions: List[Dict[str, Any]]) -> Optional[str]:
    """
    Find the most appropriate time dimension from available dimensions.
    Prioritizes: event_date > created_at > date > any dimension with 'date' in name.
    """
    # Priority order for time dimensions
    priority_names = ["event_date", "created_at", "date", "order_date", "transaction_date"]
    
    # First, let's see what dimensions we have
    all_dim_names = [d["name"] for d in dimensions]
    logger.debug(f"Available dimensions: {all_dim_names}")
    
    # Check for date/time dimensions - be more flexible with type checking
    date_dims = []
    for d in dimensions:
        dim_type = d.get("type", "").lower()
        dim_name = d["name"].lower()
        # Check if it's a date type OR has date/time in the name
        if dim_type in ["date", "timestamp", "time"] or "date" in dim_name or "time" in dim_name:
            date_dims.append(d["name"])
    
    logger.debug(f"Date/time dimensions found: {date_dims}")
    
    # Check priority names first
    for priority in priority_names:
        if priority in all_dim_names:
            logger.debug(f"Found priority time dimension: {priority}")
            return priority
    
    # Fallback to any dimension with 'date' or 'time' in the name
    for dim_name in all_dim_names:
        if "date" in dim_name.lower() or "time" in dim_name.lower():
            logger.debug(f"Found time dimension by name match: {dim_name}")
            return dim_name
    
    # Last resort - return None if no time dimension found
    logger.debug("No time dimension found")
    return None


def suggest_metrics(question: str, available_metrics: List[Dict[str, Any]]) -> List[str]:
    """
    Suggest metrics based on keywords in the question.
    Uses fuzzy matching to handle typos and variations.
    """
    question_lower = question.lower()
    suggested = []
    metric_names = [m["name"] for m in available_metrics]
    
    # Keyword to metric patterns
    keyword_patterns = {
        "revenue": ["revenue", "sales", "income"],
        "profit": ["profit", "margin", "earnings"],
        "cost": ["cost", "spend", "expense"],
        "quantity": ["quantity", "count", "number", "amount"],
        "customer": ["customer", "client", "user"],
        "order": ["order", "transaction", "purchase"],
        "product": ["product", "item", "sku"],
        "conversion": ["conversion", "rate"],
        "click": ["click", "ctr"],
        "impression": ["impression", "view"],
        "lead": ["lead", "prospect"],
        "roas": ["roas", "return on ad"],
        "attribution": ["attribution", "last click", "first click"],
    }
    
    # Check each keyword pattern
    for keyword, patterns in keyword_patterns.items():
        if any(p in question_lower for p in patterns):
            # Find metrics that match this pattern
            for metric in available_metrics:
                metric_name = metric["name"].lower()
                metric_label = metric.get("label", "").lower()
                metric_desc = metric.get("description", "").lower()
                
                if any(p in metric_name or p in metric_label or p in metric_desc for p in patterns):
                    if metric["name"] not in suggested:
                        suggested.append(metric["name"])
    
    # If no matches, try fuzzy matching on question words
    if not suggested:
        words = question_lower.split()
        for word in words:
            if len(word) > 3:  # Skip short words
                closest = get_closest_words(word, metric_names, top_k=2, threshold=2)
                suggested.extend([m for m in closest if m not in suggested])
    
    # Default to common aggregation metrics if nothing found
    if not suggested:
        for metric in available_metrics:
            if any(prefix in metric["name"].lower() for prefix in ["total", "sum", "avg", "count"]):
                suggested.append(metric["name"])
                if len(suggested) >= 2:
                    break
    
    return suggested[:3]  # Return top 3 suggestions


def suggest_dimensions(question: str, available_dimensions: List[Dict[str, Any]], 
                       metrics_selected: List[str]) -> List[str]:
    """
    Suggest dimensions based on keywords in the question.
    """
    question_lower = question.lower()
    suggested = []
    
    # Keywords that indicate grouping
    grouping_keywords = {
        "by": True,
        "per": True,
        "each": True,
        "group": True,
        "breakdown": True,
        "split": True,
    }
    
    # Find what comes after grouping keywords
    for keyword in grouping_keywords:
        pattern = rf"{keyword}\s+(\w+)"
        matches = re.findall(pattern, question_lower)
        for match in matches:
            # Find dimensions that match this word
            for dim in available_dimensions:
                dim_name = dim["name"].lower()
                dim_label = dim.get("label", "").lower()
                
                if match in dim_name or match in dim_label:
                    if dim["name"] not in suggested:
                        suggested.append(dim["name"])
    
    # Common dimension patterns
    dimension_patterns = {
        "campaign": ["campaign"],
        "channel": ["channel"],
        "platform": ["platform"],
        "customer": ["customer"],
        "product": ["product", "item", "sku", "line_items", "sold", "sell"],
        "category": ["category"],
        "region": ["region", "country", "state", "city"],
        "status": ["status"],
        "source": ["source"],
        "device": ["device"],
        "vendor": ["vendor"],
    }
    
    for keyword, patterns in dimension_patterns.items():
        if any(p in question_lower for p in patterns):
            for dim in available_dimensions:
                dim_name = dim["name"].lower()
                dim_label = dim.get("label", "").lower()
                # Check both name and label for pattern matches
                if any(p in dim_name or p in dim_label for p in patterns):
                    if dim["name"] not in suggested:
                        suggested.append(dim["name"])
                # Special case for "what did we sell" - include line_items fields
                if keyword == "product" and "line_items" in dim_name:
                    if dim["name"] not in suggested:
                        suggested.append(dim["name"])
    
    return suggested


def build_query_from_question(
    question: str,
    explore_name: str,
    available_metrics: List[Dict[str, Any]],
    available_dimensions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build a Lightdash query from natural language question and available fields.
    No hardcoded mappings - everything is discovered dynamically.
    """
    
    # Parse time filter
    time_filter = parse_time_filter(question)
    
    # Find time dimension if we have a time filter
    time_dimension = None
    if time_filter:
        time_dimension = find_time_dimension(available_dimensions)
    
    # Suggest metrics based on question
    suggested_metrics = suggest_metrics(question, available_metrics)
    if not suggested_metrics and available_metrics:
        # Default to first available metric
        suggested_metrics = [available_metrics[0]["name"]]
    
    # Suggest dimensions based on question
    suggested_dimensions = suggest_dimensions(question, available_dimensions, suggested_metrics)
    
    # Add time dimension if we have time filter
    if time_dimension and time_filter:
        # For now, just add the base time dimension without grain suffix
        # Lightdash handles time grains differently
        if time_dimension not in suggested_dimensions:
            suggested_dimensions.insert(0, time_dimension)
    
    # Build the query
    # Note: Lightdash uses underscore notation for field names, not dots
    query = {
        "explore_id": explore_name,
        "metrics": [f"{explore_name}_{m}" for m in suggested_metrics],
        "dimensions": [f"{explore_name}_{d}" for d in suggested_dimensions],
        "filters": [],
        "sort": [],
        "limit": 500
    }
    
    # Add time filter if present
    if time_filter and time_dimension:
        filter_config = {
            "field": f"{explore_name}_{time_dimension}",
            "operator": time_filter["operator"],
            "value": time_filter.get("value")
        }
        if time_filter.get("unit"):
            filter_config["unit"] = time_filter["unit"]
        query["filters"].append(filter_config)
    
    # Add sorting
    if suggested_dimensions:
        # Sort by time dimension first if present
        for dim in suggested_dimensions:
            if time_dimension and time_dimension in dim:
                query["sort"].append({
                    "field": f"{explore_name}_{dim}",
                    "order": "desc"
                })
                break
    
    # Otherwise sort by first metric
    if not query["sort"] and suggested_metrics:
        query["sort"].append({
            "field": f"{explore_name}_{suggested_metrics[0]}",
            "order": "desc"
        })
    
    return query


def validate_and_suggest_fields(
    requested_fields: List[str],
    available_fields: List[str],
    field_type: str = "field"
) -> Tuple[List[str], List[str]]:
    """
    Validate requested fields against available fields.
    Returns (valid_fields, suggestions_for_invalid).
    """
    valid = []
    suggestions = []
    
    for field in requested_fields:
        if field in available_fields:
            valid.append(field)
        else:
            # Find similar fields
            closest = get_closest_words(field, available_fields, top_k=3, threshold=3)
            if closest:
                suggestions.append(f"{field} → Did you mean: {', '.join(closest)}?")
            else:
                suggestions.append(f"{field} → No similar {field_type} found")
    
    return valid, suggestions