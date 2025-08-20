"""
Task creation operations
"""

from typing import Optional
from .base import TaskManagerBase
from ..models import Task, TaskOwners, TallyfyError
from email_validator import validate_email, EmailNotValidError


class TaskCreation(TaskManagerBase):
    """Handles task creation operations"""

    def create_task(self, org_id: str, title: str, deadline: str,
                   owners: TaskOwners, description: Optional[str] = None,
                   max_assignable: Optional[int] = None, prevent_guest_comment: Optional[bool] = None) -> Optional[Task]:
        """
        Create a standalone task in the organization.

        Args:
            org_id: Organization ID
            title: Task name (required)
            deadline: Task deadline in "YYYY-mm-dd HH:ii:ss" format
            owners: TaskOwners object with users, guests, and groups
            description: Task description (optional)
            max_assignable: Maximum number of assignees (optional)
            prevent_guest_comment: Prevent guests from commenting (optional)

        Returns:
            Task object for the created task

        Raises:
            TallyfyError: If the request fails
            ValueError: If required parameters are missing or invalid
        """
        self._validate_org_id(org_id)
        
        if not title or not isinstance(title, str):
            raise ValueError("Task title must be a non-empty string")

        if not deadline or not isinstance(deadline, str):
            raise ValueError("Task deadline must be a non-empty string in 'YYYY-mm-dd HH:ii:ss' format")

        # Validate that at least one assignee is provided
        if not owners or not isinstance(owners, TaskOwners):
            raise ValueError("TaskOwners object is required")
            
        if not owners.users and not owners.guests and not owners.groups:
            raise ValueError("At least one assignee is required (users, guests, or groups)")

        # Validate max_assignable if provided
        if max_assignable is not None and (not isinstance(max_assignable, int) or max_assignable <= 0):
            raise ValueError("max_assignable must be a positive integer")

        try:
            endpoint = f"organizations/{org_id}/tasks"

            task_data = {
                "title": title,
                "deadline": deadline,
                "owners": {
                    "users": owners.users or [],
                    "guests": owners.guests or [],
                    "groups": owners.groups or []
                },
                "task_type": "task",
                "separate_task_for_each_assignee": True,
                "status": "not-started",
                "everyone_must_complete": False,
                "is_soft_start_date": True
            }

            # Add optional fields
            if description:
                task_data["description"] = description
            if max_assignable is not None:
                task_data["max_assignable"] = max_assignable
            if prevent_guest_comment is not None:
                task_data["prevent_guest_comment"] = prevent_guest_comment

            response_data = self.sdk._make_request('POST', endpoint, data=task_data)

            task_response_data = self._extract_data(response_data)
            if task_response_data:
                # Handle both single task and list responses
                if isinstance(task_response_data, list) and task_response_data:
                    return Task.from_dict(task_response_data[0])
                elif isinstance(task_response_data, dict):
                    return Task.from_dict(task_response_data)
            
            # Check if response_data itself is the task data
            if isinstance(response_data, dict) and 'data' in response_data:
                task_data_response = response_data['data']
                if isinstance(task_data_response, dict):
                    return Task.from_dict(task_data_response)
            
            self.sdk.logger.warning("Unexpected response format for task creation")
            return None

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "create task", org_id=org_id, title=title)

    def create_simple_task(self, org_id: str, title: str, deadline: str, user_ids: Optional[list] = None, 
                          guest_emails: Optional[list] = None, group_ids: Optional[list] = None,
                          description: Optional[str] = None) -> Optional[Task]:
        """
        Create a simple task with basic assignee information.
        
        This is a convenience method that creates TaskOwners internally.

        Args:
            org_id: Organization ID
            title: Task name (required)
            deadline: Task deadline in "YYYY-mm-dd HH:ii:ss" format
            user_ids: List of user IDs to assign (optional)
            guest_emails: List of guest email addresses to assign (optional)
            group_ids: List of group IDs to assign (optional)
            description: Task description (optional)

        Returns:
            Task object for the created task

        Raises:
            TallyfyError: If the request fails
            ValueError: If required parameters are missing or no assignees provided
        """
        # Validate that at least one assignee type is provided
        if not user_ids and not guest_emails and not group_ids:
            raise ValueError("At least one assignee is required (user_ids, guest_emails, or group_ids)")

        # Create TaskOwners object
        owners = TaskOwners(
            users=user_ids or [],
            guests=guest_emails or [],
            groups=group_ids or []
        )

        return self.create_task(org_id, title, deadline, owners, description)

    def create_user_task(self, org_id: str, title: str, deadline: str, user_ids: list, 
                        description: Optional[str] = None) -> Optional[Task]:
        """
        Create a task assigned to specific users only.

        Args:
            org_id: Organization ID
            title: Task name (required)
            deadline: Task deadline in "YYYY-mm-dd HH:ii:ss" format
            user_ids: List of user IDs to assign (required)
            description: Task description (optional)

        Returns:
            Task object for the created task

        Raises:
            TallyfyError: If the request fails
            ValueError: If required parameters are missing
        """
        if not user_ids or not isinstance(user_ids, list):
            raise ValueError("user_ids must be a non-empty list")

        return self.create_simple_task(org_id, title, deadline, user_ids=user_ids, description=description)

    def create_guest_task(self, org_id: str, title: str, deadline: str, guest_emails: list, 
                         description: Optional[str] = None) -> Optional[Task]:
        """
        Create a task assigned to guests only.

        Args:
            org_id: Organization ID
            title: Task name (required)
            deadline: Task deadline in "YYYY-mm-dd HH:ii:ss" format
            guest_emails: List of guest email addresses to assign (required)
            description: Task description (optional)

        Returns:
            Task object for the created task

        Raises:
            TallyfyError: If the request fails
            ValueError: If required parameters are missing
        """
        if not guest_emails or not isinstance(guest_emails, list):
            raise ValueError("guest_emails must be a non-empty list")

        # Basic email validation
        for email in guest_emails:
            try:
                validation = validate_email(email)
                # The validated email address
                email = validation.normalized
            except EmailNotValidError as e:
                raise ValueError(f"Invalid email address: {str(e)}")

        return self.create_simple_task(org_id, title, deadline, guest_emails=guest_emails, description=description)

    def create_group_task(self, org_id: str, title: str, deadline: str, group_ids: list, 
                         description: Optional[str] = None) -> Optional[Task]:
        """
        Create a task assigned to groups only.

        Args:
            org_id: Organization ID
            title: Task name (required)
            deadline: Task deadline in "YYYY-mm-dd HH:ii:ss" format
            group_ids: List of group IDs to assign (required)
            description: Task description (optional)

        Returns:
            Task object for the created task

        Raises:
            TallyfyError: If the request fails
            ValueError: If required parameters are missing
        """
        if not group_ids or not isinstance(group_ids, list):
            raise ValueError("group_ids must be a non-empty list")

        return self.create_simple_task(org_id, title, deadline, group_ids=group_ids, description=description)