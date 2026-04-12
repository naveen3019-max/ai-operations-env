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
        "grader": "easy",
        "grader_path": "graders.grader_easy.EasyGrader",
        "grader_enabled": True,
    },
    "medium": {
        "task_class": MediumSupportHandlingTask,
        "grader": "medium",
        "grader_path": "graders.grader_medium.MediumGrader",
        "grader_enabled": True,
    },
    "hard": {
        "task_class": HardFullOperationsTask,
        "grader": "hard",
        "grader_path": "graders.grader_hard.HardGrader",
        "grader_enabled": True,
    },
}

TASKS_WITH_GRADERS = [
    {
        "task": EasyEmailClassificationTask,
        "grader": "easy",
        "grader_path": "graders.grader_easy.EasyGrader",
    },
    {
        "task": MediumSupportHandlingTask,
        "grader": "medium",
        "grader_path": "graders.grader_medium.MediumGrader",
    },
    {
        "task": HardFullOperationsTask,
        "grader": "hard",
        "grader_path": "graders.grader_hard.HardGrader",
    },
]

tasks = [
    {
        "name": "Email Classification",
        "task": EasyEmailClassificationTask,
        "grader": "easy",
        "grader_path": "graders.grader_easy.EasyGrader",
        "grader_enabled": True,
    },
    {
        "name": "Support Handling",
        "task": MediumSupportHandlingTask,
        "grader": "medium",
        "grader_path": "graders.grader_medium.MediumGrader",
        "grader_enabled": True,
    },
    {
        "name": "Full Operations Management",
        "task": HardFullOperationsTask,
        "grader": "hard",
        "grader_path": "graders.grader_hard.HardGrader",
        "grader_enabled": True,
    },
]

tasks_with_graders = tasks

__all__ = [
    "BaseTask",
    "EasyEmailClassificationTask",
    "MediumSupportHandlingTask",
    "HardFullOperationsTask",
    "TASKS",
    "TASK_REGISTRY",
    "TASKS_WITH_GRADERS",
    "tasks",
    "tasks_with_graders",
]
