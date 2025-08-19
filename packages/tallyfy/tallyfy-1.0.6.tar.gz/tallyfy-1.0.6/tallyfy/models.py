"""
Data models for Tallyfy API responses
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class TallyfyError(Exception):
    """Custom exception for Tallyfy API errors"""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


@dataclass
class Country:
    """Country data model"""
    id: int
    name: str
    phone_code: str
    iso2: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Country':
        """Create Country instance from dictionary"""
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            phone_code=data.get('phone_code', ''),
            iso2=data.get('iso2', '')
        )


@dataclass
class User:
    """User data model"""
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    full_name: str
    profile_pic: Optional[str] = None
    locale: Optional[str] = None
    active: bool = True
    is_suspended: bool = False
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    last_login_at: Optional[str] = None
    activated_at: Optional[str] = None
    support_user: bool = False
    country: Optional[Country] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    team: Optional[str] = None
    timezone: Optional[str] = None
    UTC_offset: Optional[str] = None
    last_accessed_at: Optional[str] = None
    approved_at: Optional[str] = None
    invited_by: Optional[int] = None
    disabled_at: Optional[str] = None
    disabled_by: Optional[int] = None
    reactivated_at: Optional[str] = None
    reactivated_by: Optional[int] = None
    status: Optional[str] = None
    date_format: Optional[str] = None
    last_known_ip: Optional[str] = None
    last_known_country: Optional[str] = None
    role: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary"""
        country_data = data.get('country')
        country = Country.from_dict(country_data) if country_data else None
        
        return cls(
            id=data.get('id', 0),
            email=data.get('email', ''),
            username=data.get('username', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            full_name=data.get('full_name', ''),
            profile_pic=data.get('profile_pic'),
            locale=data.get('locale'),
            active=data.get('active', True),
            is_suspended=data.get('is_suspended', False),
            created_at=data.get('created_at'),
            last_updated=data.get('last_updated'),
            last_login_at=data.get('last_login_at'),
            activated_at=data.get('activated_at'),
            support_user=data.get('support_user', False),
            country=country,
            phone=data.get('phone'),
            job_title=data.get('job_title'),
            job_description=data.get('job_description'),
            team=data.get('team'),
            timezone=data.get('timezone'),
            UTC_offset=data.get('UTC_offset'),
            last_accessed_at=data.get('last_accessed_at'),
            approved_at=data.get('approved_at'),
            invited_by=data.get('invited_by'),
            disabled_at=data.get('disabled_at'),
            disabled_by=data.get('disabled_by'),
            reactivated_at=data.get('reactivated_at'),
            reactivated_by=data.get('reactivated_by'),
            status=data.get('status'),
            date_format=data.get('date_format'),
            last_known_ip=data.get('last_known_ip'),
            last_known_country=data.get('last_known_country'),
            role=data.get('role')
        )


@dataclass
class GuestDetails:
    """Guest details data model"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[str] = None
    phone_1: Optional[str] = None
    phone_2: Optional[str] = None
    image_url: Optional[str] = None
    contact_url: Optional[str] = None
    company_url: Optional[str] = None
    opportunity_url: Optional[str] = None
    company_name: Optional[str] = None
    opportunity_name: Optional[str] = None
    external_sync_source: Optional[str] = None
    external_date_creation: Optional[str] = None
    timezone: Optional[str] = None
    reactivated_at: Optional[str] = None
    reactivated_by: Optional[int] = None
    disabled_on: Optional[str] = None
    disabled_by: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GuestDetails':
        """Create GuestDetails instance from dictionary"""
        return cls(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            status=data.get('status'),
            phone_1=data.get('phone_1'),
            phone_2=data.get('phone_2'),
            image_url=data.get('image_url'),
            contact_url=data.get('contact_url'),
            company_url=data.get('company_url'),
            opportunity_url=data.get('opportunity_url'),
            company_name=data.get('company_name'),
            opportunity_name=data.get('opportunity_name'),
            external_sync_source=data.get('external_sync_source'),
            external_date_creation=data.get('external_date_creation'),
            timezone=data.get('timezone'),
            reactivated_at=data.get('reactivated_at'),
            reactivated_by=data.get('reactivated_by'),
            disabled_on=data.get('disabled_on'),
            disabled_by=data.get('disabled_by')
        )


@dataclass
class Guest:
    """Guest data model"""
    email: str
    last_accessed_at: Optional[str] = None
    last_known_ip: Optional[str] = None
    last_known_country: Optional[str] = None
    details: Optional[GuestDetails] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Guest':
        """Create Guest instance from dictionary"""
        details_data = data.get('details')
        details = GuestDetails.from_dict(details_data) if details_data else None
        
        return cls(
            email=data.get('email', ''),
            last_accessed_at=data.get('last_accessed_at'),
            last_known_ip=data.get('last_known_ip'),
            last_known_country=data.get('last_known_country'),
            details=details
        )


@dataclass
class TaskOwners:
    """Task owners data model"""
    users: List[int] = None
    guests: List[str] = None
    groups: List[int] = None
    task_urls: List[str] = None

    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.users is None:
            self.users = []
        if self.guests is None:
            self.guests = []
        if self.groups is None:
            self.groups = []
        if self.task_urls is None:
            self.task_urls = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskOwners':
        """Create TaskOwners instance from dictionary"""
        return cls(
            users=data.get('users', []),
            guests=data.get('guests', []),
            groups=data.get('groups', []),
            task_urls=data.get('taskUrls', [])
        )


@dataclass
class Task:
    """Task data model"""
    id: str
    increment_id: int
    title: str
    original_title: str
    allow_guest_owners: bool
    run_id: Optional[str] = None
    checklist_id: Optional[str] = None
    linked_step_id: Optional[str] = None
    step_id: Optional[str] = None
    alias: Optional[str] = None
    taskdata: Optional[Dict[str, Any]] = None
    owners: Optional[TaskOwners] = None
    is_completable: bool = True
    status: str = "not-started"
    status_label: str = "not-started"
    task_type: str = "task"
    is_approved: Optional[bool] = None
    position: int = 0
    started_at: Optional[str] = None
    deadline: Optional[str] = None
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    archived_at: Optional[str] = None
    completed_at: Optional[str] = None
    starter_id: Optional[int] = None
    completer_id: Optional[int] = None
    is_oneoff_task: bool = False
    everyone_must_complete: bool = False
    completion_progress: Optional[float] = None
    has_deadline_dependent_child_tasks: bool = False
    can_complete_only_assignees: bool = False
    max_assignable: int = 0
    webhook: Optional[str] = None
    prevent_guest_comment: bool = False
    stage_id: Optional[str] = None
    problem: bool = False
    blueprint_position: Optional[int] = None
    is_soft_start_date: bool = False
    send_chromeless: Optional[bool] = None
    run_status: Optional[str] = None
    completer_guest: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task instance from dictionary"""
        owners_data = data.get('owners')
        owners = TaskOwners.from_dict(owners_data) if owners_data else None
        
        return cls(
            id=data.get('id', ''),
            increment_id=data.get('increment_id', 0),
            title=data.get('title', ''),
            original_title=data.get('original_title', ''),
            allow_guest_owners=data.get('allow_guest_owners', False),
            run_id=data.get('run_id'),
            checklist_id=data.get('checklist_id'),
            linked_step_id=data.get('linked_step_id'),
            step_id=data.get('step_id'),
            alias=data.get('alias'),
            taskdata=data.get('taskdata', {}),
            owners=owners,
            is_completable=data.get('is_completable', True),
            status=data.get('status', 'not-started'),
            status_label=data.get('status_label', 'not-started'),
            task_type=data.get('task_type', 'task'),
            is_approved=data.get('is_approved'),
            position=data.get('position', 0),
            started_at=data.get('started_at'),
            deadline=data.get('deadline'),
            created_at=data.get('created_at'),
            last_updated=data.get('last_updated'),
            archived_at=data.get('archived_at'),
            completed_at=data.get('completed_at'),
            starter_id=data.get('starter_id'),
            completer_id=data.get('completer_id'),
            is_oneoff_task=data.get('is_oneoff_task', False),
            everyone_must_complete=data.get('everyone_must_complete', False),
            completion_progress=data.get('completion_progress'),
            has_deadline_dependent_child_tasks=data.get('has_deadline_dependent_child_tasks', False),
            can_complete_only_assignees=data.get('can_complete_only_assignees', False),
            max_assignable=data.get('max_assignable', 0),
            webhook=data.get('webhook'),
            prevent_guest_comment=data.get('prevent_guest_comment', False),
            stage_id=data.get('stage_id'),
            problem=data.get('problem', False),
            blueprint_position=data.get('blueprint_position'),
            is_soft_start_date=data.get('is_soft_start_date', False),
            send_chromeless=data.get('send_chromeless'),
            run_status=data.get('run_status'),
            completer_guest=data.get('completer_guest')
        )


@dataclass
class RunProgress:
    """Run progress data model"""
    complete: int = 0
    total: int = 0
    percent: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RunProgress':
        """Create RunProgress instance from dictionary"""
        return cls(
            complete=data.get('complete', 0),
            total=data.get('total', 0),
            percent=data.get('percent', 0.0)
        )


@dataclass
class Run:
    """Run (Process) data model"""
    id: str
    increment_id: int
    checklist_id: str
    checklist_title: str
    assign_someone_else: bool
    name: str
    summary: Optional[str] = None
    status: str = "active"
    progress: Optional[RunProgress] = None
    whole_progress: Optional[RunProgress] = None
    started_by: Optional[int] = None
    prerun: Optional[Dict[str, Any]] = None
    prerun_completed_at: Optional[str] = None
    prerun_completed_by: Optional[int] = None
    prerun_length: Optional[int] = None
    starred: bool = False
    created_at: Optional[str] = None
    due_date: Optional[str] = None
    owner_id: Optional[int] = None
    started_at: Optional[str] = None
    last_updated: Optional[str] = None
    completed_at: Optional[str] = None
    late_tasks: Optional[int] = None
    archived_at: Optional[str] = None
    due_date_passed: bool = False
    collaborators: List[int] = None
    due_soon: bool = False
    max_task_deadline: Optional[str] = None

    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.collaborators is None:
            self.collaborators = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Run':
        """Create Run instance from dictionary"""
        progress_data = data.get('progress')
        progress = RunProgress.from_dict(progress_data) if progress_data else None
        
        whole_progress_data = data.get('whole_progress')
        whole_progress = RunProgress.from_dict(whole_progress_data) if whole_progress_data else None
        
        return cls(
            id=data.get('id', ''),
            increment_id=data.get('increment_id', 0),
            checklist_id=data.get('checklist_id', ''),
            checklist_title=data.get('checklist_title', ''),
            assign_someone_else=data.get('assign_someone_else', False),
            name=data.get('name', ''),
            summary=data.get('summary'),
            status=data.get('status', 'active'),
            progress=progress,
            whole_progress=whole_progress,
            started_by=data.get('started_by'),
            prerun=data.get('prerun'),
            prerun_completed_at=data.get('prerun_completed_at'),
            prerun_completed_by=data.get('prerun_completed_by'),
            prerun_length=data.get('prerun_length'),
            starred=data.get('starred', False),
            created_at=data.get('created_at'),
            due_date=data.get('due_date'),
            owner_id=data.get('owner_id'),
            started_at=data.get('started_at'),
            last_updated=data.get('last_updated'),
            completed_at=data.get('completed_at'),
            late_tasks=data.get('late_tasks'),
            archived_at=data.get('archived_at'),
            due_date_passed=data.get('due_date_passed', False),
            collaborators=data.get('collaborators', []),
            due_soon=data.get('due_soon', False),
            max_task_deadline=data.get('max_task_deadline')
        )


@dataclass
class Folder:
    """Folder data model for search results"""
    id: str
    parent: Optional[str]
    name: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Folder':
        """Create Folder instance from dictionary"""
        return cls(
            id=data.get('id', ''),
            parent=data.get('parent'),
            name=data.get('name', '')
        )


@dataclass
class Tag:
    """Tag data model for industry and topic tags"""
    id: str
    title: str
    type: str
    color: str
    created_at: Optional[str] = None
    deleted_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tag':
        """Create Tag instance from dictionary"""
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            type=data.get('type', ''),
            color=data.get('color', ''),
            created_at=data.get('created_at'),
            deleted_at=data.get('deleted_at')
        )


