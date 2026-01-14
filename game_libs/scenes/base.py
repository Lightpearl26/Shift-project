# -*- coding: utf-8 -*-

"""
game_libs.scene.base
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines the BaseScene class,
    which serves as the base class for all scenes in the game.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

# import needed built-in modules
from __future__ import annotations
from typing import TYPE_CHECKING, Optional

# import logger
from .. import logger

if TYPE_CHECKING:
    from ..managers.scene import SceneManager
    from ..managers.event import EventManager
    from pygame import Surface

# ----- BaseScene class ----- #
class BaseScene:
    """
    BaseScene object

    This is the base class for all scenes in the game.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the BaseScene.

        Args:
            - name (str): The name of the scene.
        """
        self.name: str = name
        self.scene_manager: Optional[type[SceneManager]] = None
        self.event_manager: Optional[type[EventManager]] = None
        logger.info(f"[BaseScene] Initialized scene: {self.name}")

    def init(self) -> None:
        """
        Initialize the scene.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("init() method must be overridden in subclasses.")

    def on_enter(self) -> None:
        """
        Called when the scene is entered.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("on_enter() method must be overridden in subclasses.")

    def on_exit(self) -> None:
        """
        Called when the scene is exited.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("on_exit() method must be overridden in subclasses.")

    def update(self, dt: float) -> None:
        """
        Update the scene.

        Args:
            - dt (float): Time delta since the last update.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("update() method must be overridden in subclasses.")

    def handle_events(self) -> None:
        """
        Handle input events for the scene.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("handle_events() method must be overridden in subclasses.")

    def render(self, surface: Surface) -> None:
        """
        Render the scene onto the given surface.

        Args:
            - surface (Surface): The surface to render the scene on.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("render() method must be overridden in subclasses.")
