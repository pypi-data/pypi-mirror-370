"""
User invitation operations
"""

from typing import List, Optional
from .base import UserManagerBase
from ..models import User, TallyfyError


class UserInvitation(UserManagerBase):
    """Handles user invitation operations"""

    def invite_user_to_organization(self, org_id: str, email: str, first_name: str, last_name: str, 
                                   role: str = "light", message: Optional[str] = None) -> Optional[User]:
        """
        Invite a member to your organization.

        Args:
            org_id: Organization ID
            email: Email address of the user to invite
            first_name: First name of the user (required)
            last_name: Last name of the user (required)
            role: User role - 'light', 'standard', or 'admin' (default: 'light')
            message: Custom invitation message (optional)

        Returns:
            User object for the invited user

        Raises:
            TallyfyError: If the request fails
            ValueError: If parameters are invalid
        """
        # Validate inputs
        self._validate_org_id(org_id)
        self._validate_email(email)
        self._validate_name(first_name, "First name")
        self._validate_name(last_name, "Last name")
        self._validate_role(role)
        
        try:
            endpoint = f"organizations/{org_id}/users/invite"
            
            invite_data = {
                "email": email,
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "role": role
            }
            
            # Add message if provided, otherwise use default
            if message:
                invite_data["message"] = message
            else:
                invite_data["message"] = "Please join Tallyfy - it's going to help us automate tasks between people."
            
            response_data = self.sdk._make_request('POST', endpoint, data=invite_data)

            user_data = self._extract_data(response_data, default_empty=False)
            if user_data:
                if isinstance(user_data, dict):
                    return User.from_dict(user_data)
                elif isinstance(user_data, list) and user_data:
                    return User.from_dict(user_data[0])
            
            self.sdk.logger.warning("Unexpected response format for user invitation")
            return None

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "invite user to organization", org_id=org_id, email=email)

    def invite_multiple_users(self, org_id: str, invitations: List[dict], 
                             default_role: str = "light", default_message: Optional[str] = None) -> List[Optional[User]]:
        """
        Invite multiple users to the organization in batch.
        
        Args:
            org_id: Organization ID
            invitations: List of invitation dictionaries, each containing:
                        - email (required)
                        - first_name (required)
                        - last_name (required)
                        - role (optional, defaults to default_role)
                        - message (optional, defaults to default_message)
            default_role: Default role for users where role is not specified
            default_message: Default message for users where message is not specified

        Returns:
            List of User objects for successfully invited users (None for failed invitations)

        Raises:
            TallyfyError: If any invitation fails
            ValueError: If parameters are invalid
        """
        self._validate_org_id(org_id)
        self._validate_role(default_role)
        
        if not invitations or not isinstance(invitations, list):
            raise ValueError("Invitations must be a non-empty list")
        
        results = []
        
        for i, invitation in enumerate(invitations):
            if not isinstance(invitation, dict):
                raise ValueError(f"Invitation {i} must be a dictionary")
            
            # Validate required fields
            required_fields = ['email', 'first_name', 'last_name']
            for field in required_fields:
                if field not in invitation:
                    raise ValueError(f"Invitation {i} missing required field: {field}")
            
            try:
                # Use provided values or defaults
                role = invitation.get('role', default_role)
                message = invitation.get('message', default_message)
                
                user = self.invite_user_to_organization(
                    org_id=org_id,
                    email=invitation['email'],
                    first_name=invitation['first_name'],
                    last_name=invitation['last_name'],
                    role=role,
                    message=message
                )
                results.append(user)
                
            except Exception as e:
                self.sdk.logger.error(f"Failed to invite user {invitation.get('email')}: {e}")
                results.append(None)
                # Continue with other invitations even if one fails
        
        return results

    def resend_invitation(self, org_id: str, email: str, message: Optional[str] = None) -> bool:
        """
        Resend invitation to a user who was previously invited but hasn't joined.
        
        Note: This is a convenience method that attempts to re-invite the user.
        The API may handle this as a new invitation if the previous one expired.
        
        Args:
            org_id: Organization ID
            email: Email address of the user to re-invite
            message: Custom invitation message (optional)

        Returns:
            True if resend was successful

        Raises:
            TallyfyError: If the request fails
            ValueError: If parameters are invalid
        """
        self._validate_org_id(org_id)
        self._validate_email(email)
        
        # Since there's no specific resend endpoint, we'll need to get user info first
        # and then send a new invitation. This is a limitation of the current API.
        
        # For now, we'll use a generic approach - this would need to be updated
        # based on the actual API capabilities for resending invitations
        try:
            # Create a basic invitation message for resending
            if not message:
                message = "This is a reminder to join Tallyfy - please accept your invitation to help us automate tasks between people."
            
            # Note: Without knowing the user's name, we'll use placeholder values
            # In a real implementation, you might want to store invitation data
            # or retrieve user info from a pending invitations endpoint
            result = self.invite_user_to_organization(
                org_id=org_id,
                email=email,
                first_name="User",  # Placeholder - would need actual name
                last_name="Invite", # Placeholder - would need actual name
                role="light",
                message=message
            )
            
            return result is not None
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "resend invitation", org_id=org_id, email=email)

    def invite_user_with_custom_role_permissions(self, org_id: str, email: str, first_name: str, 
                                               last_name: str, role: str, 
                                               custom_permissions: Optional[dict] = None,
                                               message: Optional[str] = None) -> Optional[User]:
        """
        Invite a user with custom role and permissions (if supported by API).
        
        Args:
            org_id: Organization ID
            email: Email address of the user to invite
            first_name: First name of the user
            last_name: Last name of the user
            role: User role
            custom_permissions: Custom permissions dictionary (if supported)
            message: Custom invitation message

        Returns:
            User object for the invited user

        Raises:
            TallyfyError: If the request fails
            ValueError: If parameters are invalid
        """
        # For now, this is the same as regular invitation since the API
        # doesn't appear to support custom permissions in the invite endpoint
        # This method exists for future extensibility
        
        if custom_permissions:
            self.sdk.logger.warning("Custom permissions are not currently supported in invitations")
        
        return self.invite_user_to_organization(
            org_id=org_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            message=message
        )

    def get_invitation_template_message(self, org_name: Optional[str] = None, 
                                      custom_text: Optional[str] = None) -> str:
        """
        Generate a customized invitation message template.
        
        Args:
            org_name: Organization name to include in the message
            custom_text: Additional custom text to include

        Returns:
            Formatted invitation message string
        """
        base_message = "Please join Tallyfy - it's going to help us automate tasks between people."
        
        if org_name:
            base_message = f"Please join {org_name} on Tallyfy - it's going to help us automate tasks between people."
        
        if custom_text:
            base_message += f"\n\n{custom_text}"
        
        return base_message

    def validate_invitation_data(self, invitation_data: dict) -> dict:
        """
        Validate and clean invitation data before sending.
        
        Args:
            invitation_data: Dictionary containing invitation fields

        Returns:
            Validated and cleaned invitation data

        Raises:
            ValueError: If validation fails
        """
        required_fields = ['email', 'first_name', 'last_name']
        
        # Check required fields
        for field in required_fields:
            if field not in invitation_data or not invitation_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate specific fields
        self._validate_email(invitation_data['email'])
        self._validate_name(invitation_data['first_name'], "First name")
        self._validate_name(invitation_data['last_name'], "Last name")
        
        # Validate role if provided
        if 'role' in invitation_data:
            self._validate_role(invitation_data['role'])
        
        # Clean and return data
        cleaned_data = {
            'email': invitation_data['email'].strip().lower(),
            'first_name': invitation_data['first_name'].strip(),
            'last_name': invitation_data['last_name'].strip(),
            'role': invitation_data.get('role', 'light'),
            'message': invitation_data.get('message', self.get_invitation_template_message())
        }
        
        return cleaned_data