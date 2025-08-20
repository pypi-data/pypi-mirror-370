"""
AI-powered form field suggestions
"""

from typing import List, Dict, Any, Optional
from .base import FormFieldManagerBase
from ..models import Step, TallyfyError


class FormFieldSuggestions(FormFieldManagerBase):
    """Handles AI-powered form field suggestions based on step content"""

    def suggest_form_fields_for_step(self, org_id: str, template_id: str, step_id: str) -> List[Dict[str, Any]]:
        """
        AI-powered suggestions for relevant form fields based on step content.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to analyze
            
        Returns:
            List of suggested form field configurations
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        self._validate_step_id(step_id)
        
        try:
            # Get the step details to analyze
            step = self._get_step_details(org_id, template_id, step_id)
            if not step:
                raise TallyfyError(f"Step {step_id} not found")
            
            # Get template context for better suggestions
            template = self.sdk.get_template(org_id, template_id)
            if not template:
                raise TallyfyError(f"Template {template_id} not found")
            
            # Analyze step content for intelligent suggestions
            step_title = step.title.lower() if step.title else ''
            step_summary = step.summary.lower() if step.summary else ''
            step_type = step.step_type or 'task'
            existing_fields = step.captures or []
            
            # Combined text for analysis
            step_text = f"{step_title} {step_summary}".strip()
            
            suggestions = []
            
            # Get field patterns for analysis
            field_patterns = self._get_field_patterns()
            
            # Check existing field types to avoid duplicates
            existing_field_types = set()
            existing_field_labels = set()
            for field in existing_fields:
                if hasattr(field, 'field_type'):
                    existing_field_types.add(field.field_type)
                if hasattr(field, 'label'):
                    existing_field_labels.add(field.label.lower())
            
            # Analyze step content against patterns
            matched_patterns = []
            for pattern_name, pattern_data in field_patterns.items():
                keyword_matches = sum(1 for keyword in pattern_data['keywords'] if keyword in step_text)
                if keyword_matches > 0:
                    matched_patterns.append((pattern_name, keyword_matches, pattern_data))
            
            # Sort by relevance (number of keyword matches)
            matched_patterns.sort(key=lambda x: x[1], reverse=True)
            
            # Generate suggestions from matched patterns
            suggested_count = 0
            max_suggestions = 5
            
            for pattern_name, matches, pattern_data in matched_patterns:
                if suggested_count >= max_suggestions:
                    break
                    
                for field_config in pattern_data['fields']:
                    if suggested_count >= max_suggestions:
                        break
                    
                    # Skip if similar field already exists
                    field_label_lower = field_config['label'].lower()
                    if field_label_lower in existing_field_labels:
                        continue
                    
                    # Add suggestion with metadata
                    suggestion = {
                        'field_config': field_config.copy(),
                        'confidence': min(0.9, 0.3 + (matches * 0.2)),  # Confidence based on keyword matches
                        'pattern_matched': pattern_name,
                        'keyword_matches': matches,
                        'priority': 'high' if matches >= 2 else 'medium' if matches >= 1 else 'low'
                    }
                    
                    # Add position suggestion
                    suggestion['field_config']['position'] = len(existing_fields) + suggested_count + 1
                    
                    suggestions.append(suggestion)
                    suggested_count += 1
            
            # If no specific patterns matched, provide generic useful fields
            if not suggestions:
                suggestions = self._get_generic_suggestions(existing_fields)
            
            # Add implementation guidance
            for suggestion in suggestions:
                suggestion['implementation'] = {
                    'method': 'add_form_field_to_step',
                    'parameters': {
                        'org_id': org_id,
                        'template_id': template_id,
                        'step_id': step_id,
                        'field_data': suggestion['field_config']
                    }
                }
            
            return suggestions
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "suggest form fields for step", org_id=org_id, template_id=template_id, step_id=step_id)

    def _get_step_details(self, org_id: str, template_id: str, step_id: str) -> Optional[Step]:
        """
        Get step details using CRUD operations to avoid circular imports.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            
        Returns:
            Step object or None if not found
        """
        from .crud_operations import FormFieldCRUD
        crud = FormFieldCRUD(self.sdk)
        return crud.get_step(org_id, template_id, step_id)

    def _get_field_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Get predefined field patterns for content analysis.
        
        Returns:
            Dictionary of field patterns with keywords and suggested fields
        """
        return {
            # Approval and Review patterns
            'approval': {
                'keywords': ['approve', 'review', 'sign off', 'accept', 'reject', 'confirm'],
                'fields': [
                    {
                        'field_type': 'dropdown',
                        'label': 'Decision',
                        'options': [
                            {'value': 'approved', 'label': 'Approved'}, 
                            {'value': 'rejected', 'label': 'Rejected'}, 
                            {'value': 'needs_revision', 'label': 'Needs Revision'}
                        ],
                        'required': True,
                        'reasoning': 'Approval steps typically need a decision field'
                    },
                    {
                        'field_type': 'textarea',
                        'label': 'Comments',
                        'required': False,
                        'reasoning': 'Comments are useful for providing feedback'
                    }
                ]
            },
            
            # Contact and Communication patterns
            'contact': {
                'keywords': ['contact', 'call', 'email', 'phone', 'reach out', 'communicate'],
                'fields': [
                    {
                        'field_type': 'text',
                        'label': 'Contact Method',
                        'required': True,
                        'reasoning': 'Track how contact was made'
                    },
                    {
                        'field_type': 'date',
                        'label': 'Contact Date',
                        'required': True,
                        'reasoning': 'Record when contact was made'
                    },
                    {
                        'field_type': 'textarea',
                        'label': 'Contact Notes',
                        'required': False,
                        'reasoning': 'Document the conversation or interaction'
                    }
                ]
            },
            
            # Document and File patterns
            'document': {
                'keywords': ['document', 'file', 'upload', 'attach', 'report', 'contract', 'agreement'],
                'fields': [
                    {
                        'field_type': 'file',
                        'label': 'Document Upload',
                        'required': True,
                        'reasoning': 'File upload for document-related steps'
                    },
                    {
                        'field_type': 'text',
                        'label': 'Document Title',
                        'required': False,
                        'reasoning': 'Name or title of the document'
                    },
                    {
                        'field_type': 'textarea',
                        'label': 'Document Description',
                        'required': False,
                        'reasoning': 'Brief description of the document'
                    }
                ]
            },
            
            # Payment and Financial patterns
            'payment': {
                'keywords': ['payment', 'invoice', 'cost', 'price', 'amount', 'bill', 'expense'],
                'fields': [
                    {
                        'field_type': 'number',
                        'label': 'Amount',
                        'required': True,
                        'reasoning': 'Financial steps need amount tracking'
                    },
                    {
                        'field_type': 'dropdown',
                        'label': 'Currency',
                        'options': [
                            {'value': 'USD', 'label': 'USD'}, 
                            {'value': 'EUR', 'label': 'EUR'}, 
                            {'value': 'GBP', 'label': 'GBP'}
                        ],
                        'required': True,
                        'reasoning': 'Specify currency for financial transactions'
                    },
                    {
                        'field_type': 'date',
                        'label': 'Payment Date',
                        'required': False,
                        'reasoning': 'Track when payment was made'
                    }
                ]
            },
            
            # Quality and Testing patterns
            'quality': {
                'keywords': ['test', 'quality', 'check', 'verify', 'validate', 'inspect'],
                'fields': [
                    {
                        'field_type': 'dropdown',
                        'label': 'Test Result',
                        'options': [
                            {'value': 'pass', 'label': 'Pass'}, 
                            {'value': 'fail', 'label': 'Fail'}, 
                            {'value': 'partial', 'label': 'Partial Pass'}
                        ],
                        'required': True,
                        'reasoning': 'Quality steps need result tracking'
                    },
                    {
                        'field_type': 'textarea',
                        'label': 'Test Notes',
                        'required': False,
                        'reasoning': 'Document test findings and issues'
                    },
                    {
                        'field_type': 'number',
                        'label': 'Score',
                        'required': False,
                        'reasoning': 'Numerical rating for quality assessment'
                    }
                ]
            },
            
            # Schedule and Time patterns
            'schedule': {
                'keywords': ['schedule', 'meeting', 'appointment', 'deadline', 'due', 'time'],
                'fields': [
                    {
                        'field_type': 'datetime',
                        'label': 'Scheduled Time',
                        'required': True,
                        'reasoning': 'Scheduling steps need date and time'
                    },
                    {
                        'field_type': 'text',
                        'label': 'Location',
                        'required': False,
                        'reasoning': 'Meeting location or venue'
                    },
                    {
                        'field_type': 'textarea',
                        'label': 'Agenda',
                        'required': False,
                        'reasoning': 'Meeting agenda or notes'
                    }
                ]
            }
        }

    def _get_generic_suggestions(self, existing_fields: List) -> List[Dict[str, Any]]:
        """
        Get generic form field suggestions when no specific patterns match.
        
        Args:
            existing_fields: List of existing form fields on the step
            
        Returns:
            List of generic field suggestions
        """
        return [
            {
                'field_config': {
                    'field_type': 'textarea',
                    'label': 'Notes',
                    'required': False,
                    'position': len(existing_fields) + 1
                },
                'confidence': 0.6,
                'pattern_matched': 'generic',
                'keyword_matches': 0,
                'priority': 'medium',
                'reasoning': 'Notes field is useful for most steps to capture additional information'
            },
            {
                'field_config': {
                    'field_type': 'dropdown',
                    'label': 'Status',
                    'options': [
                        {'value': 'completed', 'label': 'Completed'}, 
                        {'value': 'in_progress', 'label': 'In Progress'}, 
                        {'value': 'blocked', 'label': 'Blocked'}
                    ],
                    'required': False,
                    'position': len(existing_fields) + 2
                },
                'confidence': 0.5,
                'pattern_matched': 'generic',
                'keyword_matches': 0,
                'priority': 'low',
                'reasoning': 'Status tracking can be helpful for workflow management'
            }
        ]

    def suggest_field_improvements(self, org_id: str, template_id: str, step_id: str, field_id: str) -> List[Dict[str, Any]]:
        """
        Suggest improvements for an existing form field.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID to analyze
            
        Returns:
            List of improvement suggestions
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            # Get current field options using options management
            from .options_management import FormFieldOptions
            options_manager = FormFieldOptions(self.sdk)
            
            current_options = options_manager.get_dropdown_options(org_id, template_id, step_id, field_id)
            
            improvements = []
            
            # Analyze dropdown options if applicable
            if current_options:
                # Check for common improvements
                if len(current_options) > 10:
                    improvements.append({
                        'type': 'reduce_options',
                        'priority': 'medium',
                        'description': 'Consider reducing the number of dropdown options for better usability',
                        'recommendation': 'Group similar options or use a search-enabled dropdown',
                        'current_count': len(current_options)
                    })
                
                # Check for inconsistent naming
                option_lengths = [len(opt) for opt in current_options]
                if max(option_lengths) - min(option_lengths) > 20:
                    improvements.append({
                        'type': 'normalize_options',
                        'priority': 'low',
                        'description': 'Option labels have inconsistent lengths',
                        'recommendation': 'Standardize option label lengths for better visual consistency'
                    })
            
            return improvements
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "suggest field improvements", org_id=org_id, template_id=template_id, step_id=step_id, field_id=field_id)