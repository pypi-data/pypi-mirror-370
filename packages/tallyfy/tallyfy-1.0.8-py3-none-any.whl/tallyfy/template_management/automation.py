"""
Automation management functionality for templates
"""
from typing import List, Optional, Dict, Any
from .base import TemplateManagerBase
from ..models import AutomatedAction, TallyfyError
from email_validator import validate_email, EmailNotValidError


class TemplateAutomation(TemplateManagerBase):
    """Handles automation rules creation, management, and optimization"""

    def create_automation_rule(self, org_id: str, template_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create conditional automation (if-then rules).
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            rule_data: Dictionary containing automation rule data
            
        Returns:
            Dictionary containing created automation rule information
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/automated_actions"
            
            # Validate rule data
            if not isinstance(rule_data, dict):
                raise ValueError("Rule data must be a dictionary")
            
            # Build automation data
            automation_data = {}
            
            # Add alias if provided
            if 'alias' in rule_data:
                automation_data['automated_alias'] = str(rule_data['alias'])
            
            # Add conditions
            if 'conditions' in rule_data and rule_data['conditions']:
                automation_data['conditions'] = rule_data['conditions']
            else:
                raise ValueError("Automation rule must have conditions")
            
            # Add actions
            if 'actions' in rule_data and rule_data['actions']:
                automation_data['then_actions'] = rule_data['actions']
            else:
                raise ValueError("Automation rule must have actions")
            
            # Add condition logic (AND/OR)
            if 'condition_logic' in rule_data:
                automation_data['condition_logic'] = rule_data['condition_logic']
            
            response_data = self.sdk._make_request('POST', endpoint, data=automation_data)
            
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    return response_data['data']
                return response_data
            else:
                self.sdk.logger.warning("Unexpected response format for automation rule creation")
                return {'success': True, 'created_rule': automation_data}
                
        except TallyfyError:
            raise
        except ValueError as e:
            raise TallyfyError(f"Invalid automation rule data: {e}")
        except Exception as e:
            self._handle_api_error(e, "create automation rule", org_id=org_id, template_id=template_id)

    def update_automation_rule(self, org_id: str, template_id: str, automation_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify automation conditions and actions.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            automation_id: Automation rule ID to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Dictionary containing updated automation rule information
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/automated_actions/{automation_id}"
            
            # Validate update data
            if not isinstance(update_data, dict):
                raise ValueError("Update data must be a dictionary")
            
            # Build update payload with allowed fields
            allowed_fields = ['automated_alias', 'conditions', 'then_actions', 'condition_logic']
            validated_data = {}
            
            for field, value in update_data.items():
                if field in allowed_fields:
                    validated_data[field] = value
                elif field == 'alias':  # Map alias to automated_alias
                    validated_data['automated_alias'] = str(value)
                elif field == 'actions':  # Map actions to then_actions
                    validated_data['then_actions'] = value
                else:
                    self.sdk.logger.warning(f"Ignoring unknown automation field: {field}")
            
            if not validated_data:
                raise ValueError("No valid automation fields provided for update")
            
            response_data = self.sdk._make_request('PUT', endpoint, data=validated_data)
            
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    return response_data['data']
                return response_data
            else:
                self.sdk.logger.warning("Unexpected response format for automation rule update")
                return {'success': True, 'updated_rule': validated_data}
                
        except TallyfyError:
            raise
        except ValueError as e:
            raise TallyfyError(f"Invalid update data: {e}")
        except Exception as e:
            self._handle_api_error(e, "update automation rule", org_id=org_id, template_id=template_id, automation_id=automation_id)

    def delete_automation_rule(self, org_id: str, template_id: str, automation_id: str) -> Dict[str, Any]:
        """
        Remove automation rule.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            automation_id: Automation rule ID to delete
            
        Returns:
            Dictionary containing deletion confirmation
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/automated_actions/{automation_id}"
            
            response_data = self.sdk._make_request('DELETE', endpoint)
            
            if isinstance(response_data, dict):
                return response_data
            else:
                return {'success': True, 'deleted_automation_id': automation_id}
                
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "delete automation rule", org_id=org_id, template_id=template_id, automation_id=automation_id)

    def consolidate_automation_rules(self, org_id: str, template_id: str, preview_only: bool = True) -> Dict[str, Any]:
        """
        Suggest and implement automation consolidation.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            preview_only: If True, only return suggestions without implementing changes
            
        Returns:
            Dictionary containing consolidation analysis and results
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            # Get automation analysis
            analysis = self.analyze_template_automations(org_id, template_id)
            
            consolidation_results = {
                'template_id': template_id,
                'preview_only': preview_only,
                'suggestions': [],
                'implemented_changes': [],
                'warnings': [],
                'summary': {
                    'total_automations': len(analysis.get('automations', [])),
                    'redundant_rules': len(analysis.get('analysis', {}).get('redundant_rules', [])),
                    'conflicting_rules': len(analysis.get('analysis', {}).get('conflicting_rules', [])),
                    'potential_consolidations': 0
                }
            }
            
            redundant_rules = analysis.get('analysis', {}).get('redundant_rules', [])
            
            # Process redundant rules
            for redundancy in redundant_rules:
                automation_ids = redundancy.get('automation_ids', [])
                similarity_score = redundancy.get('similarity_score', 0)
                
                suggestion = {
                    'type': 'consolidation',
                    'automation_ids': automation_ids,
                    'similarity_score': similarity_score,
                    'description': f"Consolidate {len(automation_ids)} similar automation rules",
                    'recommendation': redundancy.get('recommendation', ''),
                    'estimated_effort': 'Low',
                    'impact': 'Reduced complexity and improved maintainability'
                }
                
                consolidation_results['suggestions'].append(suggestion)
                consolidation_results['summary']['potential_consolidations'] += 1
                
                # If not preview only, implement the consolidation
                if not preview_only:
                    try:
                        # This is a simplified consolidation - in practice, you'd need more sophisticated logic
                        # to merge automation rules properly
                        consolidation_results['warnings'].append(
                            f"Automatic consolidation of rules {automation_ids} requires manual review"
                        )
                    except Exception as e:
                        consolidation_results['warnings'].append(
                            f"Failed to consolidate rules {automation_ids}: {str(e)}"
                        )
            
            # Check for conflicting rules
            conflicting_rules = analysis.get('analysis', {}).get('conflicting_rules', [])
            for conflict in conflicting_rules:
                consolidation_results['warnings'].append(
                    f"Conflicting rules detected: {conflict.get('automation_ids', [])} - manual resolution required"
                )
            
            return consolidation_results
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "consolidate automation rules", org_id=org_id, template_id=template_id)

    def add_assignees_to_step(self, org_id: str, template_id: str, step_id: str, assignees: List[int], guests: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Add assignees to steps (automation-related).
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to add assignees to
            assignees: List of user IDs to assign
            guests: Optional list of guest email addresses
            
        Returns:
            Dictionary containing updated step information
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}"
            
            # Validate assignees
            if not isinstance(assignees, list):
                raise ValueError("Assignees must be a list of user IDs")
            
            for user_id in assignees:
                if not isinstance(user_id, int):
                    raise ValueError(f"User ID {user_id} must be an integer")
            
            # Validate guest emails if provided
            validated_guests = []
            if guests:
                if not isinstance(guests, list):
                    raise ValueError("Guests must be a list of email addresses")

                for guest_email in guests:
                    if not isinstance(guest_email, str):
                        raise ValueError(f"Guest email {guest_email} must be a string")
                    try:
                        validation = validate_email(guest_email)
                        # The validated email address
                        email = validation.normalized
                    except EmailNotValidError as e:
                        raise ValueError(f"Invalid email address: {str(e)}")
                    validated_guests.append(email)
            
            # Build update data
            update_data = {
                'assignees': assignees
            }
            
            if validated_guests:
                update_data['guests'] = validated_guests
            
            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)
            
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    return response_data['data']
                return response_data
            else:
                self.sdk.logger.warning("Unexpected response format for assignee update")
                return {
                    'success': True, 
                    'step_id': step_id,
                    'added_assignees': assignees,
                    'added_guests': validated_guests
                }
                
        except TallyfyError:
            raise
        except ValueError as e:
            raise TallyfyError(f"Invalid assignee data: {e}")
        except Exception as e:
            self._handle_api_error(e, "add assignees to step", org_id=org_id, template_id=template_id, step_id=step_id)

    def analyze_template_automations(self, org_id: str, template_id: str) -> Dict[str, Any]:
        """
        Analyze automations for conflicts/redundancies.
        
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
                
                # Check for conflicts (same conditions, different actions)
                for j, other_automation in enumerate(automations[i+1:], i+1):
                    other_conditions = other_automation.get('conditions', [])
                    other_actions = other_automation.get('actions', [])
                    
                    if (self._analyze_condition_similarity(conditions, other_conditions) > 0.9 and
                        actions != other_actions):
                        analysis['conflicting_rules'].append({
                            'automation_ids': [automation.get('id'), other_automation.get('id')],
                            'description': 'Same conditions with different actions may cause conflicts',
                            'severity': 'high'
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
        Helper for condition analysis.
        
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