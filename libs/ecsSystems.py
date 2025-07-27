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

# get main logger
from . import logger

# import external modules
from pygame import Vector2
from pygame.key import get_pressed
from math import cos, sin, radians
import pygame

# import modules from package
from . import ecsComponents as C


# --------------------------
# | Constants              |
# --------------------------
GRAVITY: Vector2 = Vector2(0, 960)
DRAG_BASE: float = 12.0
WALK_ACC: float = 1800.0
RUN_ACC: float = 3000.0


# --------------------------
# | Systems                |
# --------------------------
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
            coef = 18.0
        elif state.flags & C.EntityState.ON_GROUND:
            coef = 6.0
        elif state.flags & C.EntityState.WALL_SLIDING:
            coef = 10.0
        else:
            coef = 1.5

        vel.value *= 1 - coef * DRAG_BASE * dt / mass


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


def PhysicsSystem(engine, dt: float) -> None:
    # /!\ This system must be called AFTER every velocity changing system
    for eid in engine.get_entities_with(C.Position, C.Velocity):
        pos = engine.get_component(eid, C.Position)
        vel = engine.get_component(eid, C.Velocity)
        if abs(vel.value.x) < 1e-1:
            vel.value.x = 0
        if abs(vel.value.y) < 1e-1:
            vel.value.y = 0
        pos.value += vel.value * dt        


def EntityCollisionsSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Hitbox, C.EntityCollisions):
        ehitbox = engine.get_component(eid, C.Hitbox)
        colli = engine.get_component(eid, C.EntityCollisions)
        colli.reset()
        for oid in engine.get_entities_with(C.Hitbox):
            if oid != eid:
                ohitbox = engine.get_component(oid, C.Hitbox).rect.inflate(2, 2)
                left = bool(ohitbox.clipline(ehitbox.topleft, ehitbox.bottomleft))
                right = bool(ohitbox.clipline(ehitbox.topright, ehitbox.bottomright))
                top = bool(ohitbox.clipline(ehitbox.topleft, ehitbox.topright))
                bottom = bool(ohitbox.clipline(ehitbox.bottomleft, ehitbox.bottomright))
                if any((left, right, top, bottom)):
                    colli.entities.append((oid, (left, right, top, bottom)))
                    if engine.has_component(oid, C.CollisionAction):
                        action = engine.get_component(oid, C.CollisionAction).action
                        action(engine, oid, eid, dt)
                colli.left |= left
                colli.right |= right
                colli.top |= top
                colli.bottom |= bottom


def MapCollisionsSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Hitbox, C.MapCollisions):
        hitbox = engine.get_component(eid, C.Hitbox)
        col = engine.get_component(eid, C.MapCollisions)
        state = engine.get_component(eid, C.State)
        vel = engine.get_component(eid, C.Velocity)
        xdir = engine.get_component(eid, C.XDirection).value
        col.reset()
        tile_size = engine.tilemap.tileset.tile_size

        # bottom collision
        range_x: range = range(hitbox.left // tile_size, (hitbox.right-1) // tile_size+1)
        tile_y = hitbox.bottom // tile_size
        for tile_x in range_x:
            if 0 <= tile_x < engine.tilemap.width and 0 <= tile_y < engine.tilemap.height:
                tile_id = engine.tilemap.grid[tile_y][tile_x]
                if tile_id == -1:
                    continue
                tile = engine.tilemap.tileset.tiles[tile_id]
                if tile.hitbox:
                    col.bottom = True

        # top collision
        range_x: range = range(hitbox.left // tile_size, (hitbox.right-1) // tile_size+1)
        tile_y = (hitbox.top-1) // tile_size
        for tile_x in range_x:
            if 0 <= tile_x < engine.tilemap.width and 0 <= tile_y < engine.tilemap.height:
                tile_id = engine.tilemap.grid[tile_y][tile_x]
                if tile_id == -1:
                    continue
                tile = engine.tilemap.tileset.tiles[tile_id]
                if tile.hitbox:
                    col.top = True

        # left collision
        range_y: range = range(hitbox.top // tile_size, (hitbox.bottom-1) // tile_size+1)
        tile_x = (hitbox.left-1) // tile_size
        for tile_y in range_y:
            if 0 <= tile_x < engine.tilemap.width and 0 <= tile_y < engine.tilemap.height:
                tile_id = engine.tilemap.grid[tile_y][tile_x]
                if tile_id == -1:
                    continue
                tile = engine.tilemap.tileset.tiles[tile_id]
                if tile.hitbox:
                    col.left = True

        # right collision
        range_y: range = range(hitbox.top // tile_size, (hitbox.bottom-1) // tile_size+1)
        tile_x = hitbox.right // tile_size
        for tile_y in range_y:
            if 0 <= tile_x < engine.tilemap.width and 0 <= tile_y < engine.tilemap.height:
                tile_id = engine.tilemap.grid[tile_y][tile_x]
                if tile_id == -1:
                    continue
                tile = engine.tilemap.tileset.tiles[tile_id]
                if tile.hitbox:
                    col.right = True

        # gestion des conflits
        if col.topleft:
            if hitbox.top % tile_size == 0:
                col.top = False
            elif hitbox.left % tile_size == 0:
                col.left = False
            else:
                vstr = tile_size - hitbox.top % tile_size
                hstr = tile_size - hitbox.left % tile_size
                if vstr >= hstr:
                    col.top = False
                else:
                    col.left = False

        if col.topright:
            if hitbox.top % tile_size == 0:
                col.top = False
            elif hitbox.right % tile_size == 0:
                col.right = False
            else:
                vstr = tile_size - hitbox.top % tile_size
                hstr = hitbox.right % tile_size
                if vstr >= hstr:
                    col.top = False
                else:
                    col.right = False

        if col.bottomleft:
            if hitbox.bottom % tile_size == 0:
                col.bottom = False
            elif hitbox.left % tile_size == 0:
                col.left = False
            else:
                vstr = hitbox.bottom % tile_size
                hstr = tile_size - hitbox.left % tile_size
                if vstr >= hstr:
                    col.bottom = False
                else:
                    col.left = False

        if col.bottomright:
            if hitbox.bottom % tile_size == 0:
                col.bottom = False
            elif hitbox.right % tile_size == 0:
                col.right = False
            else:
                vstr = hitbox.bottom % tile_size
                hstr = hitbox.right % tile_size
                if vstr >= hstr:
                    col.bottom = False
                else:
                    col.right = False

        # reposition et changement d'état
        if col.bottom:
            state.flags |= C.EntityState.ON_GROUND
            hitbox.rect.bottom = (hitbox.bottom//tile_size)*tile_size
            vel.value.y = 0
        else:
            state.flags &= ~C.EntityState.ON_GROUND

        if col.right:
            if engine.has_component(eid, C.WallSticking):
                if xdir == 1.0:
                    winfo = engine.get_component(eid, C.WallSticking)
                    if not state.flags & (C.EntityState.WALL_STICKING | C.EntityState.WALL_SLIDING):
                        state.flags |= C.EntityState.WALL_STICKING
                        winfo.time_left = winfo.duration
                        vel.value.y = 0
                    else:
                        if winfo.time_left > 0:
                            winfo.time_left -= dt
                        else:
                            state.flags &= ~C.EntityState.WALL_STICKING
                            state.flags |= C.EntityState.WALL_SLIDING
            hitbox.rect.right = (hitbox.right//tile_size)*tile_size
            vel.value.x = 0

        if col.left:
            if engine.has_component(eid, C.WallSticking):
                if xdir == -1.0:
                    winfo = engine.get_component(eid, C.WallSticking)
                    if not state.flags & (C.EntityState.WALL_STICKING | C.EntityState.WALL_SLIDING):
                        state.flags |= C.EntityState.WALL_STICKING
                        winfo.time_left = winfo.duration
                        vel.value.y = 0
                    else:
                        if winfo.time_left > 0:
                            winfo.time_left -= dt
                        else:
                            state.flags &= ~C.EntityState.WALL_STICKING
                            state.flags |= C.EntityState.WALL_SLIDING
            hitbox.rect.left = ((hitbox.left-1)//tile_size+1)*tile_size
            vel.value.x = 0

        if not col.left and not col.right:
            state.flags &= ~C.EntityState.WALL_STICKING
            state.flags &= ~C.EntityState.WALL_SLIDING

        if col.top:
            hitbox.rect.top = ((hitbox.top-1)//tile_size + 1)*tile_size
            vel.value.y = -0.5*vel.value.y


def UpdateHitboxFromPositionSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Position, C.Hitbox):
        pos = engine.get_component(eid, C.Position)
        hit = engine.get_component(eid, C.Hitbox)
        hit.rect.center = pos.value.x, pos.value.y


def TileAnimationSystem(engine, dt: float) -> None:
    for tile in engine.tilemap.tileset.tiles:
        tile.animation_time_left -= dt
        if tile.animation_time_left <= 0:
            tile.animation_frame = (tile.animation_frame + 1) % len(tile.graphics)
            tile.animation_time_left += tile.animation_delay


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
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    jump.time_left = 0

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


def AISystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.AI):
        logic = engine.get_component(eid, C.AI).logic
        logic(eid, engine, dt)


def MovementSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Velocity):
        vel = engine.get_component(eid, C.Velocity)
        state = engine.get_component(eid, C.State)
        xdir = engine.get_component(eid, C.XDirection).value
        if state.flags & C.EntityState.ON_GROUND:
            coef = 1.0
        else:
            coef = 0.3
        if state.flags & C.EntityState.CAN_MOVE:
            if state.flags & C.EntityState.WALKING:
                vel.value.x += xdir*coef*WALK_ACC*dt
            elif state.flags & C.EntityState.RUNNING:
                vel.value.x += xdir*coef*RUN_ACC*dt


def UpdatePositionFromHitboxSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Position, C.Hitbox):
        pos = engine.get_component(eid, C.Position)
        hit = engine.get_component(eid, C.Hitbox)
        pos.value = hit.center