@dataclass
class PrerunField:
    """Prerun field data model"""
    id: str
    checklist_id: str
    alias: str
    field_type: str
    guidance: Optional[str] = None
    position: int = 1
    required: bool = True
    use_wysiwyg_editor: bool = True
    collect_time: bool = True
    options: List[Dict[str, Any]] = None
    field_validation: List[str] = None
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.options is None:
            self.options = []
        if self.field_validation is None:
            self.field_validation = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrerunField':
        """Create PrerunField instance from dictionary"""
        return cls(
            id=data.get('id', ''),
            checklist_id=data.get('checklist_id', ''),
            alias=data.get('alias', ''),
            field_type=data.get('field_type', 'text'),
            guidance=data.get('guidance'),
            position=data.get('position', 1),
            required=data.get('required', True),
            use_wysiwyg_editor=data.get('use_wysiwyg_editor', True),
            collect_time=data.get('collect_time', True),
            options=data.get('options', []),
            field_validation=data.get('field_validation', []),
            created_at=data.get('created_at'),
            last_updated=data.get('last_updated')
        )


@dataclass
class AutomationCondition:
    """Automation condition data model"""
    id: str
    conditionable_id: str
    conditionable_type: str
    operation: str
    statement: str
    logic: str
    position: int
    column_contains_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationCondition':
        """Create AutomationCondition instance from dictionary"""
        return cls(
            id=data.get('id', ''),
            conditionable_id=data.get('conditionable_id', ''),
            conditionable_type=data.get('conditionable_type', ''),
            operation=data.get('operation', ''),
            statement=data.get('statement', ''),
            logic=data.get('logic', ''),
            position=data.get('position', 0),
            column_contains_name=data.get('column_contains_name')
        )


