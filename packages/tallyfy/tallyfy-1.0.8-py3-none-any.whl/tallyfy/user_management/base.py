"""
Base class for user management operations
"""

from typing import Optional, List, Dict, Any
from ..models import TallyfyError
from email_validator import validate_email, EmailNotValidError


class UserManagerBase:
    """Base class providing common functionality for user management"""
    
    def __init__(self, sdk):
        """
        Initialize base user manager.
        
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
    
    def _validate_email(self, email: str) -> None:
        """
        Validate email parameter.
        
        Args:
            email: Email to validate
            
        Raises:
            ValueError: If email is invalid
        """
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")

        try:
            validation = validate_email(email)
            # The validated email address
            email = validation.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {str(e)}")
        # # Basic email validation
        # import re
        # email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        # if not re.match(email_pattern, email):
        #     raise ValueError(f"Invalid email address: {email}")
    
    def _validate_name(self, name: str, field_name: str) -> None:
        """
        Validate name parameter.
        
        Args:
            name: Name to validate
            field_name: Name of the field for error messages
            
        Raises:
            ValueError: If name is invalid
        """
        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError(f"{field_name} must be a non-empty string")
    
    def _validate_role(self, role: str) -> None:
        """
        Validate user role parameter.
        
        Args:
            role: Role to validate
            
        Raises:
            ValueError: If role is invalid
        """
        valid_roles = ["light", "standard", "admin"]
        if role not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
    
    def _extract_data(self, response_data, default_empty: bool = True) -> List[Dict[str, Any]]:
        """
        Extract data from API response.
        
        Args:
            response_data: Raw response from API
            default_empty: Return empty list if no data found
            
        Returns:
            Extracted data list or single item, or empty list/None
        """
        if isinstance(response_data, dict):
            if 'data' in response_data:
                return response_data['data']
            return response_data if not default_empty else []
        elif isinstance(response_data, list):
            return response_data
        return [] if default_empty else None
    
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