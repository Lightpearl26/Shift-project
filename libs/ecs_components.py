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
from enum import IntFlag, auto
from dataclasses import dataclass
from pygame import Vector2, Rect

# importing package modules
from . import ecs_ai


# --------------------------
# | Constants              |
# --------------------------
JUMP_STRENGTH: float = 1e4
JUMP_DURATION: float = 0.2
WALK_ACC: float = 1000.0
RUN_ACC: float = 2000.0


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
    """
    Property of the Entity
    """
    NONE = 0
    PHASABLE = auto()
    FLOATING = auto()


class EntityState(IntFlag):
    """
    State of the Entity
    """
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
    """
    Position of the Entity
    """
    value: Vector2

    @classmethod
    def from_dict(cls, data: dict):
        x = data.get("x", 0)
        y = data.get("y",0)
        return cls(Vector2(x, y))


@dataclass
class NextPosition(ComponentBase):
    """
    Emulated position of entity after movement
    """
    value: Vector2
    
    @classmethod
    def from_dict(cls, data: dict):
        x = data.get("x", 0)
        y = data.get("y",0)
        return cls(Vector2(x, y))


@dataclass
class Velocity(ComponentBase):
    """
    Velocity of the Entity
    """
    value: Vector2

    @classmethod
    def from_dict(cls, data: dict):
        x = data.get("x", 0)
        y = data.get("y",0)
        return cls(Vector2(x, y))


@dataclass
class Mass(ComponentBase):
    """
    Mass of the Entity
    """
    value: float = 1.0


@dataclass
class Properties(ComponentBase):
    """
    Current properties of the Entity
    """
    flags: EntityProperty = EntityProperty.NONE


@dataclass
class State(ComponentBase):
    """
    Current state of the Entity
    """
    flags: EntityState = EntityState.NONE

    def has_any_flags(self, *flags: int) -> bool:
        """
        Test if Entity has any of the given flags
        """
        return any((self.flags & flag for flag in flags))
    
    def has_all_flags(self, *flags: int) -> bool:
        """
        Test if Entity has all of the given flags
        """
        return all((self.flags & flag for flag in flags))


@dataclass
class XDirection(ComponentBase):
    """
    Direction where the Entity is facing (-1.0 for left and 1.0 for right)
    """
    value: float = 1.0


@dataclass
class Jump(ComponentBase):
    """
    Jump informations of the entity
    """
    direction: float = 0.0 #°
    strength: float = JUMP_STRENGTH
    duration: float = JUMP_DURATION
    time_left: float = 0.0


@dataclass
class EntityCollisions(ComponentBase):
    """
    State of entity collision with other entities
    """
    entities: list[tuple[int, tuple[bool, bool, bool, bool]]]
    left: bool = False
    right: bool = False
    top: bool = False
    bottom: bool = False

    @property
    def topleft(self) -> bool:
        """
        State of collision in topleft
        """
        return self.left and self.top

    @property
    def topright(self) -> bool:
        """
        State of collision in topright
        """
        return self.right and self.top

    @property
    def bottomleft(self) -> bool:
        """
        State of collision in bottomleft
        """
        return self.left and self.bottom

    @property
    def bottomright(self) -> bool:
        """
        State of collision in bottomright
        """
        return self.right and self.bottom

    @property
    def colliding(self) -> bool:
        """
        State of entity collision
        """
        return any((self.left, self.right, self.top, self.bottom))

    def reset(self) -> None:
        """
        Reset all collisions to False
        """
        self.left = False
        self.right = False
        self.top = False
        self.bottom = False
        self.entities = []


