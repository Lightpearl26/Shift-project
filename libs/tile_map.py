# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
tileMap lib
version : 1.0
____________________________________________________________________________________________________
Contains all objects and systems for tilmap
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""
# import external modules
from typing import Optional
from dataclasses import dataclass
from os.path import join
from json import load
from pygame import Surface, Rect, Vector2, SRCALPHA
from pygame.image import load as img_load

# import modules of the package
from . import logger


# --------------------------
# | Constants              |
# --------------------------
TILESET_FOLDER: str = join("assets", "Tilesets")
TILEMAP_FOLDER: str = join("assets", "Tilemaps")
AUTOTILEBITMASKS: dict[str, dict[str, list[tuple[int, int]]]] = {
    "field": {
        "TL": [(0, 0), (0, 2), (1, 1), (1, 0), (1, 2)],
        "TR": [(0, 0), (0, 1), (1, 2), (1, 0), (0, 2)],
        "BR": [(0, 0), (1, 1), (0, 2), (1, 0), (0, 1)],
        "BL": [(0, 0), (1, 2), (0, 1), (1, 0), (1, 1)],
    },
    "wall": {
        "TL": [(0, 0), (0, 1), (1, 0), (1, 1), (1, 1)],
        "TR": [(1, 0), (0, 0), (1, 1), (0, 1), (0, 1)],
        "BR": [(1, 1), (1, 0), (0, 1), (0, 0), (0, 0)],
        "BL": [(0, 1), (1, 1), (0, 0), (1, 0), (1, 0)]
    },
    "fall": {
        "TL": [(0, 0), (0, 0), (0, 1), (0, 1), (0, 1)],
        "TR": [(0, 1), (0, 0), (0, 1), (0, 0), (0, 0)],
        "BR": [(0, 1), (0, 1), (0, 0), (0, 0), (0, 0)],
        "BL": [(0, 0), (0, 1), (0, 0), (0, 1), (0, 1)]
    },
    "unique": {
        "TL": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "TR": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "BR": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "BL": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
    }
}
SHAPES: dict[str, tuple[int, int]] = {
    "field": (2, 3),
    "wall": (2, 2),
    "fall": (2, 1),
    "unique": (1, 1)
}


# --------------------------
# | TileData               |
# --------------------------
@dataclass
class TileData:
    graphics: list[Surface]
    autotilebitmask: str = "unique"
    size: int = 48
    hitbox: int = 0
    animation_delay: float = 0.333
    animation_frame: int = 0
    animation_time_left: float = 0.0

