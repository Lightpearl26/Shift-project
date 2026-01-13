#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
tileMap renderer lib
version : 1.0
____________________________________________________________________________________________________
Contains all objects for tilmap rendering
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import components
from __future__ import annotations
from pygame import Surface, Vector2

# import game components
from ..level.level import Level
from ..level.components import Camera
from .tilemap_renderer import TilemapRenderer
from .entity_renderer import EntityRenderer

# ----- LevelRenderer ----- #
class LevelRenderer:
    """
    Renderer for levels
    """
    _last_camera_pos: Vector2 | None = None

    @classmethod
    def update(cls, level: Level) -> None:
        """
        Update renderer state after a logic tick
        """
        cls._last_camera_pos = Vector2(level.camera.pos)
        EntityRenderer.update(level)

    @classmethod
    def render(cls, surface: Surface, level: Level, alpha: float) -> None:
        """
        Render the level on the given surface according to the camera rect
        """
        # Calculate interpolated camera position for consistent rendering
        prev_pos = cls._last_camera_pos or Vector2(level.camera.pos)
        curr_pos = Vector2(level.camera.pos)
        interp_camera_pos = prev_pos.lerp(curr_pos, alpha) + Vector2(0.5, 0.5)
        interp_camera = Camera(interp_camera_pos, level.camera.size)

        # Render tilemap with real and interpolated camera
        TilemapRenderer.render(level.tilemap, surface, level.camera, interp_camera)
        # Render all entities and player with interpolated camera and alpha
        EntityRenderer.render(level, surface, interp_camera, alpha)
