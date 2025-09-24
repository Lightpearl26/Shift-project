# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
Header lib
version : 1.1
____________________________________________________________________________________________________
Contains header of all libs of the game
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from __future__ import annotations
from typing import Protocol, Callable, Iterator, Self, Optional
from enum import Enum
from pygame import Vector2, Rect, Surface


####################################################################################################
# ECS protocols                                                                                    #
####################################################################################################

# ----- ECS ai protocols ----- #
class Logic(Protocol):
    """
    Base Logic of AI
    """
    def __call__(self, eid: int, engine: "Engine", dt: float) -> None: ...


class Idle(Logic, Protocol):
    """
    IDLE logic
    """


# ----- ECS components protocols ----- #
class ComponentTypes(str, Enum):
    """
	Enum for mapping any component name
    """
    AI = "AI"
    CAMERAFOLLOW = "CameraFollow"
    COLLISIONACTION = "CollisionAction"
    CONTROLLED = "Controlled"
    ENTITYCOLLISION = "EntityCollision"
    HITBOX = "Hitbox"
    JUMP = "Jump"
    MAPCOLLISION = "MapCollision"
    MASS = "Mass"
    NEXTPOSITION = "NextPosition"
    PROPERTIES = "Properties"
    STATE = "State"
    VELOCITY = "Velocity"
    WALK = "Walk"
    WALLSTICKING = "WallSticking"
    XDIRECTION = "XDirection"

    @classmethod
    def from_str(cls, name: str) -> ComponentTypes:
        """
        Convert a string to a ComponentTypes enum member.
        Raises ValueError if no match is found.
        """
        for member in cls:
            if member.value == name:
                return member
        raise ValueError(f"No ComponentTypes member with value '{name}' found.")


class Component(Protocol):
    """
    Base Instance for all ecs components
    """
    @classmethod
    def from_dict(cls, data: dict) -> Component:
        """
        Create a new component from a dict
        """


class EntityProperty(Protocol):
    """
    Flag of all entity current properties
    """
    NONE: int
    PHASABLE: int
    FLOATING: int


class EntityState(Protocol):
    """
    Flag of all entity current states
    """
    NONE: int
    ON_GROUND: int
    WALL_STICKING: int
    CROUCHING: int
    HANGING: int
    WALKING: int
    RUNNING: int
    JUMPING: int
    DASHING: int
    CLIMBING: int
    FALLING: int
    WALL_SLIDING: int
    FREEZED: int
    SLOWED: int
    SHIELDED: int
    HURTED: int
    INVISIBLE: int
    IGNORE_GRAVITY: int
    CAN_JUMP: int
    CAN_MOVE: int
    MOVING: int
    NO_DRAG: int


class Velocity(Component, Protocol):
    """
    Velocity of the Entity
    """
    value: Vector2
    x: float
    y: float


class Mass(Component, Protocol):
    """
    Mass of the Entity
    """
    value: float


class XDirection(Component, Protocol):
    """
    The direction the Entity is facing (-1.0 for left and 1.0 for right)
    """
    value: float


class Hitbox(Component, Protocol):
    """
    Hitbox of the Entity
    """
    pos: Vector2
    size: tuple[int, int]
    rect: Rect
    top: float
    bottom: float
    left: float
    right: float
    center: Vector2
    centerx: float
    centery: float
    topleft: Vector2
    topright: Vector2
    bottomleft: Vector2
    bottomright: Vector2
    width: float
    height: float


class NextPosition(Component, Protocol):
    """
    Estimated position of the Entity after applying velocity
    """
    value: Vector2
    x: float
    y: float


class State(Component, Protocol):
    """
    Current State of the Entity
    """
    flags: EntityState
    def add_flag(self: Self, *flags: EntityState) -> None:
        """
        Add states to the current flags
        """
    def remove_flag(self: Self, *flags: EntityState) -> None:
        """
        Remove states from the current flags
        """
    def has_flag(self: Self, *flags: str) -> bool:
        """
        Do same as has_all_flags but with str reference of flags
        """
    def has_all_flags(self: Self, *flags: EntityState) -> bool:
        """
        Test if Entity has all states listed
        """
    def has_any_flags(self: Self, *flags: EntityState) -> bool:
        """
        Test if Entity has any of the states listed
        """


