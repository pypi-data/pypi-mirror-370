"""
Template analysis functionality for providing insights and recommendations
"""

from typing import List, Optional, Dict, Any
from .base import TemplateManagerBase
from ..models import Template, TallyfyError


class TemplateAnalysis(TemplateManagerBase):
    """Handles template analysis and provides optimization recommendations"""

    def get_step_dependencies(self, org_id: str, template_id: str, step_id: str) -> Dict[str, Any]:
        """
        Analyze step dependencies and automation effects.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to analyze dependencies for
            
        Returns:
            Dictionary containing dependency analysis with step info, automation rules, dependencies, and affected elements
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            # Get template with full data including steps and automations
            template_endpoint = f"organizations/{org_id}/checklists/{template_id}"
            template_params = {'with': 'steps,automated_actions,prerun'}
            template_response = self.sdk._make_request('GET', template_endpoint, params=template_params)
            
            template_data = self._extract_data(template_response)
            if not template_data:
                raise TallyfyError("Unable to retrieve template data for dependency analysis")
            
            # Find the target step
            steps = template_data.get('steps', [])
            target_step = None
            for step in steps:
                if step.get('id') == step_id:
                    target_step = step
                    break
            
            if not target_step:
                raise TallyfyError(f"Step {step_id} not found in template {template_id}")
            
            # Analyze automations for dependencies
            automations = template_data.get('automated_actions', [])
            dependencies = {
                'incoming': [],  # Steps that affect this step
                'outgoing': [],  # Steps this step affects
                'field_dependencies': [],  # Form fields this step depends on
                'conditional_visibility': []  # Visibility conditions
            }
            
            step_position = target_step.get('position', 0)
            
            # Analyze each automation rule
            for automation in automations:
                conditions = automation.get('conditions', [])
                actions = automation.get('actions', [])
                
                # Check if this step is affected by the automation
                step_affected_by_conditions = False
                step_affects_others = False
                
                for condition in conditions:
                    condition_type = condition.get('type', '')
                    condition_step = condition.get('step_id')
                    
                    # Check if condition affects our target step
                    if condition_step == step_id:
                        step_affected_by_conditions = True
                    elif condition_type in ['step_completed', 'step_started']:
                        if condition_step:
                            for step in steps:
                                if step.get('id') == condition_step:
                                    dependencies['incoming'].append({
                                        'step_id': condition_step,
                                        'step_title': step.get('title', 'Unknown'),
                                        'condition_type': condition_type,
                                        'automation_id': automation.get('id'),
                                        'description': f"Step depends on '{step.get('title')}' being {condition_type.replace('_', ' ')}"
                                    })
                
                # Check if this step's actions affect other steps
                for action in actions:
                    action_type = action.get('type', '')
                    target_step_id = action.get('step_id')
                    
                    if target_step_id and target_step_id != step_id:
                        # This step affects another step
                        affected_step = None
                        for step in steps:
                            if step.get('id') == target_step_id:
                                affected_step = step
                                break
                        
                        if affected_step:
                            dependencies['outgoing'].append({
                                'step_id': target_step_id,
                                'step_title': affected_step.get('title', 'Unknown'),
                                'action_type': action_type,
                                'automation_id': automation.get('id'),
                                'description': f"Step triggers '{action_type}' on '{affected_step.get('title')}'"
                            })
                            step_affects_others = True
                
                # Check for field dependencies
                for condition in conditions:
                    if condition.get('type') == 'field_value':
                        field_label = condition.get('field_label', 'Unknown Field')
                        field_value = condition.get('value', '')
                        dependencies['field_dependencies'].append({
                            'field_label': field_label,
                            'expected_value': field_value,
                            'condition_type': 'field_value',
                            'automation_id': automation.get('id'),
                            'description': f"Depends on field '{field_label}' having value '{field_value}'"
                        })
                
                # Check for visibility conditions affecting this step
                if step_affected_by_conditions:
                    for action in actions:
                        if action.get('type') in ['show_step', 'hide_step'] and action.get('step_id') == step_id:
                            dependencies['conditional_visibility'].append({
                                'action_type': action.get('type'),
                                'automation_id': automation.get('id'),
                                'description': f"Step visibility controlled by automation conditions"
                            })
            
            # Calculate dependency complexity score
            total_deps = (len(dependencies['incoming']) + len(dependencies['outgoing']) + 
                         len(dependencies['field_dependencies']) + len(dependencies['conditional_visibility']))
            
            complexity_score = min(100, total_deps * 10)  # Cap at 100
            
            complexity_level = "Low"
            if complexity_score > 70:
                complexity_level = "High"
            elif complexity_score > 30:
                complexity_level = "Medium"
            
            return {
                'step_info': {
                    'id': step_id,
                    'title': target_step.get('title', 'Unknown'),
                    'position': step_position,
                    'summary': target_step.get('summary', '')
                },
                'dependencies': dependencies,
                'complexity_analysis': {
                    'score': complexity_score,
                    'level': complexity_level,
                    'total_dependencies': total_deps,
                    'incoming_count': len(dependencies['incoming']),
                    'outgoing_count': len(dependencies['outgoing']),
                    'field_dependencies_count': len(dependencies['field_dependencies']),
                    'visibility_conditions_count': len(dependencies['conditional_visibility'])
                },
                'recommendations': self._generate_dependency_recommendations(dependencies, complexity_level),
                'template_id': template_id,
                'analysis_timestamp': self.sdk._get_current_timestamp() if hasattr(self.sdk, '_get_current_timestamp') else None
            }
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "analyze step dependencies", org_id=org_id, template_id=template_id, step_id=step_id)

    def suggest_step_deadline(self, org_id: str, template_id: str, step_id: str) -> Dict[str, Any]:
        """
        Suggest reasonable deadlines based on step analysis.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to suggest deadline for
            
        Returns:
            Dictionary with suggested deadline configuration, reasoning, and alternatives
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            # Get template with steps
            template_endpoint = f"organizations/{org_id}/checklists/{template_id}"
            template_params = {'with': 'steps'}
            template_response = self.sdk._make_request('GET', template_endpoint, params=template_params)
            
            template_data = self._extract_data(template_response)
            if not template_data:
                raise TallyfyError("Unable to retrieve template data for deadline analysis")
            
            # Find the target step
            steps = template_data.get('steps', [])
            target_step = None
            for step in steps:
                if step.get('id') == step_id:
                    target_step = step
                    break
            
            if not target_step:
                raise TallyfyError(f"Step {step_id} not found in template {template_id}")
            
            step_title = target_step.get('title', '').lower()
            step_summary = target_step.get('summary', '').lower()
            step_content = f"{step_title} {step_summary}"
            
            # Analyze step content for deadline suggestions
            suggestions = []
            
            # Quick tasks (same day)
            quick_keywords = ['review', 'approve', 'check', 'confirm', 'verify', 'acknowledge', 'sign off']
            if any(keyword in step_content for keyword in quick_keywords):
                suggestions.append({
                    'value': 4,
                    'unit': 'hours',
                    'option': 'from',
                    'confidence': 85,
                    'reasoning': 'Quick review/approval tasks typically require immediate attention',
                    'category': 'quick_action'
                })
            
            # Communication tasks
            comm_keywords = ['email', 'call', 'contact', 'notify', 'inform', 'communicate', 'reach out']
            if any(keyword in step_content for keyword in comm_keywords):
                suggestions.append({
                    'value': 1,
                    'unit': 'days',
                    'option': 'from',
                    'confidence': 80,
                    'reasoning': 'Communication tasks should be handled promptly for good workflow',
                    'category': 'communication'
                })
            
            # Analysis/Research tasks
            analysis_keywords = ['analyze', 'research', 'investigate', 'study', 'evaluate', 'assess', 'examine']
            if any(keyword in step_content for keyword in analysis_keywords):
                suggestions.append({
                    'value': 3,
                    'unit': 'days',
                    'option': 'from',
                    'confidence': 75,
                    'reasoning': 'Analysis tasks require time for thorough investigation',
                    'category': 'analysis'
                })
            
            # Document/Report creation
            doc_keywords = ['document', 'report', 'write', 'create', 'draft', 'prepare', 'compile']
            if any(keyword in step_content for keyword in doc_keywords):
                suggestions.append({
                    'value': 5,
                    'unit': 'days',
                    'option': 'from',
                    'confidence': 70,
                    'reasoning': 'Document creation requires adequate time for quality output',
                    'category': 'documentation'
                })
            
            # Meeting/Presentation tasks
            meeting_keywords = ['meeting', 'present', 'presentation', 'demo', 'workshop', 'training']
            if any(keyword in step_content for keyword in meeting_keywords):
                suggestions.append({
                    'value': 1,
                    'unit': 'weeks',
                    'option': 'from',
                    'confidence': 65,
                    'reasoning': 'Meetings and presentations need time for scheduling and preparation',
                    'category': 'meeting'
                })
            
            # Testing/QA tasks
            test_keywords = ['test', 'testing', 'qa', 'quality', 'validate', 'verify functionality']
            if any(keyword in step_content for keyword in test_keywords):
                suggestions.append({
                    'value': 2,
                    'unit': 'days',
                    'option': 'from',
                    'confidence': 80,
                    'reasoning': 'Testing requires time for thorough validation',
                    'category': 'testing'
                })
            
            # Default fallback suggestion
            if not suggestions:
                suggestions.append({
                    'value': 2,
                    'unit': 'days',
                    'option': 'from',
                    'confidence': 50,
                    'reasoning': 'General task deadline based on common workflow patterns',
                    'category': 'general'
                })
            
            # Sort suggestions by confidence
            suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Get the best suggestion
            best_suggestion = suggestions[0]
            
            # Generate alternative suggestions
            alternatives = []
            base_value = best_suggestion['value']
            base_unit = best_suggestion['unit']
            
            if base_unit == 'hours':
                alternatives = [
                    {'value': base_value * 2, 'unit': 'hours', 'description': 'Extended timeline'},
                    {'value': 1, 'unit': 'days', 'description': 'Next business day'}
                ]
            elif base_unit == 'days':
                alternatives = [
                    {'value': max(1, base_value // 2), 'unit': 'days', 'description': 'Rushed timeline'},
                    {'value': base_value * 2, 'unit': 'days', 'description': 'Extended timeline'},
                    {'value': 1, 'unit': 'weeks', 'description': 'Weekly milestone'}
                ]
            elif base_unit == 'weeks':
                alternatives = [
                    {'value': base_value * 7, 'unit': 'days', 'description': 'Daily breakdown'},
                    {'value': base_value * 2, 'unit': 'weeks', 'description': 'Extended timeline'}
                ]
            
            return {
                'step_info': {
                    'id': step_id,
                    'title': target_step.get('title', 'Unknown'),
                    'summary': target_step.get('summary', '')
                },
                'suggested_deadline': best_suggestion,
                'alternative_suggestions': alternatives,
                'all_matches': suggestions,
                'analysis': {
                    'content_analyzed': step_content[:100] + '...' if len(step_content) > 100 else step_content,
                    'keywords_found': [keyword for keyword in quick_keywords + comm_keywords + analysis_keywords + doc_keywords + meeting_keywords + test_keywords if keyword in step_content],
                    'suggestion_count': len(suggestions)
                },
                'template_id': template_id
            }
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "suggest step deadline", org_id=org_id, template_id=template_id, step_id=step_id)

    def get_step_visibility_conditions(self, org_id: str, template_id: str, step_id: str) -> Dict[str, Any]:
        """
        Analyze when/how steps become visible based on automations.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to analyze visibility for
            
        Returns:
            Dictionary containing step visibility analysis, rules, behavior patterns, and recommendations
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            # Get template with automations and steps
            template_endpoint = f"organizations/{org_id}/checklists/{template_id}"
            template_params = {'with': 'steps,automated_actions,prerun'}
            template_response = self.sdk._make_request('GET', template_endpoint, params=template_params)
            
            template_data = self._extract_data(template_response)
            if not template_data:
                raise TallyfyError("Unable to retrieve template data for visibility analysis")
            
            # Find the target step
            steps = template_data.get('steps', [])
            target_step = None
            for step in steps:
                if step.get('id') == step_id:
                    target_step = step
                    break
            
            if not target_step:
                raise TallyfyError(f"Step {step_id} not found in template {template_id}")
            
            automations = template_data.get('automated_actions', [])
            
            visibility_rules = {
                'show_rules': [],
                'hide_rules': [],
                'conditional_rules': []
            }
            
            step_name_map = {step.get('id'): step.get('title', 'Unknown') for step in steps}
            
            # Analyze automation rules affecting this step's visibility
            for automation in automations:
                automation_id = automation.get('id')
                conditions = automation.get('conditions', [])
                actions = automation.get('actions', [])
                
                # Check if this automation affects our target step's visibility
                for action in actions:
                    if action.get('step_id') == step_id:
                        action_type = action.get('type', '')
                        
                        if action_type in ['show_step', 'hide_step']:
                            # Analyze conditions that trigger this visibility change
                            rule_conditions = []
                            for condition in conditions:
                                condition_summary = self._summarize_condition(condition, step_name_map)
                                rule_conditions.append(condition_summary)
                            
                            rule_info = {
                                'automation_id': automation_id,
                                'action_type': action_type,
                                'conditions': rule_conditions,
                                'conditions_count': len(conditions),
                                'rule_logic': automation.get('condition_logic', 'AND'),
                                'description': f"Step will be {action_type.replace('_', ' ')} when: {' AND '.join(rule_conditions) if automation.get('condition_logic', 'AND') == 'AND' else ' OR '.join(rule_conditions)}"
                            }
                            
                            if action_type == 'show_step':
                                visibility_rules['show_rules'].append(rule_info)
                            elif action_type == 'hide_step':
                                visibility_rules['hide_rules'].append(rule_info)
            
            # Determine step's default visibility
            default_visibility = "visible"  # Most steps are visible by default
            
            # Check if step has any show rules (implies it might be hidden by default)
            if visibility_rules['show_rules']:
                default_visibility = "conditionally_visible"
            
            # Analyze visibility complexity
            total_rules = len(visibility_rules['show_rules']) + len(visibility_rules['hide_rules'])
            
            complexity_level = "Simple"
            if total_rules > 3:
                complexity_level = "Complex"
            elif total_rules > 1:
                complexity_level = "Moderate"
            
            # Generate visibility behavior analysis
            behavior_patterns = []
            
            if not visibility_rules['show_rules'] and not visibility_rules['hide_rules']:
                behavior_patterns.append("Step is always visible (no conditional visibility rules)")
            
            if visibility_rules['show_rules']:
                behavior_patterns.append(f"Step becomes visible based on {len(visibility_rules['show_rules'])} condition(s)")
            
            if visibility_rules['hide_rules']:
                behavior_patterns.append(f"Step can be hidden based on {len(visibility_rules['hide_rules'])} condition(s)")
            
            if visibility_rules['show_rules'] and visibility_rules['hide_rules']:
                behavior_patterns.append("Step has both show and hide rules - visibility depends on rule evaluation order")
            
            return {
                'step_info': {
                    'id': step_id,
                    'title': target_step.get('title', 'Unknown'),
                    'default_visibility': default_visibility
                },
                'visibility_rules': visibility_rules,
                'behavior_analysis': {
                    'patterns': behavior_patterns,
                    'complexity_level': complexity_level,
                    'total_rules': total_rules,
                    'has_conditional_visibility': total_rules > 0
                },
                'recommendations': self._generate_visibility_recommendations(visibility_rules, complexity_level),
                'template_id': template_id
            }
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "analyze step visibility conditions", org_id=org_id, template_id=template_id, step_id=step_id)

    def suggest_kickoff_fields(self, org_id: str, template_id: str) -> List[Dict[str, Any]]:
        """
        Suggest relevant kickoff fields based on template analysis.
        
        Args:
            org_id: Organization ID
            template_id: Template ID to analyze
            
        Returns:
            List of suggested kickoff field configurations with reasoning
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            # Get template with full data
            template_endpoint = f"organizations/{org_id}/checklists/{template_id}"
            template_params = {'with': 'steps,automated_actions,prerun'}
            template_response = self.sdk._make_request('GET', template_endpoint, params=template_params)
            
            template_data = self._extract_data(template_response)
            if not template_data:
                raise TallyfyError("Unable to retrieve template data for kickoff field analysis")
            
            template_title = template_data.get('title', '').lower()
            template_summary = template_data.get('summary', '').lower()
            steps = template_data.get('steps', [])
            existing_prerun = template_data.get('prerun', [])
            
            # Collect all step content for analysis
            all_step_content = ""
            for step in steps:
                step_title = step.get('title', '').lower()
                step_summary = step.get('summary', '').lower()
                all_step_content += f" {step_title} {step_summary}"
            
            combined_content = f"{template_title} {template_summary} {all_step_content}"
            
            suggestions = []
            
            # Get existing field labels to avoid duplicates
            existing_labels = [field.get('label', '').lower() for field in existing_prerun]
            
            # Client/Customer information fields
            client_keywords = ['client', 'customer', 'company', 'organization', 'business', 'vendor', 'supplier']
            if any(keyword in combined_content for keyword in client_keywords):
                if 'client name' not in existing_labels and 'customer name' not in existing_labels:
                    suggestions.append({
                        'label': 'Client Name',
                        'type': 'text',
                        'required': True,
                        'description': 'Name of the client or customer for this process',
                        'reasoning': 'Template content suggests client/customer involvement',
                        'confidence': 85,
                        'category': 'client_info'
                    })
                
                if 'contact email' not in existing_labels and 'email' not in existing_labels:
                    suggestions.append({
                        'label': 'Contact Email',
                        'type': 'email',
                        'required': True,
                        'description': 'Primary email contact for this process',
                        'reasoning': 'Client/customer processes typically require contact information',
                        'confidence': 80,
                        'category': 'client_info'
                    })
            
            # Project information fields
            project_keywords = ['project', 'initiative', 'campaign', 'launch', 'implementation', 'rollout']
            if any(keyword in combined_content for keyword in project_keywords):
                if 'project name' not in existing_labels:
                    suggestions.append({
                        'label': 'Project Name',
                        'type': 'text',
                        'required': True,
                        'description': 'Name or title of the project',
                        'reasoning': 'Template appears to be project-related',
                        'confidence': 90,
                        'category': 'project_info'
                    })
                
                if 'project budget' not in existing_labels and 'budget' not in existing_labels:
                    suggestions.append({
                        'label': 'Project Budget',
                        'type': 'number',
                        'required': False,
                        'description': 'Budget allocated for this project',
                        'reasoning': 'Project templates often need budget tracking',
                        'confidence': 70,
                        'category': 'project_info'
                    })
            
            # Date-related fields
            date_keywords = ['deadline', 'due date', 'launch date', 'start date', 'completion', 'delivery']
            if any(keyword in combined_content for keyword in date_keywords):
                if 'target completion date' not in existing_labels and 'due date' not in existing_labels:
                    suggestions.append({
                        'label': 'Target Completion Date',
                        'type': 'date',
                        'required': True,
                        'description': 'When this process should be completed',
                        'reasoning': 'Template content mentions dates and deadlines',
                        'confidence': 85,
                        'category': 'scheduling'
                    })
            
            # Priority/Urgency fields
            priority_keywords = ['priority', 'urgent', 'critical', 'important', 'high priority', 'rush']
            if any(keyword in combined_content for keyword in priority_keywords):
                if 'priority level' not in existing_labels and 'priority' not in existing_labels:
                    suggestions.append({
                        'label': 'Priority Level',
                        'type': 'select',
                        'required': True,
                        'options': ['Low', 'Medium', 'High', 'Critical'],
                        'description': 'Priority level for this process',
                        'reasoning': 'Template content indicates priority considerations',
                        'confidence': 75,
                        'category': 'prioritization'
                    })
            
            # Department/Team fields
            dept_keywords = ['department', 'team', 'division', 'group', 'unit', 'office', 'branch']
            if any(keyword in combined_content for keyword in dept_keywords):
                if 'department' not in existing_labels and 'team' not in existing_labels:
                    suggestions.append({
                        'label': 'Department',
                        'type': 'text',
                        'required': False,
                        'description': 'Department or team responsible for this process',
                        'reasoning': 'Template mentions departments or teams',
                        'confidence': 70,
                        'category': 'organization'
                    })
            
            # Document/File fields
            doc_keywords = ['document', 'file', 'attachment', 'upload', 'report', 'contract', 'agreement']
            if any(keyword in combined_content for keyword in doc_keywords):
                if 'supporting documents' not in existing_labels and 'attachments' not in existing_labels:
                    suggestions.append({
                        'label': 'Supporting Documents',
                        'type': 'file',
                        'required': False,
                        'description': 'Upload any relevant documents for this process',
                        'reasoning': 'Template involves document handling',
                        'confidence': 65,
                        'category': 'documentation'
                    })
            
            # Financial fields
            financial_keywords = ['cost', 'price', 'amount', 'budget', 'expense', 'fee', 'payment', 'invoice']
            if any(keyword in combined_content for keyword in financial_keywords):
                if 'estimated cost' not in existing_labels and 'cost' not in existing_labels:
                    suggestions.append({
                        'label': 'Estimated Cost',
                        'type': 'number',
                        'required': False,
                        'description': 'Estimated cost for this process',
                        'reasoning': 'Template involves financial considerations',
                        'confidence': 75,
                        'category': 'financial'
                    })
            
            # Generic description field
            if 'description' not in existing_labels and 'details' not in existing_labels:
                suggestions.append({
                    'label': 'Additional Details',
                    'type': 'textarea',
                    'required': False,
                    'description': 'Any additional information or special requirements',
                    'reasoning': 'Provides flexibility for process-specific information',
                    'confidence': 60,
                    'category': 'general'
                })
            
            # Sort suggestions by confidence score
            suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            
            return suggestions
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "suggest kickoff fields", org_id=org_id, template_id=template_id)

    def suggest_automation_consolidation(self, org_id: str, template_id: str) -> List[Dict[str, Any]]:
        """
        AI analysis with consolidation recommendations.
        
        Args:
            org_id: Organization ID
            template_id: Template ID to analyze
            
        Returns:
            List of consolidation recommendations with detailed analysis
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            # Use the existing analyze_template_automations method
            automation_analysis = self.analyze_template_automations(org_id, template_id)
            
            recommendations = []
            
            # Extract automation data from analysis
            automations = automation_analysis.get('automations', [])
            redundancies = automation_analysis.get('analysis', {}).get('redundant_rules', [])
            conflicts = automation_analysis.get('analysis', {}).get('conflicting_rules', [])
            
            # Critical issues first
            if conflicts:
                recommendations.append({
                    'type': 'critical',
                    'priority': 'high',
                    'title': 'Resolve Conflicting Automation Rules',
                    'description': f'Found {len(conflicts)} conflicting automation rules that may cause unpredictable behavior',
                    'affected_automations': [conflict['automation_ids'] for conflict in conflicts],
                    'action_required': 'Review and modify conflicting rules to ensure consistent behavior',
                    'impact': 'High - Can cause workflow failures or unexpected results',
                    'effort': 'Medium - Requires careful analysis of rule interactions',
                    'details': conflicts
                })
            
            # Redundancy consolidation
            if redundancies:
                recommendations.append({
                    'type': 'optimization',
                    'priority': 'medium',
                    'title': 'Consolidate Redundant Automation Rules',
                    'description': f'Found {len(redundancies)} sets of redundant rules that can be consolidated',
                    'affected_automations': [red['automation_ids'] for red in redundancies],
                    'action_required': 'Combine similar rules to reduce complexity and improve maintainability',
                    'impact': 'Medium - Improves template performance and reduces maintenance overhead',
                    'effort': 'Low - Simple consolidation of similar rules',
                    'details': redundancies
                })
            
            # Complex rule simplification
            complex_rules = [auto for auto in automations if len(auto.get('conditions', [])) > 3]
            if complex_rules:
                recommendations.append({
                    'type': 'simplification',
                    'priority': 'low',
                    'title': 'Simplify Complex Automation Rules',
                    'description': f'Found {len(complex_rules)} automation rules with high complexity',
                    'affected_automations': [rule.get('id') for rule in complex_rules],
                    'action_required': 'Break down complex rules into simpler, more manageable components',
                    'impact': 'Low - Improves rule understanding and debugging',
                    'effort': 'Medium - Requires careful rule restructuring',
                    'details': [{
                        'automation_id': rule.get('id'),
                        'condition_count': len(rule.get('conditions', [])),
                        'action_count': len(rule.get('actions', []))
                    } for rule in complex_rules]
                })
            
            # Unused automation detection
            all_step_ids = set()
            for auto in automations:
                for condition in auto.get('conditions', []):
                    if condition.get('step_id'):
                        all_step_ids.add(condition.get('step_id'))
                for action in auto.get('actions', []):
                    if action.get('step_id'):
                        all_step_ids.add(action.get('step_id'))
            
            # Get template steps to check for unused automations
            template_endpoint = f"organizations/{org_id}/checklists/{template_id}"
            template_params = {'with': 'steps'}
            template_response = self.sdk._make_request('GET', template_endpoint, params=template_params)
            template_data = self._extract_data(template_response)
            
            if template_data:
                actual_step_ids = {step.get('id') for step in template_data.get('steps', [])}
                orphaned_step_refs = all_step_ids - actual_step_ids
                
                if orphaned_step_refs:
                    recommendations.append({
                        'type': 'cleanup',
                        'priority': 'low',
                        'title': 'Remove References to Deleted Steps',
                        'description': f'Found automation rules referencing {len(orphaned_step_refs)} non-existent steps',
                        'affected_automations': [],  # Would need deeper analysis to identify
                        'action_required': 'Remove or update automation rules that reference deleted steps',
                        'impact': 'Low - Prevents potential errors and improves template cleanliness',
                        'effort': 'Low - Simple cleanup of outdated references',
                        'details': {'orphaned_step_ids': list(orphaned_step_refs)}
                    })
            
            # Performance optimization suggestions
            if len(automations) > 10:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'title': 'Optimize Automation Performance',
                    'description': f'Template has {len(automations)} automation rules - consider optimization',
                    'affected_automations': [auto.get('id') for auto in automations],
                    'action_required': 'Review automation necessity and consolidate where possible',
                    'impact': 'Medium - Improves template execution speed',
                    'effort': 'Medium - Requires comprehensive automation review',
                    'details': {
                        'total_automations': len(automations),
                        'recommendation': 'Consider if all automations are necessary or if some can be combined'
                    }
                })
            
            # If no specific issues found, provide general optimization advice
            if not recommendations:
                recommendations.append({
                    'type': 'maintenance',
                    'priority': 'low',
                    'title': 'Automation Health Check Passed',
                    'description': 'No critical automation issues detected',
                    'affected_automations': [],
                    'action_required': 'Continue monitoring automation performance',
                    'impact': 'Low - Template automations are functioning well',
                    'effort': 'None - No immediate action required',
                    'details': {
                        'total_automations': len(automations),
                        'status': 'healthy'
                    }
                })
            
            return recommendations
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "suggest automation consolidation", org_id=org_id, template_id=template_id)

    def _calculate_field_similarity(self, field1_label: str, field2_label: str) -> float:
        """
        Helper for field similarity calculation.
        
        Args:
            field1_label: First field label
            field2_label: Second field label
            
        Returns:
            Float representing similarity score (0.0 to 1.0)
        """
        # Simple word-based similarity calculation
        words1 = set(field1_label.lower().split())
        words2 = set(field2_label.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def analyze_template_automations(self, org_id: str, template_id: str) -> Dict[str, Any]:
        """
        Core automation analysis method used by multiple functions.
        
        Args:
            org_id: Organization ID
            template_id: Template ID to analyze
            
        Returns:
            Dictionary containing comprehensive automation analysis
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            # Get template with automation data
            template_endpoint = f"organizations/{org_id}/checklists/{template_id}"
            template_params = {'with': 'steps,automated_actions,prerun'}
            template_response = self.sdk._make_request('GET', template_endpoint, params=template_params)
            
            template_data = self._extract_data(template_response)
            if not template_data:
                raise TallyfyError("Unable to retrieve template data for automation analysis")
            
            automations = template_data.get('automated_actions', [])
            steps = template_data.get('steps', [])
            
            # Create step lookup
            step_lookup = {step.get('id'): step.get('title', 'Unknown') for step in steps}
            
            analysis = {
                'redundant_rules': [],
                'conflicting_rules': [],
                'complex_rules': [],
                'simple_rules': [],
                'statistics': {
                    'total_automations': len(automations),
                    'avg_conditions_per_rule': 0,
                    'avg_actions_per_rule': 0
                }
            }
            
            # Analyze each automation
            total_conditions = 0
            total_actions = 0
            
            for i, automation in enumerate(automations):
                conditions = automation.get('conditions', [])
                actions = automation.get('actions', [])
                
                total_conditions += len(conditions)
                total_actions += len(actions)
                
                # Classify by complexity
                if len(conditions) > 3 or len(actions) > 2:
                    analysis['complex_rules'].append(automation.get('id'))
                else:
                    analysis['simple_rules'].append(automation.get('id'))
                
                # Check for redundancy with other automations
                for j, other_automation in enumerate(automations[i+1:], i+1):
                    similarity = self._analyze_condition_similarity(
                        conditions, other_automation.get('conditions', [])
                    )
                    
                    if similarity > 0.8:  # High similarity threshold
                        analysis['redundant_rules'].append({
                            'automation_ids': [automation.get('id'), other_automation.get('id')],
                            'similarity_score': similarity,
                            'recommendation': 'Consider consolidating these similar rules'
                        })
            
            # Calculate statistics
            if automations:
                analysis['statistics']['avg_conditions_per_rule'] = total_conditions / len(automations)
                analysis['statistics']['avg_actions_per_rule'] = total_actions / len(automations)
            
            return {
                'template_id': template_id,
                'automations': automations,
                'analysis': analysis,
                'step_lookup': step_lookup
            }
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "analyze template automations", org_id=org_id, template_id=template_id)

    def _analyze_condition_similarity(self, conditions1: List[Dict], conditions2: List[Dict]) -> float:
        """
        Helper for analyzing similarity between condition sets.
        
        Args:
            conditions1: First set of conditions
            conditions2: Second set of conditions
            
        Returns:
            Float representing similarity score (0.0 to 1.0)
        """
        if not conditions1 or not conditions2:
            return 0.0
        
        # Convert conditions to comparable strings
        set1 = set()
        set2 = set()
        
        for condition in conditions1:
            condition_str = f"{condition.get('type', '')}:{condition.get('step_id', '')}:{condition.get('value', '')}"
            set1.add(condition_str)
        
        for condition in conditions2:
            condition_str = f"{condition.get('type', '')}:{condition.get('step_id', '')}:{condition.get('value', '')}"
            set2.add(condition_str)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union)

    def _summarize_conditions(self, conditions: List[Dict], step_lookup: Dict[str, str]) -> List[str]:
        """
        Creates human-readable condition summaries.
        
        Args:
            conditions: List of condition dictionaries
            step_lookup: Mapping of step IDs to step titles
            
        Returns:
            List of human-readable condition descriptions
        """
        summaries = []
        
        for condition in conditions:
            condition_type = condition.get('type', '')
            step_id = condition.get('step_id', '')
            value = condition.get('value', '')
            
            step_name = step_lookup.get(step_id, f"Step {step_id}")
            
            if condition_type == 'step_completed':
                summaries.append(f"'{step_name}' is completed")
            elif condition_type == 'step_started':
                summaries.append(f"'{step_name}' is started")
            elif condition_type == 'field_value':
                field_label = condition.get('field_label', 'Unknown Field')
                summaries.append(f"Field '{field_label}' equals '{value}'")
            else:
                summaries.append(f"{condition_type} condition")
        
        return summaries

    def _summarize_condition(self, condition: Dict, step_lookup: Dict[str, str]) -> str:
        """
        Creates a human-readable summary of a single condition.
        
        Args:
            condition: Condition dictionary
            step_lookup: Mapping of step IDs to step titles
            
        Returns:
            Human-readable condition description
        """
        condition_type = condition.get('type', '')
        step_id = condition.get('step_id', '')
        value = condition.get('value', '')
        
        step_name = step_lookup.get(step_id, f"Step {step_id}")
        
        if condition_type == 'step_completed':
            return f"'{step_name}' is completed"
        elif condition_type == 'step_started':
            return f"'{step_name}' is started"
        elif condition_type == 'field_value':
            field_label = condition.get('field_label', 'Unknown Field')
            return f"Field '{field_label}' equals '{value}'"
        else:
            return f"{condition_type} condition"

    def _generate_visibility_recommendations(self, visibility_rules: Dict, complexity_level: str) -> List[str]:
        """
        Generates visibility-specific recommendations.
        
        Args:
            visibility_rules: Dictionary containing visibility rules
            complexity_level: String indicating complexity level
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        show_rules = visibility_rules.get('show_rules', [])
        hide_rules = visibility_rules.get('hide_rules', [])
        
        if complexity_level == "Complex":
            recommendations.append("Consider simplifying visibility conditions to improve workflow clarity")
        
        if show_rules and hide_rules:
            recommendations.append("Review show/hide rule interactions to prevent conflicts")
        
        if len(show_rules) > 2:
            recommendations.append("Multiple show conditions may create user confusion - consider consolidation")
        
        if not show_rules and not hide_rules:
            recommendations.append("Step has simple visibility - no optimization needed")
        
        return recommendations

    def _generate_dependency_recommendations(self, dependencies: Dict, complexity_level: str) -> List[str]:
        """
        Generates dependency-specific recommendations.
        
        Args:
            dependencies: Dictionary containing dependency information
            complexity_level: String indicating complexity level
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        incoming_count = len(dependencies.get('incoming', []))
        outgoing_count = len(dependencies.get('outgoing', []))
        
        if complexity_level == "High":
            recommendations.append("High dependency complexity - consider breaking step into smaller components")
        
        if incoming_count > 3:
            recommendations.append("Step has many dependencies - ensure all are necessary")
        
        if outgoing_count > 3:
            recommendations.append("Step affects many other steps - verify all impacts are intentional")
        
        if not incoming_count and not outgoing_count:
            recommendations.append("Step is independent - good for parallel execution")
        
        return recommendations