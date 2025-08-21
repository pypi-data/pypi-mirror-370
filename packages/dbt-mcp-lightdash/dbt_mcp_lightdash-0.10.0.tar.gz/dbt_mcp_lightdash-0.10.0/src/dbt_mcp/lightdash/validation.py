"""Validation and error handling utilities for Lightdash integration"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum

from dbt_mcp.lightdash.types import ChartType, FieldType

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class ErrorCategory(str, Enum):
    """Categories of errors for better user messages"""
    CONFIGURATION = "configuration"
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    NOT_FOUND = "not_found"
    INVALID_INPUT = "invalid_input"
    API_ERROR = "api_error"
    PERMISSION = "permission"
    DATA_ERROR = "data_error"


def format_error_message(error: Exception, category: ErrorCategory, context: str = "") -> str:
    """Format error message for user-friendly display"""
    
    base_messages = {
        ErrorCategory.CONFIGURATION: "Configuration error",
        ErrorCategory.CONNECTION: "Connection error",
        ErrorCategory.AUTHENTICATION: "Authentication failed",
        ErrorCategory.NOT_FOUND: "Resource not found",
        ErrorCategory.INVALID_INPUT: "Invalid input",
        ErrorCategory.API_ERROR: "API error",
        ErrorCategory.PERMISSION: "Permission denied",
        ErrorCategory.DATA_ERROR: "Data error"
    }
    
    suggestions = {
        ErrorCategory.CONFIGURATION: "Please check your Lightdash configuration in the .env file.",
        ErrorCategory.CONNECTION: "Please ensure Lightdash is running and accessible at the configured URL.",
        ErrorCategory.AUTHENTICATION: "Please verify your API key is correct and has not expired.",
        ErrorCategory.NOT_FOUND: "Please check that the resource exists and you have access to it.",
        ErrorCategory.INVALID_INPUT: "Please check your input parameters and try again.",
        ErrorCategory.API_ERROR: "This might be a temporary issue. Please try again or check Lightdash logs.",
        ErrorCategory.PERMISSION: "Please ensure your API key has the necessary permissions.",
        ErrorCategory.DATA_ERROR: "Please verify the data format and content."
    }
    
    message = f"❌ {base_messages.get(category, 'Error')}"
    
    if context:
        message += f" while {context}"
    
    message += f": {str(error)}"
    
    suggestion = suggestions.get(category)
    if suggestion:
        message += f"\n\n💡 {suggestion}"
    
    return message


def validate_chart_config(
    name: str,
    table_name: str,
    metrics: List[str],
    dimensions: List[str],
    chart_type: str
) -> Tuple[bool, Optional[str]]:
    """Validate chart configuration before creation"""
    
    # Validate name
    if not name or not name.strip():
        return False, "Chart name cannot be empty"
    
    if len(name) > 255:
        return False, "Chart name must be less than 255 characters"
    
    # Validate table name
    if not table_name or not table_name.strip():
        return False, "Table/explore name cannot be empty"
    
    # Validate chart type
    valid_types = [ct.value for ct in ChartType]
    if chart_type not in valid_types:
        return False, f"Invalid chart type '{chart_type}'. Valid types are: {', '.join(valid_types)}"
    
    # Validate metrics and dimensions
    if not metrics and not dimensions:
        return False, "Chart must have at least one metric or dimension"
    
    # Type-specific validation
    if chart_type == ChartType.BIG_NUMBER.value:
        if len(metrics) != 1:
            return False, "Big number charts must have exactly one metric"
        if dimensions:
            return False, "Big number charts cannot have dimensions"
    
    if chart_type in [ChartType.PIE.value, ChartType.FUNNEL.value]:
        if not dimensions:
            return False, f"{chart_type.title()} charts must have at least one dimension"
    
    # Validate field names
    for metric in metrics:
        if not metric or not isinstance(metric, str):
            return False, f"Invalid metric name: {metric}"
    
    for dimension in dimensions:
        if not dimension or not isinstance(dimension, str):
            return False, f"Invalid dimension name: {dimension}"
    
    return True, None


def validate_space_id(space_id: str) -> Tuple[bool, Optional[str]]:
    """Validate space UUID format"""
    
    if not space_id:
        return False, "Space ID cannot be empty"
    
    # Basic UUID format check
    parts = space_id.split('-')
    if len(parts) != 5:
        return False, "Invalid space ID format (should be UUID)"
    
    # Check lengths: 8-4-4-4-12
    expected_lengths = [8, 4, 4, 4, 12]
    for i, part in enumerate(parts):
        if len(part) != expected_lengths[i]:
            return False, "Invalid space ID format"
        
        # Check if hexadecimal
        try:
            int(part, 16)
        except ValueError:
            return False, "Invalid space ID format (not hexadecimal)"
    
    return True, None


def validate_query_parameters(
    metrics: List[str],
    group_by: List[str] = None,
    where: str = None,
    limit: int = None
) -> Tuple[bool, Optional[str]]:
    """Validate query parameters"""
    
    # Validate metrics
    if not metrics:
        return False, "At least one metric is required"
    
    for metric in metrics:
        if not metric or not isinstance(metric, str):
            return False, f"Invalid metric: {metric}"
    
    # Validate group by
    if group_by:
        for dimension in group_by:
            if not dimension or not isinstance(dimension, str):
                return False, f"Invalid dimension in group_by: {dimension}"
    
    # Validate limit
    if limit is not None:
        if not isinstance(limit, int) or limit < 1:
            return False, "Limit must be a positive integer"
        if limit > 100000:
            return False, "Limit cannot exceed 100,000 rows"
    
    # Validate where clause (basic check)
    if where:
        # Check for common SQL injection patterns
        dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
        where_upper = where.upper()
        for pattern in dangerous_patterns:
            if pattern in where_upper:
                return False, f"WHERE clause contains potentially dangerous SQL: {pattern}"
    
    return True, None


def parse_api_error(error_response: str) -> Tuple[ErrorCategory, str]:
    """Parse API error response to determine category and clean message"""
    
    error_lower = error_response.lower()
    
    # Authentication errors
    if any(term in error_lower for term in ['unauthorized', 'auth', 'api key', 'token']):
        return ErrorCategory.AUTHENTICATION, "Invalid or expired API key"
    
    # Permission errors
    if any(term in error_lower for term in ['forbidden', 'permission', 'access denied']):
        return ErrorCategory.PERMISSION, "You don't have permission to perform this action"
    
    # Not found errors
    if '404' in error_response or 'not found' in error_lower:
        return ErrorCategory.NOT_FOUND, "The requested resource was not found"
    
    # Connection errors
    if any(term in error_lower for term in ['connection', 'timeout', 'network']):
        return ErrorCategory.CONNECTION, "Could not connect to Lightdash"
    
    # Server errors
    if any(code in error_response for code in ['500', '502', '503', '504']):
        return ErrorCategory.API_ERROR, "Lightdash server error"
    
    # Default
    return ErrorCategory.API_ERROR, error_response


class ErrorHandler:
    """Centralized error handling for Lightdash operations"""
    
    @staticmethod
    def handle_api_error(error: Exception, operation: str) -> str:
        """Handle API errors with user-friendly messages"""
        
        error_str = str(error)
        
        # Parse error to get category
        if "404" in error_str:
            category = ErrorCategory.NOT_FOUND
        elif "401" in error_str or "403" in error_str:
            category = ErrorCategory.AUTHENTICATION
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            category = ErrorCategory.API_ERROR
        elif "connection" in error_str.lower():
            category = ErrorCategory.CONNECTION
        else:
            category = ErrorCategory.API_ERROR
        
        return format_error_message(error, category, operation)
    
    @staticmethod
    def handle_validation_error(error_message: str) -> str:
        """Handle validation errors"""
        return format_error_message(
            ValidationError(error_message),
            ErrorCategory.INVALID_INPUT
        )
    
    @staticmethod
    def handle_configuration_error(error: Exception) -> str:
        """Handle configuration errors"""
        return format_error_message(error, ErrorCategory.CONFIGURATION)
    
    @staticmethod
    def handle_data_error(error: Exception, context: str = "") -> str:
        """Handle data-related errors"""
        return format_error_message(error, ErrorCategory.DATA_ERROR, context)