class Properties(Component, Protocol):
    """
    Current Properties of the Entity
    """
    flags: EntityProperty
    def add_flag(self: Self, *flags: EntityProperty) -> None:
        """
        Add properties to the current flags
        """
    def remove_flag(self: Self, *flags: EntityProperty) -> None:
        """
        Remove properties from the current flags
        """
    def has_all_flags(self: Self, *flags: EntityProperty) -> bool:
        """
        Test if Entity has all properties listed
        """
    def has_any_flags(self: Self, *flags: EntityProperty) -> bool:
        """
        Test if Entity has any of the properties listed
        """


class Controlled(Component, Protocol):
    """
    Entity is controlled by a player
    """


class AI(Component, Protocol):
    """
    Ai of the Entity
    """
    logic: Logic


class Jump(Component, Protocol):
    """
    Jumping timer informations
    """
    direction: float
    strength: float
    duration: float
    time_left: float


class WallSticking(Component, Protocol):
    """
    Wallsticking timer informations
    """
    time_left: float
    duration: float


class Walk(Component, Protocol):
    """
    Movement informations
    """
    walk_speed: float
    run_speed: float


class CameraFollow(Component, Protocol):
    """
    Tag an entity to be followed by camera
    """
    deadzone: Rect
    damping: float


class EntityCollision(Component, Protocol):
    """
    Collision box with other entities
    """
    collided_entities: list[tuple[int, tuple[bool, bool, bool, bool]]]
    left: bool
    right: bool
    top: bool
    bottom: bool
    topleft: bool
    topright: bool
    bottomleft: bool
    bottomright: bool
    colliding: bool
    def reset(self: Self) -> None:
        """
        Reset all collisions to False
        """


class MapCollision(Component, Protocol):
    """
    Collision box with Tilemap
    """
    left: bool
    right: bool
    top: bool
    bottom: bool
    topleft: bool
    topright: bool
    bottomleft: bool
    bottomright: bool
    colliding: bool
    def reset(self: Self) -> None:
        """
        Reset all collisions to False
        """


class CollisionAction(Component, Protocol):
    """
    Action called by Entity when on collision
    """
    action: Callable


# ----- ECS Engine protocols ----- #
class Engine(Protocol):
    """
    ECS Engine of the game
    This class handle only data objects. No graphics updates are here.
    This engine attach components to an entity id (eid) and gives access to it
    It also attach ecs systems and call them in the current level
    """
    _components: dict[int, dict[ComponentTypes, Component]]
    _entity_counter: int

    def reset(self) -> None:
        """
        Reset the Engine to prepare for a new Level
        """

    # Entity methods
    def new_entity(self) -> int:
        """
        Create a new entity id and return it
        """
        return -1

    def remove_entity(self, eid: int) -> None:
        """
        Removes an entity id of the engine
        """

    # Components methods
    def add_component(self, eid: int, ctype: ComponentTypes, overrides: dict) -> None:
        """
        Add a new component to the Entity with id eid and apply overrides on it
        """

    def get_component(self, eid: int, ctype: ComponentTypes) -> Optional[Component]:
        """
        Get component ctype from entity eid
        If entity eid don't have component ctype, return None
        """

    def remove_component(self, eid: int, ctype: ComponentTypes) -> None:
        """
        Remove component ctype of entity eid
        """

    def has_component(self, eid: int, ctype: ComponentTypes) -> bool:
        """
        Check if the entity eid has component ctype
        """

    def get_entities_with(self, *ctypes: ComponentTypes) -> Iterator[int]:
        """
        Return an iterator with all entities' eid having all ctypes components
        """

  # Update method to process ecs core engine
    def update(self, level: Level, dt: float) -> None:
        """
        Calculate a logic frame of the game
        """


####################################################################################################
# Level protocols                                                                                  #
####################################################################################################


