"""
Base class for task management operations
"""

from typing import Optional, List, Dict, Any
from ..models import TallyfyError


class TaskManagerBase:
    """Base class providing common functionality for task management"""
    
    def __init__(self, sdk):
        """
        Initialize base task manager.
        
        Args:
            sdk: Main SDK instance
        """
        self.sdk = sdk
    
    def _validate_org_id(self, org_id: str) -> None:
        """
        Validate organization ID parameter.
        
        Args:
            org_id: Organization ID to validate
            
        Raises:
            ValueError: If org_id is invalid
        """
        if not org_id or not isinstance(org_id, str):
            raise ValueError("Organization ID must be a non-empty string")
    
    def _validate_user_id(self, user_id: int) -> None:
        """
        Validate user ID parameter.
        
        Args:
            user_id: User ID to validate
            
        Raises:
            ValueError: If user_id is invalid
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")
    
    def _validate_process_id(self, process_id: str) -> None:
        """
        Validate process ID parameter.
        
        Args:
            process_id: Process ID to validate
            
        Raises:
            ValueError: If process_id is invalid
        """
        if not process_id or not isinstance(process_id, str):
            raise ValueError("Process ID must be a non-empty string")
    
    def _extract_data(self, response_data, data_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract data from API response.
        
        Args:
            response_data: Raw response from API
            data_key: Optional key to extract from response (e.g., 'process', 'blueprint')
            
        Returns:
            Extracted data list or empty list
        """
        if isinstance(response_data, dict):
            if data_key and data_key in response_data:
                # Handle search responses with specific keys
                nested_data = response_data[data_key]
                if isinstance(nested_data, dict) and 'data' in nested_data:
                    return nested_data['data']
                elif isinstance(nested_data, list):
                    return nested_data
            elif 'data' in response_data:
                return response_data['data']
            return []
        elif isinstance(response_data, list):
            return response_data
        return []
    
    def _handle_api_error(self, error: Exception, operation: str, **context) -> None:
        """
        Handle API errors with context.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            **context: Additional context for error logging
        """
        context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
        error_msg = f"Failed to {operation}"
        if context_str:
            error_msg += f" ({context_str})"
        error_msg += f": {error}"
        
        self.sdk.logger.error(error_msg)
        
        if isinstance(error, TallyfyError):
            raise error
        else:
            raise TallyfyError(error_msg)
    
    def _build_query_params(self, **kwargs) -> Dict[str, Any]:
        """
        Build query parameters from keyword arguments, filtering out None values.
        
        Args:
            **kwargs: Keyword arguments to convert to query parameters
            
        Returns:
            Dictionary of non-None parameters
        """
        params = {}
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, bool):
                    params[key] = 'true' if value else 'false'
                else:
                    params[key] = str(value)
        return params