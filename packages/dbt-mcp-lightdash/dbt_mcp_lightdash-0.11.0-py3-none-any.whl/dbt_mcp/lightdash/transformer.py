"""Transform dbt query results to Lightdash chart format"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from dbt_mcp.lightdash.types import (
    MetricQuery,
    ChartConfig,
    TableConfig,
    CreateChartRequest,
    create_table_chart_config,
    create_metric_query,
    ChartType,
)

logger = logging.getLogger(__name__)


def transform_query_to_chart(
    query_result: str,
    chart_name: str,
    chart_description: Optional[str] = None,
    table_name: str = "query_results",
    metrics: List[str] = None,
    dimensions: List[str] = None,
    chart_type: str = "table",
    space_uuid: str = None,
) -> CreateChartRequest:
    """
    Transform a dbt semantic layer query result into a Lightdash chart configuration.
    
    Args:
        query_result: JSON string from dbt query (pandas to_json output)
        chart_name: Name for the chart
        chart_description: Optional description
        table_name: The dbt model/explore name
        metrics: List of metric names used in the query
        dimensions: List of dimension names used in the query
        chart_type: Type of chart (default: "table")
        space_uuid: UUID of the space to save the chart
        
    Returns:
        CreateChartRequest ready for Lightdash API
    """
    
    # Parse the query result to understand the data structure
    try:
        data = json.loads(query_result)
        if not data:
            raise ValueError("Query result is empty")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse query result JSON: {e}")
        raise ValueError(f"Invalid JSON in query result: {e}")
    
    # If metrics/dimensions not provided, try to infer from data
    if not metrics and not dimensions and data:
        # Take all columns as potential fields
        first_row = data[0]
        all_fields = list(first_row.keys())
        
        # Simple heuristic: numeric fields are metrics, others are dimensions
        # This is a fallback - it's better if the caller provides these
        dimensions = []
        metrics = []
        
        for field in all_fields:
            # Check if all values for this field are numeric
            is_numeric = all(
                isinstance(row.get(field), (int, float)) 
                for row in data 
                if row.get(field) is not None
            )
            
            if is_numeric:
                metrics.append(field)
            else:
                dimensions.append(field)
    
    # Create metric query
    metric_query = create_metric_query(
        dimensions=dimensions or [],
        metrics=metrics or [],
        limit=len(data)  # Set limit to actual data size
    )
    
    # Create chart configuration based on type
    if chart_type == ChartType.TABLE.value or chart_type == "table":
        chart_config = create_table_chart_config()
    else:
        # For now, default to table for unsupported types
        logger.warning(f"Chart type {chart_type} not fully supported, defaulting to table")
        chart_config = create_table_chart_config()
    
    # Create table configuration with column order
    column_order = (dimensions or []) + (metrics or [])
    table_config: TableConfig = {
        "columnOrder": column_order
    }
    
    # Build the complete chart request
    chart_request: CreateChartRequest = {
        "name": chart_name,
        "description": chart_description,
        "tableName": table_name,
        "metricQuery": metric_query,
        "chartConfig": chart_config,
        "tableConfig": table_config,
        "spaceUuid": space_uuid  # This will be handled by the client if None
    }
    
    return chart_request


def infer_chart_type_from_data(
    data: List[Dict[str, Any]], 
    metrics: List[str], 
    dimensions: List[str]
) -> str:
    """
    Infer the best chart type based on the data structure.
    
    This is a simple heuristic - defaults to table for now.
    Can be enhanced later with more sophisticated logic.
    """
    
    # For now, always return table as requested
    return ChartType.TABLE.value


def validate_chart_data(
    query_result: str,
    metrics: List[str] = None,
    dimensions: List[str] = None
) -> tuple[bool, Optional[str]]:
    """
    Validate that the query result can be transformed into a chart.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    
    try:
        data = json.loads(query_result)
    except json.JSONDecodeError:
        return False, "Invalid JSON format in query result"
    
    if not data:
        return False, "Query result is empty"
    
    if not isinstance(data, list):
        return False, "Query result must be a list of records"
    
    # Check that all records have the same structure
    if data:
        first_keys = set(data[0].keys())
        for i, record in enumerate(data[1:], 1):
            if set(record.keys()) != first_keys:
                return False, f"Inconsistent record structure at index {i}"
    
    # If metrics/dimensions provided, validate they exist in data
    if (metrics or dimensions) and data:
        all_fields = set(data[0].keys())
        
        if metrics:
            missing_metrics = set(metrics) - all_fields
            if missing_metrics:
                return False, f"Metrics not found in data: {missing_metrics}"
        
        if dimensions:
            missing_dimensions = set(dimensions) - all_fields
            if missing_dimensions:
                return False, f"Dimensions not found in data: {missing_dimensions}"
    
    return True, None