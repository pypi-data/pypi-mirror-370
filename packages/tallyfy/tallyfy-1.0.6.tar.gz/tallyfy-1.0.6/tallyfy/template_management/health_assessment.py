"""
Comprehensive template health assessment and improvement recommendations
"""

import datetime
from typing import List, Optional, Dict, Any
from .base import TemplateManagerBase
from ..models import Template, TallyfyError


class TemplateHealthAssessment(TemplateManagerBase):
    """Handles comprehensive template health analysis and improvement recommendations"""

    def assess_template_health(self, org_id: str, template_id: str) -> Dict[str, Any]:
        """
        Main comprehensive health check method.
        
        Args:
            org_id: Organization ID
            template_id: Template ID to assess
            
        Returns:
            Dictionary containing complete health assessment with scores, issues, and recommendations
            
        Raises:
            TallyfyError: If the request fails
        """
        self._validate_org_id(org_id)
        self._validate_template_id(template_id)
        
        try:
            # Get template with full data - this would need to be injected or imported
            # For now, we'll make the API call directly
            template_endpoint = f"organizations/{org_id}/checklists/{template_id}"
            template_params = {'with': 'steps,automated_actions,prerun'}
            template_response = self.sdk._make_request('GET', template_endpoint, params=template_params)
            
            template_data = self._extract_data(template_response)
            if not template_data:
                raise TallyfyError("Unable to retrieve template data for health assessment")
            
            # Initialize assessment results
            assessment = {
                'template_id': template_id,
                'template_title': template_data.get('title', 'Unknown'),
                'assessment_timestamp': self._get_current_timestamp(),
                'overall_score': 0,
                'health_rating': 'poor',
                'category_scores': {},
                'issues': [],
                'recommendations': [],
                'improvement_plan': []
            }
            
            # Perform individual assessments
            metadata_score, metadata_issues = self._assess_template_metadata(template_data)
            step_score, step_issues = self._assess_step_clarity(template_data)
            form_score, form_issues = self._assess_form_completeness(template_data)
            automation_score, automation_issues = self._assess_automation_efficiency(org_id, template_id, template_data)
            deadline_score, deadline_issues = self._assess_deadline_reasonableness(template_data)
            workflow_score, workflow_issues = self._assess_workflow_logic(template_data)
            
            # Calculate scores and compile issues
            assessment['category_scores'] = {
                'metadata_quality': {'score': metadata_score, 'max_score': 15},
                'step_clarity': {'score': step_score, 'max_score': 20},
                'form_completeness': {'score': form_score, 'max_score': 15},
                'automation_efficiency': {'score': automation_score, 'max_score': 20},
                'deadline_reasonableness': {'score': deadline_score, 'max_score': 15},
                'workflow_logic': {'score': workflow_score, 'max_score': 15}
            }
            
            # Calculate overall score (out of 100)
            total_score = (metadata_score + step_score + form_score + 
                          automation_score + deadline_score + workflow_score)
            assessment['overall_score'] = total_score
            assessment['health_rating'] = self._get_health_rating(total_score)
            
            # Compile all issues
            all_issues = (metadata_issues + step_issues + form_issues + 
                         automation_issues + deadline_issues + workflow_issues)
            assessment['issues'] = all_issues
            
            # Generate recommendations based on issues
            recommendations = []
            critical_issues = [issue for issue in all_issues if issue.get('severity') == 'critical']
            high_issues = [issue for issue in all_issues if issue.get('severity') == 'high']
            
            if critical_issues:
                recommendations.append({
                    'priority': 'critical',
                    'title': 'Address Critical Issues Immediately',
                    'description': f'Found {len(critical_issues)} critical issues that require immediate attention',
                    'action': 'Review and fix all critical issues before using this template in production'
                })
            
            if high_issues:
                recommendations.append({
                    'priority': 'high',
                    'title': 'Resolve High Priority Issues',
                    'description': f'Found {len(high_issues)} high priority issues that should be addressed soon',
                    'action': 'Plan to address these issues in the next template update'
                })
            
            if total_score < 60:
                recommendations.append({
                    'priority': 'high',
                    'title': 'Template Needs Significant Improvement',
                    'description': 'Overall template quality is below acceptable standards',
                    'action': 'Consider comprehensive template redesign or major improvements across all categories'
                })
            
            assessment['recommendations'] = recommendations
            
            # Generate improvement plan
            assessment['improvement_plan'] = self._generate_improvement_plan(all_issues, assessment['category_scores'])
            
            return assessment
            
        except TallyfyError:
            raise
        except Exception as e:
            self._handle_api_error(e, "assess template health", org_id=org_id, template_id=template_id)

    def _assess_template_metadata(self, template_data: Dict[str, Any]) -> tuple[int, List[Dict[str, Any]]]:
        """
        Assess template metadata quality.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            Tuple of (score out of 15, list of issues)
        """
        score = 0
        issues = []
        
        # Check title quality (5 points)
        title = template_data.get('title', '').strip()
        if not title:
            issues.append({
                'category': 'metadata',
                'severity': 'critical',
                'title': 'Missing Template Title',
                'description': 'Template must have a descriptive title',
                'recommendation': 'Add a clear, descriptive title that explains the template purpose'
            })
        elif len(title) < 10:
            issues.append({
                'category': 'metadata',
                'severity': 'medium',
                'title': 'Template Title Too Short',
                'description': f'Title "{title}" is very brief ({len(title)} characters)',
                'recommendation': 'Expand title to be more descriptive (aim for 10-50 characters)'
            })
            score += 2
        elif len(title) > 100:
            issues.append({
                'category': 'metadata',
                'severity': 'low',
                'title': 'Template Title Too Long',
                'description': f'Title is very long ({len(title)} characters)',
                'recommendation': 'Shorten title to be more concise (aim for 10-50 characters)'
            })
            score += 3
        else:
            score += 5
        
        # Check summary/description quality (5 points)
        summary = template_data.get('summary', '').strip()
        if not summary:
            issues.append({
                'category': 'metadata',
                'severity': 'high',
                'title': 'Missing Template Summary',
                'description': 'Template should have a summary explaining its purpose',
                'recommendation': 'Add a summary that explains when and how to use this template'
            })
        elif len(summary) < 20:
            issues.append({
                'category': 'metadata',
                'severity': 'medium',
                'title': 'Template Summary Too Brief',
                'description': f'Summary is very short ({len(summary)} characters)',
                'recommendation': 'Expand summary to provide more context about template usage'
            })
            score += 2
        else:
            score += 5
        
        # Check guidance quality (5 points)
        guidance = template_data.get('guidance', '').strip()
        if not guidance:
            issues.append({
                'category': 'metadata',
                'severity': 'medium',
                'title': 'Missing Template Guidance',
                'description': 'Template could benefit from usage guidance',
                'recommendation': 'Add guidance to help users understand how to use this template effectively'
            })
            score += 2
        elif len(guidance) < 50:
            issues.append({
                'category': 'metadata',
                'severity': 'low',
                'title': 'Template Guidance Could Be More Detailed',
                'description': 'Guidance is present but could be more comprehensive',
                'recommendation': 'Expand guidance with more detailed instructions and best practices'
            })
            score += 3
        else:
            score += 5
        
        return score, issues

    def _assess_step_clarity(self, template_data: Dict[str, Any]) -> tuple[int, List[Dict[str, Any]]]:
        """
        Assess step title clarity and descriptiveness.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            Tuple of (score out of 20, list of issues)
        """
        score = 0
        issues = []
        
        steps = template_data.get('steps', [])
        if not steps:
            issues.append({
                'category': 'steps',
                'severity': 'critical',
                'title': 'Template Has No Steps',
                'description': 'Template must have at least one step',
                'recommendation': 'Add steps to create a functional workflow'
            })
            return 0, issues
        
        step_count = len(steps)
        unclear_steps = 0
        missing_summaries = 0
        very_short_titles = 0
        
        for step in steps:
            step_title = step.get('title', '').strip()
            step_summary = step.get('summary', '').strip()
            
            # Check title clarity
            if not step_title:
                unclear_steps += 1
            elif len(step_title) < 5:
                very_short_titles += 1
            elif step_title.lower() in ['step', 'task', 'do this', 'complete', 'finish']:
                unclear_steps += 1
            
            # Check for summary
            if not step_summary:
                missing_summaries += 1
        
        # Score based on step quality
        if unclear_steps == 0 and very_short_titles == 0:
            score += 10  # Excellent step titles
        elif unclear_steps <= step_count * 0.1:  # 10% or less unclear
            score += 8
        elif unclear_steps <= step_count * 0.2:  # 20% or less unclear
            score += 6
        else:
            score += 2
        
        # Summary completeness scoring
        summary_percentage = 1 - (missing_summaries / step_count)
        if summary_percentage >= 0.8:
            score += 10
        elif summary_percentage >= 0.6:
            score += 7
        elif summary_percentage >= 0.4:
            score += 5
        else:
            score += 2
        
        # Generate issues
        if unclear_steps > 0:
            severity = 'critical' if unclear_steps > step_count * 0.3 else 'high'
            issues.append({
                'category': 'steps',
                'severity': severity,
                'title': f'{unclear_steps} Steps Have Unclear Titles',
                'description': f'{unclear_steps} out of {step_count} steps have unclear or missing titles',
                'recommendation': 'Ensure all step titles clearly describe what needs to be done'
            })
        
        if very_short_titles > 0:
            issues.append({
                'category': 'steps',
                'severity': 'medium',
                'title': f'{very_short_titles} Steps Have Very Short Titles',
                'description': f'{very_short_titles} steps have very brief titles',
                'recommendation': 'Expand step titles to be more descriptive'
            })
        
        if missing_summaries > step_count * 0.5:
            issues.append({
                'category': 'steps',
                'severity': 'medium',
                'title': 'Many Steps Missing Summaries',
                'description': f'{missing_summaries} out of {step_count} steps lack summary descriptions',
                'recommendation': 'Add summaries to provide additional context for complex steps'
            })
        
        return score, issues

    def _assess_form_completeness(self, template_data: Dict[str, Any]) -> tuple[int, List[Dict[str, Any]]]:
        """
        Assess form field quality and completeness.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            Tuple of (score out of 15, list of issues)
        """
        score = 0
        issues = []
        
        prerun_fields = template_data.get('prerun', [])
        steps = template_data.get('steps', [])
        
        # Check kickoff form completeness (10 points)
        if not prerun_fields:
            # Check if template likely needs kickoff fields
            template_content = f"{template_data.get('title', '')} {template_data.get('summary', '')}"
            step_content = " ".join([step.get('title', '') + " " + step.get('summary', '') for step in steps])
            all_content = (template_content + " " + step_content).lower()
            
            needs_fields_keywords = ['client', 'customer', 'project', 'name', 'email', 'date', 'budget', 'details']
            if any(keyword in all_content for keyword in needs_fields_keywords):
                issues.append({
                    'category': 'forms',
                    'severity': 'medium',
                    'title': 'Missing Kickoff Fields',
                    'description': 'Template could benefit from kickoff fields to collect initial information',
                    'recommendation': 'Add kickoff fields to gather necessary information before starting the workflow'
                })
                score += 5
            else:
                score += 8  # Template may not need kickoff fields
        else:
            # Assess field quality
            required_fields = len([f for f in prerun_fields if f.get('required')])
            total_fields = len(prerun_fields)
            
            if total_fields >= 3 and required_fields > 0:
                score += 10
            elif total_fields >= 1:
                score += 7
            else:
                score += 3
        
        # Check step forms (5 points)
        steps_with_forms = 0
        for step in steps:
            # This would need to be expanded based on actual step form structure
            # For now, we'll do a simple check
            if 'form' in step or 'fields' in step:
                steps_with_forms += 1
        
        if steps_with_forms > 0:
            score += 5
        else:
            # Check if steps might need forms
            form_keywords = ['input', 'enter', 'provide', 'fill', 'complete', 'details', 'information']
            steps_needing_forms = 0
            
            for step in steps:
                step_text = (step.get('title', '') + " " + step.get('summary', '')).lower()
                if any(keyword in step_text for keyword in form_keywords):
                    steps_needing_forms += 1
            
            if steps_needing_forms > 0:
                issues.append({
                    'category': 'forms',
                    'severity': 'low',
                    'title': 'Steps May Need Forms',
                    'description': f'{steps_needing_forms} steps appear to require information input',
                    'recommendation': 'Consider adding forms to steps that require information gathering'
                })
                score += 3
            else:
                score += 5
        
        return score, issues

    def _assess_automation_efficiency(self, org_id: str, template_id: str, template_data: Dict[str, Any]) -> tuple[int, List[Dict[str, Any]]]:
        """
        Assess automation rules efficiency.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            template_data: Template data dictionary
            
        Returns:
            Tuple of (score out of 20, list of issues)
        """
        score = 0
        issues = []
        
        try:
            automations = template_data.get('automated_actions', [])
            
            if not automations:
                # Template has no automations - this might be fine for simple templates
                steps = template_data.get('steps', [])
                if len(steps) > 5:
                    issues.append({
                        'category': 'automation',
                        'severity': 'low',
                        'title': 'No Automation Rules',
                        'description': 'Template has multiple steps but no automation rules',
                        'recommendation': 'Consider adding automation rules to improve workflow efficiency'
                    })
                    score += 15
                else:
                    score += 18  # Simple templates may not need automation
                return score, issues
            
            # Analyze automation complexity and conflicts
            total_automations = len(automations)
            complex_automations = 0
            simple_automations = 0
            
            for automation in automations:
                conditions = automation.get('conditions', [])
                actions = automation.get('actions', [])
                
                if len(conditions) > 3 or len(actions) > 2:
                    complex_automations += 1
                else:
                    simple_automations += 1
            
            # Score based on automation balance
            if complex_automations <= total_automations * 0.3:  # 30% or less complex
                score += 10
            elif complex_automations <= total_automations * 0.5:  # 50% or less complex
                score += 7
            else:
                score += 4
                issues.append({
                    'category': 'automation',
                    'severity': 'medium',
                    'title': 'Many Complex Automation Rules',
                    'description': f'{complex_automations} out of {total_automations} automation rules are complex',
                    'recommendation': 'Consider simplifying complex automation rules for better maintainability'
                })
            
            # Check for potential conflicts (simplified check)
            if total_automations > 10:
                issues.append({
                    'category': 'automation',
                    'severity': 'medium',
                    'title': 'High Number of Automation Rules',
                    'description': f'Template has {total_automations} automation rules',
                    'recommendation': 'Review automation rules for potential consolidation opportunities'
                })
                score += 5
            else:
                score += 10
            
        except Exception as e:
            # If automation analysis fails, give neutral score
            self.sdk.logger.warning(f"Failed to analyze automations: {e}")
            score += 10
        
        return score, issues

    def _assess_deadline_reasonableness(self, template_data: Dict[str, Any]) -> tuple[int, List[Dict[str, Any]]]:
        """
        Assess deadline appropriateness.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            Tuple of (score out of 15, list of issues)
        """
        score = 0
        issues = []
        
        steps = template_data.get('steps', [])
        if not steps:
            return 0, issues
        
        steps_with_deadlines = 0
        reasonable_deadlines = 0
        unreasonable_deadlines = 0
        
        for step in steps:
            deadline = step.get('deadline')
            if deadline:
                steps_with_deadlines += 1
                
                # Simple deadline reasonableness check
                deadline_value = deadline.get('value', 0)
                deadline_unit = deadline.get('unit', 'days')
                
                # Convert to hours for comparison
                if deadline_unit == 'minutes':
                    hours = deadline_value / 60
                elif deadline_unit == 'hours':
                    hours = deadline_value
                elif deadline_unit == 'days':
                    hours = deadline_value * 24
                elif deadline_unit == 'weeks':
                    hours = deadline_value * 24 * 7
                else:
                    hours = deadline_value * 24  # Assume days
                
                # Check reasonableness
                if 0.5 <= hours <= 8760:  # 30 minutes to 1 year
                    reasonable_deadlines += 1
                else:
                    unreasonable_deadlines += 1
        
        total_steps = len(steps)
        
        # Score based on deadline usage and reasonableness
        if steps_with_deadlines == 0:
            if total_steps > 3:
                issues.append({
                    'category': 'deadlines',
                    'severity': 'low',
                    'title': 'No Step Deadlines Set',
                    'description': 'Template has multiple steps but no deadlines',
                    'recommendation': 'Consider adding deadlines to time-sensitive steps'
                })
                score += 10
            else:
                score += 13  # Simple templates may not need deadlines
        else:
            # Score based on deadline quality
            if unreasonable_deadlines == 0:
                score += 15
            elif unreasonable_deadlines <= steps_with_deadlines * 0.2:  # 20% or less unreasonable
                score += 12
            else:
                score += 8
                issues.append({
                    'category': 'deadlines',
                    'severity': 'medium',
                    'title': 'Some Deadlines May Be Unreasonable',
                    'description': f'{unreasonable_deadlines} steps have potentially unreasonable deadlines',
                    'recommendation': 'Review step deadlines to ensure they are achievable and appropriate'
                })
        
        return score, issues

    def _assess_workflow_logic(self, template_data: Dict[str, Any]) -> tuple[int, List[Dict[str, Any]]]:
        """
        Assess overall workflow structure.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            Tuple of (score out of 15, list of issues)
        """
        score = 0
        issues = []
        
        steps = template_data.get('steps', [])
        if not steps:
            issues.append({
                'category': 'workflow',
                'severity': 'critical',
                'title': 'No Workflow Steps',
                'description': 'Template must have workflow steps',
                'recommendation': 'Add steps to create a meaningful workflow'
            })
            return 0, issues
        
        step_count = len(steps)
        
        # Check workflow length appropriateness (5 points)
        if 2 <= step_count <= 20:
            score += 5
        elif 1 <= step_count <= 30:
            score += 4
        elif step_count > 30:
            issues.append({
                'category': 'workflow',
                'severity': 'medium',
                'title': 'Very Long Workflow',
                'description': f'Template has {step_count} steps, which may be difficult to manage',
                'recommendation': 'Consider breaking down into smaller sub-workflows or templates'
            })
            score += 2
        else:
            score += 3
        
        # Check step positioning and logic (5 points)
        positions = [step.get('position', 0) for step in steps]
        unique_positions = len(set(positions))
        
        if unique_positions == step_count and min(positions) > 0:
            score += 5  # All steps have unique, valid positions
        elif unique_positions >= step_count * 0.8:  # 80% have unique positions
            score += 4
        else:
            issues.append({
                'category': 'workflow',
                'severity': 'low',
                'title': 'Inconsistent Step Positioning',
                'description': 'Some steps may have duplicate or missing positions',
                'recommendation': 'Review step order and ensure logical sequence'
            })
            score += 2
        
        # Check for logical flow (5 points)
        # This is a simplified check - in practice, you'd analyze dependencies
        first_steps = [step for step in steps if step.get('position', 0) <= 2]
        last_steps = [step for step in steps if step.get('position', 0) >= step_count - 1]
        
        if first_steps and last_steps:
            # Check if first steps are setup-like and last steps are completion-like
            first_step_content = " ".join([step.get('title', '').lower() for step in first_steps])
            last_step_content = " ".join([step.get('title', '').lower() for step in last_steps])
            
            setup_keywords = ['start', 'begin', 'initialize', 'setup', 'create', 'prepare']
            completion_keywords = ['complete', 'finish', 'finalize', 'close', 'deliver', 'submit']
            
            has_logical_start = any(keyword in first_step_content for keyword in setup_keywords)
            has_logical_end = any(keyword in last_step_content for keyword in completion_keywords)
            
            if has_logical_start and has_logical_end:
                score += 5
            elif has_logical_start or has_logical_end:
                score += 3
            else:
                score += 2
        else:
            score += 3
        
        return score, issues

    def _generate_improvement_plan(self, issues: List[Dict[str, Any]], category_scores: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate prioritized improvement plan.
        
        Args:
            issues: List of all identified issues
            category_scores: Dictionary of category scores
            
        Returns:
            List of improvement plan items
        """
        improvement_plan = []
        
        # Sort issues by severity
        critical_issues = [issue for issue in issues if issue.get('severity') == 'critical']
        high_issues = [issue for issue in issues if issue.get('severity') == 'high']
        medium_issues = [issue for issue in issues if issue.get('severity') == 'medium']
        low_issues = [issue for issue in issues if issue.get('severity') == 'low']
        
        # Create improvement items for critical issues
        if critical_issues:
            improvement_plan.append({
                'priority': 1,
                'phase': 'Immediate',
                'title': 'Fix Critical Issues',
                'description': f'Address {len(critical_issues)} critical issues that prevent template from functioning properly',
                'effort': 'High',
                'impact': 'Critical',
                'estimated_time': '2-4 hours',
                'issues_addressed': [issue['title'] for issue in critical_issues]
            })
        
        # Group issues by category for focused improvements
        category_issue_map = {}
        for issue in high_issues + medium_issues:
            category = issue.get('category', 'general')
            if category not in category_issue_map:
                category_issue_map[category] = []
            category_issue_map[category].append(issue)
        
        # Find lowest scoring categories for prioritization
        category_priorities = []
        for category, score_info in category_scores.items():
            score_percentage = (score_info['score'] / score_info['max_score']) * 100
            if score_percentage < 70:  # Focus on categories scoring below 70%
                issue_count = len(category_issue_map.get(category.split('_')[0], []))
                category_priorities.append({
                    'category': category,
                    'score_percentage': score_percentage,
                    'issue_count': issue_count
                })
        
        # Sort by score percentage (lowest first)
        category_priorities.sort(key=lambda x: x['score_percentage'])
        
        # Create improvement items for priority categories
        phase_counter = 2
        for cat_info in category_priorities[:3]:  # Top 3 categories
            category_name = cat_info['category']
            category_issues = category_issue_map.get(category_name.split('_')[0], [])
            
            if category_issues:
                improvement_plan.append({
                    'priority': phase_counter,
                    'phase': f'Phase {phase_counter - 1}',
                    'title': f'Improve {category_name.replace("_", " ").title()}',
                    'description': f'Address {len(category_issues)} issues in {category_name.replace("_", " ")} (currently {cat_info["score_percentage"]:.0f}%)',
                    'effort': 'Medium' if len(category_issues) <= 3 else 'High',
                    'impact': 'High' if cat_info['score_percentage'] < 50 else 'Medium',
                    'estimated_time': f'{len(category_issues) * 30}-{len(category_issues) * 60} minutes',
                    'issues_addressed': [issue['title'] for issue in category_issues]
                })
                phase_counter += 1
        
        # Add low priority improvements
        if low_issues:
            improvement_plan.append({
                'priority': phase_counter,
                'phase': 'Polish',
                'title': 'Address Minor Improvements',
                'description': f'Handle {len(low_issues)} minor issues for template optimization',
                'effort': 'Low',
                'impact': 'Low',
                'estimated_time': f'{len(low_issues) * 15}-{len(low_issues) * 30} minutes',
                'issues_addressed': [issue['title'] for issue in low_issues]
            })
        
        return improvement_plan

    def _get_health_rating(self, score: int) -> str:
        """
        Convert numeric score to health rating.
        
        Args:
            score: Numeric score out of 100
            
        Returns:
            Health rating as string
        """
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'fair'
        elif score >= 40:
            return 'poor'
        else:
            return 'critical'

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp for assessment.
        
        Returns:
            ISO formatted timestamp string
        """
        return datetime.datetime.now().isoformat()