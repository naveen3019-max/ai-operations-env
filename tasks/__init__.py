"""
Tasks for AI Operations Assistant Environment
"""

from tasks.base_task import BaseTask
from tasks.easy import EasyEmailClassificationTask
from tasks.medium import MediumSupportHandlingTask
from tasks.hard import HardFullOperationsTask

__all__ = [
    "BaseTask",
    "EasyEmailClassificationTask",
    "MediumSupportHandlingTask",
    "HardFullOperationsTask",
]
