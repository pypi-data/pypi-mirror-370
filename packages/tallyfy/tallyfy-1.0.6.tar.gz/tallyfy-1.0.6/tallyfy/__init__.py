"""
Tallyfy SDK - A modular Python SDK for Tallyfy API
"""

from .core import TallyfySDK, TallyfyError
from .models import *
from .user_management import UserManager, UserManagement
from .task_management import TaskManager, TaskManagement
from .template_management import TemplateManager, TemplateManagement
from .form_fields_management import FormFieldManager, FormFieldManagement

__version__ = "1.0.0"
__all__ = [
    "TallyfySDK",
    "TallyfyError",
    "UserManager",
    "UserManagement", 
    "TaskManager",
    "TaskManagement",
    "TemplateManager",
    "TemplateManagement",
    "FormFieldManager",
    "FormFieldManagement"
]