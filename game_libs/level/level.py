#-*- coding: utf-8 -*-

"""
SHIFT PROJECT game_libs
____________________________________________________________________________________________________
Level lib
version : 1.0
____________________________________________________________________________________________________
This Lib contains all Level system of the game
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from __future__ import annotations
from dataclasses import dataclass

# import needed headers
from ..header import Engine

# import submodules of the package
from .entity import EntityData, Player
from .tilemap import TilemapData
from .components import Camera


# ----- Level ----- #
@dataclass
class Level:
    """
    Instance of a Level
    """
    name: str
    engine: Engine
    tilemap: TilemapData
    camera: Camera
    player: Player
    systems: list[str]
    entities: list[EntityData]
