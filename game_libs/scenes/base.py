# -*- coding: utf-8 -*-

"""
SHIFT PROJECT Scenes
____________________________________________________________________________________________________
Base Scene class for all game scenes
version : 1.0
____________________________________________________________________________________________________
Defines the interface that all scenes must implement
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface
    from ..managers.scene import SceneManager


class BaseScene:
    """
    Base class for all game scenes.
    
    A scene represents a state of the game (title screen, pause menu, level, etc).
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the scene.
        
        Args:
            name: The name of this scene (for debugging/logging)
        """
        self.name: str = name
        self.scene_manager: type[SceneManager] | None = None

    def init(self) -> None:
        """
        Initialize scene resources.
        Called once when the scene is added to the SceneManager.
        """
        raise NotImplementedError("init method must be implemented by subclasses")

    def handle_events(self, key_events: dict[str, bool]) -> None:
        """
        Handle input events for the scene.
        
        Args:
            key_events: Dictionary of key states
        """
        raise NotImplementedError("handle_events method must be implemented by subclasses")

    def update(self, dt: float) -> None:
        """
        Update the scene state.
        
        Args:
            dt: Delta time since last frame (in milliseconds)
        """
        raise NotImplementedError("update method must be implemented by subclasses")

    def render(self, surface: Surface) -> None:
        """
        Render the scene onto the given surface.
        
        Args:
            surface: The pygame Surface to render to
        """
        raise NotImplementedError("render method must be implemented by subclasses")
