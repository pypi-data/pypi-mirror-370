"""
Base class for form field management operations
"""

from typing import Optional
from ..models import TallyfyError


class FormFieldManagerBase:
    """Base class providing common functionality for form field management"""
    
    def __init__(self, sdk):
        """
        Initialize base form field manager.
        
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
    
    def _validate_template_id(self, template_id: str) -> None:
        """
        Validate template ID parameter.
        
        Args:
            template_id: Template ID to validate
            
        Raises:
            ValueError: If template_id is invalid
        """
        if not template_id or not isinstance(template_id, str):
            raise ValueError("Template ID must be a non-empty string")
    
    def _validate_step_id(self, step_id: str) -> None:
        """
        Validate step ID parameter.
        
        Args:
            step_id: Step ID to validate
            
        Raises:
            ValueError: If step_id is invalid
        """
        if not step_id or not isinstance(step_id, str):
            raise ValueError("Step ID must be a non-empty string")
    
    def _validate_field_id(self, field_id: str) -> None:
        """
        Validate field ID parameter.
        
        Args:
            field_id: Field ID to validate
            
        Raises:
            ValueError: If field_id is invalid
        """
        if not field_id or not isinstance(field_id, str):
            raise ValueError("Field ID must be a non-empty string")
    
    def _extract_data(self, response_data) -> Optional[dict]:
        """
        Extract data from API response.
        
        Args:
            response_data: Raw response from API
            
        Returns:
            Extracted data dictionary or None
        """
        if isinstance(response_data, dict):
            if 'data' in response_data:
                return response_data['data']
            return response_data
        return None
    
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