#-*- coding: utf-8 -*-

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
from math import cos, sin, radians
from pygame import Vector2
from pygame.key import get_pressed
import pygame

# import modules from package
from . import logger
from . import ecs_components as C

# --------------------------
# | Constants              |
# --------------------------
GRAVITY: Vector2 = Vector2(0, 960)
DRAG_BASE: float = 25.0


# --------------------------
# | Systems                |
# --------------------------
def TileAnimationSystem(engine, dt: float) -> None:
    for tile in engine.tilemap.tileset.tiles:
        tile.animation_time_left -= dt
        if tile.animation_time_left <= 0:
            tile.animation_frame = (tile.animation_frame + 1) % len(tile.graphics)
            tile.animation_time_left += tile.animation_delay


def AISystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.AI):
        logic = engine.get_component(eid, C.AI).logic
        logic(eid, engine, dt)


def PlayerControlSystem(engine, dt: float) -> None:
    events = pygame.event.get()
    keys = get_pressed()

    for eid in engine.get_entities_with(C.PlayerControlled):
        direction = engine.get_component(eid, C.XDirection)
        vel = engine.get_component(eid, C.Velocity)
        state = engine.get_component(eid, C.State)
        jump = engine.get_component(eid, C.Jump)

        # Horizontal movement
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and (state.flags & C.EntityState.CAN_JUMP):
                    jump.time_left = jump.duration
                    if state.flags & C.EntityState.ON_GROUND:
                        jump.direction = 90.0
                    elif state.flags & (C.EntityState.WALL_SLIDING | C.EntityState.WALL_STICKING):
                        if direction.value == 1.0:
                            jump.direction = 120.0
                            direction.value = -1.0
                        else:
                            jump.direction = 60.0
                            direction.value = 1.0
                else:
                    pygame.event.post(event)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    jump.time_left = 0
                else:
                    pygame.event.post(event)
            else:
                pygame.event.post(event)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if state.flags & C.EntityState.CAN_MOVE:
                direction.value = 1.0
                if keys[pygame.K_LCTRL] or keys[pygame.K_a]:
                    state.flags &= ~C.EntityState.WALKING
                    state.flags |= C.EntityState.RUNNING
                    vel.value.x = C.RUN_ACC
                else:
                    state.flags |= C.EntityState.WALKING
                    state.flags &= ~C.EntityState.RUNNING
                    vel.value.x = C.WALK_ACC

        elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
            if state.flags & C.EntityState.CAN_MOVE:
                direction.value = -1.0
                if keys[pygame.K_LCTRL] or keys[pygame.K_a]:
                    state.flags &= ~C.EntityState.WALKING
                    state.flags |= C.EntityState.RUNNING
                    vel.value.x = -C.RUN_ACC
                else:
                    state.flags |= C.EntityState.WALKING
                    state.flags &= ~C.EntityState.RUNNING
                    vel.value.x = -C.WALK_ACC

        else:
            state.flags &= ~C.EntityState.WALKING
            state.flags &= ~C.EntityState.RUNNING


def DragSystem(engine, dt: float) -> None:
    # /!\ This system must be called BEFORE all other velocity changing system
    for eid in engine.get_entities_with(C.Velocity, C.Mass, C.State, C.Properties):
        state = engine.get_component(eid, C.State)
        props = engine.get_component(eid, C.Properties)
        mass = engine.get_component(eid, C.Mass).value
        vel = engine.get_component(eid, C.Velocity)

        if (state.flags & C.EntityState.NO_DRAG) or (props.flags & C.EntityProperty.FLOATING):
            continue

        if state.flags & C.EntityState.IN_WATER:
            coef = 40.0
        elif state.flags & C.EntityState.ON_GROUND:
            coef = 10.0
        elif state.flags & C.EntityState.WALL_SLIDING:
            coef = 20.0
        else:
            coef = 5.0

        vel.value *= 1 - coef * DRAG_BASE * dt / mass


def GravitySystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Velocity, C.Properties, C.State):
        properties = engine.get_component(eid, C.Properties)
        state = engine.get_component(eid, C.State)

        if properties.flags & C.EntityProperty.FLOATING:
            continue
        if state.flags & C.EntityState.IGNORE_GRAVITY:
            continue

        vel = engine.get_component(eid, C.Velocity)
        vel.value += GRAVITY * dt


def JumpSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Jump, C.Velocity, C.State, C.Mass):
        jump = engine.get_component(eid, C.Jump)
        vel = engine.get_component(eid, C.Velocity)
        state = engine.get_component(eid, C.State)
        mass = engine.get_component(eid, C.Mass).value

        if jump.time_left > 0:
            state.flags &= ~C.EntityState.CAN_JUMP
            state.flags |= C.EntityState.JUMPING
            jump.time_left -= dt
            t = radians(jump.direction)
            force = jump.strength * Vector2(cos(t), -sin(t))
            vel.value += force / mass * dt
        else:
            state.flags &= ~C.EntityState.JUMPING
            if not state.flags & C.EntityState.CAN_JUMP:
                state.flags |= C.EntityState.FALLING
            else:
                state.flags &= ~C.EntityState.FALLING


def MovementSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Velocity, C.Walk):
        vel = engine.get_component(eid, C.Velocity)
        state = engine.get_component(eid, C.State)
        xdir = engine.get_component(eid, C.XDirection).value
        if state.flags & C.EntityState.ON_GROUND:
            coef = 1.0
        else:
            coef = 0.3
        if state.flags & C.EntityState.CAN_MOVE:
            speed = 0.0
            if state.flags & C.EntityState.WALKING:
                speed = engine.get_component(eid, C.Walk).walk_speed
            elif state.flags & C.EntityState.RUNNING:
                speed = engine.get_component(eid, C.Walk).run_speed
            vel.value.x += xdir*coef*speed*dt


def MovePredictionSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Velocity, C.Position, C.NextPosition):
        vel = engine.get_component(eid, C.Velocity)
        pos = engine.get_component(eid, C.Position)
        next_pos = engine.get_component(eid, C.NextPosition)

        next_pos.value = pos.value + vel.value * dt


def MapCollisionSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Hitbox, C.MapCollisions, C.XDirection):
        hitbox = engine.get_component(eid, C.Hitbox)
        next_pos = engine.get_component(eid, C.NextPosition)
        vel = engine.get_component(eid, C.Velocity)
        col = engine.get_component(eid, C.MapCollisions)
        state = engine.get_component(eid, C.State)
        xdir = engine.get_component(eid, C.XDirection).value

        col.reset()

        # moving vector
        d = next_pos.value - hitbox.center
        test_rect = hitbox.rect.copy()
        test_rect.center = hitbox.center + d
        step = d.normalize() if d.length() > 0 else Vector2(0, 0)

        while d.dot(step) > 0 and engine.tilemap.colliderect(test_rect):
            d -= step
            test_rect.center = Vector2(test_rect.center) - step

        if engine.tilemap.colliderect(test_rect):
            test_rect = hitbox.rect.copy() # invert change

        # Now that collisions are resolved test limit collisions tlrb
        for direction in ["left", "right", "top", "bottom"]:
            setattr(col, direction, engine.tilemap.touch(test_rect)[direction])

        # update position
        next_pos.value = Vector2(test_rect.center)
        # Wall-sticking and on-ground flags
        if col.right:
            vel.value.x = 0
            if xdir == 1.0 and not (col.bottom or col.top) and not state.has_any_flags(C.EntityState.JUMPING):
                if engine.has_component(eid, C.WallSticking):
                    wstick = engine.get_component(eid, C.WallSticking)
                    if not state.has_any_flags(C.EntityState.WALL_STICKING, C.EntityState.WALL_SLIDING):
                        state.flags |= C.EntityState.WALL_STICKING
                        wstick.time_left = wstick.duration
                        vel.value.y = 0
                    else:
                        if wstick.time_left > 0:
                            wstick.time_left -= dt
                        else:
                            state.flags &= ~C.EntityState.WALL_STICKING
                            state.flags |= C.EntityState.WALL_SLIDING
        elif col.left:
            vel.value.x = 0
            if xdir == -1.0 and not (col.bottom or col.top) and not state.has_any_flags(C.EntityState.JUMPING):
                if engine.has_component(eid, C.WallSticking):
                    wstick = engine.get_component(eid, C.WallSticking)
                    if not state.has_any_flags(C.EntityState.WALL_STICKING, C.EntityState.WALL_SLIDING):
                        state.flags |= C.EntityState.WALL_STICKING
                        wstick.time_left = wstick.duration
                        vel.value.y = 0
                    else:
                        if wstick.time_left > 0:
                            wstick.time_left -= dt
                        else:
                            state.flags &= ~C.EntityState.WALL_STICKING
                            state.flags |= C.EntityState.WALL_SLIDING
        else:
            state.flags &= ~(C.EntityState.WALL_STICKING | C.EntityState.WALL_SLIDING)

        if col.bottom:
            vel.value.y = 0
            state.flags |= C.EntityState.ON_GROUND
        else:
            state.flags &= ~C.EntityState.ON_GROUND

        if col.top:
            vel.value.y = 60


def UpdateHitboxAndPositionSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Position, C.Hitbox, C.NextPosition):
        pos = engine.get_component(eid, C.Position)
        hitbox = engine.get_component(eid, C.Hitbox)
        next_pos = engine.get_component(eid, C.NextPosition)

        # Applique la position calculée après collisions
        pos.value = next_pos.value
        hitbox.rect.center = next_pos.value.x, next_pos.value.y


def EntityCollisionsSystem(engine, dt: float) -> None:
    entities = list(engine.get_entities_with(C.Hitbox, C.Position))
    for i, eid1 in enumerate(entities):
        hitbox1 = engine.get_component(eid1, C.Hitbox)
        for eid2 in entities[i+1:]:
            hitbox2 = engine.get_component(eid2, C.Hitbox)
            if hitbox1.rect.colliderect(hitbox2.rect):
                if engine.has_component(eid2, C.CollisionAction):
                    action = engine.get_component(eid2, C.CollisionAction)
                    action(engine, eid1, eid2)


def UpdateEntityStateSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.State):
        state = engine.get_component(eid, C.State)
        # Exemple : enlever certains états selon conditions (ON_GROUND + WALL_SLIDING etc.)
        if state.has_all_flags(C.EntityState.WALL_SLIDING, C.EntityState.ON_GROUND):
            state.flags &= ~C.EntityState.WALL_SLIDING
        if state.has_all_flags(C.EntityState.WALL_STICKING, C.EntityState.ON_GROUND):
            state.flags &= ~C.EntityState.WALL_STICKING


def CameraSystem(engine, dt: float) -> None:
    follow_entities = list(engine.get_entities_with(C.CameraFollow, C.Position))
    if not follow_entities:
        return

    eid = follow_entities[0]
    pos = engine.get_component(eid, C.Position).value
    follow = engine.get_component(eid, C.CameraFollow)

    cam = engine.camera
    follow.deadzone.center = cam.pos
    cam_w, cam_h = cam.size
    map_w = engine.tilemap.width * engine.tilemap.tileset.tile_size
    map_h = engine.tilemap.height * engine.tilemap.tileset.tile_size

    new_cam_x = cam.pos.x
    new_cam_y = cam.pos.y

    if pos.x < follow.deadzone.left:
        new_cam_x -= follow.deadzone.left - pos.x
    elif pos.x > follow.deadzone.right:
        new_cam_x += pos.x - follow.deadzone.right

    if pos.y < follow.deadzone.top:
        new_cam_y -= follow.deadzone.top - pos.y
    elif pos.y > follow.deadzone.bottom:
        new_cam_y += pos.y - follow.deadzone.bottom

    cam_x = cam.pos.x + (new_cam_x - cam.pos.x) * min(dt*follow.damping, 1.0)
    cam_y = cam.pos.y + (new_cam_y - cam.pos.y) * min(dt*follow.damping, 1.0)

    if map_w > cam_w:
        cam_x = max(cam_w / 2, min(cam_x, map_w - cam_w / 2))
    else:
        cam_x = map_w / 2

    if map_h > cam_h:
        cam_y = max(cam_h / 2, min(cam_y, map_h - cam_h / 2))
    else:
        cam_y = map_h / 2

    cam.pos = Vector2(cam_x, cam_y)
