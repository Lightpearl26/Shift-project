#ecsComponents.py
# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
ECS libs Components
version : 1.0
____________________________________________________________________________________________________
Contains components of our game ecs
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# importing external modules
from typing import Any
from pygame import Vector2, Rect
from enum import IntFlag, auto
from dataclasses import dataclass

# importing package modules
from .ecsAI import AILogic, Idle


# --------------------------
# | Constants              |
# --------------------------
JUMP_STRENGTH: float = 1e4
JUMP_DURATION: float = 0.2


# --------------------------
# | Enums                  |
# --------------------------
class EntityProperty(IntFlag):
    NONE = 0
    PHASABLE = auto()
    FLOATING = auto()


class EntityState(IntFlag):
    NONE = 0
    # positionnal state
    ON_GROUND = auto()
    WALL_STICKING = auto()
    CROUCHING = auto()
    HANGING = auto()
    IN_WATER = auto()
    # movement state
    WALKING = auto()
    RUNNING = auto()
    JUMPING = auto()
    DASHING = auto()
    CLIMBING = auto()
    FALLING = auto()
    WALL_SLIDING = auto()
    # status state
    FREEZED = auto()
    SLOWED = auto()
    SHIELDED = auto()
    HURTED = auto()
    INVISIBLE = auto()

    # combined state
    IGNORE_GRAVITY = ON_GROUND | WALL_STICKING | FREEZED | DASHING | HANGING
    CAN_JUMP = ON_GROUND | WALL_SLIDING | WALL_STICKING | HANGING
    MOVING = WALKING | RUNNING | JUMPING | DASHING | FALLING | WALL_SLIDING | CLIMBING


# --------------------------
# | Components             |
# --------------------------
@dataclass
class Position:
    value: Vector2


@dataclass
class Velocity:
    value: Vector2


@dataclass
class Mass:
    value: float = 1.0


@dataclass
class Properties:
    flags: EntityProperty = EntityProperty.NONE


@dataclass
class State:
    flags: EntityState = EntityState.NONE


@dataclass
class XDirection:
    value: float = 1.0


@dataclass
class Jump:
    direction: float = 0.0 # angle in degree
    strength: float = JUMP_STRENGTH
    duration: float = JUMP_DURATION
    time_left: float = 0.0


@dataclass
class EntityCollisions:
    left: bool = False
    right: bool = False
    top: bool = False
    bottom: bool = False
    
    @property
    def topleft(self) -> bool:
        return self.left and self.top
    
    @property
    def topright(self) -> bool:
        return self.right and self.top
    
    @property
    def bottomleft(self) -> bool:
        return self.left and self.bottom
    
    @property
    def bottomright(self) -> bool:
        return self.right and self.bottom
    
    @property
    def colliding(self) -> bool:
        return any((self.left, self.right, self.top, self.bottom))
    
    def reset(self) -> None:
        self.left = False
        self.right = False
        self.top = False
        self.botton = False


@dataclass
class MapCollisions:
    left: bool = False
    right: bool = False
    top: bool = False
    bottom: bool = False
    
    @property
    def topleft(self) -> bool:
        return self.left and self.top
    
    @property
    def topright(self) -> bool:
        return self.right and self.top
    
    @property
    def bottomleft(self) -> bool:
        return self.left and self.bottom
    
    @property
    def bottomright(self) -> bool:
        return self.right and self.bottom
    
    @property
    def colliding(self) -> bool:
        return any((self.left, self.right, self.top, self.bottom))
    
    def reset(self) -> None:
        self.left = False
        self.right = False
        self.top = False
        self.botton = False


@dataclass
class Hitbox:
    rect: Rect

    @property
    def center(self) -> Vector2:
        return Vector2(*self.rect.center)
    
    @property
    def top(self) -> int:
        return self.rect.top
    
    @property
    def bottom(self) -> int:
        return self.rect.bottom
    
    @property
    def left(self) -> int:
        return self.rect.left
    
    @property
    def right(self) -> int:
        return self.rect.right
    
    @property
    def topleft(self) -> Vector2:
        return Vector2(*self.rect.topleft)
    
    @property
    def height(self) -> int:
        return self.rect.height
    
    @property
    def width(self) -> int:
        return self.rect.width


@dataclass
class Drag:
    base: float = 8.0

    def get_coef(self, entityState: State) -> float:
        if entityState.flags & EntityState.ON_GROUND:
            return self.base
        elif entityState.flags & EntityState.WALL_SLIDING:
            return 2.0*self.base
        return self.base*0.5
    
    
@dataclass
class AI:
    logic: AILogic = Idle()


@dataclass
class PlayerControlled:
    pass
