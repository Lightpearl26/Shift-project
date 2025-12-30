# -*- coding: utf-8 -*-

"""
SHIFT PROJECT Scenes Package
____________________________________________________________________________________________________
Game scenes (title, level, pause, options, game over) and transitions
version : 1.0
____________________________________________________________________________________________________
All game scene classes inherit from BaseScene and are managed by SceneManager
All transitions inherit from BaseTransition
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from .base import BaseScene
from .title import WelcomeScreen
from . import transitions

__all__ = [
    "BaseScene",
    "WelcomeScreen",
    "transitions",
]
