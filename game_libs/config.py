# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
game_libs.config
version : 1.1
____________________________________________________________________________________________________
Contains config of all default constants of the game
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external module
from os.path import join
from pygame import FULLSCREEN
from pygame import (
    K_z,
    K_UP,
    K_s,
    K_DOWN,
    K_q,
    K_LEFT,
    K_d,
    K_RIGHT,
    K_SPACE,
    K_LSHIFT,
    K_RSHIFT,
    K_ESCAPE,
    K_p
)

# ----- System constants ----- #
LOG_DEBUG: bool = False
SCREEN_SIZE: tuple[int, int] = (1920, 1080) # px²
SCREEN_FLAGS: int = FULLSCREEN
TPS_MAX: int = 20 # max ticks per second
UDP_LISTENING_PORT: int = 2802
SERVER_LOG_FOLDER: str = join("cache", "server", "logs")
PLAYER_TIMEOUT: float = 60.0 # seconds

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
SOUNDS_FOLDER: str = join("assets", "audio", "sounds")
MUSICS_FOLDER: str = join("assets", "audio", "musics")
VIDEOS_FOLDER: str = join("assets", "video")
FONT_FOLDER: str = join("assets", "fonts")

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

# ----- Key constants ----- #
KEYS_UP: set[int] = {K_z, K_UP}
KEYS_DOWN: set[int] = {K_s, K_DOWN}
KEYS_LEFT: set[int] = {K_q, K_LEFT}
KEYS_RIGHT: set[int] = {K_d, K_RIGHT}
KEYS_JUMP: set[int] = {K_SPACE} | KEYS_UP
KEYS_SPRINT: set[int] = {K_LSHIFT, K_RSHIFT}
KEYS_PAUSE: set[int] = {K_ESCAPE, K_p}
