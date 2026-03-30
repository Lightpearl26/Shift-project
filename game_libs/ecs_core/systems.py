#-*- coding: utf-8 -*-
# pylint: disable=unused-argument

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
ECS libs Systems
version : 1.0
____________________________________________________________________________________________________
Contains systems of our game ecs
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from __future__ import annotations
from typing import TYPE_CHECKING
from math import cos, sin, radians
from pygame import Vector2, Rect

# import config
from .. import config
from .. import logger

# import Intflags from components
from .components import EntityProperty

# import header
from ..header import ComponentTypes as C
from ..managers.event import KeyState
from ..managers.audio import AudioManager

if TYPE_CHECKING:
    from ..level.level import Level
    from ..ecs_core.engine import Engine
    from ..ecs_core.components import (
        XDirection,
        Velocity,
        State,
        Jump,
        Walk,
        Logic,
        Mass,
        Properties,
        NextPosition,
        Hitbox,
        MapCollision,
        WallSticking,
        CameraFollow,
        Controlled,
        EntityCollision,
        EntityAction
    )


# ----- TileAnimationSystem ----- #
def tile_animation_system(engine: Engine, level: Level, dt: float) -> None:
    """
    System updating animation of the tiles of the level
    """
    level.tilemap.tileset.update_animation(dt)
    for parallax in level.tilemap.parallax:
        if hasattr(parallax, "tm"):
            parallax.tm.tileset.update_animation(dt)


# ----- AiSystem ----- #
def ai_system(engine: Engine, level: Level, dt: float) -> None:
    """
    System calling AI logics for entities
    """
    for eid in engine.get_entities_with(C.AI):
        ai_comp = engine.get_component(eid, C.AI)
        logic: Logic = ai_comp.logic
        logic(eid, engine, level, dt, ai_comp.runtime)


# ----- PlayerControlSystem ----- #
def player_control_system(engine: Engine, level: Level, dt: float) -> None:
    """
    System handling user input to player
    """
    for eid in engine.get_entities_with(C.CONTROLLED):
        xdir: XDirection = engine.get_component(eid, C.XDIRECTION)
        state: State = engine.get_component(eid, C.STATE)
        jump: Jump = engine.get_component(eid, C.JUMP)
        controlled: Controlled = engine.get_component(eid, C.CONTROLLED)
        keys = controlled.key_state
        if state.has_flag("CAN_JUMP"):
            if keys.get("JUMP") == KeyState.PRESSED:
                if state.has_flag("ON_GROUND"):
                    jump.time_left = jump.duration
                    jump.direction = 90.0
                if state.has_flag("WALL_STICKING") or state.has_flag("WALL_SLIDING"):
                    jump.time_left = jump.duration
                    if xdir.value == 1.0:
                        jump.direction = 120.0
                        xdir.value = -1.0
                    else:
                        jump.direction = 60.0
                        xdir.value = 1.0
                AudioManager.play_se("JUMP")
            else:
                jump.time_left = 0.0

        if state.has_flag("JUMPING") and not keys.get("JUMP") in (KeyState.HELD, KeyState.PRESSED):
            jump.time_left = 0.0

        if state.has_flag("CAN_MOVE"):
            if keys.get("RIGHT") == KeyState.HELD:
                xdir.value = 1.0
                state.add_flag("RUNNING")

            elif keys.get("LEFT") == KeyState.HELD:
                xdir.value = -1.0
                state.add_flag("RUNNING")

            else:
                state.remove_flag("RUNNING")


# ----- DragSystem ----- #
def drag_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Apply drag to the velocity
    """
    for eid in engine.get_entities_with(C.MASS):
        state: State = engine.get_component(eid, C.STATE)
        props: Properties = engine.get_component(eid, C.PROPERTIES)
        mass: Mass = engine.get_component(eid, C.MASS)
        vel: Velocity = engine.get_component(eid, C.VELOCITY)

        if state.has_flag("NO_DRAG") or props.has_all_flags(EntityProperty.FLOATING):
            continue

        if state.has_flag("ON_GROUND"):
            coef = 10.0
        elif state.has_flag("WALL_SLIDING"):
            coef = 20.0
        else:
            coef = 5.0

        drag_factor = 1.0 - coef * config.DRAG_BASE * dt * mass.value
        drag_factor = max(0.0, min(1.0, drag_factor))  # Clamp pour éviter l'inversion

        vel.value *= drag_factor

        if vel.value.length() < 0.01:
            vel.value = Vector2(0, 0)


# ----- GravitySystem ----- #
def gravity_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Apply gravity to entity velocity
    """
    for eid in engine.get_entities_with(C.STATE): # get all entities
        props: Properties = engine.get_component(eid, C.PROPERTIES)
        state: State = engine.get_component(eid, C.STATE)

        if props.has_all_flags(EntityProperty.FLOATING) or state.has_flag("IGNORE_GRAVITY"):
            continue

        vel: Velocity = engine.get_component(eid, C.VELOCITY)
        vel.y += config.GRAVITY * dt


