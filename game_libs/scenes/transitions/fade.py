# -*- coding: utf-8 -*-

"""
SHIFT PROJECT Scenes
____________________________________________________________________________________________________
Fade transitions (FadeIn, FadeOut, CrossFade)
version : 1.0
____________________________________________________________________________________________________
Fade transitions between scenes
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Surface, SRCALPHA

from .base import BaseTransition

if TYPE_CHECKING:
    from ..base import BaseScene


class FadeOut(BaseTransition):
    """Fade to black (or other color) transition."""

    def __init__(self,
                 duration: float,
                 color: tuple[int, int, int] = (0, 0, 0),
                 scene: BaseScene | None = None) -> None:
        super().__init__(duration)
        self._color = color
        self._overlay: Surface | None = None
        self._scene = scene

    def render(self, surface: Surface) -> None:
        if not self._is_playing:
            return

        # Render the scene first
        if self._scene is not None:
            self._scene.render(surface)

        # Create overlay if needed
        if self._overlay is None or self._overlay.get_size() != surface.get_size():
            self._overlay = Surface(surface.get_size(), SRCALPHA)

        # Calculate alpha (0 = transparent, 255 = opaque)
        alpha = int(255 * self.progress)
        self._overlay.fill((*self._color, alpha))
        surface.blit(self._overlay, (0, 0))


class FadeIn(BaseTransition):
    """Fade from black (or other color) transition."""

    def __init__(self,
                 duration: float,
                 color: tuple[int, int, int] = (0, 0, 0),
                 scene: BaseScene | None = None) -> None:
        super().__init__(duration)
        self._color = color
        self._overlay: Surface | None = None
        self._scene = scene

    def render(self, surface: Surface) -> None:
        if not self._is_playing:
            return

        # Render the scene first
        if self._scene is not None:
            self._scene.render(surface)

        # Create overlay if needed
        if self._overlay is None or self._overlay.get_size() != surface.get_size():
            self._overlay = Surface(surface.get_size(), SRCALPHA)

        # Calculate alpha (255 = opaque, 0 = transparent)
        alpha = int(255 * (1.0 - self.progress))
        self._overlay.fill((*self._color, alpha))
        surface.blit(self._overlay, (0, 0))


class CrossFade(BaseTransition):
    """Cross-fade between two scenes."""

    def __init__(self, duration: float, old_scene: BaseScene, new_scene: BaseScene) -> None:
        super().__init__(duration)
        self._old_scene = old_scene
        self._new_scene = new_scene
        self._old_surface: Surface | None = None
        self._new_surface: Surface | None = None

    def render(self, surface: Surface) -> None:
        if not self._is_playing:
            return

        size = surface.get_size()

        # Create temp surfaces if needed
        if self._old_surface is None or self._old_surface.get_size() != size:
            self._old_surface = Surface(size, SRCALPHA)
        if self._new_surface is None or self._new_surface.get_size() != size:
            self._new_surface = Surface(size, SRCALPHA)

        # Render both scenes
        self._old_surface.fill((0, 0, 0, 0))
        self._old_scene.render(self._old_surface)

        self._new_surface.fill((0, 0, 0, 0))
        self._new_scene.render(self._new_surface)

        # Blend with alpha
        old_alpha = int(255 * (1.0 - self.progress))
        new_alpha = int(255 * self.progress)

        self._old_surface.set_alpha(old_alpha)
        self._new_surface.set_alpha(new_alpha)

        surface.blit(self._old_surface, (0, 0))
        surface.blit(self._new_surface, (0, 0))
