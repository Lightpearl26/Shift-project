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
        prev_pos = cls._last_camera_pos or Vector2(level.camera.pos)
        curr_pos = Vector2(level.camera.pos)

        # Smooth camera for entities (keeps player smooth)
        interp_pos = prev_pos.lerp(curr_pos, alpha) if cls._last_camera_pos is not None else curr_pos
        interp_camera = Camera(interp_pos, level.camera.size)

        # Render tilemap with interpolated camera (snapping happens inside renderer)
        TilemapRenderer.render(level.tilemap, surface, interp_camera)
        # Render entities with interpolated camera for smoothness
        EntityRenderer.render(level, surface, interp_camera, alpha)
