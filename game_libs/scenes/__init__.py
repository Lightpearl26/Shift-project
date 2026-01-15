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
from .welcome import WelcomeScene
from .main_menu import MainMenuScene

__all__ = [
    "BaseScene",
    "WelcomeScene",
    "MainMenuScene"
]