# ----- JumpSystem ----- #
def jump_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Apply jump if initiated to entity velocity
    """
    for eid in engine.get_entities_with(C.JUMP, C.MASS):
        jump: Jump = engine.get_component(eid, C.JUMP)
        vel: Velocity = engine.get_component(eid, C.VELOCITY)
        state: State = engine.get_component(eid, C.STATE)
        mass: Mass = engine.get_component(eid, C.MASS)

        if jump.time_left > 0:
            state.remove_flag("CAN_JUMP")
            state.add_flag("JUMPING")
            jump.time_left -= dt
            t = radians(jump.direction)
            force = jump.strength * Vector2(cos(t), -sin(t))
            vel.value += force / mass.value * dt
        else:
            state.remove_flag("JUMPING")
            if not state.has_flag("CAN_JUMP"):
                state.add_flag("FALLING")
            else:
                state.remove_flag("FALLING")


# ----- MovementSystem ----- #
def movement_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Apply correctly walking or running initiated before
    """
    for eid in engine.get_entities_with(C.WALK, C.XDIRECTION):
        vel: Velocity = engine.get_component(eid, C.VELOCITY)
        state: State = engine.get_component(eid, C.STATE)
        xdir: XDirection = engine.get_component(eid, C.XDIRECTION)
        walk: Walk = engine.get_component(eid, C.WALK)

        if state.has_flag("ON_GROUND"):
            coef = 1.0
        else:
            coef = 0.3

        if state.has_flag("CAN_MOVE"):
            speed = 0.0
            if state.has_flag("WALKING"):
                speed = walk.walk_speed
            elif state.has_flag("RUNNING"):
                speed = walk.run_speed

            vel.x += xdir.value*coef*speed*dt


# ----- MovePredictionSystem ----- #
def move_prediction_system(engine: Engine, level: Level, dt: float) -> None:
    """
    update NextPosition component of entity
    """
    for eid in engine.get_entities_with(C.NEXTPOSITION):
        vel: Velocity = engine.get_component(eid, C.VELOCITY)
        hit: Hitbox = engine.get_component(eid, C.HITBOX)
        next_pos: NextPosition = engine.get_component(eid, C.NEXTPOSITION)

        next_pos.value = hit.pos + vel.value * dt


