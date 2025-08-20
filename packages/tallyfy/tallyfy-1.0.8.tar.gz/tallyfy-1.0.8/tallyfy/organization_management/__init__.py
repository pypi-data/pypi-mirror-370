"""
Organization management module for Tallyfy SDK
"""

from .base import OrganizationManagerBase
from .retrieval import OrganizationRetrieval

class OrganizationManager(OrganizationRetrieval):
    """
    Complete organization management interface combining all functionality.
    
    This class provides access to:
    - Organization retrieval operations
    
    Example:
        >>> from tallyfy import TallyfySDK
        >>> sdk = TallyfySDK(api_key="your_api_key")
        >>> orgs = sdk.organizations.get_current_user_organizations()
        >>> print(f"User belongs to {len(orgs.data)} organizations")
    """
    pass

# Maintain backward compatibility
OrganizationManagement = OrganizationManager

__all__ = ['OrganizationManager', 'OrganizationManagement', 'OrganizationRetrieval', 'OrganizationManagerBase']