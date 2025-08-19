"""
User and guest retrieval operations
"""

from typing import List, Optional
from .base import UserManagerBase
from ..models import User, Guest, TallyfyError


class UserRetrieval(UserManagerBase):
    """Handles user and guest retrieval operations"""

    def get_current_user_info(self, org_id: str) -> Optional[User]:
        """
        Get current user with full profile data.

        Args:
            org_id: Organization ID

        Returns:
            A User object with full profile data

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        
        try:
            endpoint = f"organizations/{org_id}/me"
            response_data = self.sdk._make_request('GET', endpoint)

            user_data = self._extract_data(response_data, default_empty=False)
            if user_data:
                # Handle both single user data and wrapped responses
                if isinstance(user_data, list) and user_data:
                    return User.from_dict(user_data[0])
                elif isinstance(user_data, dict):
                    return User.from_dict(user_data)
            
            self.sdk.logger.warning("Unexpected response format for getting current user")
            return None

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get current user info", org_id=org_id)

    def get_organization_users(self, org_id: str, with_groups: bool = False) -> List[User]:
        """
        Get all organization members with full profile data.

        Args:
            org_id: Organization ID
            with_groups: Include user groups data

        Returns:
            List of User objects with full profile data

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        
        try:
            endpoint = f"organizations/{org_id}/users"
            params = self._build_query_params(**{'with': 'groups'} if with_groups else {})
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)

            users_data = self._extract_data(response_data)
            if users_data:
                return [User.from_dict(user_data) for user_data in users_data]
            else:
                self.sdk.logger.warning("Unexpected response format for users")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get organization users", org_id=org_id)

    def get_organization_users_list(self, org_id: str) -> List[User]:
        """
        Get all organization members with minimal data for listing.

        Args:
            org_id: Organization ID

        Returns:
            List of User objects with minimal data

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        
        try:
            endpoint = f"organizations/{org_id}/users-list"
            response_data = self.sdk._make_request('GET', endpoint)

            users_data = self._extract_data(response_data)
            if users_data:
                return [User.from_dict(user_data) for user_data in users_data]
            else:
                self.sdk.logger.warning("Unexpected response format for users list")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get organization users list", org_id=org_id)

    def get_organization_guests(self, org_id: str, with_stats: bool = False) -> List[Guest]:
        """
        Get all guests in an organization with full profile data.

        Args:
            org_id: Organization ID
            with_stats: Include guest statistics

        Returns:
            List of Guest objects with full profile data

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        
        try:
            endpoint = f"organizations/{org_id}/guests"
            params = self._build_query_params(**{'with': 'stats'} if with_stats else {})
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)

            guests_data = self._extract_data(response_data)
            if guests_data:
                return [Guest.from_dict(guest_data) for guest_data in guests_data]
            else:
                self.sdk.logger.warning("Unexpected response format for guests")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get organization guests", org_id=org_id)

    def get_organization_guests_list(self, org_id: str) -> List[Guest]:
        """
        Get organization guests with minimal data.

        Args:
            org_id: Organization ID

        Returns:
            List of Guest objects with minimal data

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        
        try:
            endpoint = f"organizations/{org_id}/guests-list"
            response_data = self.sdk._make_request('GET', endpoint)

            # Handle different response formats
            guests_data = self._extract_data(response_data)
            if guests_data:
                # Handle both list of guests and single guest responses
                if isinstance(guests_data, list):
                    return [Guest.from_dict(guest_data) for guest_data in guests_data]
                else:
                    return [Guest.from_dict(guests_data)]
            else:
                self.sdk.logger.warning("Unexpected response format for guests list")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get organization guests list", org_id=org_id)

    def get_all_organization_members(self, org_id: str, include_guests: bool = True, 
                                   with_groups: bool = False, with_stats: bool = False) -> dict:
        """
        Get all organization members and optionally guests in a single call.
        
        This is a convenience method that combines users and guests data.

        Args:
            org_id: Organization ID
            include_guests: Whether to include guests in the results
            with_groups: Include user groups data
            with_stats: Include guest statistics

        Returns:
            Dictionary with 'users' and optionally 'guests' keys

        Raises:
            TallyfyError: If the request fails
        """
        result = {}
        
        # Get users
        result['users'] = self.get_organization_users(org_id, with_groups=with_groups)
        
        # Get guests if requested
        if include_guests:
            result['guests'] = self.get_organization_guests(org_id, with_stats=with_stats)
        
        return result

    def get_user_by_email(self, org_id: str, email: str) -> Optional[User]:
        """
        Find a user by email address within an organization.
        
        Args:
            org_id: Organization ID
            email: Email address to search for

        Returns:
            User object if found, None otherwise

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_email(email)
        
        # Get all users and search for the email
        users = self.get_organization_users(org_id)
        
        for user in users:
            if hasattr(user, 'email') and user.email and user.email.lower() == email.lower():
                return user
        
        return None

    def get_guest_by_email(self, org_id: str, email: str) -> Optional[Guest]:
        """
        Find a guest by email address within an organization.
        
        Args:
            org_id: Organization ID
            email: Email address to search for

        Returns:
            Guest object if found, None otherwise

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_email(email)
        
        # Get all guests and search for the email
        guests = self.get_organization_guests(org_id)
        
        for guest in guests:
            if hasattr(guest, 'email') and guest.email and guest.email.lower() == email.lower():
                return guest
        
        return None

    def search_members_by_name(self, org_id: str, name_query: str, include_guests: bool = True) -> dict:
        """
        Search for organization members by name (first name, last name, or full name).
        
        Args:
            org_id: Organization ID
            name_query: Name to search for (case-insensitive partial match)
            include_guests: Whether to include guests in the search

        Returns:
            Dictionary with 'users' and optionally 'guests' keys containing matching members

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        
        if not name_query or not isinstance(name_query, str):
            raise ValueError("Name query must be a non-empty string")
        
        name_query_lower = name_query.lower()
        result = {'users': [], 'guests': []}
        
        # Search users
        users = self.get_organization_users(org_id)
        for user in users:
            user_matches = False
            
            # Check first name
            if hasattr(user, 'first_name') and user.first_name:
                if name_query_lower in user.first_name.lower():
                    user_matches = True
            
            # Check last name
            if hasattr(user, 'last_name') and user.last_name:
                if name_query_lower in user.last_name.lower():
                    user_matches = True
            
            # Check full name
            if hasattr(user, 'first_name') and hasattr(user, 'last_name'):
                if user.first_name and user.last_name:
                    full_name = f"{user.first_name} {user.last_name}".lower()
                    if name_query_lower in full_name:
                        user_matches = True
            
            if user_matches:
                result['users'].append(user)
        
        # Search guests if requested
        if include_guests:
            guests = self.get_organization_guests(org_id)
            for guest in guests:
                guest_matches = False
                
                # Check first name
                if hasattr(guest, 'first_name') and guest.first_name:
                    if name_query_lower in guest.first_name.lower():
                        guest_matches = True
                
                # Check last name
                if hasattr(guest, 'last_name') and guest.last_name:
                    if name_query_lower in guest.last_name.lower():
                        guest_matches = True
                
                # Check full name
                if hasattr(guest, 'first_name') and hasattr(guest, 'last_name'):
                    if guest.first_name and guest.last_name:
                        full_name = f"{guest.first_name} {guest.last_name}".lower()
                        if name_query_lower in full_name:
                            guest_matches = True
                
                if guest_matches:
                    result['guests'].append(guest)
        
        return result