# --------------------------
# | AutoTileRenderer       |
# --------------------------
class AutoTileRenderer:
    corner_neighbors: dict[str, tuple[int, int, int]] = {
        "TL": (1, 3, 0),
        "TR": (4, 1, 2),
        "BL": (3, 6, 5),
        "BR": (6, 4, 7)
    }
    corner_bitmask: dict[int, int] = {
        0b000: 0, # No neighbor
        0b001: 1, # top connexion
        0b010: 2, # left connexion
        0b011: 3, # top & left connexion
        0b100: 0,
        0b101: 1,
        0b110: 2,
        0b111: 4, # filled
    }

    def __init__(self) -> None:
        self._cache = {}

    def render(self, tdata: TileData, neighbors: list[int]) -> Surface:
        key = (id(tdata), tdata.animation_frame, tuple(neighbors))
        if key in self._cache:
            return self._cache[key]

        surf = Surface((tdata.size, tdata.size), SRCALPHA)

        for i, corner in enumerate(("TL","TR", "BL", "BR")):
            offsetx, offsety = tdata.size//2 * (i%2), tdata.size // 2 * (i//2)
            bitmask = sum(neighbors[b]<<j for j, b in enumerate(self.corner_neighbors[corner]))
            x, y = AUTOTILEBITMASKS[tdata.autotilebitmask][corner][self.corner_bitmask[bitmask]]
            corner_graphic = tdata.graphics[tdata.animation_frame].subsurface(
                Rect(x*tdata.size+offsetx, y*tdata.size+offsety, tdata.size//2, tdata.size//2)
            )
            surf.blit(corner_graphic, (offsetx, offsety))

        self._cache[key] = surf
        return surf.convert_alpha()


# --------------------------
# | TilesetData            |
# --------------------------
@dataclass
class TilesetData:
    name: str
    tiles: list[TileData]
    tile_size: int
    renderer: AutoTileRenderer = AutoTileRenderer()

    @classmethod
    def load(cls, name: str):
        tiles = []
        folder = join(TILESET_FOLDER, name)
        graphics_folder = join(folder, "graphics")

        with open(join(folder, "data.json"), "r", encoding="utf-8") as file:
            data = load(file)

            tsize = data.get("tile_size")
            images = {
                f: img_load(join(graphics_folder, f)).convert_alpha()
                for f in data.get("files")
            }
            for tile in data.get("tiles"):
                graphics = []
                for frame in tile.get("frames"):
                    x = frame[0]*tsize
                    y = frame[1]*tsize
                    width = SHAPES[tile.get("type")][0]*tsize
                    height = SHAPES[tile.get("type")][1]*tsize
                    graphics.append(
                        images[tile.get("file")].subsurface(Rect(x, y, width, height))
                    )
                tile_data = TileData(graphics)
                tile_data.size = tsize
                tile_data.hitbox = tile.get("hitbox")
                tile_data.autotilebitmask = tile.get("type")
                tiles.append(tile_data)

        logger.debug(f"Tileset [{name}] loaded")

        return cls(name, tiles, tsize)


@dataclass
class Parallax:
    data: dict

    def __init__(self, data) -> None:
        self.data = data
        self._cache: Optional[Surface] | Optional[TileMap] = None

    def render(self) -> Surface:
        """
        Renders the parallax
        """
        if self.data["type"] == "img":
            # Fix image
            if not self._cache:
                self._cache = img_load(self.data["path"]).convert_alpha()
            return self._cache
        else:
            # Tilemap
            if not self._cache:
                self._cache = TileMap.load(self.data["name"])
            tm = self._cache
            tm_w = tm.width*tm.tileset.tile_size
            tm_h = tm.height*tm.tileset.tile_size
            surface = Surface((tm_w, tm_h), SRCALPHA)
            for y, row in enumerate(tm.grid):
                for x, tid in enumerate(row):
                    if tid == -1:
                        continue
                    tdata = tm.tileset.tiles[tid]
                    neighboorhood = tm.get_tile_neighbors(x, y)
                    tsurf = tm.tileset.renderer.render(tdata, neighboorhood)
                    surface.blit(tsurf, (x*tm.tileset.tile_size, y*tm.tileset.tile_size))

            return surface


# --------------------------
# | TileMap                |
# --------------------------
@dataclass
class TileMap:
    name: str
    width: int
    height: int
    tileset: TilesetData
    bgm: str
    bgs: str
    grid: list[list[int]]
    entities: list
    parallax: list[Parallax]

    @classmethod
    def load(cls, name: str):
        with open(join(TILEMAP_FOLDER, f"{name}.json"), "r", encoding="utf-8") as file:
            data = load(file)
            width, height = data.get("size")
            bgm = data.get("bgm")
            bgs = data.get("bgs")
            tileset = TilesetData.load(data.get("tileset"))
            grid = data.get("tiles")
            entities = data.get("entities", [])
            parallax = [Parallax(d) for d in data.get("parallax", [])]

        logger.debug(f"Map [{name}] loaded")

        return cls(name, width, height, tileset, bgm, bgs, grid, entities, parallax)

    def get_tile_neighbors(self, x: int, y: int) -> list[int]:
        offsets = [(-1, -1), (0, -1), (1, -1),
                   (-1,  0),          (1,  0),
                   (-1,  1), (0,  1), (1,  1)]
        neighbors = []
        for dx, dy in offsets:
            tx, ty = x + dx, y + dy
            if 0 <= tx < self.width and 0 <= ty < self.height:
                neighbors.append(int(self.grid[ty][tx] == self.grid[y][x]))
            else:
                neighbors.append(1)
        return neighbors


# --------------------------
# | TileMapRenderer        |
# --------------------------
class TileMapRenderer:
    def render_parallax(self, tilemap: TileMap, parallax: Parallax, surface: Surface, camera) -> None:
        cam_rect = camera.rect
        map_w = tilemap.width*tilemap.tileset.tile_size
        map_h = tilemap.height*tilemap.tileset.tile_size
        p_surf = parallax.render()
        p_w, p_h = p_surf.get_size()

        offset = Vector2(0, 0)
        
        if map_w > cam_rect.width:
            offset.x = -(p_w-cam_rect.width) * (cam_rect.left / (map_w - cam_rect.width))
        else:
            # centrer le parallax si map plus petite que la caméra
            offset.x = (cam_rect.width-p_w)/2

        if map_h > cam_rect.height:
            offset.y = -(p_h-cam_rect.height) * (cam_rect.top / (map_h - cam_rect.height))
        else:
            offset.y = (cam_rect.height-p_h)/2

        surface.blit(p_surf, (int(offset.x), int(offset.y)))

    def render(self, tilemap: TileMap, surface: Surface, camera) -> None:
        # Render parallaxes
        for parallax in tilemap.parallax:
            self.render_parallax(tilemap, parallax, surface, camera)

        # Render main tilemap
        cam_rect = camera.rect
        for y, row in enumerate(tilemap.grid):
            for x, tid in enumerate(row):
                if tid == -1:
                    continue
                tdata = tilemap.tileset.tiles[tid]
                posx = x * tdata.size - cam_rect.left
                posy = y * tdata.size - cam_rect.top
                tile_rect = Rect(posx, posy, tdata.size, tdata.size)
                if tile_rect.colliderect(surface.get_rect()):
                    neighbors = tilemap.get_tile_neighbors(x, y)
                    tile_surf = tilemap.tileset.renderer.render(tdata, neighbors)
                    surface.blit(tile_surf, (posx, posy))