@dataclass
class AutomationDeadline:
    """Automation deadline data model"""
    value: int
    unit: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationDeadline':
        """Create AutomationDeadline instance from dictionary"""
        return cls(
            value=data.get('value', 0),
            unit=data.get('unit', 'days')
        )


@dataclass
class AutomationAssignees:
    """Automation assignees data model"""
    users: List[int] = None
    guests: List[str] = None
    groups: List[str] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.users is None:
            self.users = []
        if self.guests is None:
            self.guests = []
        if self.groups is None:
            self.groups = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationAssignees':
        """Create AutomationAssignees instance from dictionary"""
        return cls(
            users=data.get('users', []),
            guests=data.get('guests', []),
            groups=data.get('groups', [])
        )


@dataclass
class AutomationAction:
    """Automation action data model"""
    id: str
    action_type: str
    action_verb: str
    target_step_id: Optional[str] = None
    position: int = 0
    actionable_id: Optional[str] = None
    actionable_type: Optional[str] = None
    deadline: Optional[AutomationDeadline] = None
    assignees: Optional[AutomationAssignees] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationAction':
        """Create AutomationAction instance from dictionary"""
        deadline_data = data.get('deadline')
        deadline = AutomationDeadline.from_dict(deadline_data) if deadline_data else None
        
        assignees_data = data.get('assignees')
        assignees = AutomationAssignees.from_dict(assignees_data) if assignees_data else None
        
        return cls(
            id=data.get('id', ''),
            action_type=data.get('action_type', ''),
            action_verb=data.get('action_verb', ''),
            target_step_id=data.get('target_step_id'),
            position=data.get('position', 0),
            actionable_id=data.get('actionable_id'),
            actionable_type=data.get('actionable_type'),
            deadline=deadline,
            assignees=assignees
        )


