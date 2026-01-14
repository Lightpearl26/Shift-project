# -*- coding : utf-8 -*-
#pylint: disable=no-value-for-parameter

"""
game_libs.managers.scene
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module manages scenes for the game,
    including scene transitions, loading, and unloading.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2025
"""

# Import needed built-in modules
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from enum import Enum, auto

# import game_libs objects
from .. import scenes
from ..managers.event import EventManager

# import game logger
from .. import logger

if TYPE_CHECKING:
    from ..transitions import BaseTransition
    from pygame import Surface


# ----- SceneState enum ----- #
class SceneState(Enum):
    """
    Enum representing the state of the SceneManager.
    """
    NORMAL = auto()
    TRANSITION_IN = auto()
    TRANSITION_OUT = auto()


# ----- SceneManager class ----- #
class SceneManager:
    """
    SceneManager object
    """
    _scenes: dict[str, scenes.BaseScene] = {}
    _current_scene: Optional[scenes.BaseScene] = None
    _next_scene: Optional[scenes.BaseScene] = None
    _previous_scene: Optional[scenes.BaseScene] = None
    _state: SceneState = SceneState.NORMAL

    _transition_out: Optional[BaseTransition] = None
    _transition_in: Optional[BaseTransition] = None

    @classmethod
    def init(cls) -> None:
        """
        Initialize the SceneManager.
        """
        for scene_class_name in scenes.__all__:
            if scene_class_name != "BaseScene":
                logger.info(f"[SceneManager] Available scene: {scene_class_name}")

                # First we instanciate the scene
                scene_class = getattr(scenes, scene_class_name)
                scene_inst: scenes.BaseScene = scene_class()
                scene_inst.scene_manager = cls
                scene_inst.event_manager = EventManager
                scene_name = scene_inst.name
                cls._scenes[scene_name] = scene_inst

                # Then we initialize it
                scene_inst.init()
                logger.info(f"[SceneManager] Initialized scene: {scene_name}")

        logger.info("[SceneManager] Initialization complete.")

    @classmethod
    def handle_events(cls) -> None:
        """
        Handle events for the current scene.
        """
        if cls._state != SceneState.NORMAL or not cls._current_scene:
            return

        cls._current_scene.handle_events()

    @classmethod
    def update(cls, dt: float) -> None:
        """
        Update the current scene.
        args:
            dt (float): Delta time since last update in seconds.
        """
        if cls._current_scene is None:
            return

        # Update transitions if any
        if cls._state == SceneState.TRANSITION_OUT and cls._transition_out:
            cls._transition_out.update(dt)
            if cls._transition_out.is_complete:
                # Unload current scene
                cls._current_scene.on_exit()
                logger.info(f"[SceneManager] Unloaded scene: {cls._current_scene.name}")

                # Load new scene
                cls._next_scene.on_enter()
                cls._previous_scene = cls._current_scene
                cls._current_scene = cls._next_scene
                cls._next_scene = None
                logger.info(f"[SceneManager] Loaded scene: {cls._current_scene.name}")

                # Start transition in
                if cls._transition_in:
                    cls._transition_in.start()
                    cls._state = SceneState.TRANSITION_IN
                else:
                    cls._state = SceneState.NORMAL

        elif cls._state == SceneState.TRANSITION_IN and cls._transition_in:
            cls._transition_in.update(dt)
            if cls._transition_in.is_complete:
                cls._state = SceneState.NORMAL

        # Update the current scene
        cls._current_scene.update(dt)

    @classmethod
    def render(cls, surface: Surface) -> None:
        """
        Render the current scene.
        args:
            surface (Surface): The surface to render the scene onto.
        """
        if cls._current_scene is None:
            return

        if cls._state == SceneState.TRANSITION_OUT and cls._transition_out:
            cls._current_scene.render(surface)
            cls._transition_out.render(surface)
        elif cls._state == SceneState.TRANSITION_IN and cls._transition_in:
            cls._current_scene.render(surface)
            cls._transition_in.render(surface)
        else:
            cls._current_scene.render(surface)

    @classmethod
    def get_scene(cls, name: str) -> Optional[scenes.BaseScene]:
        """
        Get a scene by its name.

        Args:
            - name (str) The name of the scene.

        Returns:
            - scene.BaseScene | None: The scene instance if found, else None.
        """
        return cls._scenes.get(name, None)

    @classmethod
    def get_current_scene(cls) -> Optional[scenes.BaseScene]:
        """
        Get the current active scene.

        Returns:
            - scene.BaseScene | None: The current scene instance if any, else None.
        """
        return cls._current_scene

    @classmethod
    def get_previous_scene(cls) -> Optional[scenes.BaseScene]:
        """
        Get the previous scene before the current one.

        Returns:
            - scene.BaseScene | None: The previous scene instance if any, else None.
        """
        return cls._previous_scene

    @classmethod
    def change_scene(cls,
                     name: str,
                     transition_out: Optional[BaseTransition] = None,
                     transition_in: Optional[BaseTransition] = None) -> None:
        """
        Change the current scene to a new scene.
        Args:
            - name (str) The name of the new scene to switch to.
            - transition_out (BaseTransition | None): Optional transition for exiting the scene.
            - transition_in (BaseTransition | None): Optional transition for entering the scene.
        """
        new_scene = cls.get_scene(name)
        if new_scene is None:
            logger.error(f"[SceneManager] Scene '{name}' not found!")
            return
        cls._next_scene = new_scene
        cls._transition_out = transition_out
        cls._transition_in = transition_in
        if cls._transition_out:
            cls._transition_out.start()
            cls._state = SceneState.TRANSITION_OUT
        else:
            # No transition out, switch immediately
            if cls._current_scene:
                cls._current_scene.on_exit()
                logger.info(f"[SceneManager] Unloaded scene: {cls._current_scene.name}")
            cls._next_scene.on_enter()
            cls._previous_scene = cls._current_scene
            cls._current_scene = cls._next_scene
            cls._next_scene = None
            logger.info(f"[SceneManager] Loaded scene: {cls._current_scene.name}")
            if cls._transition_in:
                cls._transition_in.start()
                cls._state = SceneState.TRANSITION_IN
            else:
                cls._state = SceneState.NORMAL
