# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
ECS libs Engine
version : 1.1
____________________________________________________________________________________________________
Contains engine of our game ecs
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from __future__ import annotations
from typing import Iterator, Callable, Optional, TYPE_CHECKING, TypeAlias

# import header
from ..header import ComponentTypes as C

# import config
from .. import config

# import logger
from .. import logger

# import components from ecs_core
from . import components

# import systems from ecs_core
from . import systems

if TYPE_CHECKING:
    from ..level.level import Level

# ----- Type Aliases ----- #
SystemFunc: TypeAlias = Callable[..., None]


# ----- Engine ----- #
class Engine:
    """
    ECS Engine of the game
    This class handle only data objects. No graphics updates are here.
    This engine attach components to an entity id (eid) and gives access to it
    It also attach ecs systems and call them in the current level
    """
    def __init__(self) -> None:
        self._components: dict[int, dict[C, components.Component]] = {}
        self._entity_counter = 0

    def reset(self) -> None:
        """
        Reset the Engine to prepare for a new Level
        """
        self._components.clear()
        self._entity_counter = 0

    # Entity methods
    def new_entity(self) -> int:
        """
        Create a new entity id and return it
        """
        eid = self._entity_counter
        self._components[eid] = {}
        self._entity_counter += 1
        return eid

    def remove_entity(self, eid: int) -> None:
        """
        Removes an entity id of the engine
        """
        self._components.pop(eid, None)

    # Components methods
    def add_component(self, eid: int, ctype: C, overrides: dict) -> None:
        """
        Add a new component to the Entity with id eid and apply overrides on it
        """
        cls: type[components.Component] = components.__dict__.get(ctype.value)
        if not cls:
            raise ValueError(f"Missing component {ctype.value}. Doesn't exist")
        if not eid in self._components:
            raise ValueError(f"Entity with id {eid} doesn't exists")
        self._components[eid][ctype] = cls.from_dict(overrides)

    def get_component(self, eid: int, ctype: C) -> Optional[components.Component]:
        """
        Get component ctype from entity eid
        If entity eid don't have component ctype, return None
        """
        return self._components[eid].get(ctype)

    def remove_component(self, eid: int, ctype: C) -> None:
        """
        Remove component ctype of entity eid
        """
        self._components[eid].pop(ctype, None)

    def has_component(self, eid: int, ctype: C) -> bool:
        """
        Check if the entity eid has component ctype
        """
        return ctype in self._components[eid]

    def get_entities_with(self, *ctypes: C) -> Iterator[int]:
        """
        Return an iterator with all entities' eid having all ctypes components
        """
        for eid, comps in self._components.items():
            if all(c in comps for c in ctypes):
                yield eid

  # Update method to process ecs core engine
    def update(self, level: Level, dt: float) -> None:
        """
        Calculate a logic frame of the game
        """
        for system_name in config.SYSTEM_PRIORITY:
            system_func: SystemFunc = systems.__dict__.get(system_name)
            if system_func and system_name in level.systems:
                try:
                    system_func(self, level, dt)
                    logger.debug(f"System [{system_name}] executed successfully")
                except AttributeError as e:
                    logger.warning(f"System [{system_name}] failed due to missing attribute: {e}")
                except TypeError as e:
                    logger.warning(f"System [{system_name}] failed due to type error: {e}")
                except ZeroDivisionError as e:
                    logger.warning(f"System [{system_name}] failed due to division by zero: {e}")
                except ValueError as e:
                    logger.warning(f"System [{system_name}] failed due to invalid value: {e}")

            elif system_name in level.systems:
                logger.warning(f"System [{system_name}] listed in level"
                               " but missing in systems module")
        logger.debug("Engine update successful")
