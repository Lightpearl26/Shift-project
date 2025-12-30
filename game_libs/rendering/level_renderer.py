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
from pygame import Surface

# import game components
from ..level.level import Level
from .tilemap_renderer import TilemapRenderer
from .entity_renderer import EntityRenderer

# ----- LevelRenderer ----- #
class LevelRenderer:
    """
    Renderer for levels
    """

    @classmethod
    def render(cls, surface: Surface, level: Level, alpha: float) -> None:
        """
        Render the level on the given surface according to the camera rect
        """
        # Render tilemap
        TilemapRenderer.render(level.tilemap, surface, level.camera, alpha)
        EntityRenderer.render_entity_hitbox(level, surface, alpha)
