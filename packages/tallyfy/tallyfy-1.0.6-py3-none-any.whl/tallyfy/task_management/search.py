"""
Task and process search operations
"""

from typing import List
from .base import TaskManagerBase
from ..models import SearchResult, TallyfyError


class TaskSearch(TaskManagerBase):
    """Handles task and process search operations"""

    def search_processes_by_name(self, org_id: str, process_name: str) -> str:
        """
        Search for processes by name using the search endpoint.

        Args:
            org_id: Organization ID
            process_name: Name or partial name of the process to search for

        Returns:
            Process ID of the found process

        Raises:
            TallyfyError: If no process found, multiple matches, or search fails
        """
        self._validate_org_id(org_id)
        
        if not process_name or not isinstance(process_name, str):
            raise ValueError("Process name must be a non-empty string")
        
        try:
            search_endpoint = f"organizations/{org_id}/search"
            search_params = {
                'on': 'process', 
                'per_page': '20',
                'search': process_name
            }
            
            search_response = self.sdk._make_request('GET', search_endpoint, params=search_params)
            
            if isinstance(search_response, dict) and 'process' in search_response:
                process_data = search_response['process']
                if 'data' in process_data and process_data['data']:
                    processes = process_data['data']
                    
                    # First try exact match (case-insensitive)
                    exact_matches = [p for p in processes if p['name'].lower() == process_name.lower()]
                    if exact_matches:
                        return exact_matches[0]['id']
                    elif len(processes) == 1:
                        # Single search result, use it
                        return processes[0]['id']
                    else:
                        # Multiple matches found, provide helpful error with options
                        match_names = [f"'{p['name']}'" for p in processes[:5]]  # Show max 5
                        raise TallyfyError(f"Multiple processes found matching '{process_name}': {', '.join(match_names)}. Please be more specific.")
                else:
                    raise TallyfyError(f"No process found matching name: {process_name}")
            else:
                raise TallyfyError(f"Search failed for process name: {process_name}")
                
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "search processes by name", org_id=org_id, process_name=process_name)

    def search(self, org_id: str, search_query: str, search_type: str = "process", per_page: int = 20) -> List[SearchResult]:
        """
        Search for processes, templates, or tasks in the organization.

        Args:
            org_id: Organization ID
            search_query: Text to search for
            search_type: Type of search - 'process', 'blueprint', or 'task' (default: 'process'). blueprint equals template
            per_page: Number of results per page (default: 20)

        Returns:
            List of SearchResult objects

        Raises:
            TallyfyError: If the request fails
            ValueError: If search_type is not valid
        """
        self._validate_org_id(org_id)
        
        if not search_query or not isinstance(search_query, str):
            raise ValueError("Search query must be a non-empty string")
        
        # Validate search type
        valid_types = ["process", "blueprint", "task"]
        if search_type not in valid_types:
            raise ValueError(f"Search type must be one of: {', '.join(valid_types)}")
        
        if per_page <= 0 or per_page > 100:
            raise ValueError("per_page must be between 1 and 100")
        
        try:
            endpoint = f"organizations/{org_id}/search"
            params = {
                'on': search_type,
                'per_page': str(per_page),
                'search': search_query
            }
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)
            
            search_data = self._extract_data(response_data, search_type)
            if search_data:
                return [SearchResult.from_dict(result_data, search_type) for result_data in search_data]
            else:
                self.sdk.logger.info(f"No {search_type} results found for query: {search_query}")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "search", org_id=org_id, search_query=search_query, search_type=search_type)

    def search_processes(self, org_id: str, search_query: str, per_page: int = 20) -> List[SearchResult]:
        """
        Search for processes in the organization.

        Args:
            org_id: Organization ID
            search_query: Text to search for
            per_page: Number of results per page (default: 20)

        Returns:
            List of SearchResult objects for processes

        Raises:
            TallyfyError: If the request fails
        """
        return self.search(org_id, search_query, "process", per_page)

    def search_templates(self, org_id: str, search_query: str, per_page: int = 20) -> List[SearchResult]:
        """
        Search for templates (blueprints) in the organization.

        Args:
            org_id: Organization ID
            search_query: Text to search for
            per_page: Number of results per page (default: 20)

        Returns:
            List of SearchResult objects for templates

        Raises:
            TallyfyError: If the request fails
        """
        return self.search(org_id, search_query, "blueprint", per_page)

    def search_tasks(self, org_id: str, search_query: str, per_page: int = 20) -> List[SearchResult]:
        """
        Search for tasks in the organization.

        Args:
            org_id: Organization ID
            search_query: Text to search for
            per_page: Number of results per page (default: 20)

        Returns:
            List of SearchResult objects for tasks

        Raises:
            TallyfyError: If the request fails
        """
        return self.search(org_id, search_query, "task", per_page)

    def find_process_by_name(self, org_id: str, process_name: str, exact_match: bool = True) -> List[SearchResult]:
        """
        Find processes by name with flexible matching options.

        Args:
            org_id: Organization ID
            process_name: Name of the process to search for
            exact_match: If True, only return exact matches (case-insensitive)

        Returns:
            List of SearchResult objects matching the criteria

        Raises:
            TallyfyError: If the request fails
        """
        results = self.search_processes(org_id, process_name)
        
        if exact_match:
            # Filter for exact matches (case-insensitive)
            exact_results = []
            for result in results:
                if hasattr(result, 'name') and result.name.lower() == process_name.lower():
                    exact_results.append(result)
            return exact_results
        
        return results