@dataclass
class AutomatedAction:
    """Automated action data model"""
    id: str
    automated_alias: str
    conditions: List[AutomationCondition] = None
    then_actions: List[AutomationAction] = None
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    archived_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.conditions is None:
            self.conditions = []
        if self.then_actions is None:
            self.then_actions = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomatedAction':
        """Create AutomatedAction instance from dictionary"""
        conditions_data = data.get('conditions', [])
        conditions = [AutomationCondition.from_dict(cond_data) for cond_data in conditions_data] if conditions_data else []
        
        actions_data = data.get('then_actions', [])
        then_actions = [AutomationAction.from_dict(action_data) for action_data in actions_data] if actions_data else []
        
        return cls(
            id=data.get('id', ''),
            automated_alias=data.get('automated_alias', ''),
            conditions=conditions,
            then_actions=then_actions,
            created_at=data.get('created_at'),
            last_updated=data.get('last_updated'),
            archived_at=data.get('archived_at')
        )


@dataclass
class Template:
    """Template data model"""
    id: str
    title: str
    summary: Optional[str] = None
    starred: bool = True
    webhook: Optional[str] = None
    explanation_video: Optional[str] = None
    guidance: Optional[str] = None
    icon: Optional[str] = None
    alias: Optional[str] = None
    prerun: List[PrerunField] = None
    automated_actions: List[AutomatedAction] = None
    created_by: Optional[int] = None
    owner_id: Optional[int] = None
    started_processes: int = 0
    kickoff_title: Optional[str] = None
    kickoff_description: Optional[str] = None
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    archived_at: Optional[str] = None
    is_public: bool = True
    is_featured: bool = True
    users: List[int] = None
    groups: List[str] = None
    public_cover: Optional[str] = None
    industry_tags: List[Tag] = None
    topic_tags: List[Tag] = None
    type: Optional[str] = None
    default_process_name_format: Optional[str] = None
    is_public_kickoff: bool = True
    dual_version_enabled: bool = True
    is_published_state: bool = True
    auto_naming: bool = True
    last_updated_by: Optional[str] = None
    linked_tasks: List[Task] = None
    folderize_process: bool = True
    tag_process: bool = True
    allow_launcher_change_name: bool = True
    is_pinned: bool = True
    ko_form_blueprint_id: Optional[str] = None
    default_folder: Optional[str] = None
    folder_changeable_by_launcher: bool = True
    kickoff_sharing_user_id: Optional[int] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.prerun is None:
            self.prerun = []
        if self.automated_actions is None:
            self.automated_actions = []
        if self.users is None:
            self.users = []
        if self.groups is None:
            self.groups = []
        if self.industry_tags is None:
            self.industry_tags = []
        if self.topic_tags is None:
            self.topic_tags = []
        if self.linked_tasks is None:
            self.linked_tasks = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """Create Template instance from dictionary"""
        prerun_data = data.get('prerun', [])
        prerun = [PrerunField.from_dict(field_data) for field_data in prerun_data] if prerun_data else []
        
        automated_actions_data = data.get('automated_actions', [])
        automated_actions = [AutomatedAction.from_dict(action_data) for action_data in automated_actions_data] if automated_actions_data else []
        
        industry_tags_data = data.get('industry_tags', [])
        industry_tags = [Tag.from_dict(tag_data) for tag_data in industry_tags_data] if industry_tags_data else []
        
        topic_tags_data = data.get('topic_tags', [])
        topic_tags = [Tag.from_dict(tag_data) for tag_data in topic_tags_data] if topic_tags_data else []
        
        linked_tasks_data = data.get('linked_tasks', [])
        linked_tasks = [Task.from_dict(task_data) for task_data in linked_tasks_data] if linked_tasks_data else []
        
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            summary=data.get('summary'),
            starred=data.get('starred', True),
            webhook=data.get('webhook'),
            explanation_video=data.get('explanation_video'),
            guidance=data.get('guidance'),
            icon=data.get('icon'),
            alias=data.get('alias'),
            prerun=prerun,
            automated_actions=automated_actions,
            created_by=data.get('created_by'),
            owner_id=data.get('owner_id'),
            started_processes=data.get('started_processes', 0),
            kickoff_title=data.get('kickoff_title'),
            kickoff_description=data.get('kickoff_description'),
            created_at=data.get('created_at'),
            last_updated=data.get('last_updated'),
            archived_at=data.get('archived_at'),
            is_public=data.get('is_public', True),
            is_featured=data.get('is_featured', True),
            users=data.get('users', []),
            groups=data.get('groups', []),
            public_cover=data.get('public_cover'),
            industry_tags=industry_tags,
            topic_tags=topic_tags,
            type=data.get('type'),
            default_process_name_format=data.get('default_process_name_format'),
            is_public_kickoff=data.get('is_public_kickoff', True),
            dual_version_enabled=data.get('dual_version_enabled', True),
            is_published_state=data.get('is_published_state', True),
            auto_naming=data.get('auto_naming', True),
            last_updated_by=data.get('last_updated_by'),
            linked_tasks=linked_tasks,
            folderize_process=data.get('folderize_process', True),
            tag_process=data.get('tag_process', True),
            allow_launcher_change_name=data.get('allow_launcher_change_name', True),
            is_pinned=data.get('is_pinned', True),
            ko_form_blueprint_id=data.get('ko_form_blueprint_id'),
            default_folder=data.get('default_folder'),
            folder_changeable_by_launcher=data.get('folder_changeable_by_launcher', True),
            kickoff_sharing_user_id=data.get('kickoff_sharing_user_id')
        )


