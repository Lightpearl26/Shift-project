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
from pygame import Surface, Vector2, Color, SRCALPHA

# import game components
from ..level.entity import EntityData
from ..level.components import Camera

# import needed headers
from ..header import Level, Hitbox


# ----- EntityRenderer ----- #
class EntityRenderer:
    """
    Renderer for debugging entities
    """
    _last_entity_pos: dict[int, Vector2] = {}
    _last_camera_pos: Vector2 | None = None

    @classmethod
    def render_entity_hitbox(cls, level: Level, surface: Surface, alpha: float) -> None:
        """
        Render the hitbox of an entity
        """
        entity: EntityData
        for entity in level.entities:
            hitbox: Hitbox = level.engine.get_component(entity.eid, "Hitbox")
            if hitbox is not None:
                # interpolate position
                prev_pos = cls._last_entity_pos.get(entity.eid, Vector2(hitbox.rect.topleft))
                curr_pos = Vector2(hitbox.rect.topleft)
                interp_pos = prev_pos.lerp(curr_pos, alpha)
                cls._last_entity_pos[entity.eid] = Vector2(int(interp_pos.x), int(interp_pos.y))

                prev_pos = cls._last_camera_pos or Vector2(level.camera.pos)
                curr_pos = level.camera.pos
                interp_cam_pos = prev_pos.lerp(curr_pos, alpha)
                interp_camera = Camera(interp_cam_pos, level.camera.size)
                cls._last_camera_pos = Vector2(int(interp_cam_pos.x), int(interp_cam_pos.y))

                # create a surface for the hitbox
                hitbox_surf: Surface = Surface((hitbox.size), SRCALPHA)
                hitbox_surf.fill(Color(255, 0, 0, 100))  # semi-transparent red

                # calculate position on screen
                screen_x: int = int(interp_pos.x - interp_camera.rect.x)
                screen_y: int = int(interp_pos.y - interp_camera.rect.y)

                # blit the hitbox surface onto the main surface
                surface.blit(hitbox_surf, (screen_x, screen_y))
