# -*- coding: utf-8 -*-

"""
game_libs.transition.base
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines polygons related transitions.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

# import needed built-in modules
from __future__ import annotations
from typing import TYPE_CHECKING
import math

# import pygame modules
from pygame.draw import polygon

# import logger
from .. import logger

# import config
from .. import config

# import transition base class
from .base import BaseTransition

if TYPE_CHECKING:
    from pygame import Surface
    

# ----- LeftHexagonTransition ----- #
class LeftHexagonTransition(BaseTransition):
    """
    Transition effect using hexagon shapes to fill screen starting by left.
    """
    def __init__(self, duration: float = 1000.0, color: tuple[int, ...] = (175, 175, 175)) -> None:
        """
        Initialize the LeftHexagonTransition.

        args:
            duration (float): Duration of the transition in milliseconds.
            color (tuple[int, ...]): Color of the hexagons.
        """
        super().__init__(duration)
        self.color = color
        self._hexagon_radius = 50
        logger.info(f"[{self.__class__.__name__}] Initialized with duration: {self._duration}s")
        
    def _blit_hexagon(self, surface: Surface, center: tuple[int, int]) -> None:
        """
        Blit a hexagon on the surface at the given center.
        """
        points = [
            (center[0] + self._hexagon_radius * math.cos(math.radians(angle)), 
             center[1] + self._hexagon_radius * math.sin(math.radians(angle)))
            for angle in [30, 90, 150, 210, 270, 330]
        ]
        polygon(surface, self.color, points)
        polygon(surface, (0, 0, 0), points, 2)  # draw border
        
    def render(self, surface: Surface) -> None:
        """
        Render transition on surface.
        """
        width, height = surface.get_size()
        nb_hex_x = math.ceil(width / (self._hexagon_radius * math.sqrt(3))*self.progress) + 1
        nb_hex_y = math.ceil(height / (self._hexagon_radius * 1.5)) + 1
        
        for x in range(nb_hex_x):
            for y in range(nb_hex_y):
                if y % 2 == 0:
                    center_x = x * self._hexagon_radius * math.sqrt(3)
                else:
                    center_x = x * self._hexagon_radius * math.sqrt(3) + (self._hexagon_radius * math.sqrt(3)) / 2
                center_y = y * self._hexagon_radius * 1.5
                self._blit_hexagon(surface, (int(center_x), int(center_y)))