@dataclass
class StepStartDate:
    """Step start date data model"""
    value: int = 0
    unit: str = "days"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepStartDate':
        """Create StepStartDate instance from dictionary"""
        return cls(
            value=data.get('value', 0),
            unit=data.get('unit', 'days')
        )


@dataclass
class StepDeadline:
    """Step deadline data model"""
    value: int = 0
    unit: str = "days"
    option: str = "from"
    step: str = "start_run"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepDeadline':
        """Create StepDeadline instance from dictionary"""
        return cls(
            value=data.get('value', 0),
            unit=data.get('unit', 'days'),
            option=data.get('option', 'from'),
            step=data.get('step', 'start_run')
        )


@dataclass
class StepBpToLaunch:
    """Step blueprint to launch data model"""
    id: Optional[str] = None
    default_name_format: Optional[str] = None
    tasks_within_process: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepBpToLaunch':
        """Create StepBpToLaunch instance from dictionary"""
        return cls(
            id=data.get('id'),
            default_name_format=data.get('default_name_format'),
            tasks_within_process=data.get('tasks_within_process', True)
        )


@dataclass
class Capture:
    """Capture (form field) data model"""
    id: str
    step_id: str
    field_type: str
    label: str
    guidance: Optional[str] = None
    position: int = 1
    required: bool = True
    options: List[Dict[str, Any]] = None
    columns: List[Dict[str, Any]] = None
    default_value_enabled: bool = False
    default_value: Optional[str] = None
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.options is None:
            self.options = []
        if self.columns is None:
            self.columns = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Capture':
        """Create Capture instance from dictionary"""
        return cls(
            id=data.get('id', ''),
            step_id=data.get('step_id', ''),
            field_type=data.get('field_type', 'text'),
            label=data.get('label', ''),
            guidance=data.get('guidance'),
            position=data.get('position', 1),
            required=data.get('required', True),
            options=data.get('options', []),
            columns=data.get('columns', []),
            default_value_enabled=data.get('default_value_enabled', False),
            default_value=data.get('default_value'),
            created_at=data.get('created_at'),
            last_updated=data.get('last_updated')
        )