# ----- MapCollisionSystem ----- #
def map_collision_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Resolve map collisions of the entity
    """
    for eid in engine.get_entities_with(C.MAPCOLLISION, C.XDIRECTION):
        hitbox: Hitbox = engine.get_component(eid, C.HITBOX)
        next_pos: NextPosition = engine.get_component(eid, C.NEXTPOSITION)
        vel: Velocity = engine.get_component(eid, C.VELOCITY)
        col: MapCollision = engine.get_component(eid, C.MAPCOLLISION)
        state: State = engine.get_component(eid, C.STATE)
        xdir: XDirection = engine.get_component(eid, C.XDIRECTION)

        # First we reset previous collisions
        col.reset()

        # Then we apply AABB collisions system
        d = next_pos.value - hitbox.pos
        test_rect = hitbox.rect.copy()
        test_rect.center = hitbox.pos + d

        if level.tilemap.colliderect(test_rect):
            # On cherche la distance maximale sans collision sur chaque axe séparément
            # Mouvement horizontal
            temp_rect = hitbox.rect.copy()
            temp_rect.center = hitbox.pos
            dx = d.x
            if dx != 0:
                step_x = 1 if dx > 0 else -1
                for _ in range(int(abs(dx))):
                    temp_rect.centerx += step_x
                    if level.tilemap.colliderect(temp_rect):
                        temp_rect.centerx -= step_x
                        break
            # Mouvement vertical
            dy = d.y
            if dy != 0:
                step_y = 1 if dy > 0 else -1
                for _ in range(int(abs(dy))):
                    temp_rect.centery += step_y
                    if level.tilemap.colliderect(temp_rect):
                        temp_rect.centery -= step_y
                        break
            test_rect = temp_rect

        # Si toujours collision (cas extrême), on annule le mouvement
        if level.tilemap.colliderect(test_rect):
            test_rect = hitbox.rect.copy()

        # Now that collisions are resolved we check for boundary collisions
        for direction in ["left", "right", "top", "bottom"]:
            setattr(col, direction, level.tilemap.touch(test_rect)[direction])

        # We update next_pos with adjusted value
        next_pos.value = Vector2(test_rect.center)

        # We update entity state according to collisions
        if col.right:
            vel.x = 0
            if xdir.value == 1.0 and not (col.top or col.bottom) and not state.has_flag("JUMPING"):
                if engine.has_component(eid, C.WALLSTICKING):
                    wstick: WallSticking = engine.get_component(eid, C.WALLSTICKING)
                    if not state.has_any_flags("WALL_SLIDING", "WALL_STICKING"):
                        state.add_flag("WALL_STICKING")
                        wstick.time_left = wstick.duration
                        vel.y = 0
                    else:
                        if wstick.time_left > 0:
                            wstick.time_left -= dt
                        else:
                            state.remove_flag("WALL_STICKING")
                            state.add_flag("WALL_SLIDING")

        elif col.left:
            vel.x = 0
            if xdir.value == -1.0 and not (col.top or col.bottom) and not state.has_flag("JUMPING"):
                if engine.has_component(eid, C.WALLSTICKING):
                    wstick: WallSticking = engine.get_component(eid, C.WALLSTICKING)
                    if not state.has_any_flags("WALL_SLIDING", "WALL_STICKING"):
                        state.add_flag("WALL_STICKING")
                        wstick.time_left = wstick.duration
                        vel.y = 0
                    else:
                        if wstick.time_left > 0:
                            wstick.time_left -= dt
                        else:
                            state.remove_flag("WALL_STICKING")
                            state.add_flag("WALL_SLIDING")

        else:
            state.remove_flag("WALL_SLIDING", "WALL_STICKING")

        if col.bottom:
            vel.y = 0
            state.add_flag("ON_GROUND")
        else:
            state.remove_flag("ON_GROUND")

        if col.top:
            vel.y = 60.0


# ---- EntityCollisionSystem ----- #
def entity_collision_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Resolve entity collisions of the entity
    """
    entity_ids = list(engine.get_entities_with(C.ENTITYCOLLISION))
    logger.info(f"[entity_collision_system] Début, entités à tester: {entity_ids}")
    for eid in entity_ids:
        props: Properties = engine.get_component(eid, C.PROPERTIES)
        if props.has_all_flags(EntityProperty.PHASABLE):
            continue
        hitbox: Hitbox = engine.get_component(eid, C.HITBOX)
        next_pos: NextPosition = engine.get_component(eid, C.NEXTPOSITION)
        vel: Velocity = engine.get_component(eid, C.VELOCITY)
        col: EntityCollision = engine.get_component(eid, C.ENTITYCOLLISION)

        # We reset previous collisions
        col.collided_entities.clear()
        col.bottom = False
        col.top = False
        col.left = False
        col.right = False

        test_rect = hitbox.rect.copy()
        test_rect.center = next_pos.value

        for other_eid in engine.get_entities_with(C.HITBOX):
            if other_eid == eid:
                continue
            other_props: Properties = engine.get_component(other_eid, C.PROPERTIES)
            if other_props.has_all_flags(EntityProperty.PHASABLE):
                continue
            other_hitbox: Hitbox = engine.get_component(other_eid, C.HITBOX)
            if test_rect.colliderect(other_hitbox.rect.inflate(2, 2)):
                logger.debug(f"[entity_collision_system] Collision détectée entre entité {eid} et entité {other_eid}")
                # Correction stricte AABB pour chaque collision
                dx = (other_hitbox.rect.centerx - test_rect.centerx)
                dy = (other_hitbox.rect.centery - test_rect.centery)
                overlap_x = (other_hitbox.rect.width + test_rect.width) // 2 - abs(dx)
                overlap_y = (other_hitbox.rect.height + test_rect.height) // 2 - abs(dy)
                if overlap_x > 0 and overlap_y > 0:
                    if overlap_x < overlap_y:
                        # Correction horizontale
                        if dx > 0:
                            test_rect.centerx -= overlap_x
                        else:
                            test_rect.centerx += overlap_x
                        vel.x = 0
                    else:
                        # Correction verticale
                        if dy > 0:
                            test_rect.centery -= overlap_y
                        else:
                            test_rect.centery += overlap_y
                        vel.y = 0
                    # Met à jour la position corrigée
                    next_pos.value = Vector2(test_rect.center)
                # Enregistre la collision à partir de la position corrigée (next_pos)
                entity_rect = hitbox.rect.copy()
                entity_rect.center = next_pos.value
                bottom = entity_rect.bottom <= other_hitbox.rect.top
                top = entity_rect.top >= other_hitbox.rect.bottom
                left = entity_rect.left >= other_hitbox.rect.right
                right = entity_rect.right <= other_hitbox.rect.left
                col.collided_entities.append(
                    (
                        other_eid,
                        (left, right, top, bottom)
                    )
                )
                col.bottom = col.bottom or bottom
                col.top = col.top or top
                col.left = col.left or left
                col.right = col.right or right

        # Mise à jour des états après toutes les collisions
        state: State = engine.get_component(eid, C.STATE)
        if col.bottom:
            state.add_flag("ON_GROUND")


