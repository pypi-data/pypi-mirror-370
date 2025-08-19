"""
Basic CRUD operations for template management
"""

from typing import List, Optional, Dict, Any
from .base import TemplateManagerBase
from ..models import Template, Step, TallyfyError, TemplatesList
from email_validator import validate_email, EmailNotValidError

class TemplateBasicOperations(TemplateManagerBase):
    """Handles basic template CRUD operations"""

    def search_templates_by_name(self, org_id: str, template_name: str) -> str:
        """
        Search for template by name using the search endpoint.

        Args:
            org_id: Organization ID
            template_name: Name or partial name of the template to search for

        Returns:
            Template ID of the found template

        Raises:
            TallyfyError: If no template found, multiple matches, or search fails
        """
        self._validate_org_id(org_id)

        try:
            search_endpoint = f"organizations/{org_id}/search"
            search_params = {
                'on': 'blueprint',
                'per_page': '20',
                'search': template_name
            }

            search_response = self.sdk._make_request('GET', search_endpoint, params=search_params)

            if isinstance(search_response, dict) and 'blueprint' in search_response:
                template_data = search_response['blueprint']
                if 'data' in template_data and template_data['data']:
                    templates = template_data['data']

                    # First try exact match (case-insensitive)
                    exact_matches = [p for p in templates if p['title'].lower() == template_name.lower()]
                    if exact_matches:
                        return exact_matches[0]['id']
                    elif len(templates) == 1:
                        # Single search result, use it
                        return templates[0]['id']
                    else:
                        # Multiple matches found, provide helpful error with options
                        match_names = [f"'{p['title']}'" for p in templates[:10]]  # Show max 10
                        raise TallyfyError(
                            f"Multiple templates found matching '{template_name}': {', '.join(match_names)}. Please be more specific.")
                else:
                    raise TallyfyError(f"No template found matching name: {template_name}")
            else:
                raise TallyfyError(f"Search failed for template name: {template_name}")

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "search templates by name", org_id=org_id, template_name=template_name)

    def get_template(self, org_id: str, template_id: Optional[str] = None, template_name: Optional[str] = None) -> Optional[Template]:
        """
        Get a template (checklist) by its ID or name with full details including prerun fields,
        automated actions, linked tasks, and metadata.

        Args:
            org_id: Organization ID
            template_id: Template (checklist) ID
            template_name: Template (checklist) name

        Returns:
            Template object with complete template data

        Raises:
            TallyfyError: If the request fails
        """
        if not template_id and not template_name:
            raise ValueError("Either template_id or template_name must be provided")

        self._validate_org_id(org_id)

        try:
            # If template_name is provided but not template_id, search for the template first
            if template_name and not template_id:
                template_id = self.search_templates_by_name(org_id, template_name)

            endpoint = f"organizations/{org_id}/checklists/{template_id}"
            response_data = self.sdk._make_request('GET', endpoint)

            template_data = self._extract_data(response_data)
            if template_data:
                return Template.from_dict(template_data)
            return None

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get template", org_id=org_id, template_id=template_id)

    def get_all_templates(self, org_id: str) -> TemplatesList:
        """
        Get all templates (checklists) for an organization with pagination metadata.

        Args:
            org_id: Organization ID

        Returns:
            TemplatesList object containing list of templates and pagination metadata

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)

        try:
            endpoint = f"organizations/{org_id}/checklists"
            response_data = self.sdk._make_request('GET', endpoint)

            if isinstance(response_data, dict):
                return TemplatesList.from_dict(response_data)
            else:
                self.sdk.logger.warning("Unexpected response format for templates list")
                return TemplatesList(data=[], meta=None)

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get all templates", org_id=org_id)

    def update_template_metadata(self, org_id: str, template_id: str, **kwargs) -> Optional[Template]:
        """
        Update template metadata like title, summary, guidance, icons, etc.

        Args:
            org_id: Organization ID
            template_id: Template ID to update
            **kwargs: Template metadata fields to update (title, summary, guidance, icon, etc.)

        Returns:
            Updated Template object

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)

        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}"

            # Build update data from kwargs
            update_data = {}
            allowed_fields = [
                'title', 'summary', 'guidance', 'icon', 'alias', 'webhook',
                'explanation_video', 'kickoff_title', 'kickoff_description',
                'is_public', 'is_featured', 'auto_naming', 'folderize_process',
                'tag_process', 'allow_launcher_change_name', 'is_pinned',
                'default_folder', 'folder_changeable_by_launcher'
            ]

            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_data[field] = value
                else:
                    self.sdk.logger.warning(f"Ignoring unknown template field: {field}")

            if not update_data:
                raise ValueError("No valid template fields provided for update")

            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)

            template_data = self._extract_data(response_data)
            if template_data:
                return Template.from_dict(template_data)
            return None

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "update template metadata", org_id=org_id, template_id=template_id)

    def get_template_with_steps(self, org_id: str, template_id: Optional[str] = None, template_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get template with full step details and structure.

        Args:
            org_id: Organization ID
            template_id: Template ID to retrieve
            template_name: Template name to retrieve (alternative to template_id)

        Returns:
            Dictionary containing template data with full step details

        Raises:
            TallyfyError: If the request fails
        """
        if not template_id and not template_name:
            raise ValueError("Either template_id or template_name must be provided")

        self._validate_org_id(org_id)

        try:
            # If template_name is provided but not template_id, search for the template first
            if template_name and not template_id:
                template_id = self.search_templates_by_name(org_id, template_name)

            # Get template with steps included
            endpoint = f"organizations/{org_id}/checklists/{template_id}"
            params = {'with': 'steps,automated_actions,prerun'}

            response_data = self.sdk._make_request('GET', endpoint, params=params)

            template_data = self._extract_data(response_data)
            if template_data:
                return {
                    'template': Template.from_dict(template_data),
                    'raw_data': template_data,
                    'step_count': len(template_data.get('steps', [])),
                    'steps': template_data.get('steps', []),
                    'automation_count': len(template_data.get('automated_actions', [])),
                    'prerun_field_count': len(template_data.get('prerun', []))
                }
            return None

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get template with steps", org_id=org_id, template_id=template_id)

    def duplicate_template(self, org_id: str, template_id: str, new_name: str, copy_permissions: bool = False) -> Optional[Template]:
        """
        Create a copy of a template for safe editing.

        Args:
            org_id: Organization ID
            template_id: Template ID to duplicate
            new_name: Name for the new template copy
            copy_permissions: Whether to copy template permissions (default: False)

        Returns:
            New Template object

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)

        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/duplicate"

            duplicate_data = {
                'title': new_name,
                'copy_permissions': copy_permissions
            }

            response_data = self.sdk._make_request('POST', endpoint, data=duplicate_data)

            template_data = self._extract_data(response_data)
            if template_data:
                return Template.from_dict(template_data)
            return None

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "duplicate template", org_id=org_id, template_id=template_id)

    def get_template_steps(self, org_id: str, template_id: str) -> List[Step]:
        """
        Get all steps of a template.

        Args:
            org_id: Organization ID
            template_id: Template ID

        Returns:
            List of Step objects

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)

        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps"
            response_data = self.sdk._make_request('GET', endpoint)

            if isinstance(response_data, dict) and 'data' in response_data:
                steps_data = response_data['data']
                return [Step.from_dict(step_data) for step_data in steps_data]
            elif isinstance(response_data, list):
                return [Step.from_dict(step_data) for step_data in response_data]
            else:
                self.sdk.logger.warning("Unexpected response format for template steps")
                return []

        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get template steps", org_id=org_id, template_id=template_id)

    def edit_description_on_step(self, org_id: str, template_id: str, step_id: str, description: str) -> Dict[str, Any]:
        """
        Edit the description/summary of a specific step in a template.

        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to edit description for
            description: New description/summary text for the step

        Returns:
            Dictionary containing updated step information

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)

        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}"

            # Validate description
            if not isinstance(description, str):
                raise ValueError("Description must be a string")

            description = description.strip()
            if not description:
                raise ValueError("Description cannot be empty")

            # Update data with correct payload structure
            update_data = {
                'summary': description
            }

            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)

            if isinstance(response_data, dict):
                if 'data' in response_data:
                    return response_data['data']
                return response_data
            else:
                self.sdk.logger.warning("Unexpected response format for step description update")
                return {'success': True, 'updated_summary': description}

        except TallyfyError:
            raise
        except ValueError as e:
            raise TallyfyError(f"Invalid description data: {e}")
        except Exception as e:
            self._handle_api_error(e, "edit step description", org_id=org_id, template_id=template_id, step_id=step_id)

    def add_step_to_template(self, org_id: str, template_id: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new step to a template.

        Args:
            org_id: Organization ID
            template_id: Template ID
            step_data: Dictionary containing step data including title, summary, position, etc.

        Returns:
            Dictionary containing created step information

        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)

        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps"

            # Validate step data
            if not isinstance(step_data, dict):
                raise ValueError("Step data must be a dictionary")

            # Validate required fields
            if 'title' not in step_data or not step_data['title']:
                raise ValueError("Step title is required")

            title = step_data['title'].strip()
            if not title:
                raise ValueError("Step title cannot be empty")

            # Build step creation data with defaults
            create_data = {'title': title}

            # Add optional string fields
            optional_string_fields = ['summary', 'step_type', 'alias', 'webhook', 'checklist_id']
            for field in optional_string_fields:
                if field in step_data and step_data[field]:
                    create_data[field] = str(step_data[field]).strip()

            # Add optional integer fields
            if 'position' in step_data:
                position = step_data['position']
                if isinstance(position, int) and position > 0:
                    create_data['position'] = position
                else:
                    raise ValueError("Position must be a positive integer")

            if 'max_assignable' in step_data:
                max_assignable = step_data['max_assignable']
                if isinstance(max_assignable, int) and max_assignable > 0:
                    create_data['max_assignable'] = max_assignable
                elif max_assignable is not None:
                    raise ValueError("max_assignable must be a positive integer or None")

            # Add boolean fields
            boolean_fields = [
                'allow_guest_owners', 'skip_start_process', 'can_complete_only_assignees',
                'everyone_must_complete', 'prevent_guest_comment', 'is_soft_start_date',
                'role_changes_every_time'
            ]
            for field in boolean_fields:
                if field in step_data:
                    create_data[field] = bool(step_data[field])

            # Add assignees if provided
            if 'assignees' in step_data and step_data['assignees']:
                assignees_list = step_data['assignees']
                if isinstance(assignees_list, list):
                    for user_id in assignees_list:
                        if not isinstance(user_id, int):
                            raise ValueError(f"User ID {user_id} must be an integer")
                    create_data['assignees'] = assignees_list
                else:
                    raise ValueError("Assignees must be a list of user IDs")

            # Add guests if provided
            if 'guests' in step_data and step_data['guests']:
                guests_list = step_data['guests']
                if isinstance(guests_list, list):
                    for guest_email in guests_list:
                        try:
                            validation = validate_email(guest_email)
                            # The validated email address
                            email = validation.normalized
                        except EmailNotValidError as e:
                            raise ValueError(f"Invalid email address: {str(e)}")
                    create_data['guests'] = guests_list
                else:
                    raise ValueError("Guests must be a list of email addresses")
            
            # Add roles if provided
            if 'roles' in step_data and step_data['roles']:
                roles_list = step_data['roles']
                if isinstance(roles_list, list):
                    create_data['roles'] = [str(role) for role in roles_list]
                else:
                    raise ValueError("Roles must be a list of role names")

            response_data = self.sdk._make_request('POST', endpoint, data=create_data)
            
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    return response_data['data']
                return response_data
            else:
                self.sdk.logger.warning("Unexpected response format for step creation")
                return {'success': True, 'created_step': create_data}
                
        except TallyfyError:
            raise
        except ValueError as e:
            raise TallyfyError(f"Invalid step data: {e}")
        except Exception as e:
            self._handle_api_error(e, "add step to template", org_id=org_id, template_id=template_id)