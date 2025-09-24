#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
entity lib
version : 1.0
____________________________________________________________________________________________________
Contains all objects for entities
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from dataclasses import dataclass
from pygame import Surface

# import needed header
from ..header import (
    Engine,
    Velocity,
    State,
    Jump,
    Walk,
    XDirection,
    ComponentTypes as C
)


# ----- EntityBlueprint ----- #
@dataclass
class EntityBlueprint:
    """
    Instance linked to blueprint
    """
    name: str
    components: list[str]
    overrides: dict[str, dict]


# ----- EntityData ----- #
@dataclass
class EntityData:
    """
    Data of an Entity
    """
    eid: int
    engine: Engine
    sprite: Surface
    overrides: dict[str, dict]


# ----- PlayerData ----- #
@dataclass
class Player(EntityData):
    """
    Instance of the player
    """
    eid: int
    engine: Engine
    sprite: Surface
    overrides: dict[str, dict]

    @property
    def velocity(self) -> Velocity:
        """
        Velocity of the player
        """
        return self.engine.get_component(self.eid, C.VELOCITY)

    @property
    def state(self) -> State:
        """
        State of the player
        """
        return self.engine.get_component(self.eid, C.STATE)

    @property
    def jump_infos(self) -> Jump:
        """
        Jump infos of the player
        """
        return self.engine.get_component(self.eid, C.JUMP)

    @property
    def walk_infos(self) -> Walk:
        """
        Walk infos of the player
        """
        return self.engine.get_component(self.eid, C.WALK)

    @property
    def xdir(self) -> XDirection:
        """
        X direction of the player
        """
        return self.engine.get_component(self.eid, C.XDIRECTION)
