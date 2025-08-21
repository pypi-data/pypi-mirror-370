"""Type definitions for Lightdash integration"""

from typing import TypedDict, Optional, List, Dict, Any, Literal
from enum import Enum


class ChartType(str, Enum):
    """Supported chart types in Lightdash"""
    TABLE = "table"
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    AREA = "area"
    PIE = "pie"
    FUNNEL = "funnel"
    BIG_NUMBER = "big_number"
    

class FieldType(str, Enum):
    """Field types in Lightdash"""
    DIMENSION = "dimension"
    METRIC = "metric"


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class Space(TypedDict):
    """Lightdash space"""
    uuid: str
    name: str
    isPrivate: bool
    access: List[str]


class Field(TypedDict):
    """Field in a Lightdash explore"""
    name: str
    label: str
    type: str  # dimension or metric
    fieldType: str  # string, number, date, etc.
    description: Optional[str]
    hidden: bool


class Explore(TypedDict):
    """Lightdash explore (dbt model)"""
    name: str
    label: str
    tags: List[str]
    baseTable: str
    joinedTables: List[str]
    fields: Dict[str, Field]


class ChartConfig(TypedDict):
    """Chart visualization configuration"""
    type: str  # ChartType value
    config: Dict[str, Any]  # Type-specific config


class TableConfig(TypedDict):
    """Table-specific configuration"""
    columnOrder: List[str]


class MetricQuery(TypedDict):
    """Query definition for a chart"""
    dimensions: List[str]
    metrics: List[str]
    filters: Dict[str, Any]
    sorts: List[Dict[str, str]]
    limit: int
    tableCalculations: List[Dict[str, Any]]


class Chart(TypedDict):
    """Lightdash chart/saved query"""
    uuid: str
    name: str
    description: Optional[str]
    tableName: str
    metricQuery: MetricQuery
    chartConfig: ChartConfig
    tableConfig: TableConfig
    spaceUuid: str
    updatedAt: str
    updatedByUser: Dict[str, Any]


class CreateChartRequest(TypedDict):
    """Request to create a new chart"""
    name: str
    description: Optional[str]
    tableName: str
    metricQuery: MetricQuery
    chartConfig: ChartConfig
    tableConfig: TableConfig
    spaceUuid: str


class UpdateChartRequest(TypedDict, total=False):
    """Request to update an existing chart"""
    name: Optional[str]
    description: Optional[str]
    metricQuery: Optional[MetricQuery]
    chartConfig: Optional[ChartConfig]
    tableConfig: Optional[TableConfig]
    spaceUuid: Optional[str]


class RunQueryRequest(TypedDict):
    """Request to run a query"""
    dimensions: List[str]
    metrics: List[str]
    filters: Dict[str, Any]
    sorts: List[Dict[str, str]]
    limit: int


class RunQueryResponse(TypedDict):
    """Response from running a query"""
    rows: List[Dict[str, Any]]
    fields: Dict[str, Field]


# Helper functions for creating common configurations

def create_table_chart_config() -> ChartConfig:
    """Create a default table chart configuration"""
    return {
        "type": ChartType.TABLE.value,
        "config": {
            "showTableNames": True,
            "showResultsTotal": True,
            "showColumnCalculation": False
        }
    }


def create_bar_chart_config(x_field: str, y_fields: List[str]) -> ChartConfig:
    """Create a bar chart configuration"""
    return {
        "type": ChartType.BAR.value,
        "config": {
            "layout": {
                "xField": x_field,
                "yField": y_fields
            },
            "eChartsConfig": {
                "series": [],
                "legend": {"show": True},
                "grid": {"containLabel": True}
            }
        }
    }


def create_line_chart_config(x_field: str, y_fields: List[str]) -> ChartConfig:
    """Create a line chart configuration"""
    return {
        "type": ChartType.LINE.value,
        "config": {
            "layout": {
                "xField": x_field,
                "yField": y_fields
            },
            "eChartsConfig": {
                "series": [],
                "legend": {"show": True},
                "grid": {"containLabel": True}
            }
        }
    }


def create_big_number_config(field: str) -> ChartConfig:
    """Create a big number chart configuration"""
    return {
        "type": ChartType.BIG_NUMBER.value,
        "config": {
            "selectedField": field,
            "style": {
                "textAlign": "center"
            }
        }
    }


def create_metric_query(
    dimensions: List[str] = None,
    metrics: List[str] = None,
    filters: Dict[str, Any] = None,
    sorts: List[Dict[str, str]] = None,
    limit: int = 500
) -> MetricQuery:
    """Create a metric query with defaults"""
    return {
        "dimensions": dimensions or [],
        "metrics": metrics or [],
        "filters": filters or {},
        "sorts": sorts or [],
        "limit": limit,
        "tableCalculations": []
    }