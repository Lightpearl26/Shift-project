#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
tileMap lib
version : 1.0
____________________________________________________________________________________________________
Contains all objects for tilmap
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import  external modules
from __future__ import annotations
from typing import Optional
from dataclasses import dataclass
from pygame import Surface, Rect

# import needed protocols
from ..header import ParallaxData

# create constants of the module
SHAPES: dict[str, tuple[int, int]] = {
    "field": (2, 3),
    "wall": (2, 2),
    "fall": (2, 1),
    "unique": (1, 1)
}


# ----- TileData ----- #
@dataclass
class TileData:
    """
    Data of a tile
    """
    graphics: tuple[Surface, ...]
    autotilebitmask: str = "unique"
    hitbox: int = 0
    size: int = 48
    animation_delay: float = 0.333 #s
    animation_frame: int = 0
    animation_time_left: float = 0.0 #s
    blueprint: Optional[dict] = None

# ----- TilesetData ----- #
@dataclass
class TilesetData:
    """
    Data of a Tileset
    """
    name: str
    tiles: list[TileData]
    tile_size: int

    def update_animation(self, dt: float) -> None:
        """
        update tiles animations
        """
        tile: TileData
        for tile in self.tiles:
            tile.animation_time_left -= dt
            if tile.animation_time_left < 0:
                tile.animation_time_left += tile.animation_delay
                tile.animation_frame = (tile.animation_frame + 1) % len(tile.graphics)


# ----- ParallaxData ----- #
@dataclass
class FixedParallaxData:
    """
    Data of a Parallax
    """
    img: Surface
    blueprint: Optional[dict] = None


@dataclass
class TilemapParallaxData:
    """
    Data of a Parallax
    """
    tm: TilemapData
    animated: bool
    blueprint: Optional[dict] = None


# ----- TilemapData ----- #
@dataclass
class TilemapData:
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

    def _hitbox_at(self, x: int, y: int) -> bool:
        """
        Test if the tile (x, y) has hitbox
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            tid = self.grid[y][x]
            return tid != -1 and self.tileset.tiles[tid].hitbox
        return False

    def get_tile_neighbors(self, x: int, y: int) -> list[bool]:
        """
        Return a list of the neighbors connections to the tile in (x, y)
        the order of tiles are:
        (-1, -1), (0, -1), (1, -1),
        (-1,  0),          (1,  0),
        (-1,  1), (0,  1), (1,  1)
        If we are in border it return True by default
        """
        offset = [(-1, -1), (0, -1), (1, -1),
                  (-1,  0),          (1,  0),
                  (-1,  1), (0,  1), (1,  1)]
        neighbors = []
        for dx, dy in offset:
            tx, ty = x+dx, y+dy
            if 0 <= tx < self.width and 0 <= ty < self.height:
                neighbors.append(self.grid[ty][tx] == self.grid[y][x])
            else:
                neighbors.append(True)
        return neighbors

    def colliderect(self, rect: Rect) -> bool:
        """
        Check if a Rect overlap a colliding tile
        """
        tile_size = self.tileset.tile_size
        range_x = range(max(0, rect.left//tile_size-1), min(rect.right//tile_size+1, self.width))
        range_y = range(max(0, rect.top//tile_size-1), min(rect.bottom//tile_size+1, self.height))
        for x in range_x:
            for y in range_y:
                tid = self.grid[y][x]
                if tid != -1 and self.tileset.tiles[tid].hitbox:
                    tile_rect = Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    if tile_rect.colliderect(rect):
                        return True
        return False

    def touch(self, rect: Rect) -> dict[str, bool]:
        """
        Test if a rect is touching a colliding tile in all 4 directions
        """
        tile_size = self.tileset.tile_size
        touching = dict.fromkeys(["top", "bottom", "left", "right"], False)

        tile_range_x = range(max(0, rect.left // tile_size),
                            min((rect.right-1) // tile_size + 1, self.width))
        tile_range_y = range(max(0, rect.top // tile_size),
                            min((rect.bottom-1) // tile_size + 1, self.height))

        touching["left"] = any(self._hitbox_at((rect.left-1) // tile_size, y) for y in tile_range_y)
        touching["right"] = any(self._hitbox_at((rect.right) // tile_size, y) for y in tile_range_y)
        touching["top"] = any(self._hitbox_at(x, (rect.top-1) // tile_size) for x in tile_range_x)
        touching["bottom"] = any(self._hitbox_at(x, (rect.bottom) // tile_size) for x in tile_range_x)

        return touching
