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

# import Intflags from components
from .components import EntityState, EntityProperty

# import header
from ..header import ComponentTypes as C
from ..managers.event import KeyState

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
        Controlled
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
        logic: Logic = engine.get_component(eid, C.AI).logic
        logic(eid, engine, level, dt)


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
            else:
                jump.time_left = 0.0

        if state.has_flag("JUMPING") and not keys.get("JUMP") in (KeyState.HELD, KeyState.PRESSED):
            jump.time_left = 0.0

        if state.has_flag("CAN_MOVE"):
            if keys.get("RIGHT") == KeyState.HELD:
                xdir.value = 1.0
                running = keys.get("SPRINT") == KeyState.HELD
                state.add_flag(EntityState.RUNNING if running else EntityState.WALKING)
                state.remove_flag(EntityState.WALKING if running else EntityState.RUNNING)

            elif keys.get("LEFT") == KeyState.HELD:
                xdir.value = -1.0
                running = keys.get("SPRINT") == KeyState.HELD
                state.add_flag(EntityState.RUNNING if running else EntityState.WALKING)
                state.remove_flag(EntityState.WALKING if running else EntityState.RUNNING)

            else:
                state.remove_flag(EntityState.RUNNING)
                state.remove_flag(EntityState.WALKING)


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
            state.remove_flag(EntityState.CAN_JUMP)
            state.add_flag(EntityState.JUMPING)
            jump.time_left -= dt
            t = radians(jump.direction)
            force = jump.strength * Vector2(cos(t), -sin(t))
            vel.value += force / mass.value * dt
        else:
            state.remove_flag(EntityState.JUMPING)
            if not state.has_flag("CAN_JUMP"):
                state.add_flag(EntityState.FALLING)
            else:
                state.remove_flag(EntityState.FALLING)


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
        step = d.normalize() if d.length() > 0 else Vector2(0, 0)

        while d.dot(step) > 0 and level.tilemap.colliderect(test_rect):
            d -= step # We adjust the position
            test_rect.center = Vector2(test_rect.center) - step

        if level.tilemap.colliderect(test_rect):
            # if still collisions we cancel movement
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
                    if not state.has_any_flags(EntityState.WALL_SLIDING, EntityState.WALL_STICKING):
                        state.add_flag(EntityState.WALL_STICKING)
                        wstick.time_left = wstick.duration
                        vel.y = 0
                    else:
                        if wstick.time_left > 0:
                            wstick.time_left -= dt
                        else:
                            state.remove_flag(EntityState.WALL_STICKING)
                            state.add_flag(EntityState.WALL_SLIDING)

        elif col.left:
            vel.x = 0
            if xdir.value == -1.0 and not (col.top or col.bottom) and not state.has_flag("JUMPING"):
                if engine.has_component(eid, C.WALLSTICKING):
                    wstick: WallSticking = engine.get_component(eid, C.WALLSTICKING)
                    if not state.has_any_flags(EntityState.WALL_SLIDING, EntityState.WALL_STICKING):
                        state.add_flag(EntityState.WALL_STICKING)
                        wstick.time_left = wstick.duration
                        vel.y = 0
                    else:
                        if wstick.time_left > 0:
                            wstick.time_left -= dt
                        else:
                            state.remove_flag(EntityState.WALL_STICKING)
                            state.add_flag(EntityState.WALL_SLIDING)

        else:
            state.remove_flag(EntityState.WALL_SLIDING, EntityState.WALL_STICKING)

        if col.bottom:
            vel.y = 0
            state.add_flag(EntityState.ON_GROUND)
        else:
            state.remove_flag(EntityState.ON_GROUND)

        if col.top:
            vel.y = 60.0


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
