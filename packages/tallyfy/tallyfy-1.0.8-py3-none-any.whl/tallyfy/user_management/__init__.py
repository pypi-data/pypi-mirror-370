"""
User Management Package

This package provides a refactored, modular approach to user management
functionality, breaking down the monolithic UserManagement class into
specialized components for better maintainability and separation of concerns.

Classes:
    UserRetrieval: User and guest retrieval operations
    UserInvitation: User invitation operations
    UserManager: Unified interface combining all functionality
"""

from .base import UserManagerBase
from .retrieval import UserRetrieval
from .invitation import UserInvitation


class UserManager:
    """
    Unified interface for user management functionality.
    
    This class provides access to all user management capabilities
    through a single interface while maintaining the modular structure
    underneath.
    """
    
    def __init__(self, sdk):
        """
        Initialize user manager with SDK instance.
        
        Args:
            sdk: Main SDK instance
        """
        self.retrieval = UserRetrieval(sdk)
        self.invitation = UserInvitation(sdk)
        
        # For backward compatibility, expose common methods at the top level
        
        # Retrieval methods
        self.get_current_user_info = self.retrieval.get_current_user_info
        self.get_organization_users = self.retrieval.get_organization_users
        self.get_organization_users_list = self.retrieval.get_organization_users_list
        self.get_organization_guests = self.retrieval.get_organization_guests
        self.get_organization_guests_list = self.retrieval.get_organization_guests_list
        self.get_all_organization_members = self.retrieval.get_all_organization_members
        self.get_user_by_email = self.retrieval.get_user_by_email
        self.get_guest_by_email = self.retrieval.get_guest_by_email
        self.search_members_by_name = self.retrieval.search_members_by_name
        
        # Invitation methods
        self.invite_user_to_organization = self.invitation.invite_user_to_organization
        self.invite_multiple_users = self.invitation.invite_multiple_users
        self.resend_invitation = self.invitation.resend_invitation
        self.invite_user_with_custom_role_permissions = self.invitation.invite_user_with_custom_role_permissions
        self.get_invitation_template_message = self.invitation.get_invitation_template_message
        self.validate_invitation_data = self.invitation.validate_invitation_data


# For backward compatibility, create an alias
UserManagement = UserManager

__all__ = [
    'UserManagerBase',
    'UserRetrieval', 
    'UserInvitation',
    'UserManager',
    'UserManagement'  # Backward compatibility alias
]