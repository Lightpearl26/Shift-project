# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
ECS libs Components
version : 1.1
____________________________________________________________________________________________________
Contains components of our game ecs
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# importing external modules
from __future__ import annotations
from typing import Callable
from enum import IntFlag, auto
from dataclasses import dataclass
from pygame import Rect, Vector2

# import configs
from .. import config

# import ai
from . import ai


# ----- Base class ----- #
class Component:
    """
    Base Instance for all ecs components
    """
    @classmethod
    def from_dict(cls, data: dict) -> "Component":
        """
        Create a new component from a dict
        """
        return cls(**data)


# ----- Enums ----- #
class EntityProperty(IntFlag):
    """
    Flag of all entity current properties
    """
    NONE: int = 0
    PHASABLE: int = auto()
    FLOATING: int = auto()


class EntityState(IntFlag):
    """
    Flag of all entity current states
    """
    NONE: int = 0

    # positionnal state
    ON_GROUND: int = auto()
    WALL_STICKING: int = auto()
    CROUCHING: int = auto()
    HANGING: int = auto()

    # movement state
    WALKING: int = auto()
    RUNNING: int = auto()
    JUMPING: int = auto()
    DASHING: int = auto()
    CLIMBING: int = auto()
    FALLING: int = auto()
    WALL_SLIDING: int = auto()

    # status state
    FREEZED: int = auto()
    SLOWED: int = auto()
    SHIELDED: int = auto()
    HURTED: int = auto()
    INVISIBLE: int = auto()

    # combined state
    IGNORE_GRAVITY: int = ON_GROUND | WALL_STICKING | FREEZED | DASHING | HANGING
    CAN_JUMP: int = ON_GROUND | WALL_STICKING | WALL_SLIDING | HANGING | CLIMBING
    CAN_MOVE: int = ON_GROUND | FALLING | HANGING | CLIMBING
    MOVING: int = WALKING | RUNNING | JUMPING | DASHING | FALLING | WALL_SLIDING | CLIMBING
    NO_DRAG: int = CROUCHING | WALL_STICKING | DASHING | HANGING | FREEZED | CLIMBING


# ----- Physic Components ----- #
@dataclass
class Velocity(Component):
    """
    Velocity of the Entity
    """
    value: Vector2

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> Velocity:
        x = data.get("x", 0.0)
        y = data.get("y", 0.0)
        return cls(Vector2(x, y))

    @property
    def x(self: Velocity) -> float:
        """
        X coordinate
        """
        return self.value.x

    @x.setter
    def x(self: Velocity, value: float) -> None:
        self.value.x = value

    @property
    def y(self: Velocity) -> float:
        """
        Y coordinate
        """
        return self.value.y

    @y.setter
    def y(self: Velocity, value: float) -> None:
        self.value.y = value


@dataclass
class Mass(Component):
    """
    Mass of the Entity
    """
    value: float = 1.0


@dataclass
class XDirection(Component):
    """
    The direction the Entity is facing (-1.0 for left and 1.0 for right)
    """
    value: float = 1.0


