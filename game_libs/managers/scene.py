#-*- coding: utf-8 -*-
#pylint: disable=import-outside-toplevel, no-value-for-parameter

"""
SHIFT PROJECT game_libs
____________________________________________________________________________________________________
Scene Manager
version : 1.0
____________________________________________________________________________________________________
Manages scene lifecycle and transitions
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from enum import Enum, auto
from .. import logger

if TYPE_CHECKING:
    from pygame import Surface
    from ..scenes.base import BaseScene
    from ..scenes.transitions.base import BaseTransition


# ----- Scene States ----- #
class SceneState(Enum):
    """
    Enumeration of possible scene manager states.
    """
    NORMAL = auto()
    TRANSITIONING_OUT = auto()
    TRANSITIONING_IN = auto()


# ----- Scene Manager ----- #
class SceneManager:
    """
    Manages scenes and transitions between them.
        Static class that manages all game scenes.
    """
    _scenes: dict[str, BaseScene] = {}
    _current_scene: str | None = None
    _next_scene: str | None = None
    _state: SceneState = SceneState.NORMAL

    _transition_out: BaseTransition | None = None
    _transition_in: BaseTransition | None = None

    @classmethod
    def init(cls) -> None:
        """Initialize the SceneManager and load all scenes."""
        from .. import scenes
        for attr in scenes.__all__:
            if not (attr == "transitions" or attr == "BaseScene"):
                scene_class = getattr(scenes, attr)
                scene_instance = scene_class()
                cls.add_scene(scene_instance)
        logger.info(f"[SceneManager] initialized with {len(cls._scenes)} scenes.")

    @classmethod
    def add_scene(cls, scene: BaseScene) -> None:
        """
        Add a scene to the manager.
        
        Args:
            scene: The scene instance to add
        """
        cls._scenes[scene.name] = scene
        scene.scene_manager = cls
        logger.info(f"[SceneManager] added scene '{scene.name}'.")

    @classmethod
    def get_scene(cls, scene_name: str) -> BaseScene:
        """
        Get a scene by name.
        
        Args:
            scene_name: Name of the scene to retrieve
        
        Returns:
            The requested scene instance
        """
        if scene_name not in cls._scenes:
            logger.error(f"[SceneManager] Scene '{scene_name}' not found.")
            raise KeyError(f"Scene '{scene_name}' not found.")
        return cls._scenes[scene_name]

    @classmethod
    def set_scene(cls, scene_name: str) -> None:
        """
        Set the current scene (without transition).
        
        Args:
            scene_name: Name of the scene to activate
        """
        if scene_name not in cls._scenes:
            logger.error(f"[SceneManager] Scene '{scene_name}' not found.")
            return

        cls._current_scene = scene_name
        # Initialize the scene when it becomes active
        cls._scenes[scene_name].init()
        cls._state = SceneState.NORMAL

    @classmethod
    def change_scene(
        cls,
        scene_name: str,
        transition_out: BaseTransition | None = None,
        transition_in: BaseTransition | None = None
    ) -> None:
        """
        Change to a new scene, optionally with transitions.
        
        Args:
            scene_name: Name of the scene to transition to
            transition_out: Optional transition out of current scene
            transition_in: Optional transition into new scene
        """
        if scene_name not in cls._scenes:
            logger.error(f"[SceneManager] Scene '{scene_name}' not found.")
            return

        cls._next_scene = scene_name
        cls._transition_out = transition_out
        cls._transition_in = transition_in

        logger.info(
            f"[SceneManager] changing scene '{cls._current_scene}' to scene '{scene_name}'."
        )

        if transition_out is not None and cls._current_scene is not None:
            # Start transition out
            cls._state = SceneState.TRANSITIONING_OUT
            logger.info("[SceneManager] starting transition out.")
            cls._transition_out.play()
        else:
            # No transition, switch immediately
            cls._switch_to_next_scene()

    @classmethod
    def update(cls, dt: float) -> None:
        """
        Update the current scene or transition.
        
        Args:
            dt: Delta time since last frame (in milliseconds)
        """
        if cls._state == SceneState.NORMAL:
            if cls._current_scene is not None:
                cls._scenes[cls._current_scene].update(dt)
            else:
                raise RuntimeError("No current scene to update.")

        elif cls._state == SceneState.TRANSITIONING_OUT:
            if cls._transition_out is not None:
                cls._transition_out.update(dt)

                if cls._transition_out.is_complete:
                    # Transition out finished, switch scene
                    cls._switch_to_next_scene()

        elif cls._state == SceneState.TRANSITIONING_IN:
            if cls._transition_in is not None:
                cls._transition_in.update(dt)

                # Update the new scene during transition in
                if cls._current_scene is not None:
                    cls._scenes[cls._current_scene].update(dt)

                if cls._transition_in.is_complete:
                    # Transition in finished, return to normal
                    cls._state = SceneState.NORMAL
                    cls._transition_in = None
        logger.debug(f"[SceneManager] update dt={dt:.4f} in state {cls._state.name}.")

    @classmethod
    def render(cls, surface: Surface) -> None:
        """
        Render the current scene or transition.
        
        Args:
            surface: The pygame Surface to render to
        """
        if cls._state == SceneState.NORMAL:
            if cls._current_scene is not None:
                cls._scenes[cls._current_scene].render(surface)
            else:
                raise RuntimeError("No current scene to render.")

        elif cls._state == SceneState.TRANSITIONING_OUT:
            if cls._transition_out is not None:
                cls._transition_out.render(surface)

        elif cls._state == SceneState.TRANSITIONING_IN:
            if cls._transition_in is not None:
                cls._transition_in.render(surface)
        logger.debug(f"[SceneManager] render in state {cls._state.name}.")

    @classmethod
    def handle_events(cls, key_events: dict[str, dict[str, bool]]) -> None:
        """
        Handle input events for the current scene.
        
        Args:
            key_events: Dictionary of key states from EventManager
        """
        # Don't process events during transitions
        if cls._state != SceneState.NORMAL:
            return

        if cls._current_scene is not None:
            cls._scenes[cls._current_scene].handle_events(key_events)

    @classmethod
    def _switch_to_next_scene(cls) -> None:
        """Internal method to switch from current scene to next scene"""
        # Switch to next scene
        cls._current_scene = cls._next_scene
        cls._next_scene = None

        # Initialize/reset the newly activated scene
        if cls._current_scene is not None:
            cls._scenes[cls._current_scene].init()
            logger.debug(f"[SceneManager] switched to scene '{cls._current_scene}'.")

        # Start transition in if specified
        if cls._transition_in is not None and cls._current_scene is not None:
            cls._state = SceneState.TRANSITIONING_IN
            logger.info("[SceneManager] starting transition in.")
            cls._transition_in.play()
        else:
            # No transition in, return to normal immediately
            cls._state = SceneState.NORMAL

        # Clean up transition out
        cls._transition_out = None
