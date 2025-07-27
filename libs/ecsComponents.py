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
from typing import Callable
from pygame import Vector2, Rect
from enum import IntFlag, auto
from dataclasses import dataclass

# importing package modules
from . import ecsAI


# --------------------------
# | Constants              |
# --------------------------
JUMP_STRENGTH: float = 1e4
JUMP_DURATION: float = 0.2


# --------------------------
# | Base class             |
# --------------------------
class ComponentBase:
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


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
    CAN_JUMP = ON_GROUND | WALL_SLIDING | WALL_STICKING | HANGING | CLIMBING
    CAN_MOVE = ON_GROUND | FALLING
    MOVING = WALKING | RUNNING | JUMPING | DASHING | FALLING | WALL_SLIDING | CLIMBING
    NO_DRAG = CROUCHING | WALL_STICKING | DASHING | HANGING | FREEZED | CLIMBING


# --------------------------
# | Components             |
# --------------------------
@dataclass
class Position(ComponentBase):
    value: Vector2

    @classmethod
    def from_dict(cls, data: dict):
        x = data.get("x", 0)
        y = data.get("y",0)
        return cls(Vector2(x, y))


@dataclass
class Velocity(ComponentBase):
    value: Vector2

    @classmethod
    def from_dict(cls, data: dict):
        x = data.get("x", 0)
        y = data.get("y",0)
        return cls(Vector2(x, y))


@dataclass
class Mass(ComponentBase):
    value: float = 1.0


@dataclass
class Properties(ComponentBase):
    flags: EntityProperty = EntityProperty.NONE


@dataclass
class State(ComponentBase):
    flags: EntityState = EntityState.NONE


@dataclass
class XDirection(ComponentBase):
    value: float = 1.0


@dataclass
class Jump(ComponentBase):
    direction: float = 0.0 # angle in degree
    strength: float = JUMP_STRENGTH
    duration: float = JUMP_DURATION
    time_left: float = 0.0


@dataclass
class EntityCollisions(ComponentBase):
    entities: list[tuple[int, tuple[bool, bool, bool, bool]]]
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
        self.bottom = False
        self.entities = []


@dataclass
class MapCollisions(ComponentBase):
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
        self.bottom = False


@dataclass
class Hitbox(ComponentBase):
    rect: Rect

    @classmethod
    def from_dict(cls, data: dict):
        x = data.get("x", 0)
        y = data.get("y", 0)
        width = data.get("width", 0)
        height = data.get("height", 0)
        return cls(Rect(x, y, width, height))

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
    def topright(self) -> Vector2:
        return Vector2(*self.rect.topright)
    
    @property
    def bottomleft(self) -> Vector2:
        return Vector2(*self.rect.bottomleft)
    
    @property
    def bottomright(self) -> Vector2:
        return Vector2(*self.rect.bottomright)

    @property
    def height(self) -> int:
        return self.rect.height
    
    @property
    def width(self) -> int:
        return self.rect.width
    
    
@dataclass
class AI(ComponentBase):
    logic: ecsAI.AILogic = ecsAI.Idle()

    @classmethod
    def from_dict(cls, data: dict):
        logic_cls = getattr(ecsAI, data.get("name", "Idle"))
        args = data.get("args", dict())
        return cls(logic=logic_cls(**args))


@dataclass
class PlayerControlled(ComponentBase):
    pass


@dataclass
class WallSticking(ComponentBase):
    time_left: float = 0.0
    duration: float = 0.2


@dataclass
class CollisionAction(ComponentBase):
    action: Callable


@dataclass
class Camera:
    rect: Rect

    @property
    def pos(self) -> Vector2:
        return Vector2(self.rect.topleft)

    @property
    def size(self) -> tuple[int, int]:
        return self.rect.size
