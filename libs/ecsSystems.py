# -*- coding: utf-8 -*-

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
from . import ecsComponents as C

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
            direction.value = 1.0
            if keys[pygame.K_LCTRL] or keys[pygame.K_a]:
                state.flags &= ~C.EntityState.WALKING
                state.flags |= C.EntityState.RUNNING
            else:
                state.flags |= C.EntityState.WALKING
                state.flags &= ~C.EntityState.RUNNING

        elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
            direction.value = -1.0
            if keys[pygame.K_LCTRL] or keys[pygame.K_a]:
                state.flags &= ~C.EntityState.WALKING
                state.flags |= C.EntityState.RUNNING
            else:
                state.flags |= C.EntityState.WALKING
                state.flags &= ~C.EntityState.RUNNING

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
            coef = 1.0

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
            acc = 0.0
            if state.flags & C.EntityState.WALKING:
                acc = engine.get_component(eid, C.Walk).walk_acc
            elif state.flags & C.EntityState.RUNNING:
                acc = engine.get_component(eid, C.Walk).run_acc
            vel.value.x += xdir*coef*acc*dt


def MovePredictionSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Velocity, C.Position, C.NextPosition):
        vel = engine.get_component(eid, C.Velocity)
        pos = engine.get_component(eid, C.Position)
        next_pos = engine.get_component(eid, C.NextPosition)

        next_pos.value = pos.value + vel.value * dt


def MapCollisionSystem(engine, dt: float) -> None:
    tile_size = engine.tilemap.tileset.tile_size

    for eid in engine.get_entities_with(C.Hitbox,
                                        C.NextPosition,
                                        C.Velocity,
                                        C.MapCollisions,
                                        C.State,
                                        C.XDirection):
        hitbox = engine.get_component(eid, C.Hitbox)
        next_pos = engine.get_component(eid, C.NextPosition)
        vel = engine.get_component(eid, C.Velocity)
        col = engine.get_component(eid, C.MapCollisions)
        state = engine.get_component(eid, C.State)
        xdir = engine.get_component(eid, C.XDirection).value

        col.reset()

        dx = next_pos.value.x - hitbox.rect.centerx + xdir
        dy = next_pos.value.y - hitbox.rect.centery + 1

        test_rect = hitbox.rect.copy()

        if dx != 0:
            sign_x = 1 if dx > 0 else -1
            remaining_dx = abs(dx)
            while remaining_dx > 0:
                step = min(remaining_dx, tile_size)
                test_rect.centerx += sign_x * step

                x_edge = test_rect.right - 1 if sign_x > 0 else test_rect.left
                y_start = test_rect.top // tile_size
                y_end = (test_rect.bottom - 1) // tile_size
                tile_x = x_edge // tile_size

                coll = False
                for tile_y in range(y_start, y_end+1):
                    if 0 <= tile_x < engine.tilemap.width and 0 <= tile_y < engine.tilemap.height:
                        tile_id = engine.tilemap.grid[tile_y][tile_x]
                        coll |= (tile_id != -1 and engine.tilemap.tileset.tiles[tile_id].hitbox)

                if coll:
                    if sign_x > 0:
                        test_rect.right = tile_x * tile_size
                        col.right = True
                    else:
                        test_rect.left = (tile_x + 1) * tile_size
                        col.left = True
                    vel.value.x = 0
                    break

                remaining_dx -= step

        if dy != 0:
            sign_y = 1 if dy > 0 else -1
            remaining_dy = abs(dy)
            while remaining_dy > 0:
                step = min(remaining_dy, tile_size)
                test_rect.centery += sign_y * step

                y_edge = test_rect.bottom - 1 if sign_y > 0 else test_rect.top
                x_start = test_rect.left // tile_size
                x_end = (test_rect.right - 1) // tile_size
                tile_y = y_edge // tile_size

                coll = False
                for tile_x in range(x_start, x_end+1):
                    if 0 <= tile_x < engine.tilemap.width and 0 <= tile_y < engine.tilemap.height:
                        tile_id = engine.tilemap.grid[tile_y][tile_x]
                        coll |= (tile_id != -1 and engine.tilemap.tileset.tiles[tile_id].hitbox)

                if coll:
                    if sign_y > 0:
                        test_rect.bottom = tile_y * tile_size
                        col.bottom = True
                    else:
                        test_rect.top = (tile_y + 1) * tile_size
                        col.top = True
                    vel.value.y = 0
                    break

                remaining_dy -= step

        if not (col.left or col.right):
            test_rect.centerx -= xdir
        if not (col.top or col.bottom):
            test_rect.centery -= 1

        next_pos.value = Vector2(*test_rect.center)

        if col.bottom:
            state.flags |= C.EntityState.ON_GROUND

        else:
            state.flags &= ~C.EntityState.ON_GROUND

        if col.right and xdir == 1.0 and not col.bottom:
            if engine.has_component(eid, C.WallSticking):
                wstick = engine.get_component(eid, C.WallSticking)
                if not state.has_any_flags(C.EntityState.WALL_STICKING,
                                    C.EntityState.WALL_SLIDING):
                    state.flags |= C.EntityState.WALL_STICKING
                    wstick.time_left = wstick.duration
                    vel.value.y = 0
                else:
                    if wstick.time_left > 0:
                        wstick.time_left -= dt
                    else:
                        state.flags &= ~C.EntityState.WALL_STICKING
                        state.flags |= C.EntityState.WALL_SLIDING

        elif col.left and xdir == -1.0 and not col.bottom:
            if engine.has_component(eid, C.WallSticking):
                wstick = engine.get_component(eid, C.WallSticking)
                if not state.has_any_flags(C.EntityState.WALL_STICKING,
                                    C.EntityState.WALL_SLIDING):
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
