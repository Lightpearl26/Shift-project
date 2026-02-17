# -*- coding: utf-8 -*-

"""
SHIFT PROJECT Scenes Package
____________________________________________________________________________________________________
Game scenes (title, level, pause, options, game over)
version : 1.0
____________________________________________________________________________________________________
All game scene classes inherit from BaseScene and are managed by SceneManager
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from .base import BaseScene
from .welcome import WelcomeScene
from .main_menu import MainMenuScene
from .game_test import GameTestScene
from .pause_menu import PauseMenuScene
from .options import OptionScene

__all__ = [
    "BaseScene",
    "WelcomeScene",
    "MainMenuScene",
    "GameTestScene",
    "PauseMenuScene",
    "OptionScene"
]
