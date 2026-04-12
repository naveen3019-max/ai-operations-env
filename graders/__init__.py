"""
Graders for task evaluation
"""

from graders.base_grader import BaseGrader
from graders.grader_easy import EasyGrader
from graders.grader_medium import MediumGrader
from graders.grader_hard import HardGrader

GRADERS = {
    "easy": EasyGrader,
    "medium": MediumGrader,
    "hard": HardGrader,
}

GRADER_REGISTRY = {
    "easy": {
        "class": EasyGrader,
        "module": "graders.grader_easy",
        "path": "graders.grader_easy.EasyGrader",
        "alias_path": "graders.easy.EasyGrader",
        "enabled": True,
    },
    "medium": {
        "class": MediumGrader,
        "module": "graders.grader_medium",
        "path": "graders.grader_medium.MediumGrader",
        "alias_path": "graders.medium.MediumGrader",
        "enabled": True,
    },
    "hard": {
        "class": HardGrader,
        "module": "graders.grader_hard",
        "path": "graders.grader_hard.HardGrader",
        "alias_path": "graders.hard.HardGrader",
        "enabled": True,
    },
}

graders = GRADER_REGISTRY

__all__ = [
    "BaseGrader",
    "EasyGrader",
    "MediumGrader",
    "HardGrader",
    "GRADERS",
    "GRADER_REGISTRY",
    "graders",
]
