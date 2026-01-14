# -*- coding: utf-8 -*-

"""
game_libs.transition.fade
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

# import pygame modules
from pygame import Surface, SRCALPHA

# import base transition
from .base import BaseTransition

# import logger
from .. import logger

if TYPE_CHECKING:
    pass


# ----- FadeIn transition class ----- #
class FadeIn(BaseTransition):
    """
    Fade In Transition
    """
    def __init__(self, duration: float = 1000.0, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        """
        Initialize the Fade In transition.

        args:
            duration (float): Duration of the transition in milliseconds.
            color (tuple[int, int, int]): RGB color of the fade effect.
        """
        super().__init__(duration)
        self._color = color
        logger.info(f"[FadeIn] Initialized with duration: {duration}ms and color: {color}")

    def render(self, surface: Surface) -> None:
        """
        Render the Fade In transition on the given surface.

        args:
            surface (Surface): The surface to render the transition on.
        """
        alpha = int((1.0 - self.progress) * 255)
        fade_surface = Surface(surface.get_size(), SRCALPHA)
        fade_surface.fill((*self._color, alpha))
        surface.blit(fade_surface, (0, 0))


# ----- FadeOut transition class ----- #
class FadeOut(BaseTransition):
    """
    Fade Out Transition
    """
    def __init__(self, duration: float = 1000.0, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        """
        Initialize the Fade Out transition.

        args:
            duration (float): Duration of the transition in milliseconds.
            color (tuple[int, int, int]): RGB color of the fade effect.
        """
        super().__init__(duration)
        self._color = color
        logger.info(f"[FadeOut] Initialized with duration: {duration}ms and color: {color}")

    def render(self, surface: Surface) -> None:
        """
        Render the Fade Out transition on the given surface.

        args:
            surface (Surface): The surface to render the transition on.
        """
        alpha = int(self.progress * 255)
        fade_surface = Surface(surface.get_size(), SRCALPHA)
        fade_surface.fill((*self._color, alpha))
        surface.blit(fade_surface, (0, 0))
