"""
Task Management Package

This package provides a refactored, modular approach to task management
functionality, breaking down the monolithic TaskManagement class into
specialized components for better maintainability and separation of concerns.

Classes:
    TaskRetrieval: Task and process retrieval operations
    TaskSearch: Search operations for tasks, processes, and templates  
    TaskCreation: Task creation operations
    TaskManager: Unified interface combining all functionality
"""

from .base import TaskManagerBase
from .retrieval import TaskRetrieval
from .search import TaskSearch
from .creation import TaskCreation


class TaskManager:
    """
    Unified interface for task management functionality.
    
    This class provides access to all task management capabilities
    through a single interface while maintaining the modular structure
    underneath.
    """
    
    def __init__(self, sdk):
        """
        Initialize task manager with SDK instance.
        
        Args:
            sdk: Main SDK instance
        """
        self.retrieval = TaskRetrieval(sdk)
        self._search_service = TaskSearch(sdk)  # Use private name to avoid conflict
        self.creation = TaskCreation(sdk)
        
        # For backward compatibility, expose common methods at the top level
        
        # Retrieval methods
        self.get_my_tasks = self.retrieval.get_my_tasks
        self.get_user_tasks = self.retrieval.get_user_tasks
        self.get_tasks_for_process = self.retrieval.get_tasks_for_process
        self.get_organization_runs = self.retrieval.get_organization_runs
        self.get_organization_processes = self.retrieval.get_organization_processes
        
        # Search methods
        self.search_processes_by_name = self._search_service.search_processes_by_name
        self.search = self._search_service.search  # Main search method for backward compatibility
        self.search_processes = self._search_service.search_processes
        self.search_templates = self._search_service.search_templates
        self.search_tasks = self._search_service.search_tasks
        self.find_process_by_name = self._search_service.find_process_by_name
        
        # Creation methods
        self.create_task = self.creation.create_task
        self.create_simple_task = self.creation.create_simple_task
        self.create_user_task = self.creation.create_user_task
        self.create_guest_task = self.creation.create_guest_task
        self.create_group_task = self.creation.create_group_task
    
    @property
    def search_service(self):
        """Access to the TaskSearch service object for advanced search operations."""
        return self._search_service


# For backward compatibility, create an alias
TaskManagement = TaskManager

__all__ = [
    'TaskManagerBase',
    'TaskRetrieval', 
    'TaskSearch',
    'TaskCreation',
    'TaskManager',
    'TaskManagement'  # Backward compatibility alias
]