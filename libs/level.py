# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
Level lib
version : 1.0
____________________________________________________________________________________________________
Contains setup for a level of the game
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# get main logger of the game
from . import logger

# import external module
from typing import Callable, Any, Generator

# import modules from package
from . import ecsComponents as ecsC
from . import ecsSystems as ecsS
from . import ecsAI

# --------------------------
# | Constants              |
# --------------------------
SYSTEMS: dict[str, Callable] = {
    name: func
    for name, func in ecsS.__dict__.items()
    if callable(func) and not name.startswith("_")
}


# --------------------------
# | Engine                 |
# --------------------------
class Engine:
    """
    Engine object

    This object represent the engine of a level
    """
    def __init__(self) -> None:
        self._components: dict[int, dict[type, Any]] = {}
        self._entities: set[int] = set()
        self._systems: list[Callable] = []
        self._next_eid: int = 0
        self.tilemap: None = None

    def create_entity(self) -> int:
        """
        create a new entity and returns its id
        """
        eid = self._next_eid
        self._entities.add(eid)
        self._next_eid += 1
        self._components[eid] = {}
        return eid
    
    def remove_entity(self, eid: int) -> None:
        """
        Remove an entity from the engine
        """
        self._entities.discard(eid)
        self._components.pop(eid, None)
    
    def add_component(self, eid: int, component: Any) -> None:
        """
        Add a new component to entity with id eid
        """
        self._components[eid][type(component)] = component

    def get_component(self, eid: int, component_type: type) -> Any:
        """
        Get the specified component from entity with id eid
        """
        return self._components[eid].get(component_type)
    
    def get_entities_with(self, *component_types: type) -> Generator:
        """
        create a generator that gives all entities having component_types
        """
        for eid in self._entities:
            if all(ctype in self._components[eid] for ctype in component_types):
                yield eid

    def add_system(self, *systems: str) -> None:
        """
        Add a new system to our engine
        """
        for system in systems:
            self._systems.append(SYSTEMS[system])

    def update(self,dt: float) -> None:
        for system in self._systems:
            system(self, dt)