"""MCP Resources for Lightdash data access"""

import json
import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from dbt_mcp.config.config import LightdashConfig
from dbt_mcp.lightdash.client import LightdashAPIClient

logger = logging.getLogger(__name__)


def register_lightdash_resources(
    dbt_mcp: FastMCP,
    lightdash_config: LightdashConfig,
) -> None:
    """Register Lightdash-related MCP resources"""
    
    @dbt_mcp.resource(
        uri="lightdash://spaces",
        name="Lightdash Spaces",
        description="List of all available Lightdash spaces in the project",
        mime_type="application/json"
    )
    async def list_spaces_resource() -> str:
        """Resource that provides list of Lightdash spaces"""
        try:
            client = LightdashAPIClient(lightdash_config)
            
            # Get project details which includes spaces
            project = await client.get_project()
            spaces = project.get("spaces", [])
            
            return json.dumps({
                "spaces": [
                    {
                        "uuid": space.get("uuid"),
                        "name": space.get("name"),
                        "isPrivate": space.get("isPrivate", False),
                        "chartCount": space.get("dashboardCount", 0) + space.get("savedChartCount", 0)
                    }
                    for space in spaces
                ],
                "defaultSpace": lightdash_config.default_space_id,
                "totalSpaces": len(spaces)
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error fetching spaces: {e}")
            return json.dumps({"error": str(e)})
    
    @dbt_mcp.resource(
        uri="lightdash://explores",
        name="Lightdash Explores",
        description="List of all available explores (dbt models) in Lightdash",
        mime_type="application/json"
    )
    async def list_explores_resource() -> str:
        """Resource that provides list of Lightdash explores"""
        try:
            client = LightdashAPIClient(lightdash_config)
            
            # Get catalog which includes explores
            catalog = await client.get_catalog()
            explores = []
            
            for item in catalog:
                if item.get("type") == "table":
                    explores.append({
                        "name": item.get("name"),
                        "label": item.get("label"),
                        "description": item.get("description"),
                        "tags": item.get("tags", []),
                        "fieldCount": len(item.get("fields", []))
                    })
            
            return json.dumps({
                "explores": explores,
                "totalExplores": len(explores)
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error fetching explores: {e}")
            return json.dumps({"error": str(e)})
    
    @dbt_mcp.resource(
        uri="lightdash://metrics",
        name="Lightdash Metrics",
        description="Summary of all available metrics across explores",
        mime_type="application/json"
    )
    async def list_metrics_resource() -> str:
        """Resource that provides summary of all metrics"""
        try:
            client = LightdashAPIClient(lightdash_config)
            
            # Get all explores to collect metrics
            catalog = await client.get_catalog()
            metrics_by_explore = {}
            total_metrics = 0
            
            for table in catalog:
                if table.get("type") == "table":
                    explore_name = table.get("name")
                    metrics = []
                    
                    for field in table.get("fields", []):
                        if field.get("fieldType") == "metric":
                            metrics.append({
                                "name": field.get("name"),
                                "label": field.get("label"),
                                "type": field.get("type"),
                                "description": field.get("description")
                            })
                    
                    if metrics:
                        metrics_by_explore[explore_name] = metrics
                        total_metrics += len(metrics)
            
            return json.dumps({
                "metricsByExplore": metrics_by_explore,
                "totalMetrics": total_metrics,
                "exploresWithMetrics": len(metrics_by_explore)
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return json.dumps({"error": str(e)})
    
    @dbt_mcp.resource(
        uri="lightdash://charts",
        name="Lightdash Charts",
        description="List of all charts across all spaces",
        mime_type="application/json"
    )
    async def list_all_charts_resource() -> str:
        """Resource that provides all charts"""
        try:
            client = LightdashAPIClient(lightdash_config)
            
            # Get saved charts (all spaces)
            saved_charts = await client.list_saved_charts()
            
            charts = []
            for chart in saved_charts:
                charts.append({
                    "uuid": chart.get("uuid"),
                    "name": chart.get("name"),
                    "description": chart.get("description"),
                    "chartType": chart.get("chartType"),
                    "tableName": chart.get("tableName"),
                    "spaceName": chart.get("space", {}).get("name"),
                    "spaceUuid": chart.get("space", {}).get("uuid"),
                    "updatedAt": chart.get("updatedAt"),
                    "updatedByUser": chart.get("updatedByUser", {}).get("name")
                })
            
            # Group by space
            charts_by_space = {}
            for chart in charts:
                space_name = chart.get("spaceName", "Unknown")
                if space_name not in charts_by_space:
                    charts_by_space[space_name] = []
                charts_by_space[space_name].append(chart)
            
            return json.dumps({
                "charts": charts,
                "chartsBySpace": charts_by_space,
                "totalCharts": len(charts),
                "spaceCount": len(charts_by_space)
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error fetching charts: {e}")
            return json.dumps({"error": str(e)})
    
    logger.info(f"Registered 4 Lightdash resources")