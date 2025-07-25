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
WALK_SPEED: float = 100.0
RUN_SPEED: float = 200.0


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
    for eid in engine.get_entities_with(C.Velocity, C.State, C.Drag, C.Mass):
        state = engine.get_component(eid, C.State)
        drag_coef = engine.get_component(eid, C.Drag).get_coef(state)
        mass = engine.get_component(eid, C.Mass).value

        vel = engine.get_component(eid, C.Velocity)
        vel.value -=  drag_coef * vel.value * dt / mass


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


def PhysicsSystem(engine, dt: float) -> None:
    # /!\ This system must be called AFTER every velocity changing system
    for eid in engine.get_entities_with(C.Position, C.Velocity):
        pos = engine.get_component(eid, C.Position)
        vel = engine.get_component(eid, C.Velocity)
        pos.value += vel.value * dt


def EntityCollisionsSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Hitbox, C.EntityCollisions):
        ehitbox = engine.get_component(eid, C.Hitbox)
        colli = engine.get_component(eid, C.EntityCollisions)
        colli.reset()
        for oid in engine.get_entities_with(C.Hitbox):
            if oid != eid:
                ohitbox = engine.get_component(oid, C.Hitbox).rect.copy()
                ohitbox.x -= 1
                ohitbox.y -= 1
                ohitbox.width += 2
                ohitbox.height += 2
                colli.left = bool(ohitbox.clipline(ehitbox.topleft, ehitbox.bottomleft))
                colli.right = bool(ohitbox.clipline(ehitbox.topright, ehitbox.bottomright))
                colli.top = bool(ohitbox.clipline(ehitbox.topleft, ehitbox.topright))
                colli.bottom = bool(ohitbox.clipline(ehitbox.bottomleft, ehitbox.bottomright))


def MapCollisionSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Hitbox, C.MapCollisions):
        hitbox = engine.get_component(eid, C.Hitbox)
        col = engine.get_component(eid, C.MapCollisions)
        #col.left, col.right, col.top, col.bottom = engine.tilemap.get_collisions(hitbox)


def EntityUpdateSystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.Position, C.Hitbox):
        pos = engine.get_component(eid, C.Position)
        hit = engine.get_component(eid, C.Hitbox)
        hit.rect.center = int(pos.value.x), int(pos.value.y)


def PlayerControlSystem(engine, dt: float) -> None:
    events = pygame.event.get()
    keys = pygame.key.get_pressed()

    for eid in engine.get_entities_with(C.PlayerControlled, C.Velocity, C.XDirection, C.State, C.Jump):
        vel = engine.get_component(eid, C.Velocity)
        direction = engine.get_component(eid, C.XDirection)
        state = engine.get_component(eid, C.State)
        jump = engine.get_component(eid, C.Jump)

        # Horizontal movement
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and (state.flags & C.EntityState.CAN_JUMP):
                    jump.time_left = jump.duration
                    jump.direction = 90.0
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    jump.time_left = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.value = 1.0
            if keys[pygame.K_LCTRL] or keys[pygame.K_a]:
                vel.value.x = RUN_SPEED
            else:
                vel.value.x = WALK_SPEED
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            direction.value = -1.0
            if keys[pygame.K_LCTRL] or keys[pygame.K_a]:
                vel.value.x = -RUN_SPEED
            else:
                vel.value.x = -WALK_SPEED


def AISystem(engine, dt: float) -> None:
    for eid in engine.get_entities_with(C.AI):
        logic = engine.get_component(eid, C.AI).logic
        logic(eid, engine, dt)
