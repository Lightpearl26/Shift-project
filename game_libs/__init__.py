#-*- coding: utf-8 -*-

"""
SHIFT PROJECT game_libs
____________________________________________________________________________________________________
game_libs
version : 1.0
____________________________________________________________________________________________________
This Package contains all game libs
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from . import config

from .logger import Logger, LoggerInterrupt

# create main logger of the system
logger: Logger = Logger()

from . import (
    header,
    ecs_core,
    level,
    rendering,
    assets_cache,
    assets_registry
)
