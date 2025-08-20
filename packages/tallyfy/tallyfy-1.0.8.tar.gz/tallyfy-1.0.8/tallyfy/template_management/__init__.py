"""
Template Management Package

This package provides a refactored, modular approach to template management
functionality, breaking down the monolithic TemplateManagement class into
specialized components for better maintainability and separation of concerns.

Classes:
    TemplateBasicOperations: CRUD operations for templates
    TemplateAnalysis: Analysis and insights for templates
    TemplateAutomation: Automation rule management
    TemplateHealthAssessment: Comprehensive template health checks
    TemplateManager: Unified interface combining all functionality
"""

from .base import TemplateManagerBase
from .basic_operations import TemplateBasicOperations
from .analysis import TemplateAnalysis
from .automation import TemplateAutomation
from .health_assessment import TemplateHealthAssessment


class TemplateManager:
    """
    Unified interface for template management functionality.
    
    This class provides access to all template management capabilities
    through a single interface while maintaining the modular structure
    underneath.
    """
    
    def __init__(self, sdk):
        """
        Initialize template manager with SDK instance.
        
        Args:
            sdk: Main SDK instance
        """
        self.basic_operations = TemplateBasicOperations(sdk)
        self.analysis = TemplateAnalysis(sdk)
        self.automation = TemplateAutomation(sdk)
        self.health_assessment = TemplateHealthAssessment(sdk)
        
        # For backward compatibility, expose common methods at the top level
        self.search_templates_by_name = self.basic_operations.search_templates_by_name
        self.get_template = self.basic_operations.get_template
        self.get_all_templates = self.basic_operations.get_all_templates
        self.update_template_metadata = self.basic_operations.update_template_metadata
        self.get_template_with_steps = self.basic_operations.get_template_with_steps
        self.duplicate_template = self.basic_operations.duplicate_template
        self.get_template_steps = self.basic_operations.get_template_steps
        self.edit_description_on_step = self.basic_operations.edit_description_on_step
        self.add_step_to_template = self.basic_operations.add_step_to_template
        
        # Analysis methods
        self.get_step_dependencies = self.analysis.get_step_dependencies
        self.suggest_step_deadline = self.analysis.suggest_step_deadline
        self.get_step_visibility_conditions = self.analysis.get_step_visibility_conditions
        self.suggest_kickoff_fields = self.analysis.suggest_kickoff_fields
        self.suggest_automation_consolidation = self.analysis.suggest_automation_consolidation
        
        # Automation methods
        self.create_automation_rule = self.automation.create_automation_rule
        self.update_automation_rule = self.automation.update_automation_rule
        self.delete_automation_rule = self.automation.delete_automation_rule
        self.consolidate_automation_rules = self.automation.consolidate_automation_rules
        self.add_assignees_to_step = self.automation.add_assignees_to_step
        self.analyze_template_automations = self.automation.analyze_template_automations
        
        # Health assessment method
        self.assess_template_health = self.health_assessment.assess_template_health


# For backward compatibility, create an alias
TemplateManagement = TemplateManager

__all__ = [
    'TemplateManagerBase',
    'TemplateBasicOperations', 
    'TemplateAnalysis',
    'TemplateAutomation',
    'TemplateHealthAssessment',
    'TemplateManager',
    'TemplateManagement'  # Backward compatibility alias
]