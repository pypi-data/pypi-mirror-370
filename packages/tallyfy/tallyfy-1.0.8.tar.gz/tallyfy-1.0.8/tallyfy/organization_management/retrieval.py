"""
Organization retrieval operations
"""

from typing import List, Optional
from .base import OrganizationManagerBase
from ..models import Organization, OrganizationsList, TallyfyError


class OrganizationRetrieval(OrganizationManagerBase):
    """Handles organization retrieval operations"""

    def get_current_user_organizations(self, page: int = 1, per_page: int = 10) -> OrganizationsList:
        """
        Get all organizations the current member is a part of.

        Args:
            page: Page number (default: 1)
            per_page: Number of results per page (default: 10, max: 100)

        Returns:
            OrganizationsList object containing organizations and pagination metadata

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = "me/organizations"
            params = self._build_query_params(page=page, per_page=min(per_page, 100))
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)

            # Return the structured response with pagination
            return OrganizationsList.from_dict(response_data)

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get my organizations", page=page, per_page=per_page)