@dataclass
class MapCollisions(ComponentBase):
    """
    State of Entity collision with the current Map
    """
    left: bool = False
    right: bool = False
    top: bool = False
    bottom: bool = False

    @property
    def topleft(self) -> bool:
        """
        State of topleft collision
        """
        return self.left and self.top

    @property
    def topright(self) -> bool:
        """
        State of topright collision
        """
        return self.right and self.top

    @property
    def bottomleft(self) -> bool:
        """
        State of bottomleft collision
        """
        return self.left and self.bottom

    @property
    def bottomright(self) -> bool:
        """
        State of bottomright collision
        """
        return self.right and self.bottom

    @property
    def colliding(self) -> bool:
        """
        State of collision
        """
        return any((self.left, self.right, self.top, self.bottom))

    def reset(self) -> None:
        """
        Reset all collisions to False
        """
        self.left = False
        self.right = False
        self.top = False
        self.bottom = False


@dataclass
class Hitbox(ComponentBase):
    """
    Hitbox rect of the Entity
    """
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
        """
        Get center point of the Hitbox
        """
        return Vector2(self.rect.centerx, self.rect.centery)

    @property
    def top(self) -> int:
        """
        Get top coordinate of the hitbox
        """
        return self.rect.top

    @property
    def bottom(self) -> int:
        """
        Get bottom coordinate of the hitbox
        """
        return self.rect.bottom

    @property
    def left(self) -> int:
        """
        Get left coordinate of the hitbox
        """
        return self.rect.left

    @property
    def right(self) -> int:
        """
        Get right coordinate of the hitbox
        """
        return self.rect.right

    @property
    def topleft(self) -> Vector2:
        """
        Get topleft point of the hitbox
        """
        return Vector2(self.rect.left, self.rect.top)

    @property
    def topright(self) -> Vector2:
        """
        Get topright point of the hitbox
        """
        return Vector2(self.rect.right, self.rect.top)

    @property
    def bottomleft(self) -> Vector2:
        """
        Get bottomleft point of the hitbox
        """
        return Vector2(self.rect.left, self.rect.bottom)

    @property
    def bottomright(self) -> Vector2:
        """
        Get bottomright point of the hitbox
        """
        return Vector2(self.rect.right, self.rect.bottom)

    @property
    def height(self) -> int:
        """
        Get height of the hitbox
        """
        return self.rect.height

    @property
    def width(self) -> int:
        """
        Get width of the hitbox
        """
        return self.rect.width

    @property
    def size(self) -> tuple[int, int]:
        """
        Get size of the hitbox
        """
        return (self.width, self.height)


@dataclass
class AI(ComponentBase):
    """
    AI of the Entity
    """
    logic: ecs_ai.AILogic = ecs_ai.Idle()

    @classmethod
    def from_dict(cls, data: dict):
        logic_cls = getattr(ecs_ai, data.get("name", "Idle"))
        args = data.get("args", dict())
        return cls(logic=logic_cls(**args))


@dataclass
class PlayerControlled(ComponentBase):
    """
    Entity is controlled by a player
    """


@dataclass
class WallSticking(ComponentBase):
    """
    Wallsticking informations of the entity
    """
    time_left: float = 0.0
    duration: float = 0.1


@dataclass
class CollisionAction(ComponentBase):
    """
    Action called by Entity when on collision
    """
    action: Callable


@dataclass
class Camera:
    """
    Camera of the Game
    """
    pos: Vector2
    size: tuple[int, int]

    @property
    def rect(self) -> Rect:
        """
        Returns the rect of the camera
        """
        w, h = self.size
        topleft = self.pos - Vector2(w/2, h/2)
        return Rect(int(topleft.x), int(topleft.y), w, h)

    def transform_coords(self, coords: Vector2) -> Vector2:
        """
        Transforms coords to match camera
        """
        return coords - Vector2(self.rect.left, self.rect.top)


@dataclass
class CameraFollow(ComponentBase):
    """
    Tags an entity to be followed by camera
    """
    deadzone: Rect
    damping: float = 8.0

    @classmethod
    def from_dict(cls, data: dict):
        w, h = data.get("deadzone").get("width"), data.get("deadzone").get("height")
        damping = data.get("damping", 8.0)
        return cls(Rect(0, 0, w, h), damping)


@dataclass
class Walk(ComponentBase):
    """
    walking and running informations of the Entity
    """
    walk_acc: float = WALK_ACC
    run_acc: float = RUN_ACC