@dataclass
class Step:
    """Step data model"""
    id: str
    checklist_id: str
    title: str
    alias: Optional[str] = None
    summary: Optional[str] = None
    step_type: Optional[str] = None
    position: int = 1
    allow_guest_owners: bool = False
    max_assignable: int = 1
    skip_start_process: bool = False
    can_complete_only_assignees: bool = False
    everyone_must_complete: bool = False
    webhook: Optional[str] = None
    start_date: Optional[StepStartDate] = None
    is_soft_start_date: bool = False
    deadline: Optional[StepDeadline] = None
    bp_to_launch: Optional[StepBpToLaunch] = None
    assignees: List[int] = None
    guests: List[str] = None
    captures: List[Capture] = None
    prevent_guest_comment: bool = False
    roles: List[str] = None
    role_changes_every_time: bool = False
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    archived_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.assignees is None:
            self.assignees = []
        if self.guests is None:
            self.guests = []
        if self.captures is None:
            self.captures = []
        if self.roles is None:
            self.roles = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Step':
        """Create Step instance from dictionary"""
        start_date_data = data.get('start_date')
        start_date = StepStartDate.from_dict(start_date_data) if start_date_data else None
        
        deadline_data = data.get('deadline')
        deadline = StepDeadline.from_dict(deadline_data) if deadline_data else None
        
        bp_to_launch_data = data.get('bp_to_launch')
        bp_to_launch = StepBpToLaunch.from_dict(bp_to_launch_data) if bp_to_launch_data else None
        
        captures_data = data.get('captures', [])
        captures = [Capture.from_dict(capture_data) for capture_data in captures_data] if captures_data else []
        
        return cls(
            id=data.get('id', ''),
            checklist_id=data.get('checklist_id', ''),
            title=data.get('title', ''),
            alias=data.get('alias'),
            summary=data.get('summary'),
            step_type=data.get('step_type'),
            position=data.get('position', 1),
            allow_guest_owners=data.get('allow_guest_owners', False),
            max_assignable=data.get('max_assignable', 1),
            skip_start_process=data.get('skip_start_process', False),
            can_complete_only_assignees=data.get('can_complete_only_assignees', False),
            everyone_must_complete=data.get('everyone_must_complete', False),
            webhook=data.get('webhook'),
            start_date=start_date,
            is_soft_start_date=data.get('is_soft_start_date', False),
            deadline=deadline,
            bp_to_launch=bp_to_launch,
            assignees=data.get('assignees', []),
            guests=data.get('guests', []),
            captures=captures,
            prevent_guest_comment=data.get('prevent_guest_comment', False),
            roles=data.get('roles', []),
            role_changes_every_time=data.get('role_changes_every_time', False),
            created_at=data.get('created_at'),
            last_updated=data.get('last_updated'),
            archived_at=data.get('archived_at')
        )


