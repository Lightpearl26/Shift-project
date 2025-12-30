# -*- coding: utf-8 -*-

"""
SHIFT PROJECT Scenes
____________________________________________________________________________________________________
Base Transition class for scene transitions
version : 1.0
____________________________________________________________________________________________________
Defines the interface that all transitions must implement
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface


class BaseTransition:
    """
    Abstract base class for all scene transitions.
    
    A transition handles the visual effect between two scenes.
    Compatible with the static SceneManager architecture.
    """

    def __init__(self, duration: float) -> None:
        """
        Initialize the transition.
        
        Args:
            duration: Duration of the transition in milliseconds
        """
        self._duration = duration / 1000.0  # Convert ms to seconds
        self._elapsed = 0.0
        self._is_playing = False
        self._is_complete = False

    @property
    def duration(self) -> float:
        """Get the transition duration in milliseconds"""
        return self._duration * 1000.0  # Return in milliseconds

    @property
    def progress(self) -> float:
        """
        Get the transition progress (0.0 to 1.0).
        
        Returns:
            Float between 0.0 (start) and 1.0 (end)
        """
        if self._duration <= 0:
            return 1.0
        return min(1.0, self._elapsed / self._duration)

    @property
    def is_playing(self) -> bool:
        """Whether the transition is currently playing"""
        return self._is_playing

    @property
    def is_complete(self) -> bool:
        """Whether the transition has finished"""
        return self._is_complete

    def play(self) -> None:
        """
        Start playing the transition with the given scene.
        
        Args:
            scene: The scene to transition from or to
        """
        self._is_playing = True
        self._is_complete = False
        self._elapsed = 0.0

    def update(self, dt: float) -> None:
        """
        Update the transition (called every frame).
        
        Args:
            dt: Delta time since last frame (in seconds)
        """
        if not self._is_playing or self._is_complete:
            return

        self._elapsed += dt

        if self._elapsed >= self._duration:
            self._elapsed = self._duration
            self._is_complete = True
            self._is_playing = False

    def render(self, surface: Surface) -> None:
        """
        Render the transition effect.
        
        Args:
            surface: The pygame Surface to render to
        """
        raise NotImplementedError("render method must be implemented by subclasses")

    def reset(self) -> None:
        """Reset the transition to initial state"""
        self._elapsed = 0.0
        self._is_playing = False
        self._is_complete = False
