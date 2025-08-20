"""
Form Fields Management Package

This package provides a refactored, modular approach to form field management
functionality, breaking down the monolithic FormFieldManagement class into
specialized components for better maintainability and separation of concerns.

Classes:
    FormFieldCRUD: Basic CRUD operations for form fields
    FormFieldOptions: Dropdown options management  
    FormFieldSuggestions: AI-powered form field suggestions
    FormFieldManager: Unified interface combining all functionality
"""

from .base import FormFieldManagerBase
from .crud_operations import FormFieldCRUD
from .options_management import FormFieldOptions
from .suggestions import FormFieldSuggestions


class FormFieldManager:
    """
    Unified interface for form field management functionality.
    
    This class provides access to all form field management capabilities
    through a single interface while maintaining the modular structure
    underneath.
    """
    
    def __init__(self, sdk):
        """
        Initialize form field manager with SDK instance.
        
        Args:
            sdk: Main SDK instance
        """
        self.crud = FormFieldCRUD(sdk)
        self.options = FormFieldOptions(sdk)
        self.suggestions = FormFieldSuggestions(sdk)
        
        # For backward compatibility, expose common methods at the top level
        self.add_form_field_to_step = self.crud.add_form_field_to_step
        self.update_form_field = self.crud.update_form_field
        self.move_form_field = self.crud.move_form_field
        self.delete_form_field = self.crud.delete_form_field
        self.get_step = self.crud.get_step
        
        # Options management methods
        self.get_dropdown_options = self.options.get_dropdown_options
        self.update_dropdown_options = self.options.update_dropdown_options
        self.add_dropdown_option = self.options.add_dropdown_option
        self.remove_dropdown_option = self.options.remove_dropdown_option
        self.reorder_dropdown_options = self.options.reorder_dropdown_options
        
        # Suggestions methods
        self.suggest_form_fields_for_step = self.suggestions.suggest_form_fields_for_step
        self.suggest_field_improvements = self.suggestions.suggest_field_improvements


# For backward compatibility, create an alias
FormFieldManagement = FormFieldManager

__all__ = [
    'FormFieldManagerBase',
    'FormFieldCRUD', 
    'FormFieldOptions',
    'FormFieldSuggestions',
    'FormFieldManager',
    'FormFieldManagement'  # Backward compatibility alias
]