#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
tileMap renderer lib
version : 1.0
____________________________________________________________________________________________________
Contains all objects for tilmap rendering
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from __future__ import annotations
from pygame import Surface, Rect, Vector2, SRCALPHA

# import tilemap components
from ..level.tilemap import (
    TileData,
    FixedParallaxData,
    TilemapParallaxData,
    TilemapData,
    ParallaxData
)
from ..level.components import Camera

# ----- Constants of the module ----- #
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
        "TL": [(0, 0), (0, 0), (1, 0), (1, 0), (1, 0)],
        "TR": [(1, 0), (0, 0), (1, 0), (0, 0), (0, 0)],
        "BR": [(1, 0), (1, 0), (0, 0), (0, 0), (0, 0)],
        "BL": [(0, 0), (1, 0), (0, 0), (1, 0), (1, 0)]
    },
    "unique": {
        "TL": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "TR": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "BR": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "BL": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
    }
}


# ----- TileRenderer ----- #
class TileRenderer:
    """
    Renderer for tiles applying autotiling
    """
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
    _cache: dict[tuple[int, int, tuple[bool, ...]], Surface] = {}

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear Renderer cache
        """
        cls._cache.clear()

    @classmethod
    def render(cls, tdata: TileData, neighbors: list[bool]) -> Surface:
        """
        Render a tile according to neighborhood
        """
        key = (id(tdata), tdata.animation_frame, tuple(neighbors))

        if key in cls._cache:
            return cls._cache[key]

        surf = Surface((tdata.size, tdata.size), SRCALPHA)

        for i, corner in enumerate(("TL", "TR", "BL", "BR")):
            offsetx, offsety = tdata.size//2 * (i%2), tdata.size // 2 * (i//2)

            bitmask = sum(neighbors[b]<<j for j, b in enumerate(cls.corner_neighbors[corner]))
            x, y = AUTOTILEBITMASKS[tdata.autotilebitmask][corner][cls.corner_bitmask[bitmask]]
            corner_graphic = tdata.graphics[tdata.animation_frame].subsurface(
                Rect(x*tdata.size+offsetx, y*tdata.size+offsety, tdata.size//2, tdata.size//2)
            )
            surf.blit(corner_graphic, (offsetx, offsety))

        cls._cache[key] = surf
        return surf

# ----- ParallaxRenderers ----- #
class FixedParallaxRenderer:
    """
    Renderer for Fixed Parallax
    """
    @classmethod
    def render(cls, pdata: FixedParallaxData) -> Surface:
        """
        Render the parallax
        """
        return pdata.img


class TilemapParallaxRenderer:
    """
    Renderer for Tilemap Parallax
    """
    _cache: dict[str, Surface] = {}

    @classmethod
    def render(cls, pdata: TilemapParallaxData) -> Surface:
        """
        Render the Parallax
        """
        if not pdata.animated and pdata.tm.name in cls._cache:
            return cls._cache[pdata.tm.name]

        surf = Surface(
            (
                pdata.tm.width*pdata.tm.tileset.tile_size,
                pdata.tm.height*pdata.tm.tileset.tile_size
            ),
            SRCALPHA
        )
        for y, row in enumerate(pdata.tm.grid):
            for x, tid in enumerate(row):
                if tid != -1:
                    tdata = pdata.tm.tileset.tiles[tid]
                    neighbors = pdata.tm.get_tile_neighbors(x, y)
                    surf.blit(
                        TileRenderer.render(tdata, neighbors),
                        Vector2(x, y)*pdata.tm.tileset.tile_size
                    )

        if not pdata.animated:
            cls._cache[pdata.tm.name] = surf

        return surf


# ----- TilemapRenderer ----- #
class TilemapRenderer:
    """
    Renderer of Tilemap
    """
    _neighbors_cache: dict[tuple[int, int], tuple[bool, ...]] = {}
    _last_surface: Surface | None = None
    _last_camera_pos: Vector2 | None = None
    _animated_tiles: list[tuple[int, int]] = []

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear Renderer cache
        """
        cls._neighbors_cache.clear()
        cls._animated_tiles.clear()
        cls._last_surface = None
        cls._last_camera_pos = None

    @classmethod
    def _render_parallax(cls,
                         tilemap: TilemapData,
                         parallax: ParallaxData,
                         surface: Surface,
                         camera: Camera) -> None:
        """
        Render the parallax on the surface
        """
        cam_rect = camera.rect
        map_w = tilemap.width*tilemap.tileset.tile_size
        map_h = tilemap.height*tilemap.tileset.tile_size
        if isinstance(parallax, FixedParallaxData):
            p_surf = FixedParallaxRenderer.render(parallax)
        else:
            p_surf = TilemapParallaxRenderer.render(parallax)
        p_w, p_h = p_surf.get_size()

        offset = Vector2(0, 0)

        if map_w > cam_rect.width:
            offset.x = -(p_w-cam_rect.width) * (cam_rect.left / (map_w - cam_rect.width))
        else:
            # centrer le parallax si map plus petite que la caméra
            offset.x = (map_w - p_w) / 2 + (cam_rect.width - map_w) / 2

        if map_h > cam_rect.height:
            offset.y = -(p_h-cam_rect.height) * (cam_rect.top / (map_h - cam_rect.height))
        else:
            offset.y = (map_h - p_h) / 2 + (cam_rect.height - map_h) / 2

        if cam_rect.width >= map_w and cam_rect.height >= map_h:
            area = Rect((p_w - map_w) // 2, (p_h - map_h) // 2, map_w, map_h)
            dest = ((cam_rect.width - map_w) // 2, (cam_rect.height - map_h) // 2)
            surface.blit(p_surf, dest, area=area)
        else:
            surface.blit(p_surf, offset)

    @classmethod
    def _redraw_full(cls, tilemap: TilemapData, camera: Camera) -> None:
        """
        Redraw full tilemap
        """
        cam_rect = camera.rect
        tile_size = tilemap.tileset.tile_size

        cls._last_surface.fill((0, 0, 0, 0))
        cls._animated_tiles.clear()

        # get visible boundaries
        range_x = range(cam_rect.left//tile_size, min(cam_rect.right//tile_size+1, tilemap.width))
        range_y = range(cam_rect.top//tile_size, min(cam_rect.bottom//tile_size+1, tilemap.height))

        tiles_drawn = 0
        for y in range_y:
            for x in range_x:
                tid = tilemap.grid[y][x]

                if tid == -1:
                    continue

                tdata = tilemap.tileset.tiles[tid]
                pos = Vector2(x, y)*tile_size - Vector2(cam_rect.topleft)

                if (x, y) not in cls._neighbors_cache:
                    cls._neighbors_cache[(x, y)] = tilemap.get_tile_neighbors(x, y)
                neighbors = cls._neighbors_cache[(x, y)]

                tile_surf = TileRenderer.render(tdata, neighbors)
                cls._last_surface.blit(tile_surf, pos)
                tiles_drawn += 1

                # check if tile is animated
                if len(tdata.graphics) > 1:
                    cls._animated_tiles.append((x, y))

    @classmethod
    def _redraw_dirty(cls, tilemap: TilemapData, camera: Camera) -> None:
        """
        Redraw animated tiles of tilemap
        """
        cam_rect = camera.rect
        tile_size = tilemap.tileset.tile_size

        for (x, y) in cls._animated_tiles:
            tid = tilemap.grid[y][x] # can't be -1

            tdata = tilemap.tileset.tiles[tid]
            pos = Vector2(x, y)*tile_size - Vector2(cam_rect.topleft)

            neighbors = cls._neighbors_cache[(x, y)] # can't be None
            tile_surf = TileRenderer.render(tdata, neighbors)

            cls._last_surface.blit(tile_surf, pos)

    @classmethod
    def render(cls, tilemap: TilemapData, surface: Surface, camera_interp: Camera) -> None:
        """
        Render the tilemap on surface with interpolated camera (snapped to pixel grid)
        """
        interp_pos = Vector2(camera_interp.pos)

        # Snap interpolated position to integer pixels for tilemap grid alignment
        render_pos = Vector2(round(interp_pos.x), round(interp_pos.y))

        # No offset: tilemap stays on pixel grid
        offset = (0, 0)
        
        # render parallax with snapped camera
        tile_cam = Camera(render_pos, camera_interp.size)
        for parallax in reversed(tilemap.parallax):
            cls._render_parallax(tilemap, parallax, surface, tile_cam)
            

        if not cls._last_surface:
            cls._last_surface = Surface(camera_interp.rect.size, SRCALPHA)

        # Redraw when interpolated camera position (snapped) changes by 1+ pixel
        # This gives fluid tile updates without sub-pixel jitter
        if cls._last_camera_pos is None or (render_pos - cls._last_camera_pos).length() >= 1.0:
            cls._redraw_full(tilemap, tile_cam)
            cls._last_camera_pos = Vector2(render_pos)
        else:
            # Just update animated tiles with current camera position
            cls._redraw_dirty(tilemap, tile_cam)

        # Blit the pre-rendered tilemap at pixel boundary
        surface.blit(cls._last_surface, offset)
