"""
CRUD operations for form field management
"""

from typing import Dict, Any, Optional
from .base import FormFieldManagerBase
from ..models import Capture, Step, TallyfyError


class FormFieldCRUD(FormFieldManagerBase):
    """Handles basic CRUD operations for form fields"""

    def add_form_field_to_step(self, org_id: str, template_id: str, step_id: str, field_data: Dict[str, Any]) -> Optional[Capture]:
        """
        Add form fields (text, dropdown, date, etc.) to a step.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_data: Form field creation data including field_type, label, required, etc.
            
        Returns:
            Created Capture object or None if creation failed
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        self._validate_step_id(step_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}/captures"
            
            # Validate required fields
            required_fields = ['field_type', 'label']
            for field in required_fields:
                if field not in field_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Set defaults for optional fields
            capture_data = {
                'field_type': field_data['field_type'],
                'label': field_data['label'],
                'required': field_data.get('required', True),
                'position': field_data.get('position', 1)
            }
            
            # Add optional fields if provided
            optional_fields = ['guidance', 'options', 'default_value', 'default_value_enabled']
            for field in optional_fields:
                if field in field_data:
                    capture_data[field] = field_data[field]
            
            response_data = self.sdk._make_request('POST', endpoint, data=capture_data)
            
            extracted_data = self._extract_data(response_data)
            if extracted_data:
                return Capture.from_dict(extracted_data)
            else:
                self.sdk.logger.warning("Unexpected response format for form field creation")
                return None
                
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "add form field to step", org_id=org_id, template_id=template_id, step_id=step_id)

    def update_form_field(self, org_id: str, template_id: str, step_id: str, field_id: str, **kwargs) -> Optional[Capture]:
        """
        Update form field properties, validation, options.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            **kwargs: Form field properties to update
            
        Returns:
            Updated Capture object or None if update failed
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        self._validate_step_id(step_id)
        self._validate_field_id(field_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}/captures/{field_id}"
            
            # Build update data from kwargs
            update_data = {}
            allowed_fields = [
                'field_type', 'label', 'guidance', 'position', 'required',
                'options', 'default_value', 'default_value_enabled'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_data[field] = value
                else:
                    self.sdk.logger.warning(f"Ignoring unknown form field: {field}")
            
            if not update_data:
                raise ValueError("No valid form field properties provided for update")
            
            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)
            
            extracted_data = self._extract_data(response_data)
            if extracted_data:
                return Capture.from_dict(extracted_data)
            else:
                self.sdk.logger.warning("Unexpected response format for form field update")
                return None
                
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "update form field", org_id=org_id, template_id=template_id, step_id=step_id, field_id=field_id)

    def move_form_field(self, org_id: str, template_id: str, from_step: str, field_id: str, to_step: str, position: int = 1) -> bool:
        """
        Move form field between steps.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            from_step: Source step ID
            field_id: Form field ID to move
            to_step: Target step ID
            position: Position in target step (default: 1)
            
        Returns:
            True if move was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        self._validate_step_id(from_step)
        self._validate_field_id(field_id)
        self._validate_step_id(to_step)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{from_step}/captures/{field_id}/move"
            
            move_data = {
                'to_step_id': to_step,
                'position': position
            }
            
            response_data = self.sdk._make_request('POST', endpoint, data=move_data)
            
            # Check if move was successful
            return isinstance(response_data, dict) and response_data.get('success', False)
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "move form field", org_id=org_id, template_id=template_id, from_step=from_step, field_id=field_id, to_step=to_step)

    def delete_form_field(self, org_id: str, template_id: str, step_id: str, field_id: str) -> bool:
        """
        Delete a form field from a step.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            
        Returns:
            True if deletion was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        self._validate_step_id(step_id)
        self._validate_field_id(field_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}/captures/{field_id}"
            
            response_data = self.sdk._make_request('DELETE', endpoint)
            
            # Check if deletion was successful
            return isinstance(response_data, dict) and response_data.get('success', False)
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "delete form field", org_id=org_id, template_id=template_id, step_id=step_id, field_id=field_id)

    def get_step(self, org_id: str, template_id: str, step_id: str) -> Optional[Step]:
        """
        Get a specific step with its details.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            
        Returns:
            Step object or None if not found
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        self._validate_step_id(step_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}"
            response_data = self.sdk._make_request('GET', endpoint)
            
            extracted_data = self._extract_data(response_data)
            if extracted_data:
                return Step.from_dict(extracted_data)
            else:
                self.sdk.logger.warning("Unexpected response format for step")
                return None
                
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get step", org_id=org_id, template_id=template_id, step_id=step_id)