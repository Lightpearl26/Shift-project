# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
Config lib
version : 1.1
____________________________________________________________________________________________________
Contains config of all default constants of the game
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external module
from os.path import join
from pygame import FULLSCREEN

# ----- System constants ----- #
LOG_DEBUG: bool = False
SCREEN_SIZE: tuple[int, int] = (1920, 1080) # px²
SCREEN_FLAGS: int = FULLSCREEN
TPS_MAX: int = 20 # max ticks per second

# ----- Jumping constants ----- #
JUMP_STRENGTH: float = 2.8e5 # N
JUMP_DURATION: float = 0.2 # s

# ----- Wallsticking constants ----- #
WALLSTICK_DURATION: float = 0.5 # s

# ----- Movement constants ----- #
WALK_SPEED: float = 1500.0 # px/s
RUN_SPEED: float = 2000.0 # px/s

# ----- Camera constants ----- #
CAMERA_DAMPING: float = 8.0
CAMERA_SIZE: tuple[int, int] = (1920, 1080) # px²

# ----- Physics constants ----- #
DRAG_BASE: float = 0.005 # kg/s
GRAVITY: float = 960 # px/s²

# ----- Path constants ----- #
TILESET_GRAPHICS_FOLDER: str = join("assets", "tilesets", "graphics")
TILESET_DATA_FOLDER: str = join("assets", "tilesets", "data")
TILEMAP_FOLDER: str = join("assets", "tilemaps")
BLUEPRINTS_FOLDER: str = join("assets", "blueprints")
LEVELS_FOLDER: str = join("assets", "levels")

# ----- Tilemap constants ----- #
AUTOTILING_SHAPES: dict[str, tuple[int, int]] = {
    "field": (2, 3),
    "wall": (2, 2),
    "fall": (2, 1),
    "unique": (1, 1)
}

# ----- Engine constants ----- #
SYSTEM_PRIORITY: list[str] = [
    "tile_animation_system",
    "ai_system",
    "player_control_system",
    "drag_system",
    "gravity_system",
    "jump_system",
    "movement_system",
    "move_prediction_system",
    "map_collision_system",
    "sync_hitbox_system",
    "camera_system"
]
