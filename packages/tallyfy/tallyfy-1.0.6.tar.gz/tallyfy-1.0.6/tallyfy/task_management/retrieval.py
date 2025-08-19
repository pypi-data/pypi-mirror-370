"""
Task and process retrieval operations
"""

from typing import List, Optional
from .base import TaskManagerBase
from ..models import Task, Run, TallyfyError


class TaskRetrieval(TaskManagerBase):
    """Handles task and process retrieval operations"""

    def get_my_tasks(self, org_id: str) -> List[Task]:
        """
        Get all tasks assigned to the current user in the organization.

        Args:
            org_id: Organization ID

        Returns:
            List of Task objects assigned to the current user

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        
        try:
            endpoint = f"organizations/{org_id}/me/tasks"
            response_data = self.sdk._make_request('GET', endpoint)

            tasks_data = self._extract_data(response_data)
            if tasks_data:
                return [Task.from_dict(task_data) for task_data in tasks_data]
            else:
                self.sdk.logger.warning("Unexpected response format for tasks")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get my tasks", org_id=org_id)

    def get_user_tasks(self, org_id: str, user_id: int) -> List[Task]:
        """
        Get all tasks assigned to the given user in the organization.

        Args:
            org_id: Organization ID
            user_id: User ID

        Returns:
            List of Task objects assigned to the given user ID

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_user_id(user_id)
        
        try:
            endpoint = f"organizations/{org_id}/users/{user_id}/tasks"
            params = {
                'per_page': '100',
                'sort_by': 'newest',
                'status': 'all',
                'with': 'run,threads_count,step,tags,folders,member_watchers.watcher'
            }
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)

            tasks_data = self._extract_data(response_data)
            if tasks_data:
                return [Task.from_dict(task_data) for task_data in tasks_data]
            else:
                self.sdk.logger.warning("Unexpected response format for user tasks")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get user tasks", org_id=org_id, user_id=user_id)

    def get_tasks_for_process(self, org_id: str, process_id: Optional[str] = None, process_name: Optional[str] = None) -> List[Task]:
        """
        Get all tasks for a given process (run).

        Args:
            org_id: Organization ID
            process_id: Process (run) ID to get tasks for
            process_name: Process (run) name to get tasks for (alternative to process_id)

        Returns:
            List of Task objects for the specified process

        Raises:
            TallyfyError: If the request fails
            ValueError: If neither process_id nor process_name is provided
        """
        self._validate_org_id(org_id)
        
        if not process_id and not process_name:
            raise ValueError("Either process_id or process_name must be provided")
        
        try:
            # If process_name is provided but not process_id, search for the process first
            if process_name and not process_id:
                # We need to import TaskSearch here to avoid circular imports
                from .search import TaskSearch
                search = TaskSearch(self.sdk)
                process_id = search.search_processes_by_name(org_id, process_name)
            
            self._validate_process_id(process_id)
            
            endpoint = f"organizations/{org_id}/runs/{process_id}/tasks"
            response_data = self.sdk._make_request('GET', endpoint)

            tasks_data = self._extract_data(response_data)
            if tasks_data:
                return [Task.from_dict(task_data) for task_data in tasks_data]
            else:
                self.sdk.logger.warning("Unexpected response format for process tasks")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get tasks for process", org_id=org_id, process_id=process_id, process_name=process_name)

    def get_organization_runs(self, org_id: str, with_data: Optional[str] = None, 
                            form_fields_values: Optional[bool] = None,
                            owners: Optional[str] = None, task_status: Optional[str] = None,
                            groups: Optional[str] = None, status: Optional[str] = None,
                            folder: Optional[str] = None, checklist_id: Optional[str] = None,
                            starred: Optional[bool] = None, run_type: Optional[str] = None,
                            tag: Optional[str] = None) -> List[Run]:
        """
        Get all processes (runs) in the organization.

        Args:
            org_id: Organization ID
            with_data: Comma-separated data to include (e.g., 'checklist,tasks,assets,tags')
            form_fields_values: Include form field values
            owners: Filter by specific member IDs
            task_status: Filter by task status ('all', 'in-progress', 'completed')
            groups: Filter by group IDs
            status: Filter by process status ('active', 'problem', 'delayed', 'complete', 'archived')
            folder: Filter by folder ID
            checklist_id: Filter by template ID
            starred: Filter by starred status
            run_type: Filter by type ('procedure', 'form', 'document')
            tag: Filter by tag ID

        Returns:
            List of Run objects

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        
        try:
            endpoint = f"organizations/{org_id}/runs"
            
            # Build parameters using base class helper
            params = self._build_query_params(
                with_=with_data,  # Use with_ to avoid Python keyword conflict
                form_fields_values=form_fields_values,
                owners=owners,
                task_status=task_status,
                groups=groups,
                status=status,
                folder=folder,
                checklist_id=checklist_id,
                starred=starred,
                type=run_type,  # API expects 'type' parameter
                tag=tag
            )
            
            # Handle the 'with' parameter specially due to Python keyword conflict
            if with_data:
                params['with'] = with_data
                if 'with_' in params:
                    del params['with_']
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)

            runs_data = self._extract_data(response_data)
            if runs_data:
                return [Run.from_dict(run_data) for run_data in runs_data]
            else:
                self.sdk.logger.warning("Unexpected response format for organization runs")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get organization runs", org_id=org_id)

    def get_organization_processes(self, org_id: str, **kwargs) -> List[Run]:
        """
        Alias for get_organization_runs for better naming consistency.
        
        Args:
            org_id: Organization ID
            **kwargs: Same parameters as get_organization_runs
            
        Returns:
            List of Run objects
        """
        return self.get_organization_runs(org_id, **kwargs)