@dataclass
class Hitbox(Component):
    """
    Hitbox of the Entity
    """
    pos: Vector2
    size: tuple[int, int]

    @classmethod
    def from_dict(cls, data: dict[str, float | int]) -> Hitbox:
        x = data.get("x", 0.0)
        y = data.get("y", 0.0)
        width = data.get("width", 0)
        height = data.get("height", 0)
        return cls(Vector2(x, y), (width, height))

    @property
    def rect(self: Hitbox) -> Rect:
        """
        Get the pygame Rect of the hitbox
        """
        topleft = self.pos - Vector2(self.size[0]/2, self.size[1]/2)
        return Rect(topleft, self.size)

    @rect.setter
    def rect(self: Hitbox, value: Rect) -> None:
        self.pos = Vector2(value.center)
        self.size = value.size

    def _get_prop(self: Hitbox, prop: str) -> float | Vector2:
        """
        Get a rect property of the Hitbox and convert it
        """
        p = getattr(self.rect, prop, None)
        if p and isinstance(p, int | float):
            return float(p)
        if p and isinstance(p, tuple):
            return Vector2(p)
        raise AttributeError(f"Attribut {prop} doesn't exists")

    def _set_prop(self: Hitbox, prop: str, value: float | Vector2) -> None:
        """
        Set a Rect property of the Hitbox
        """
        rect = self.rect
        setattr(rect, prop, value)
        self.pos = Vector2(rect.center)
        self.size = rect.size

    top = property(lambda obj, p="top": Hitbox._get_prop(obj, p),
                   lambda obj, value, p="top": Hitbox._set_prop(obj, p, value),
                   doc="Hitbox Rect top property")
    bottom = property(lambda obj, p="bottom": Hitbox._get_prop(obj, p),
                      lambda obj, value, p="bottom": Hitbox._set_prop(obj, p, value),
                      doc="Hitboc Rect bottom property")
    left = property(lambda obj, p="left": Hitbox._get_prop(obj, p),
                    lambda obj, value, p="left": Hitbox._set_prop(obj, p, value),
                    doc="Hitbox Rect left property")
    right = property(lambda obj, p="right": Hitbox._get_prop(obj, p),
                     lambda obj, value, p="right": Hitbox._set_prop(obj, p, value),
                     doc="Hitbox rect right property")
    center = property(lambda obj, p="center": Hitbox._get_prop(obj, p),
                      lambda obj, value, p="center": Hitbox._set_prop(obj, p, value),
                      doc="Hitbox Rect center property")
    centerx = property(lambda obj, p="centerx": Hitbox._get_prop(obj, p),
                       lambda obj, value, p="centerx": Hitbox._set_prop(obj, p, value),
                       doc="Hitbox rect centerx property")
    centery = property(lambda obj, p="centery": Hitbox._get_prop(obj, p),
                       lambda obj, value, p="centery": Hitbox._set_prop(obj, p, value),
                       doc="Hitbox rect centery property")
    topleft = property(lambda obj, p="topleft": Hitbox._get_prop(obj, p),
                       lambda obj, value, p="topleft": Hitbox._set_prop(obj, p, value),
                       doc="Hitbox rect topleft property")
    topright = property(lambda obj, p="topright": Hitbox._get_prop(obj, p),
                        lambda obj, value, p="topright": Hitbox._set_prop(obj, p, value),
                        doc="=Hitbox rect topright property")
    bottomleft = property(lambda obj, p="bottomleft": Hitbox._get_prop(obj, p),
                          lambda obj, value, p="bottomleft": Hitbox._set_prop(obj, p, value),
                          doc="Hitbox Rect bottomleft property")
    bottomright = property(lambda obj, p="bottomright": Hitbox._get_prop(obj, p),
                           lambda obj, value, p="bottomright": Hitbox._set_prop(obj, p, value),
                           doc="Hitbox Rect bottomright property")
    width = property(lambda obj, p="width": Hitbox._get_prop(obj, p),
                     lambda obj, value, p="width": Hitbox._set_prop(obj, p, value),
                     doc="Hitbox Rect width property")
    height = property(lambda obj, p="height": Hitbox._get_prop(obj, p),
                      lambda obj, value, p="height": Hitbox._set_prop(obj, p, value),
                      doc="Hitbox Rect height property")


@dataclass
class NextPosition(Component):
    """
    Estimated position of the Entity after applying velocity
    """
    value: Vector2

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> NextPosition:
        x = data.get("x", 0.0)
        y = data.get("y", 0.0)
        return cls(Vector2(x, y))

    @property
    def x(self: NextPosition) -> float:
        """
        X coordinate
        """
        return self.value.x

    @x.setter
    def x(self: NextPosition, value: float) -> None:
        self.value.x = value

    @property
    def y(self: NextPosition) -> float:
        """
        Y coordinate
        """
        return self.value.y

    @y.setter
    def y(self: NextPosition, value: float) -> None:
        self.value.y = value


# ----- Flags Components ----- #
@dataclass
class State(Component):
    """
    Current State of the Entity
    """
    flags: EntityState = EntityState.NONE

    def add_flag(self: State, *flags: EntityState) -> None:
        """
        Add states to the current flags
        """
        for flag in flags:
            self.flags |= flag

    def remove_flag(self: State, *flags: EntityState) -> None:
        """
        Remove states from the current flags
        """
        for flag in flags:
            self.flags &= ~flag

    def has_flag(self: State, *flags: str) -> bool:
        """
        Do same as has_all_flags but with str reference of flags
        """
        return self.has_all_flags(*(getattr(EntityState, flag) for flag in flags))

    def has_all_flags(self: State, *flags: EntityState) -> bool:
        """
        Test if Entity has all states listed
        """
        return all(self.flags & flag for flag in flags)

    def has_any_flags(self: State, *flags: EntityState) -> bool:
        """
        Test if Entity has any of the states listed
        """
        return any(self.flags & flag for flag in flags)


