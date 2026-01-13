#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
Entity renderer lib (temporaire)
version : 1.0
____________________________________________________________________________________________________
Affiche les hitbox des entités en couleur
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from __future__ import annotations
from typing import TYPE_CHECKING
from pygame import Surface, Color, Vector2, SRCALPHA

# import game components
from ..level.entity import EntityData
from ..level.components import Camera

if TYPE_CHECKING:
    from ..level.level import Level
    from ..ecs_core.components import Hitbox


# ----- EntityRenderer ----- #
class EntityRenderer:
    """
    Renderer for debugging entities
    """
    _last_entity_pos: dict[int, Vector2] = {}

    @classmethod
    def update(cls, level: Level) -> None:
        """
        Update entity positions after a logic tick
        """
        # Store player position
        if level.player is not None:
            hitbox: Hitbox = level.engine.get_component(level.player.eid, "Hitbox")
            if hitbox is not None:
                cls._last_entity_pos[level.player.eid] = Vector2(hitbox.rect.topleft)
        
        # Store other entities positions
        entity: EntityData
        for entity in level.entities:
            hitbox: Hitbox = level.engine.get_component(entity.eid, "Hitbox")
            if hitbox is not None:
                cls._last_entity_pos[entity.eid] = Vector2(hitbox.rect.topleft)

    @classmethod
    def _render_entity(cls,
                       hitbox: Hitbox,
                       eid: int,
                       surface: Surface,
                       camera_interp: Camera,
                       alpha: float,
                       color: tuple[int, int, int, int]) -> None:
        """
        Internal method to render an entity hitbox
        """
        # Interpolate position
        prev_pos = cls._last_entity_pos.get(eid, Vector2(hitbox.rect.topleft))
        curr_pos = Vector2(hitbox.rect.topleft)
        interp_pos = prev_pos.lerp(curr_pos, alpha)

        # create a surface for the hitbox
        hitbox_surf: Surface = Surface((hitbox.size), SRCALPHA)
        hitbox_surf.fill(Color(*color))

        # calculate position on screen with interpolated position and camera (rounded to integer pixels)
        screen_x: int = int(interp_pos.x) - int(camera_interp.rect.x)
        screen_y: int = int(interp_pos.y) - int(camera_interp.rect.y)

        # blit the hitbox surface onto the main surface
        surface.blit(hitbox_surf, (screen_x, screen_y))

    @classmethod
    def render(cls, level: Level, surface: Surface, camera_interp: Camera, alpha: float) -> None:
        """
        Render all entities and player with interpolated camera and positions
        """
        # Render other entities
        entity: EntityData
        for entity in level.entities:
            hitbox: Hitbox = level.engine.get_component(entity.eid, "Hitbox")
            if hitbox is not None:
                cls._render_entity(hitbox, entity.eid, surface, camera_interp, alpha, (255, 0, 0, 100))

        # Render player
        if level.player is not None:
            hitbox: Hitbox = level.engine.get_component(level.player.eid, "Hitbox")
            if hitbox is not None:
                cls._render_entity(hitbox, level.player.eid, surface, camera_interp, alpha, (0, 255, 0, 100))
