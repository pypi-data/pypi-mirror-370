"""
Base class for organization management operations
"""

import logging
from typing import Dict, Any, List, Optional
from ..models import TallyfyError


class OrganizationManagerBase:
    """Base class providing common functionality for organization management operations"""

    def __init__(self, sdk):
        """
        Initialize the organization manager base.
        
        Args:
            sdk: The main Tallyfy SDK instance
        """
        self.sdk = sdk
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _extract_data(self, response_data: Dict[str, Any], default_empty: bool = True) -> Any:
        """
        Extract data from API response.
        
        Args:
            response_data: Raw API response
            default_empty: Return empty list if no data found
            
        Returns:
            Extracted data
        """
        if not response_data:
            return [] if default_empty else None
            
        # Handle direct data responses
        if 'data' in response_data:
            return response_data['data']
        
        # Handle responses where the main content is directly available
        # This is common for single item responses
        return response_data if not default_empty else []

    def _handle_api_error(self, error: Exception, operation: str, **context) -> None:
        """
        Handle and log API errors consistently.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            **context: Additional context for debugging
        """
        context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
        error_message = f"Failed to {operation}"
        if context_str:
            error_message += f" ({context_str})"
        
        self.logger.error(f"{error_message}: {str(error)}")
        
        if isinstance(error, TallyfyError):
            raise error
        else:
            raise TallyfyError(f"{error_message}: {str(error)}")

    def _build_query_params(self, **kwargs) -> Dict[str, Any]:
        """
        Build query parameters for API requests.
        
        Args:
            **kwargs: Parameters to include in the query string
            
        Returns:
            Dictionary of query parameters with None values filtered out
        """
        return {key: value for key, value in kwargs.items() if value is not None}