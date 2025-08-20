"""
Core SDK functionality and base classes
"""

import requests
import time
import logging
from typing import Dict, Any, Optional

from .models import TallyfyError


class BaseSDK:
    """
    Base SDK class with common functionality for HTTP requests and error handling
    """

    def __init__(self, api_key: str, base_url: str = "https://api.tallyfy.com", timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Setup default headers
        self.default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Tallyfy-Client': 'TallyfySDK',
            'Authorization': f'Bearer {api_key}'
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Setup session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: URL parameters
            data: Request body data
            
        Returns:
            Parsed JSON response data
            
        Raises:
            TallyfyError: If request fails after all retries
        """
        url = self._build_url(endpoint)
        
        # Prepare request arguments
        request_args = {
            'timeout': self.timeout,
            'params': params
        }
        
        if data:
            request_args['json'] = data
        
        # Retry logic
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                response = self.session.request(method, url, **request_args)
                
                # Parse response
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = response.text
                
                # Check if request was successful
                if response.ok:
                    return response_data
                else:
                    error_msg = f"API request failed with status {response.status_code}"
                    if isinstance(response_data, dict) and 'message' in response_data:
                        error_msg += f": {response_data['message']}"
                    elif isinstance(response_data, str):
                        error_msg += f": {response_data}"
                    
                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        raise TallyfyError(
                            error_msg,
                            status_code=response.status_code,
                            response_data=response_data
                        )
                    
                    # Retry on server errors (5xx)
                    if attempt < self.max_retries:
                        self.logger.warning(f"Request failed, retrying in {self.retry_delay}s...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise TallyfyError(
                            error_msg,
                            status_code=response.status_code,
                            response_data=response_data
                        )
                        
            except requests.exceptions.RequestException as req_error:
                last_exception = req_error
                if attempt < self.max_retries:
                    self.logger.warning(f"Request failed with {type(req_error).__name__}, retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    break
        
        # If we get here, all retries failed
        raise TallyfyError(f"Request failed after {self.max_retries + 1} attempts: {str(last_exception)}")

    def close(self):
        """Close the HTTP session and cleanup resources"""
        if hasattr(self, 'session'):
            self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


class TallyfySDK(BaseSDK):
    """
    High-level SDK for Tallyfy API endpoints
    Provides typed methods for interacting with Tallyfy's REST API
    """

    def __init__(self, api_key: str, base_url: str = "https://api.tallyfy.com", timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(api_key, base_url, timeout, max_retries, retry_delay)
        
        # Initialize management modules
        from .user_management import UserManager
        from .task_management import TaskManager  
        from .template_management import TemplateManager
        from .form_fields_management import FormFieldManager
        from .organization_management import OrganizationManager
        
        self.users = UserManager(self)
        self.tasks = TaskManager(self)
        self.templates = TemplateManager(self)
        self.form_fields = FormFieldManager(self)
        self.organizations = OrganizationManager(self)

    def get_current_user_info(self, org_id: str):
        """Get current user information."""
        return self.users.get_current_user_info(org_id)
    
    def get_current_user_organizations(self, page: int = 1, per_page: int = 10):
        """Get all organizations the current member is a part of."""
        return self.organizations.get_current_user_organizations(page, per_page)
    # Backward compatibility methods - delegate to management modules
    def get_organization_users(self, org_id: str, with_groups: bool = False):
        """Get all organization members with full profile data."""
        return self.users.get_organization_users(org_id, with_groups)
    
    def get_organization_users_list(self, org_id: str):
        """Get organization members with minimal data."""
        return self.users.get_organization_users_list(org_id)
    
    def get_organization_guests(self, org_id: str, with_stats: bool = False):
        """Get organization guests with full profile data."""
        return self.users.get_organization_guests(org_id, with_stats)
    
    def get_organization_guests_list(self, org_id: str):
        """Get organization guests with minimal data."""
        return self.users.get_organization_guests_list(org_id)
    
    def invite_user_to_organization(self, org_id: str, email: str, first_name: str, last_name: str, role: str = "light", message: Optional[str] = None):
        """Invite a member to your organization."""
        return self.users.invite_user_to_organization(org_id, email, first_name, last_name, role, message)
    
    def get_my_tasks(self, org_id: str):
        """Get tasks assigned to the current user."""
        return self.tasks.get_my_tasks(org_id)
    
    def get_user_tasks(self, org_id: str, user_id: int):
        """Get tasks assigned to a specific user."""
        return self.tasks.get_user_tasks(org_id, user_id)
    
    def get_tasks_for_process(self, org_id: str, process_id: Optional[str] = None, process_name: Optional[str] = None):
        """Get all tasks for a given process."""
        return self.tasks.get_tasks_for_process(org_id, process_id, process_name)
    
    def get_organization_runs(self, org_id: str, with_data: Optional[str] = None, 
                            form_fields_values: Optional[bool] = None, owners: Optional[str] = None,
                            task_status: Optional[str] = None, groups: Optional[str] = None,
                            status: Optional[str] = None, folder: Optional[str] = None,
                            checklist_id: Optional[str] = None, starred: Optional[bool] = None,
                            run_type: Optional[str] = None, tag: Optional[str] = None):
        """Get all processes (runs) in the organization."""
        return self.tasks.get_organization_runs(org_id, with_data, form_fields_values, owners, task_status, groups, status, folder, checklist_id, starred, run_type, tag)
    
    def create_task(self, org_id: str, title: str, deadline: str, description: Optional[str] = None, owners = None, max_assignable: Optional[int] = None, prevent_guest_comment: Optional[bool] = None):
        """Create a standalone task."""
        return self.tasks.create_task(org_id=org_id, title=title, deadline=deadline, description=description, owners=owners, max_assignable=max_assignable, prevent_guest_comment=prevent_guest_comment)
    
    def search_processes_by_name(self, org_id: str, process_name: str):
        """Search processes by name."""
        return self.tasks.search_processes_by_name(org_id, process_name)
    
    def search_templates_by_name(self, org_id: str, template_name: str):
        """Search templates by name."""
        return self.templates.search_templates_by_name(org_id, template_name)
    
    def search(self, org_id: str, search_query: str, search_type: str = "process", per_page: int = 20):
        """Universal search for processes, templates, or tasks."""
        return self.tasks.search(org_id, search_query, search_type, per_page)
    
    def get_template(self, org_id: str, template_id: Optional[str] = None, template_name: Optional[str] = None):
        """Get template by ID or name."""
        return self.templates.get_template(org_id, template_id, template_name)

    def get_all_templates(self, org_id: str):
        """Get all templates by organization."""
        return self.templates.get_all_templates(org_id)

    def update_template_metadata(self, org_id: str, template_id: str, **kwargs):
        """Update template metadata."""
        return self.templates.update_template_metadata(org_id, template_id, **kwargs)
    
    def get_template_with_steps(self, org_id: str, template_id: Optional[str] = None, template_name: Optional[str] = None):
        """Get template with steps."""
        return self.templates.get_template_with_steps(org_id, template_id, template_name)
    
    def duplicate_template(self, org_id: str, template_id: str, new_name: str, copy_permissions: bool = False):
        """Duplicate template."""
        return self.templates.duplicate_template(org_id, template_id, new_name, copy_permissions)
    
    def get_template_steps(self, org_id: str, template_id: str):
        """Get template steps."""
        return self.templates.get_template_steps(org_id, template_id)
    
    def get_step_dependencies(self, org_id: str, template_id: str, step_id: str):
        """Analyze step dependencies."""
        return self.templates.get_step_dependencies(org_id, template_id, step_id)
    
    def suggest_step_deadline(self, org_id: str, template_id: str, step_id: str):
        """Suggest step deadline."""
        return self.templates.suggest_step_deadline(org_id, template_id, step_id)
    
    # Form field methods
    def add_form_field_to_step(self, org_id: str, template_id: str, step_id: str, field_data: Dict[str, Any]):
        """Add form field to step."""
        return self.form_fields.add_form_field_to_step(org_id, template_id, step_id, field_data)
    
    def update_form_field(self, org_id: str, template_id: str, step_id: str, field_id: str, **kwargs):
        """Update form field."""
        return self.form_fields.update_form_field(org_id, template_id, step_id, field_id, **kwargs)
    
    def move_form_field(self, org_id: str, template_id: str, from_step: str, field_id: str, to_step: str, position: int = 1):
        """Move form field between steps."""
        return self.form_fields.move_form_field(org_id, template_id, from_step, field_id, to_step, position)
    
    def delete_form_field(self, org_id: str, template_id: str, step_id: str, field_id: str):
        """Delete form field."""
        return self.form_fields.delete_form_field(org_id, template_id, step_id, field_id)
    
    # Automation management methods
    def create_automation_rule(self, org_id: str, template_id: str, automation_data: Dict[str, Any]):
        """Create conditional automation (if-then rules)."""
        return self.templates.create_automation_rule(org_id, template_id, automation_data)
    
    def update_automation_rule(self, org_id: str, template_id: str, automation_id: str, **kwargs):
        """Modify automation conditions and actions."""
        return self.templates.update_automation_rule(org_id, template_id, automation_id, **kwargs)
    
    def delete_automation_rule(self, org_id: str, template_id: str, automation_id: str):
        """Remove an automation rule."""
        return self.templates.delete_automation_rule(org_id, template_id, automation_id)
    
    def analyze_template_automations(self, org_id: str, template_id: str):
        """Analyze all automations for conflicts, redundancies, and optimization opportunities."""
        return self.templates.analyze_template_automations(org_id, template_id)
    
    def consolidate_automation_rules(self, org_id: str, template_id: str, preview: bool = True):
        """Suggest and optionally implement automation consolidation."""
        return self.templates.consolidate_automation_rules(org_id, template_id, preview)
    
    def get_step_visibility_conditions(self, org_id: str, template_id: str, step_id: str):
        """Analyze when/how a step becomes visible based on all automations."""
        return self.templates.get_step_visibility_conditions(org_id, template_id, step_id)
    
    def suggest_automation_consolidation(self, org_id: str, template_id: str):
        """AI analysis of automation rules with consolidation recommendations."""
        return self.templates.suggest_automation_consolidation(org_id, template_id)
    
    # Kickoff field management methods
    # def add_kickoff_field(self, org_id: str, template_id: str, field_data: Dict[str, Any]):
    #     """Add kickoff/prerun fields to template."""
    #     return self.templates.add_kickoff_field(org_id, template_id, field_data)
    
    # def update_kickoff_field(self, org_id: str, template_id: str, field_id: str, **kwargs):
    #     """Update kickoff field properties."""
    #     return self.templates.update_kickoff_field(org_id, template_id, field_id, **kwargs)
    
    def suggest_kickoff_fields(self, org_id: str, template_id: str):
        """Suggest relevant kickoff fields based on template analysis."""
        return self.templates.suggest_kickoff_fields(org_id, template_id)
    
    def get_dropdown_options(self, org_id: str, template_id: str, step_id: str, field_id: str):
        """Get dropdown options."""
        return self.form_fields.get_dropdown_options(org_id, template_id, step_id, field_id)
    
    def update_dropdown_options(self, org_id: str, template_id: str, step_id: str, field_id: str, options):
        """Update dropdown options."""
        return self.form_fields.update_dropdown_options(org_id, template_id, step_id, field_id, options)
    
    def suggest_form_fields_for_step(self, org_id: str, template_id: str, step_id: str):
        """AI-powered form field suggestions."""
        return self.form_fields.suggest_form_fields_for_step(org_id, template_id, step_id)
    
    def assess_template_health(self, org_id: str, template_id: str):
        """Comprehensive template health check analyzing multiple aspects."""
        return self.templates.assess_template_health(org_id, template_id)
    
    def add_assignees_to_step(self, org_id: str, template_id: str, step_id: str, assignees: Dict[str, Any]):
        """Add assignees to a specific step in a template."""
        return self.templates.add_assignees_to_step(org_id, template_id, step_id, assignees)
    
    def edit_description_on_step(self, org_id: str, template_id: str, step_id: str, description: str):
        """Edit the description/summary of a specific step in a template."""
        return self.templates.edit_description_on_step(org_id, template_id, step_id, description)
    
    def add_step_to_template(self, org_id: str, template_id: str, step_data: Dict[str, Any]):
        """Add a new step to a template."""
        return self.templates.add_step_to_template(org_id, template_id, step_data)