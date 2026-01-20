# -*- coding: utf-8 -*-

"""
game_libs.transition.base
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines the base class for scene transitions.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

# import needed built-in modules
from __future__ import annotations
from typing import TYPE_CHECKING

# import logger
from .. import logger

if TYPE_CHECKING:
    from pygame import Surface


# ----- BaseTransition class ----- #
class BaseTransition:
    """
    Base class for scene transitions.
    """
    def __init__(self, duration: float = 1.0) -> None:
        """
        Initialize the BaseTransition.

        args:
            duration (float): Duration of the transition in milliseconds.
        """
        self._duration = duration / 1000.0  # Convert to seconds
        self._elapsed_time: float = 0.0
        self._is_playing: bool = False
        self._is_complete: bool = False
        logger.info(f"[{self.__class__.__name__}] Initialized with duration: {self._duration}s")

    @property
    def progress(self) -> float:
        """
        Get the progress of the transition as a float between 0.0 and 1.0.
        """
        progress = min(self._elapsed_time / self._duration, 1.0)
        return progress

    @property
    def duration(self) -> float:
        """
        Get the duration of the transition in milliseconds.
        """
        return self._duration * 1000.0  # Return in milliseconds

    @property
    def is_complete(self) -> bool:
        """
        Check if the transition is complete.
        """
        return self._is_complete

    @property
    def is_playing(self) -> bool:
        """
        Check if the transition is currently playing.
        """
        return self._is_playing

    def start(self) -> None:
        """
        Start the transition.
        """
        self._is_playing = True
        self._is_complete = False
        self._elapsed_time = 0.0
        logger.info(f"[{self.__class__.__name__}] Transition started.")

    def update(self, dt: float) -> None:
        """
        Update the transition state.

        args:
            dt (float): Time delta since the last update in seconds.
        """
        self._elapsed_time += dt
        logger.debug(f"[{self.__class__.__name__}] Updated elapsed time: {self._elapsed_time}s")

        if self._elapsed_time >= self._duration:
            self._elapsed_time = self._duration
            self._is_complete = True
            self._is_playing = False
            logger.info(f"[{self.__class__.__name__}] Transition completed.")

    def render(self, surface: Surface) -> None:
        """
        Render the transition effect on the given surface.

        args:
            surface (Surface): The surface to render the transition on.
        """
        raise NotImplementedError("render() method must be implemented by subclasses.")

    def reset(self) -> None:
        """
        Reset the transition to its initial state.
        """
        self._elapsed_time = 0.0
        self._is_playing = False
        self._is_complete = False
        logger.info(f"[{self.__class__.__name__}] Transition reset.")
