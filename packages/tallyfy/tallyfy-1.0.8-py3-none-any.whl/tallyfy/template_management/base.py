"""
Base class for template management functionality
"""

from typing import Any, Optional
from ..models import TallyfyError


class TemplateManagerBase:
    """Base class providing shared functionality for template management operations"""
    
    def __init__(self, sdk):
        """Initialize with SDK instance"""
        self.sdk = sdk
    
    def _validate_org_id(self, org_id: str) -> None:
        """Validate organization ID parameter"""
        if not org_id or not isinstance(org_id, str):
            raise ValueError("Organization ID must be a non-empty string")
    
    def _validate_template_id(self, template_id: str) -> None:
        """Validate template ID parameter"""
        if not template_id or not isinstance(template_id, str):
            raise ValueError("Template ID must be a non-empty string")
    
    def _handle_api_error(self, error: Exception, operation: str, **context) -> None:
        """Common error handling for API operations"""
        error_msg = f"Failed to {operation}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            error_msg += f" ({context_str})"
        error_msg += f": {error}"
        
        self.sdk.logger.error(error_msg)
        if isinstance(error, TallyfyError):
            raise
        else:
            raise TallyfyError(error_msg)
    
    def _validate_response(self, response: Any, expected_key: Optional[str] = None) -> bool:
        """Validate API response format"""
        if not isinstance(response, dict):
            return False
        
        if expected_key and expected_key not in response:
            return False
            
        return True
    
    def _extract_data(self, response: dict, data_key: str = 'data') -> Any:
        """Extract data from API response with validation"""
        if not self._validate_response(response, data_key):
            self.sdk.logger.warning("Unexpected response format")
            return None
        
        return response.get(data_key)