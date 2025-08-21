"""
DSPy-powered field selector for dynamic schema understanding.
Hybrid approach that learns to select fields based on natural language questions.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import json

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    logging.warning("DSPy not installed. Smart field selection will fall back to static rules.")

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient

logger = logging.getLogger(__name__)


if DSPY_AVAILABLE:
    class FieldSelectionSignature(dspy.Signature):
        """DSPy signature for selecting fields from available schema."""
        
        question = dspy.InputField(desc="Natural language question from user")
        available_metrics = dspy.InputField(desc="List of available metrics with descriptions")
        available_dimensions = dspy.InputField(desc="List of available dimensions with descriptions")
        
        selected_metrics = dspy.OutputField(desc="List of metric names to use")
        selected_dimensions = dspy.OutputField(desc="List of dimension names to use")
        reasoning = dspy.OutputField(desc="Explanation of why these fields were selected")
else:
    class FieldSelectionSignature:
        """Dummy signature when DSPy is not available."""
        pass


class SmartFieldSelector:
    """
    Hybrid field selector that uses DSPy when available,
    falls back to static rules when not.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config
        self.client = LightdashAPIClient(config.lightdash_config) if config and config.lightdash_config else None
        self.explore_cache = {}
        
        if DSPY_AVAILABLE:
            # Initialize DSPy with a simple model
            # In production, you might want to use a more sophisticated model
            lm = dspy.OpenAI(model="gpt-3.5-turbo", max_tokens=500)
            dspy.settings.configure(lm=lm)
            
            # Create the DSPy program
            self.selector = dspy.ChainOfThought(FieldSelectionSignature)
            
            # Load training examples if available
            self.load_training_data()
        else:
            self.selector = None
    
    def load_training_data(self):
        """Load training examples for DSPy optimization."""
        # Training data maps common questions to field selections
        self.training_examples = [
            # Sales/Revenue questions
            {
                "question": "what did we sell",
                "metrics": ["total_product_quantity_sold"],
                "dimensions": ["line_items_titles"]
            },
            {
                "question": "revenue last 7 days",
                "metrics": ["total_gross_revenue", "total_net_revenue"],
                "dimensions": ["event_date"]
            },
            {
                "question": "sales by platform",
                "metrics": ["total_gross_revenue", "total_net_revenue"],
                "dimensions": ["platform"]
            },
            {
                "question": "top customers",
                "metrics": ["total_gross_revenue"],
                "dimensions": ["customer_id", "customer_email"]
            },
            {
                "question": "profit margins",
                "metrics": ["total_estimated_profit", "total_gross_revenue"],
                "dimensions": ["event_date"]
            },
            
            # Marketing/Ads questions
            {
                "question": "ad spend by campaign",
                "metrics": ["total_cost"],
                "dimensions": ["campaign_name"]
            },
            {
                "question": "campaign performance",
                "metrics": ["total_cost", "total_clicks", "total_impressions"],
                "dimensions": ["campaign_name", "campaign_status"]
            },
            {
                "question": "cost per click",
                "metrics": ["avg_cost_per_click", "total_clicks"],
                "dimensions": ["channel", "platform"]
            },
            
            # Attribution questions
            {
                "question": "ROAS by channel",
                "metrics": ["avg_pixel_roas", "total_attributed_revenue", "total_spend"],
                "dimensions": ["channel"]
            },
            {
                "question": "conversion tracking",
                "metrics": ["total_conversions", "avg_pixel_conversion_rate"],
                "dimensions": ["campaign_name", "device_type"]
            },
            
            # Lead questions
            {
                "question": "leads by state",
                "metrics": ["total_lead_count"],
                "dimensions": ["state"]
            },
            {
                "question": "cost per lead",
                "metrics": ["cost_per_lead", "total_lead_count"],
                "dimensions": ["country", "state"]
            }
        ]
    
    async def get_explore_fields(self, explore_name: str) -> Dict[str, List[Dict]]:
        """Fetch and cache explore fields from Lightdash."""
        if explore_name in self.explore_cache:
            return self.explore_cache[explore_name]
        
        if not self.client:
            return {"metrics": [], "dimensions": []}
        
        try:
            explore = await self.client.get_explore(explore_name)
            
            # Parse fields from explore
            fields = {"metrics": [], "dimensions": []}
            
            # Extract from tables in explore
            for table_name, table_data in explore.get("tables", {}).items():
                # Get metrics
                for metric_name, metric_info in table_data.get("metrics", {}).items():
                    if not metric_info.get("hidden", False):
                        fields["metrics"].append({
                            "name": metric_name,
                            "label": metric_info.get("label", metric_name),
                            "type": metric_info.get("type", "unknown"),
                            "description": metric_info.get("description", ""),
                            "table": table_name
                        })
                
                # Get dimensions
                for dim_name, dim_info in table_data.get("dimensions", {}).items():
                    if not dim_info.get("hidden", False):
                        fields["dimensions"].append({
                            "name": dim_name,
                            "label": dim_info.get("label", dim_name),
                            "type": dim_info.get("type", "unknown"),
                            "description": dim_info.get("description", ""),
                            "table": table_name
                        })
            
            self.explore_cache[explore_name] = fields
            return fields
            
        except Exception as e:
            logger.error(f"Failed to get explore fields: {e}")
            return {"metrics": [], "dimensions": []}
    
    def select_fields_with_dspy(
        self, 
        question: str, 
        available_fields: Dict[str, List[Dict]]
    ) -> Tuple[List[str], List[str], str]:
        """Use DSPy to select fields."""
        if not DSPY_AVAILABLE or not self.selector:
            return self.select_fields_static(question, available_fields)
        
        try:
            # Format fields for DSPy
            metrics_str = json.dumps([
                f"{m['name']} ({m['label']}): {m['description']}"
                for m in available_fields["metrics"]
            ])
            
            dimensions_str = json.dumps([
                f"{d['name']} ({d['label']}): {d['description']}"
                for d in available_fields["dimensions"]
            ])
            
            # Run DSPy selector
            result = self.selector(
                question=question,
                available_metrics=metrics_str,
                available_dimensions=dimensions_str
            )
            
            # Parse results
            selected_metrics = self.parse_field_names(
                result.selected_metrics, 
                available_fields["metrics"]
            )
            selected_dimensions = self.parse_field_names(
                result.selected_dimensions, 
                available_fields["dimensions"]
            )
            
            return selected_metrics, selected_dimensions, result.reasoning
            
        except Exception as e:
            logger.warning(f"DSPy selection failed, falling back to static: {e}")
            return self.select_fields_static(question, available_fields)
    
    def parse_field_names(self, dspy_output: str, available_fields: List[Dict]) -> List[str]:
        """Parse DSPy output to extract valid field names."""
        # DSPy might return field names in various formats
        # Try to extract and validate them
        field_names = []
        field_dict = {f["name"]: f for f in available_fields}
        
        # Try to parse as JSON list first
        try:
            names = json.loads(dspy_output)
            if isinstance(names, list):
                field_names = [n for n in names if n in field_dict]
        except:
            # Fall back to string parsing
            for field in available_fields:
                if field["name"] in dspy_output or field["label"] in dspy_output:
                    field_names.append(field["name"])
        
        return field_names
    
    def select_fields_static(
        self, 
        question: str, 
        available_fields: Dict[str, List[Dict]]
    ) -> Tuple[List[str], List[str], str]:
        """Fallback static field selection based on keywords."""
        question_lower = question.lower()
        selected_metrics = []
        selected_dimensions = []
        
        # Create lookup dictionaries
        metrics_by_name = {m["name"]: m for m in available_fields["metrics"]}
        dims_by_name = {d["name"]: d for d in available_fields["dimensions"]}
        
        # Product-related questions
        if any(kw in question_lower for kw in ["what did we sell", "products", "items sold"]):
            # Look for product quantity metrics
            for m in ["total_product_quantity_sold", "product_quantity_sold"]:
                if m in metrics_by_name:
                    selected_metrics.append(m)
            
            # Look for product dimensions
            for d in ["line_items_titles", "line_items_skus", "product_name"]:
                if d in dims_by_name:
                    selected_dimensions.append(d)
                    break
        
        # Revenue/Sales questions
        elif any(kw in question_lower for kw in ["revenue", "sales", "income"]):
            for m in ["total_gross_revenue", "total_net_revenue", "total_revenue"]:
                if m in metrics_by_name:
                    selected_metrics.append(m)
                if len(selected_metrics) >= 2:
                    break
        
        # Marketing/Ads questions
        elif any(kw in question_lower for kw in ["ad spend", "campaign", "marketing"]):
            for m in ["total_cost", "total_impressions", "total_clicks"]:
                if m in metrics_by_name:
                    selected_metrics.append(m)
        
        # Attribution questions
        elif any(kw in question_lower for kw in ["roas", "attribution", "conversion"]):
            for m in ["avg_pixel_roas", "total_attributed_revenue", "total_conversions"]:
                if m in metrics_by_name:
                    selected_metrics.append(m)
        
        # Lead questions
        elif any(kw in question_lower for kw in ["lead", "cost per lead"]):
            for m in ["total_lead_count", "cost_per_lead"]:
                if m in metrics_by_name:
                    selected_metrics.append(m)
        
        # Default to primary metrics if nothing selected
        if not selected_metrics and available_fields["metrics"]:
            # Take first 2 metrics that look like primary ones
            for m in available_fields["metrics"][:5]:
                if "revenue" in m["name"].lower() or "total" in m["name"].lower():
                    selected_metrics.append(m["name"])
                    if len(selected_metrics) >= 2:
                        break
        
        # Dimension selection based on keywords
        dimension_keywords = {
            "by campaign": ["campaign_name", "campaign_id"],
            "by channel": ["channel"],
            "by platform": ["platform"],
            "by customer": ["customer_id", "customer_email"],
            "by state": ["state", "customer_from_state_code"],
            "by country": ["country", "customer_from_country_code"],
            "by product": ["line_items_titles", "product_name"],
            "by date": ["event_date", "created_at"],
            "by month": ["event_date", "created_at"],
            "by week": ["event_date", "created_at"]
        }
        
        for keyword, field_options in dimension_keywords.items():
            if keyword in question_lower:
                for field in field_options:
                    if field in dims_by_name:
                        selected_dimensions.append(field)
                        break
        
        # Add time dimension if time period mentioned
        if any(kw in question_lower for kw in ["last", "yesterday", "today", "this", "days", "week", "month"]):
            for d in ["event_date", "created_at", "date"]:
                if d in dims_by_name and d not in selected_dimensions:
                    selected_dimensions.append(d)
                    break
        
        reasoning = f"Selected based on keyword matching for: {', '.join([kw for kw in ['product', 'revenue', 'campaign', 'lead'] if kw in question_lower])}"
        
        return selected_metrics, selected_dimensions, reasoning
    
    async def select_fields(
        self, 
        question: str, 
        explore_name: str
    ) -> Dict[str, Any]:
        """
        Main entry point for field selection.
        Returns selected metrics and dimensions for the given question.
        """
        # Get available fields for the explore
        available_fields = await self.get_explore_fields(explore_name)
        
        if not available_fields["metrics"] and not available_fields["dimensions"]:
            logger.warning(f"No fields found for explore {explore_name}")
            return {
                "metrics": [],
                "dimensions": [],
                "reasoning": "No fields available in explore"
            }
        
        # Select fields using DSPy or static rules
        if DSPY_AVAILABLE and self.selector:
            metrics, dimensions, reasoning = self.select_fields_with_dspy(question, available_fields)
        else:
            metrics, dimensions, reasoning = self.select_fields_static(question, available_fields)
        
        logger.info(f"Selected fields for '{question}': metrics={metrics}, dimensions={dimensions}")
        
        return {
            "metrics": metrics,
            "dimensions": dimensions,
            "reasoning": reasoning
        }