@dataclass
class Properties(Component):
    """
    Current Properties of the Entity
    """
    flags: EntityProperty = EntityProperty.NONE

    def add_flag(self: Properties, *flags: EntityProperty) -> None:
        """
        Add properties to the current flags
        """
        for flag in flags:
            self.flags |= flag

    def remove_flag(self: Properties, *flags: EntityProperty) -> None:
        """
        Remove properties from the current flags
        """
        for flag in flags:
            self.flags &= ~flag

    def has_all_flags(self: Properties, *flags: EntityProperty) -> bool:
        """
        Test if Entity has all properties listed
        """
        return all(self.flags & flag for flag in flags)

    def has_any_flags(self: Properties, *flags: EntityProperty) -> bool:
        """
        Test if Entity has any of the properties listed
        """
        return any(self.flags & flag for flag in flags)


# ----- Control Components ----- #
@dataclass
class Controlled(Component):
    """
    Entity is controlled by a player
    """


@dataclass
class AI(Component):
    """
    Ai of the Entity
    """
    logic: ai.Logic = ai.Idle()

    @classmethod
    def from_dict(cls, data: dict) -> AI:
        logic_cls = getattr(ai, data.get("name", "Idle"))
        args = data.get("args", {})
        return cls(logic=logic_cls(**args))


# ----- Action timers Components ----- #
@dataclass
class Jump(Component):
    """
    Jumping timer informations
    """
    direction: float = 0.0 # °
    strength: float = config.JUMP_STRENGTH
    duration: float = config.JUMP_DURATION
    time_left: float = 0.0


@dataclass
class WallSticking(Component):
    """
    Wallsticking timer informations
    """
    time_left: float = 0.0
    duration: float = config.WALLSTICK_DURATION


@dataclass
class Walk(Component):
    """
    Movement informations
    """
    walk_speed: float = config.WALK_SPEED
    run_speed: float = config.RUN_SPEED


# ----- Collision box Components ----- #
@dataclass
class CameraFollow(Component):
    """
    Tag an entity to be followed by camera
    """
    deadzone: Rect
    damping: float = config.CAMERA_DAMPING

    @classmethod
    def from_dict(cls, data: dict) -> CameraFollow:
        size = data.get("deadzone", (0, 0))
        damping = data.get("damping", config.CAMERA_DAMPING)
        return cls(Rect((0, 0), size), damping)


@dataclass
class EntityCollision(Component):
    """
    Collision box with other entities
    """
    collided_entities: list[tuple[int, tuple[bool, bool, bool, bool]]]
    left: bool = False
    right: bool = False
    top: bool = False
    bottom: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> EntityCollision:
        return cls([], False, False, False, False)

    @property
    def topleft(self: EntityCollision) -> bool:
        """
        State of collision in topleft
        """
        return self.left and self.top

    @property
    def topright(self: EntityCollision) -> bool:
        """
        State of collision in topright
        """
        return self.right and self.top

    @property
    def bottomleft(self: EntityCollision) -> bool:
        """
        State of collision in bottomleft
        """
        return self.left and self.bottom

    @property
    def bottomright(self: EntityCollision) -> bool:
        """
        State of collision in bottomright
        """
        return self.right and self.bottom

    @property
    def colliding(self: EntityCollision) -> bool:
        """
        State of entity collision
        """
        return any((self.left, self.right, self.top, self.bottom))

    def reset(self: EntityCollision) -> None:
        """
        Reset all collisions to False
        """
        self.left = False
        self.right = False
        self.top = False
        self.bottom = False
        self.collided_entities = []


@dataclass
class MapCollision(Component):
    """
    Collision box with Tilemap
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
class CollisionAction(Component):
    """
    Action called by Entity when on collision
    """
    action: Callable