@dataclass
class SearchResult:
    """Search result data model for templates, processes, and tasks"""
    id: str
    increment_id: int
    search_type: str
    
    # Common fields
    name: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    
    # Template-specific fields
    steps_count: Optional[int] = None
    icon: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    organization_id: Optional[str] = None
    folders: Optional[List[Folder]] = None
    
    # Process-specific fields
    due_date_passed: Optional[bool] = None
    due_soon: Optional[bool] = None
    
    # Task-specific fields
    status_label: Optional[str] = None
    position: Optional[int] = None
    deadline: Optional[str] = None
    created_at: Optional[str] = None
    starter_id: Optional[int] = None
    is_oneoff_task: Optional[bool] = None
    owners: Optional[TaskOwners] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.folders is None:
            self.folders = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], search_type: str) -> 'SearchResult':
        """Create SearchResult instance from dictionary"""
        folders_data = data.get('folders', [])
        folders = [Folder.from_dict(folder_data) for folder_data in folders_data] if folders_data else []
        
        owners_data = data.get('owners')
        owners = TaskOwners.from_dict(owners_data) if owners_data else None
        
        return cls(
            id=data.get('id', ''),
            increment_id=data.get('increment_id', 0),
            search_type=search_type,
            name=data.get('name'),
            title=data.get('title'),
            status=data.get('status'),
            type=data.get('type'),
            steps_count=data.get('steps_count'),
            icon=data.get('icon'),
            is_public=data.get('is_public'),
            is_featured=data.get('is_featured'),
            organization_id=data.get('organization_id'),
            folders=folders,
            due_date_passed=data.get('due_date_passed'),
            due_soon=data.get('due_soon'),
            status_label=data.get('status_label'),
            position=data.get('position'),
            deadline=data.get('deadline'),
            created_at=data.get('created_at'),
            starter_id=data.get('starter_id'),
            is_oneoff_task=data.get('is_oneoff_task'),
            owners=owners
        )


@dataclass
class PaginationLinks:
    """Pagination links data model"""
    next: Optional[str] = None
    prev: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaginationLinks':
        """Create PaginationLinks instance from dictionary"""
        return cls(
            next=data.get('next'),
            prev=data.get('prev')
        )


@dataclass
class PaginationMeta:
    """Pagination metadata model"""
    total: int
    count: int
    per_page: int
    current_page: int
    total_pages: int
    links: Optional[PaginationLinks] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaginationMeta':
        """Create PaginationMeta instance from dictionary"""
        links_data = data.get('links', {})
        links = PaginationLinks.from_dict(links_data) if links_data else None
        
        return cls(
            total=data.get('total', 0),
            count=data.get('count', 0),
            per_page=data.get('per_page', 0),
            current_page=data.get('current_page', 1),
            total_pages=data.get('total_pages', 0),
            links=links
        )


@dataclass
class TemplatesList:
    """Templates list response with pagination"""
    data: List[Template]
    meta: PaginationMeta
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplatesList':
        """Create TemplatesList instance from dictionary"""
        templates_data = data.get('data', [])
        templates = [Template.from_dict(template_data) for template_data in templates_data]
        
        meta_data = data.get('meta', {})
        pagination_meta = meta_data.get('pagination', {})
        meta = PaginationMeta.from_dict(pagination_meta)
        
        return cls(
            data=templates,
            meta=meta
        )