# -*- coding: utf-8 -*-

"""
SHIFT PROJECT Scenes - Transitions Package
____________________________________________________________________________________________________
Scene transition effects
version : 1.0
____________________________________________________________________________________________________
All transitions work with the static SceneManager architecture
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from .base import BaseTransition
from .fade import FadeIn, FadeOut, CrossFade
from .polygon import (
    LeftHexagonTransition,
    RightHexagonTransition,
    LeftHexagonReverseTransition,
    RightHexagonReverseTransition,
)
from .video import VideoTransition

__all__ = [
    "BaseTransition",
    "FadeIn",
    "FadeOut",
    "CrossFade",
    "LeftHexagonTransition",
    "RightHexagonTransition",
    "LeftHexagonReverseTransition",
    "RightHexagonReverseTransition",
    "VideoTransition",
]
