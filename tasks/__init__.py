"""
Tasks for AI Operations Assistant Environment
"""

from tasks.base_task import BaseTask
from tasks.easy import EasyEmailClassificationTask
from tasks.medium import MediumSupportHandlingTask
from tasks.hard import HardFullOperationsTask


TASKS = [
    EasyEmailClassificationTask,
    MediumSupportHandlingTask,
    HardFullOperationsTask,
]

TASK_REGISTRY = {
    "easy": {
        "task_class": EasyEmailClassificationTask,
        "grader": "graders.grader_easy.EasyGrader",
        "grader_enabled": True,
    },
    "medium": {
        "task_class": MediumSupportHandlingTask,
        "grader": "graders.grader_medium.MediumGrader",
        "grader_enabled": True,
    },
    "hard": {
        "task_class": HardFullOperationsTask,
        "grader": "graders.grader_hard.HardGrader",
        "grader_enabled": True,
    },
}

TASKS_WITH_GRADERS = [
    {
        "task": EasyEmailClassificationTask,
        "grader": "graders.grader_easy.EasyGrader",
    },
    {
        "task": MediumSupportHandlingTask,
        "grader": "graders.grader_medium.MediumGrader",
    },
    {
        "task": HardFullOperationsTask,
        "grader": "graders.grader_hard.HardGrader",
    },
]

__all__ = [
    "BaseTask",
    "EasyEmailClassificationTask",
    "MediumSupportHandlingTask",
    "HardFullOperationsTask",
    "TASKS",
    "TASK_REGISTRY",
    "TASKS_WITH_GRADERS",
]
