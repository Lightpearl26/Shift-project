# -*- coding: utf-8 -*-

"""
SHIFT PROJECT Scenes
____________________________________________________________________________________________________
Polygon transitions (LeftHexagonTransition, RightHexagonTransition)
version : 1.0
____________________________________________________________________________________________________
Hexagon fill transitions between scenes
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import math

import pygame
from pygame import Surface, SRCALPHA

from .base import BaseTransition

if TYPE_CHECKING:
    from ..base import BaseScene


def hexagon_points_pointy(cx: float, cy: float, radius: float) -> list[tuple[float, float]]:
    """Calculate pointy-top hexagon points centered at (cx, cy)."""
    points = []
    for i in range(6):
        # Start at 30° (π/6) and go 60° increments for pointy-top orientation
        angle_rad = math.radians(30 + 60 * i)
        points.append((
            cx + radius * math.cos(angle_rad),
            cy + radius * math.sin(angle_rad)
        ))
    return points


# ----- Left Hexagon Transition ----- #
class LeftHexagonTransition(BaseTransition):
    """
    Transition with hexagons filling from left to right.
    Progressively covers the scene with hexagons in a honeycomb pattern.
    """
    def __init__(self,
                 duration: float,
                 fill_color: tuple[int, int, int] = (20, 20, 30),
                 border_color: tuple[int, int, int] = (100, 100, 120),
                 border_width: int = 2,
                 hex_size: int = 40,
                 scene: BaseScene | None = None) -> None:
        super().__init__(duration)
        self._fill_color = fill_color
        self._border_color = border_color
        self._border_width = border_width
        self._hex_size = hex_size
        self._scene = scene
        self._overlay: Surface | None = None

    def render(self, surface: Surface) -> None:
        if not self._is_playing:
            return

        # Render the scene first
        if self._scene is not None:
            self._scene.render(surface)

        # Create overlay if needed
        if self._overlay is None or self._overlay.get_size() != surface.get_size():
            self._overlay = Surface(surface.get_size(), SRCALPHA)

        self._overlay.fill((0, 0, 0, 0))  # Clear overlay

        # Calculate hexagon dimensions for perfect honeycomb tiling (pointy-top)
        # Centers positioned on equilateral triangular lattice
        width, height = surface.get_size()
        radius = self._hex_size / 2

        # For pointy-top hexagons touching in honeycomb pattern:
        # Hexagon width (flat-to-flat): sqrt(3) * radius
        # Hexagon height (point-to-point): 2 * radius
        #
        # Equilateral triangular lattice parameters:
        # - Distance between adjacent centers: sqrt(3) * radius
        # - Horizontal spacing (between rows): sqrt(3) * radius
        # - Vertical spacing (between rows): 1.5 * radius
        # - Every other row offset horizontally by: sqrt(3)/2 * radius
        center_dist = radius * (3 ** 0.5)  # sqrt(3) * radius
        horiz_spacing = center_dist
        vert_spacing = radius * 1.5
        row_offset = center_dist / 2  # sqrt(3)/2 * radius

        # Progress determines how far across the screen to fill
        fill_x = width * self.progress

        # Draw hexagons with centers on triangular lattice (row by row)
        row = 0
        y = -radius * 2
        while y < height + radius * 2:
            # Offset every other row horizontally for triangular lattice
            x_offset = row_offset if row % 2 else 0
            x = -radius * 2 + x_offset
            
            while x < fill_x + radius * 2:
                center_x = x
                center_y = y
                
                # Only draw if hexagon center is within the fill zone
                if center_x <= fill_x:
                    points = hexagon_points_pointy(center_x, center_y, radius)
                    # Draw filled hexagon
                    pygame.draw.polygon(self._overlay, self._fill_color, points)
                    # Draw border
                    if self._border_width > 0:
                        pygame.draw.polygon(self._overlay, self._border_color, points, self._border_width)
                
                x += horiz_spacing
            
            y += vert_spacing
            row += 1

        surface.blit(self._overlay, (0, 0))


# ----- Right Hexagon Transition ----- #
class RightHexagonTransition(BaseTransition):
    """
    Transition with hexagons filling from right to left.
    Progressively covers the scene with hexagons in a honeycomb pattern.
    """
    def __init__(self,
                 duration: float,
                 fill_color: tuple[int, int, int] = (20, 20, 30),
                 border_color: tuple[int, int, int] = (100, 100, 120),
                 border_width: int = 2,
                 hex_size: int = 40,
                 scene: BaseScene | None = None) -> None:
        super().__init__(duration)
        self._fill_color = fill_color
        self._border_color = border_color
        self._border_width = border_width
        self._hex_size = hex_size
        self._scene = scene
        self._overlay: Surface | None = None

    def render(self, surface: Surface) -> None:
        if not self._is_playing:
            return

        # Render the scene first
        if self._scene is not None:
            self._scene.render(surface)

        # Create overlay if needed
        if self._overlay is None or self._overlay.get_size() != surface.get_size():
            self._overlay = Surface(surface.get_size(), SRCALPHA)

        self._overlay.fill((0, 0, 0, 0))  # Clear overlay

        # Calculate hexagon dimensions for perfect honeycomb tiling (pointy-top)
        # Centers positioned on equilateral triangular lattice
        width, height = surface.get_size()
        radius = self._hex_size / 2
        
        # For pointy-top hexagons touching in honeycomb pattern:
        # Hexagon width (flat-to-flat): sqrt(3) * radius
        # Hexagon height (point-to-point): 2 * radius
        # 
        # Equilateral triangular lattice parameters:
        # - Distance between adjacent centers: sqrt(3) * radius
        # - Horizontal spacing (between rows): sqrt(3) * radius
        # - Vertical spacing (between rows): 1.5 * radius
        # - Every other row offset horizontally by: sqrt(3)/2 * radius
        center_dist = radius * (3 ** 0.5)  # sqrt(3) * radius
        horiz_spacing = center_dist
        vert_spacing = radius * 1.5
        row_offset = center_dist / 2  # sqrt(3)/2 * radius
        
        # Progress determines how far from the right to fill
        fill_x = width * (1.0 - self.progress)

        # Draw hexagons with centers on triangular lattice (row by row)
        row = 0
        y = -radius * 2
        while y < height + radius * 2:
            # Offset every other row horizontally for triangular lattice
            x_offset = row_offset if row % 2 else 0
            x = width + radius * 2 + x_offset
            
            while x > fill_x - radius * 2:
                center_x = x
                center_y = y
                
                # Only draw if hexagon center is within the fill zone (from right)
                if center_x >= fill_x:
                    points = hexagon_points_pointy(center_x, center_y, radius)
                    # Draw filled hexagon
                    pygame.draw.polygon(self._overlay, self._fill_color, points)
                    # Draw border
                    if self._border_width > 0:
                        pygame.draw.polygon(self._overlay, self._border_color, points, self._border_width)
                
                x -= horiz_spacing
            
            y += vert_spacing
            row += 1

        surface.blit(self._overlay, (0, 0))


# ----- Left Hexagon Reverse Transition ----- #
class LeftHexagonReverseTransition(LeftHexagonTransition):
    """
    Reverse of LeftHexagonTransition: hexagons disappear from left to right.
    """
    def render(self, surface: Surface) -> None:
        if not self._is_playing:
            return

        if self._scene is not None:
            self._scene.render(surface)

        if self._overlay is None or self._overlay.get_size() != surface.get_size():
            self._overlay = Surface(surface.get_size(), SRCALPHA)

        self._overlay.fill((0, 0, 0, 0))

        width, height = surface.get_size()
        radius = self._hex_size / 2

        center_dist = radius * (3 ** 0.5)
        horiz_spacing = center_dist
        vert_spacing = radius * 1.5
        row_offset = center_dist / 2

        # Reverse fill: decreases with progress
        fill_x = width * (1.0 - self.progress)

        row = 0
        y = -radius * 2
        while y < height + radius * 2:
            x_offset = row_offset if row % 2 else 0
            x = -radius * 2 + x_offset

            while x < width + radius * 2:
                center_x = x
                center_y = y

                if center_x <= fill_x:
                    points = hexagon_points_pointy(center_x, center_y, radius)
                    pygame.draw.polygon(self._overlay, self._fill_color, points)
                    if self._border_width > 0:
                        pygame.draw.polygon(self._overlay, self._border_color, points, self._border_width)

                x += horiz_spacing

            y += vert_spacing
            row += 1

        surface.blit(self._overlay, (0, 0))


# ----- Right Hexagon Reverse Transition ----- #
class RightHexagonReverseTransition(RightHexagonTransition):
    """
    Reverse of RightHexagonTransition: hexagons disappear from right to left.
    """
    def render(self, surface: Surface) -> None:
        if not self._is_playing:
            return

        if self._scene is not None:
            self._scene.render(surface)

        if self._overlay is None or self._overlay.get_size() != surface.get_size():
            self._overlay = Surface(surface.get_size(), SRCALPHA)

        self._overlay.fill((0, 0, 0, 0))

        width, height = surface.get_size()
        radius = self._hex_size / 2

        center_dist = radius * (3 ** 0.5)
        horiz_spacing = center_dist
        vert_spacing = radius * 1.5
        row_offset = center_dist / 2

        # Reverse fill: decreases with progress
        fill_x = width * self.progress

        row = 0
        y = -radius * 2
        while y < height + radius * 2:
            x_offset = row_offset if row % 2 else 0
            x = width + radius * 2 + x_offset

            while x > -radius * 2:
                center_x = x
                center_y = y

                if center_x >= fill_x:
                    points = hexagon_points_pointy(center_x, center_y, radius)
                    pygame.draw.polygon(self._overlay, self._fill_color, points)
                    if self._border_width > 0:
                        pygame.draw.polygon(self._overlay, self._border_color, points, self._border_width)

                x -= horiz_spacing

            y += vert_spacing
            row += 1

        surface.blit(self._overlay, (0, 0))
