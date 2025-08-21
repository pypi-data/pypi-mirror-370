"""MCP Prompts for Lightdash workflows"""

import logging
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from dbt_mcp.config.config import LightdashConfig
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def register_lightdash_prompts(
    dbt_mcp: FastMCP,
    lightdash_config: LightdashConfig,
) -> None:
    """Register Lightdash-related MCP prompts"""
    
    @dbt_mcp.prompt(
        name="lightdash-metric-analysis",
        description="Generate a metric analysis query for Lightdash"
    )
    async def metric_analysis_prompt(
        business_question: str,
        explore_hint: str = ""
    ) -> str:
        """Generate a prompt for metric analysis"""
        prompt = f"""Analyze this business question and suggest how to query it in Lightdash:

Business Question: {business_question}
{f'Suggested Explore: {explore_hint}' if explore_hint else ''}

Please provide:
1. Which Lightdash tool(s) to use (list_explores, get_explore, run_metric_query, etc.)
2. The specific metrics and dimensions needed
3. Any filters or time ranges to apply
4. Whether to save as a chart and suggested chart name

Start by using list_explores or list_metrics_enhanced to understand available data."""
        
        return prompt
    
    @dbt_mcp.prompt(
        name="lightdash-dashboard-builder",
        description="Plan a Lightdash dashboard with multiple charts"
    )
    async def dashboard_builder_prompt(
        dashboard_purpose: str,
        target_audience: str = "general users",
        update_frequency: str = "as needed"
    ) -> str:
        """Generate a prompt for dashboard planning"""
        prompt = f"""Help me plan a Lightdash dashboard:

Purpose: {dashboard_purpose}
Target Audience: {target_audience}
Update Frequency: {update_frequency}

Please suggest:
1. 4-6 key charts that should be included
2. For each chart:
   - Chart name and description
   - Metrics and dimensions to use
   - Visualization type recommendation
   - Filters or date ranges
3. Logical grouping/layout of charts
4. Which Lightdash space to use

Use list_explores and list_metrics_enhanced to find available data."""
        
        return prompt
    
    @dbt_mcp.prompt(
        name="lightdash-chart-optimization",
        description="Optimize an existing Lightdash chart for better insights"
    )
    async def chart_optimization_prompt(
        chart_id: str,
        optimization_goal: str = "better insights"
    ) -> str:
        """Generate a prompt for chart optimization"""
        prompt = f"""Analyze and optimize this Lightdash chart:

Chart ID: {chart_id}
Optimization Goal: {optimization_goal}

Steps:
1. Use get_chart to retrieve current configuration
2. Analyze the current setup and identify improvements
3. Suggest optimizations:
   - Better metrics or calculated fields
   - More effective groupings or filters
   - Clearer naming and descriptions
   - Alternative visualization types
4. Create an improved version with create_chart

Focus on making the chart more actionable for business users."""
        
        return prompt
    
    @dbt_mcp.prompt(
        name="lightdash-data-exploration",
        description="Explore available data in Lightdash to answer questions"
    )
    async def data_exploration_prompt(
        topic: str,
        specific_questions: str = ""
    ) -> str:
        """Generate a prompt for data exploration"""
        questions_text = specific_questions if specific_questions else "General insights about this topic"
        
        prompt = f"""Explore Lightdash data about: {topic}

Questions to answer:
{questions_text}

Exploration approach:
1. Use list_explores to find relevant data models
2. Use get_explore on promising models to see available fields
3. Use list_metrics_enhanced to understand metrics across models
4. Run exploratory queries with run_metric_query (small limits)
5. Identify interesting patterns or insights
6. Save valuable findings as charts

Provide a summary of available data and initial findings."""
        
        return prompt
    
    logger.info(f"Registered {len([metric_analysis_prompt, dashboard_builder_prompt, chart_optimization_prompt, data_exploration_prompt])} Lightdash prompts")