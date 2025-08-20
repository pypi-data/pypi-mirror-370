"""
Dropdown options management for form fields
"""

from typing import List, Dict, Any, Optional
from .base import FormFieldManagerBase
from ..models import TallyfyError


class FormFieldOptions(FormFieldManagerBase):
    """Handles dropdown options management for form fields"""

    def get_dropdown_options(self, org_id: str, template_id: str, step_id: str, field_id: str) -> List[str]:
        """
        Get current dropdown options for analysis.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            
        Returns:
            List of dropdown option strings
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        self._validate_step_id(step_id)
        self._validate_field_id(field_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}/captures/{field_id}"
            
            response_data = self.sdk._make_request('GET', endpoint)
            
            extracted_data = self._extract_data(response_data)
            if extracted_data:
                options = extracted_data.get('options', [])
                
                # Extract option values/labels
                if isinstance(options, list):
                    return [
                        opt.get('label', opt.get('value', str(opt))) if isinstance(opt, dict) else str(opt) 
                        for opt in options
                    ]
                else:
                    return []
            else:
                self.sdk.logger.warning("Unexpected response format for form field options")
                return []
                
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "get dropdown options", org_id=org_id, template_id=template_id, step_id=step_id, field_id=field_id)

    def update_dropdown_options(self, org_id: str, template_id: str, step_id: str, field_id: str, options: List[str]) -> bool:
        """
        Update dropdown options (for external data integration).
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            options: List of new option strings
            
        Returns:
            True if update was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        self._validate_step_id(step_id)
        self._validate_field_id(field_id)
        
        try:
            # Format options for API
            formatted_options = []
            for i, option in enumerate(options):
                if isinstance(option, str):
                    formatted_options.append({
                        'value': option.lower().replace(' ', '_'),
                        'label': option,
                        'position': i + 1
                    })
                elif isinstance(option, dict):
                    formatted_options.append(option)
                else:
                    formatted_options.append({
                        'value': str(option),
                        'label': str(option),
                        'position': i + 1
                    })
            
            # Update the field with new options using CRUD operations
            # We need to import FormFieldCRUD here to avoid circular imports
            from .crud_operations import FormFieldCRUD
            crud = FormFieldCRUD(self.sdk)
            
            updated_capture = crud.update_form_field(
                org_id, template_id, step_id, field_id,
                options=formatted_options
            )
            
            return updated_capture is not None
                
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "update dropdown options", org_id=org_id, template_id=template_id, step_id=step_id, field_id=field_id)

    def add_dropdown_option(self, org_id: str, template_id: str, step_id: str, field_id: str, new_option: str, position: Optional[int] = None) -> bool:
        """
        Add a single new option to an existing dropdown field.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            new_option: New option to add
            position: Position to insert the option (None = append to end)
            
        Returns:
            True if addition was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            # Get current options
            current_options = self.get_dropdown_options(org_id, template_id, step_id, field_id)
            
            # Add new option at specified position or end
            if position is not None and 0 <= position <= len(current_options):
                current_options.insert(position, new_option)
            else:
                current_options.append(new_option)
            
            # Update with new options list
            return self.update_dropdown_options(org_id, template_id, step_id, field_id, current_options)
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "add dropdown option", org_id=org_id, template_id=template_id, step_id=step_id, field_id=field_id)

    def remove_dropdown_option(self, org_id: str, template_id: str, step_id: str, field_id: str, option_to_remove: str) -> bool:
        """
        Remove a specific option from a dropdown field.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            option_to_remove: Option to remove
            
        Returns:
            True if removal was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            # Get current options
            current_options = self.get_dropdown_options(org_id, template_id, step_id, field_id)
            
            # Remove the specified option if it exists
            if option_to_remove in current_options:
                current_options.remove(option_to_remove)
                
                # Update with modified options list
                return self.update_dropdown_options(org_id, template_id, step_id, field_id, current_options)
            else:
                self.sdk.logger.warning(f"Option '{option_to_remove}' not found in dropdown field {field_id}")
                return False
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "remove dropdown option", org_id=org_id, template_id=template_id, step_id=step_id, field_id=field_id)

    def reorder_dropdown_options(self, org_id: str, template_id: str, step_id: str, field_id: str, ordered_options: List[str]) -> bool:
        """
        Reorder dropdown options to match the provided list.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            ordered_options: List of options in desired order
            
        Returns:
            True if reordering was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            # Get current options to validate
            current_options = self.get_dropdown_options(org_id, template_id, step_id, field_id)
            
            # Validate that all provided options exist in current options
            missing_options = set(ordered_options) - set(current_options)
            if missing_options:
                raise ValueError(f"Cannot reorder: options not found in field: {missing_options}")
            
            # Update with reordered options
            return self.update_dropdown_options(org_id, template_id, step_id, field_id, ordered_options)
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "reorder dropdown options", org_id=org_id, template_id=template_id, step_id=step_id, field_id=field_id)