# ----- EntityActionSystem ----- #
def entity_action_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Handle entities actions on collision with other entities
    """
    entity_ids = list(engine.get_entities_with(C.ENTITYCOLLISION, C.ENTITYACTION))
    logger.info(f"[entity_action_system] Entités à tester: {entity_ids}")
    for eid in entity_ids:
        col: EntityCollision = engine.get_component(eid, C.ENTITYCOLLISION)
        action: EntityAction = engine.get_component(eid, C.ENTITYACTION)
        logger.info(f"[entity_action_system] eid={eid} collided_entities={col.collided_entities}")
        action(eid, engine, level, dt)



# ----- UpdateHitboxSystem ----- #
def sync_hitbox_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Update hitbox if movement made
    """
    for eid in engine.get_entities_with(C.NEXTPOSITION):
        hitbox: Hitbox = engine.get_component(eid, C.HITBOX)
        next_pos: NextPosition = engine.get_component(eid, C.NEXTPOSITION)

        hitbox.pos = next_pos.value


# ----- CameraSystem ----- #
def camera_system(engine: Engine, level: Level, dt: float) -> None:
    """
    Making camera following the marked entity
    """
    eid = next(engine.get_entities_with(C.CAMERAFOLLOW), None)

    if eid is None:
        return

    rect: Rect = engine.get_component(eid, C.HITBOX).rect
    follow: CameraFollow = engine.get_component(eid, C.CAMERAFOLLOW)

    cam = level.camera
    follow.deadzone.center = cam.pos
    cam_w, cam_h = cam.size
    map_w = level.tilemap.width * level.tilemap.tileset.tile_size
    map_h = level.tilemap.height * level.tilemap.tileset.tile_size

    new_cam = cam.pos

    if rect.left < follow.deadzone.left:
        new_cam.x -= follow.deadzone.left - rect.left
    elif rect.right > follow.deadzone.right:
        new_cam.x += rect.right - follow.deadzone.right

    if rect.top < follow.deadzone.top:
        new_cam.y -= follow.deadzone.top - rect.top
    elif rect.bottom > follow.deadzone.bottom:
        new_cam.y += rect.bottom - follow.deadzone.bottom

    # Smooth follow
    t = min(dt * follow.damping, 1.0)
    cam_pos = cam.pos.lerp(new_cam, t)

    if map_w > cam_w:
        cam_pos.x = max(cam_w / 2, min(cam_pos.x, map_w - cam_w / 2))
    else:
        cam_pos.x = map_w / 2

    if map_h > cam_h:
        cam_pos.y = max(cam_h / 2, min(cam_pos.y, map_h - cam_h / 2))
    else:
        cam_pos.y = map_h / 2

    cam.pos = cam_pos
