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
from .fade import FadeIn, FadeOut
from .video import VideoTransition
from .disintegrate import Disintegrate, Integrate
from .dust import DustIn, DustOut

__all__ = [
    "BaseTransition",
    "FadeIn",
    "FadeOut",
    "VideoTransition",
    "Disintegrate",
    "Integrate",
    "DustIn",
    "DustOut"
]
