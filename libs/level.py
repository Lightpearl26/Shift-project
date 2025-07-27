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
from pygame import Rect
from json import load, dump
from os import listdir
from os.path import join, isfile, splitext

# import modules from package
from . import tileMap
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
COMPONENTS: dict[str, type] = {
    name: obj
    for name, obj in ecsC.__dict__.items()
    if isinstance(obj, type) and issubclass(obj, ecsC.ComponentBase)
}
BLUEPRINTS_FOLDER = join("assets", "blueprints")


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
        self._entity_loader: EntityLoader = EntityLoader(BLUEPRINTS_FOLDER)
        self.camera = ecsC.Camera(Rect(0, 0, 0, 0))
        self.tilemap: tileMap.TileMap = tileMap.TileMap.load("empty")
        self.tilemap_renderer: tileMap.TileMapRenderer = tileMap.TileMapRenderer()

    def load_tilemap(self, name: str) -> None:
        self.tilemap = tileMap.TileMap.load(name)

    def create_entity(self) -> int:
        """
        create a new entity and returns its id
        """
        eid = self._next_eid
        self._entities.add(eid)
        self._next_eid += 1
        self._components[eid] = {}
        return eid
    
    def new_entity(self, name: str, overrides: dict[str, dict] | None = None) -> int:
        eid = self._entity_loader.load(self, name)
        if eid == -1:
            return -1

        if overrides:
            for comp_name, comp_data in overrides.items():
                comp_cls = COMPONENTS.get(comp_name)
                if not comp_cls:
                    logger.warning(f"Unknown override component '{comp_name}'")
                    continue
                try:
                    component = comp_cls.from_dict(comp_data)
                    self.add_component(eid, component)
                except Exception as e:
                    logger.error(f"Failed to override component '{comp_name}': {e}")
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

    def has_component(self, eid: int, component_type: type) -> bool:
        return component_type in self._components[eid]

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

    def update(self, dt: float) -> None:
        #self.tilemap.update(dt)
        for system in self._systems:
            system(self, dt)


# --------------------------
# | EntityLoader           |
# --------------------------
class EntityLoader:
    """
    EntityLoader object

    This object load blueprints of entities and translate it to engine
    """
    def __init__(self, blueprints_folder: str) -> None:
        self._folder: str = blueprints_folder
        self._blueprints: dict[str, dict] = {}
        self.load_all()
        logger.info("Loading all entities blueprint successfully")

    def load_all(self) -> None:
        for file in listdir(self._folder):
            path = join(self._folder, file)
            if isfile(path) and file.endswith(".json"):
                try:
                    with open(path, "r") as f:
                        data = load(f)
                    name = splitext(file)[0]
                    self._blueprints[name] = data
                except Exception as e:
                    logger.error(f"Error loading {file}: {e}")

    def load(self, engine: Engine, name: str) -> int:
        entity_data = self._blueprints.get(name)
        if not entity_data:
            logger.error(f"Blueprint '{name}' not found.")
            return -1

        eid = engine.create_entity()
        for comp_name, comp_data in entity_data.items():
            comp_cls = COMPONENTS.get(comp_name)
            if not comp_cls:
                logger.warning(f"Unknown component '{comp_name}' in blueprint '{name}'")
                continue
            try:
                component = comp_cls.from_dict(comp_data)
                engine.add_component(eid, component)
            except Exception as e:
                logger.error(f"Failed to parse component '{comp_name}': {e}")
        return eid