# ----- Level Tilemap protocols ----- #
class TileData(Protocol):
    """
    Data of a Tile
    """
    graphics: tuple[Surface, ...]
    autotilebitmask: str
    hitbox: int
    animation_delay: float
    animation_frame: int
    animation_time_left: float
    blueprint: dict


class TilesetData(Protocol):
    """
    Data of a Tileset
    """
    name: str
    tiles: list[TileData]
    tile_size: int

    def update_animation(self, dt: float) -> None:
        """
        Update all tiles animation
        """

    @classmethod
    def load(cls, name: str) -> Self:
        """
        Load Tileset data from name
        """


class ParallaxData(Protocol):
    """
    Data of a Parallax
    """
    blueprint: dict
    @classmethod
    def load(cls, arg: str) -> Self:
        """
        Load Parallax layer
        """


class TilemapData(Protocol):
    """
    Data of a Tilemap
    """
    name: str
    width: int
    height: int
    tileset: TilesetData
    bgm: str
    bgs: str
    grid: list[list[int]]
    entities: list[dict]
    parallax: list[ParallaxData]

    @classmethod
    def load(cls, name: str) -> Self:
        """
        Load Tilemap data from name
        """

    def get_tile_neighbors(self: Self, x: int, y: int) -> list[bool]:
        """
        Return a list of the neighbors connections to the tile in (x, y)
        the order of tiles are:
        (-1, -1), (0, -1), (1, -1),
        (-1,  0),          (1,  0),
        (-1,  1), (0,  1), (1,  1)
        If we are in border it return True by default
        """

    def colliderect(self: Self, rect: Rect) -> bool:
        """
        Check if a Rect overlap a colliding tile
        """

    def touch(self: Self, rect: Rect) -> dict[str, bool]:
        """
        Test if a rect is touching a colliding tile in all 4 directions
        """


# ----- Level Entity protocols ----- #
class EntityBlueprint(Protocol):
    """
    Instance linked to blueprint
    """
    name: str
    components: list[str]
    overrides: dict[str, dict]


class EntityData(Protocol):
    """
    Data of an Entity
    """
    eid: int
    engine: Engine
    sprite: Surface
    blueprint: dict


class Player(EntityData, Protocol):
    """
    Instance of the player
    """
    velocity: Velocity
    state: State
    jump_infos: Jump
    walk_infos: Walk
    xdir: XDirection


# ----- Level Components protocols ----- #
class Camera(Protocol):
    """
    Camera of the Level
    """
    pos: Vector2
    size: tuple[int, int]
    rect: Rect
    top: float
    bottom: float
    left: float
    right: float
    center: Vector2
    centerx: float
    centery: float
    topleft: Vector2
    topright: Vector2
    bottomleft: Vector2
    bottomright: Vector2
    width: float
    height: float


# ----- Level protocols ----- #
class Level(Protocol):
    """
    Level temp protocol TODO
    """
    name: str
    engine: Engine
    tilemap: TilemapData
    camera: Camera
    player: Player
    systems: list[str]
    entities: list[EntityData]


####################################################################################################
# Rendering protocols                                                                              #
####################################################################################################


# ----- Tilemap Rendering protocols ----- #
class TileRenderer(Protocol):
    """
    Renderer for tiles applying autotilling
    """
    @classmethod
    def render(cls, tdata: TileData, neighbors: list[bool]) -> Surface:
        """
        Render a tile according to neighborhood
        """


class FixedParallaxRenderer(Protocol):
    """
    Renderer for Fixed Parallax
    """
    @classmethod
    def render(cls, pdata: ParallaxData) -> Surface:
        """
        Render the parallax
        """


class TilemapParallaxRenderer(Protocol):
    """
    Renderer for Tilemap Parallax
    """
    @classmethod
    def render(cls, pdata: ParallaxData) -> Surface:
        """
        Render the Parallax
        """


class TilemapRenderer(Protocol):
    """
    Renderer of Tilemap
    """
    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear Renderer cache
        """

    @classmethod
    def render(cls, tilemap: TilemapData, surface: Surface, camera) -> None:
        """
        Render the tilemap on surface
        """
