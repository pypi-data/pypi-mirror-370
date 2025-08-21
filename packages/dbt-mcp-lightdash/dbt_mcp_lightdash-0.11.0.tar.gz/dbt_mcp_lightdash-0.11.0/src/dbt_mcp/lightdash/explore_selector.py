"""
Intelligent explore selection based on query intent.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# Explore metadata - describes what each explore is best for
EXPLORE_METADATA = {
    "orders": {
        "description": "Order-level data with revenue, profit, and customer information",
        "keywords": ["order", "revenue", "profit", "sales", "customer", "product"],
        "metrics": ["revenue", "profit", "order_count", "average_order_value"],
        "use_for": ["sales analysis", "revenue reporting", "customer analytics", "product sales"]
    },
    "ads": {
        "description": "Advertising campaign data with impressions, clicks, and spend",
        "keywords": ["campaign", "impression", "click", "ctr", "spend", "cost"],
        "metrics": ["impressions", "clicks", "spend", "ctr", "cpc"],
        "use_for": ["campaign performance", "ad spend analysis", "click-through rates"]
    },
    "pixel_joined": {
        "description": "Attribution and conversion data with ROAS and multi-touch attribution",
        "keywords": ["roas", "attribution", "conversion", "pixel", "last click", "first click", "tracking"],
        "metrics": ["roas", "conversions", "attributed_revenue", "conversion_rate"],
        "use_for": ["ROAS analysis", "attribution modeling", "conversion tracking", "performance marketing"],
        "required_filters": {
            "attribution_mode": ["last_click", "first_click", "linear", "time_decay", "position_based"],
            "attribution_window": ["1_day", "7_day", "14_day", "30_day"],
            "note": "IMPORTANT: Always filter by attribution_mode and attribution_window to avoid inflated numbers from aggregating all attribution models"
        }
    },
    "geo_reports_table": {
        "description": "Geographic and lead generation data by region",
        "keywords": ["geo", "geographic", "region", "state", "country", "lead", "location"],
        "metrics": ["leads", "lead_value", "cost_per_lead"],
        "use_for": ["geographic analysis", "lead generation", "regional performance"]
    }
}


def score_explore_for_question(explore_name: str, question: str) -> int:
    """
    Score how well an explore matches a question.
    Higher score = better match.
    """
    question_lower = question.lower()
    score = 0
    
    if explore_name not in EXPLORE_METADATA:
        return 0
    
    metadata = EXPLORE_METADATA[explore_name]
    
    # Check for exact explore name match
    if explore_name in question_lower:
        score += 10
    
    # Check keywords (weighted heavily)
    for keyword in metadata["keywords"]:
        if keyword in question_lower:
            score += 5
            # Special boost for specific terms
            if keyword in ["roas", "attribution", "conversion"] and explore_name == "pixel_joined":
                score += 10  # Strong signal for pixel_joined
            elif keyword in ["revenue", "profit", "sales"] and explore_name == "orders":
                score += 3
    
    # Check use cases
    for use_case in metadata["use_for"]:
        if any(word in question_lower for word in use_case.split()):
            score += 2
    
    # Check metric names
    for metric in metadata["metrics"]:
        if metric in question_lower:
            score += 4
    
    # Penalty for wrong explore
    # If question mentions ROAS/attribution but explore is not pixel_joined
    if any(term in question_lower for term in ["roas", "attribution", "last click", "first click"]):
        if explore_name != "pixel_joined":
            score -= 10
    
    # If question mentions products/what we sold but explore is not orders
    if any(term in question_lower for term in ["product", "sold", "sell", "what did we"]):
        if explore_name != "orders":
            score -= 5
    
    return score


def select_best_explore(explores: List[Dict[str, Any]], question: str) -> str:
    """
    Select the best explore for a given question.
    """
    explore_scores = {}
    
    for explore in explores:
        explore_name = explore['name']
        score = score_explore_for_question(explore_name, question)
        explore_scores[explore_name] = score
        logger.debug(f"Explore '{explore_name}' scored {score} for question: {question[:50]}...")
    
    # Sort by score and get the best one
    best_explore = max(explore_scores, key=explore_scores.get)
    best_score = explore_scores[best_explore]
    
    # Log the selection
    logger.info(f"Selected explore '{best_explore}' (score: {best_score}) for question")
    
    # If no good match found (all scores <= 0), default to first explore
    if best_score <= 0:
        logger.warning("No good explore match found, using first available")
        return explores[0]['name'] if explores else None
    
    return best_explore


def get_explore_description(explore_name: str) -> str:
    """
    Get a human-readable description of what an explore contains.
    """
    if explore_name in EXPLORE_METADATA:
        return EXPLORE_METADATA[explore_name]["description"]
    return f"Data from {explore_name} table"