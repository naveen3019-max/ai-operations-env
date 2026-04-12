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
        "grader_key": "easy",
        "grader_path": "graders.grader_easy.EasyGrader",
        "grader_import_path": "graders.easy.EasyGrader",
        "grader_enabled": True,
    },
    "medium": {
        "task_class": MediumSupportHandlingTask,
        "grader": "graders.grader_medium.MediumGrader",
        "grader_key": "medium",
        "grader_path": "graders.grader_medium.MediumGrader",
        "grader_import_path": "graders.medium.MediumGrader",
        "grader_enabled": True,
    },
    "hard": {
        "task_class": HardFullOperationsTask,
        "grader": "graders.grader_hard.HardGrader",
        "grader_key": "hard",
        "grader_path": "graders.grader_hard.HardGrader",
        "grader_import_path": "graders.hard.HardGrader",
        "grader_enabled": True,
    },
}

TASKS_WITH_GRADERS = [
    {
        "task": EasyEmailClassificationTask,
        "grader": "graders.grader_easy.EasyGrader",
        "grader_key": "easy",
        "grader_path": "graders.grader_easy.EasyGrader",
        "grader_import_path": "graders.easy.EasyGrader",
    },
    {
        "task": MediumSupportHandlingTask,
        "grader": "graders.grader_medium.MediumGrader",
        "grader_key": "medium",
        "grader_path": "graders.grader_medium.MediumGrader",
        "grader_import_path": "graders.medium.MediumGrader",
    },
    {
        "task": HardFullOperationsTask,
        "grader": "graders.grader_hard.HardGrader",
        "grader_key": "hard",
        "grader_path": "graders.grader_hard.HardGrader",
        "grader_import_path": "graders.hard.HardGrader",
    },
]

TASKS_WITH_GRADERS_COUNT = len(TASKS_WITH_GRADERS)

tasks = [
    {
        "name": "Email Classification",
        "task": EasyEmailClassificationTask,
        "grader": "graders.grader_easy.EasyGrader",
        "grader_key": "easy",
        "grader_path": "graders.grader_easy.EasyGrader",
        "grader_import_path": "graders.easy.EasyGrader",
        "grader_enabled": True,
    },
    {
        "name": "Support Handling",
        "task": MediumSupportHandlingTask,
        "grader": "graders.grader_medium.MediumGrader",
        "grader_key": "medium",
        "grader_path": "graders.grader_medium.MediumGrader",
        "grader_import_path": "graders.medium.MediumGrader",
        "grader_enabled": True,
    },
    {
        "name": "Full Operations Management",
        "task": HardFullOperationsTask,
        "grader": "graders.grader_hard.HardGrader",
        "grader_key": "hard",
        "grader_path": "graders.grader_hard.HardGrader",
        "grader_import_path": "graders.hard.HardGrader",
        "grader_enabled": True,
    },
]

tasks_with_graders = tasks
tasks_with_graders_count = len(tasks_with_graders)

__all__ = [
    "BaseTask",
    "EasyEmailClassificationTask",
    "MediumSupportHandlingTask",
    "HardFullOperationsTask",
    "TASKS",
    "TASK_REGISTRY",
    "TASKS_WITH_GRADERS",
    "TASKS_WITH_GRADERS_COUNT",
    "tasks",
    "tasks_with_graders",
    "tasks_with_graders_count",
]
