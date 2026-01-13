# -*- coding: utf-8 -*-

"""
SHIFT PROJECT - Map Editor
____________________________________________________________________________________________________
Rewritten Map Editor Compatible with New Renderer
____________________________________________________________________________________________________
"""

from __future__ import annotations

import os
from typing import Optional
from json import dumps

from tkinter.filedialog import asksaveasfilename, askopenfilename

import pygame
from pygame import MOUSEBUTTONDOWN, NOFRAME, QUIT, Rect, Vector2, display, time, SRCALPHA

from game_libs import config
from game_libs.assets_registry import AssetsRegistry
from game_libs.ecs_core.engine import Engine
from game_libs.level.components import Camera
from game_libs.level.tilemap import TilesetData, TilemapData, FixedParallaxData, TilemapParallaxData, TileData
from game_libs.level.level import Level
from game_libs.rendering.tilemap_renderer import TilemapRenderer, TileRenderer
from pygame_ui import (Frame, IconButton, Label, Menubar, Popup, Selector,
                       TabbedFrame, TextEntry, UIApp, UIWidget, DropdownList,
                       DualListToggle, Button, ListView)

os.environ["SDL_VIDEO_CENTERED"] = "1"
display.init()
display.set_mode((1, 1), NOFRAME)
display.set_icon(pygame.image.load("icon.ico").convert())

brush_icon = pygame.image.load("assets/Editor/brush.png")
fill_icon = pygame.image.load("assets/Editor/fill.png")
rect_icon = pygame.image.load("assets/Editor/rectangle.png")
new_icon = pygame.image.load("assets/Editor/new.png")
open_icon = pygame.image.load("assets/Editor/open.png")
save_icon = pygame.image.load("assets/Editor/save.png")
tilemap_icon = pygame.image.load("assets/Editor/tilemap.png")
entity_icon = pygame.image.load("assets/Editor/entity.png")
layer_icon = pygame.image.load("assets/Editor/layer.png")


# ----- Utility Functions ----- #
def inline_dict(value: dict) -> str:
    """Format a dictionary into a single-line string for display."""
    items = []
    for k, v in value.items():
        if isinstance(v, str):
            v_str = f'"{v}"'
        elif isinstance(v, dict):
            v_str = inline_dict(v)
        else:
            v_str = str(v)
        items.append(f'"{k}": {v_str}')
    return "{" + ", ".join(items) + "}"

def format_grid(grid: list[list[int]], indent_nb: int) -> str:
    """Format a 2D grid into a string for display."""
    maxl = max(len(str(cell)) for row in grid for cell in row)
    return (
        "[\n" +
        "\n".join(
            "\t"*(indent_nb+1) + "[" + (", ").join(
                f"{cell: >{maxl}}" for cell in row
            ) + "]," for row in grid
        )[:-1] +
        "\n\t"*(indent_nb) + "]"
    )


# ----- TilePicker Widget ----- #
class TilePicker(Frame):
    """A tile picker widget to select tiles from a tileset."""
    
    def __init__(self, parent: Optional[UIWidget], rect: Rect, tilemap=None):
        super().__init__(parent, rect)
        self.logger = self.app.label_info
        self.selected: int = -1
        self.hovered: int = -1
        self.tilemap = tilemap
        self._update_size()

    def get_tilemap(self):
        return self.tilemap if self.tilemap is not None else self.app.level.tilemap

    def _update_size(self):
        tilemap = self.get_tilemap()
        tile_size = tilemap.tileset.tile_size
        tiles_per_row = max(1, self.rect.width // tile_size)
        n_tiles = len(tilemap.tileset.tiles)
        n_rows = (n_tiles + tiles_per_row - 1) // tiles_per_row
        self.size = (self.rect.width, max(self.rect.height, n_rows * tile_size))
        self.surface = pygame.Surface(self.size, SRCALPHA)

    def handle_event(self, event):
        if not self.displayed:
            return False
        
        tilemap = self.get_tilemap()
        tile_size = tilemap.tileset.tile_size
        tiles_per_row = max(1, self.rect.width // tile_size)
        n_tiles = len(tilemap.tileset.tiles)

        if self.hover and event.type == pygame.MOUSEMOTION:
            pos = Vector2(event.pos) - Vector2(self.global_rect.topleft) + self.scroll
            x = int(pos.x // tile_size)
            y = int(pos.y // tile_size)
            idx = int(y * tiles_per_row + x)
            self.hovered = idx if 0 <= idx < n_tiles else -1
            return True
        
        if self.focus and event.type == MOUSEBUTTONDOWN and event.button == 1:
            pos = Vector2(event.pos) - Vector2(self.global_rect.topleft) + self.scroll
            x = int(pos.x // tile_size)
            y = int(pos.y // tile_size)
            idx = int(y * tiles_per_row + x)
            if 0 <= idx < n_tiles:
                self.selected = idx
                self.logger.text = f"Selected tile {self.selected}"
                return True
        
        return super().handle_event(event)

    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        
        tilemap = self.get_tilemap()
        tile_size = tilemap.tileset.tile_size
        tiles_per_row = max(1, self.rect.width // tile_size)
        
        self._update_size()
        self.surface.fill(self.app.theme.colors["bg"])

        for idx, tile in enumerate(tilemap.tileset.tiles):
            x = (idx % tiles_per_row) * tile_size
            y = (idx // tiles_per_row) * tile_size
            self.surface.blit(TileRenderer.render(tile, [False]*8), (x, y))
            rect_tile = pygame.Rect(x, y, tile_size, tile_size)
            if idx == self.selected:
                pygame.draw.rect(self.surface, self.app.theme.colors["accent"], rect_tile, 2)
            elif idx == self.hovered:
                pygame.draw.rect(self.surface, self.app.theme.colors["hover"], rect_tile, 2)

        surface_rect = Rect(self.scroll, self.rect.size)
        surface.blit(self.surface.subsurface(surface_rect), self.rect)
        self.draw_scrollbars(surface)
        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(2, 2), 2)


# ----- MapCanvas Widget ----- #
class MapCanvas(Frame):
    """A map canvas widget to display and edit a tilemap."""
    
    def __init__(self, parent: Optional[UIWidget], rect: Rect, tilemap=None):
        Frame.__init__(self, parent, rect)
        self.logger = self.app.label_info
        self.tilemap = tilemap
        tm = self.get_tilemap()
        width = tm.width * tm.tileset.tile_size
        height = tm.height * tm.tileset.tile_size
        self.size = (width, height)
        
        self.tile_picker: TilePicker = self.app.tile_picker
        self.tool_selector: Selector = self.app.tools_selector
        self.painting: bool = False
        self.erasing: bool = False
        self.estimating_rect: bool = False
        self.rect_start: Optional[Vector2] = None
        
        # Cached surfaces for viewport rendering
        self._tilemap_cache = None
        self._cache_camera_pos = None

    def get_tilemap(self):
        return self.tilemap if self.tilemap is not None else self.app.level.tilemap

    def reinit(self):
        """Reinitialize the canvas."""
        tm = self.get_tilemap()
        width = tm.width * tm.tileset.tile_size
        height = tm.height * tm.tileset.tile_size
        self.size = (width, height)
        self._tilemap_cache = None
        self._cache_camera_pos = None
        TilemapRenderer.clear_cache()

    @property
    def viewport_camera(self) -> Camera:
        """Create a camera for the viewport."""
        center = self.scroll + Vector2(self.rect.width // 2, self.rect.height // 2)
        return Camera(center, (self.rect.width, self.rect.height))

    def fill(self, event: pygame.event.Event):
        """Fill a tile region with selected tile."""
        if self.tool_selector.selected_name != "fill":
            return
        
        tm = self.get_tilemap()
        mouse_pos = Vector2(event.pos)
        x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
        y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
        
        if 0 <= x < tm.width and 0 <= y < tm.height:
            target_tile = tm.grid[y][x]
            replacement_tile = self.tile_picker.selected
            if target_tile == replacement_tile or replacement_tile == -1:
                return
            
            to_fill = [(x, y)]
            filled = set()
            while to_fill:
                cx, cy = to_fill.pop()
                if (cx, cy) in filled:
                    continue
                current_tile = tm.grid[cy][cx]
                if current_tile == target_tile:
                    tm.grid[cy][cx] = replacement_tile
                    filled.add((cx, cy))
                    if cx > 0:
                        to_fill.append((cx - 1, cy))
                    if cx < tm.width - 1:
                        to_fill.append((cx + 1, cy))
                    if cy > 0:
                        to_fill.append((cx, cy - 1))
                    if cy < tm.height - 1:
                        to_fill.append((cx, cy + 1))
            
            self.logger.text = f"Filled {len(filled)} tiles"
            self._tilemap_cache = None  # Invalidate cache

    def handle_event(self, event: pygame.event.Event):
        if not self.displayed:
            return False
        
        tm = self.get_tilemap()
        
        if self.focus and event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.tool_selector.selected_name == "brush":
                self.painting = True
            elif self.tool_selector.selected_name == "fill":
                self.fill(event)
                self.app.minimap.update_minimap()
            elif self.tool_selector.selected_name == "rect":
                mouse_pos = Vector2(event.pos)
                x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
                y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
                if 0 <= x < tm.width and 0 <= y < tm.height:
                    self.estimating_rect = True
                    self.rect_start = Vector2(x, y)
        
        if self.focus and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.erasing = True

        if self.focus and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.painting = False
            if self.estimating_rect and self.rect_start is not None:
                mouse_pos = Vector2(event.pos)
                x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
                y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
                if 0 <= x < tm.width and 0 <= y < tm.height:
                    x1 = int(min(self.rect_start.x, x))
                    x2 = int(max(self.rect_start.x, x))
                    y1 = int(min(self.rect_start.y, y))
                    y2 = int(max(self.rect_start.y, y))
                    if self.tile_picker.selected != -1:
                        for iy in range(y1, y2 + 1):
                            for ix in range(x1, x2 + 1):
                                tm.grid[iy][ix] = self.tile_picker.selected
                self.estimating_rect = False
                self.rect_start = None
                self._tilemap_cache = None
                self.app.minimap.update_minimap()

        if self.focus and event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.erasing = False

        if self.painting:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
            y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
            if 0 <= x < tm.width and 0 <= y < tm.height:
                if self.tile_picker.selected != -1 and tm.grid[y][x] != self.tile_picker.selected:
                    tm.grid[y][x] = self.tile_picker.selected
                    self._tilemap_cache = None
            self.app.minimap.update_minimap()

        if self.erasing:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
            y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
            if 0 <= x < tm.width and 0 <= y < tm.height:
                if tm.grid[y][x] != -1:
                    tm.grid[y][x] = -1
                    self._tilemap_cache = None
            self.app.minimap.update_minimap()
        
        return super().handle_event(event)

    def render(self, surface):
        if not self.displayed:
            return
        
        tm = self.get_tilemap()
        
        # Create a full-size surface for the renderer
        full_surface = pygame.Surface((tm.width * tm.tileset.tile_size, tm.height * tm.tileset.tile_size), SRCALPHA)
        TilemapRenderer.clear_cache()
        
        # Create camera for this viewport
        camera = self.viewport_camera
        TilemapRenderer.render(tm, full_surface, camera, camera)
        
        # Extract viewport portion and blit
        viewport_rect = pygame.Rect(self.scroll.x, self.scroll.y, self.rect.width, self.rect.height)
        surface.blit(full_surface, self.rect, area=viewport_rect)

        # Draw tile highlighter
        if self.estimating_rect and self.rect_start is not None:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
            y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
            if 0 <= x < tm.width and 0 <= y < tm.height:
                x1 = min(int(self.rect_start.x), x)
                x2 = max(int(self.rect_start.x), x)
                y1 = min(int(self.rect_start.y), y)
                y2 = max(int(self.rect_start.y), y)
                pygame.draw.rect(
                    surface,
                    self.app.theme.colors["accent"],
                    Rect(
                        Vector2(x1, y1) * tm.tileset.tile_size - self.scroll + Vector2(self.rect.topleft),
                        ((x2 - x1 + 1) * tm.tileset.tile_size, (y2 - y1 + 1) * tm.tileset.tile_size)
                    ),
                    2
                )
        else:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
            y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
            if 0 <= x < tm.width and 0 <= y < tm.height:
                pygame.draw.rect(
                    surface,
                    self.app.theme.colors["accent"],
                    Rect(
                        Vector2(x, y) * tm.tileset.tile_size - self.scroll + Vector2(self.rect.topleft),
                        (tm.tileset.tile_size, tm.tileset.tile_size)
                    ),
                    2
                )

        self.draw_scrollbars(surface)


# ----- Tile Properties Editor ----- #
class TilePropertiesEditor(Frame):
    """A properties editor for tiles."""
    
    def __init__(self, parent: Optional[UIWidget], rect: Rect):
        super().__init__(parent, rect)
        self.logger = self.app.label_info
        self.selected_tile: int = -1
        Label(self, (10, 10), "Tile Properties")
        Label(self, (10, 100), "Bitmask:")
        Label(self, (10, 200), "Hitbox:")
        Label(self, (10, 300), "Animation Delay:")
        self.bitmask_editor = TextEntry(self, Rect(self.rect.right-130, 150, 120, 30))
        self.hitbox_editor = TextEntry(self, Rect(self.rect.right-130, 250, 120, 30))
        self.animation_delay_editor = TextEntry(self, Rect(self.rect.right-130, 350, 120, 30))

    def handle_event(self, event):
        if not self.displayed:
            return False
        
        if (any((self.bitmask_editor.focus, self.hitbox_editor.focus,
                 self.animation_delay_editor.focus))
            and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            if self.selected_tile != -1:
                tile = self.app.level.tilemap.tileset.tiles[self.selected_tile]
                try:
                    bitmask = self.bitmask_editor.text
                    if bitmask not in ["unique", "field", "fall", "wall"]:
                        raise ValueError()
                    tile.autotilebitmask = bitmask
                    self.logger.text = f"Set bitmask of tile {self.selected_tile} to {bitmask}"
                except ValueError:
                    self.logger.text = "Error: Invalid bitmask value"
                try:
                    hitbox = int(self.hitbox_editor.text)
                    if hitbox not in [0, 1]:
                        raise ValueError()
                    tile.hitbox = hitbox
                    self.logger.text = f"Set hitbox to {hitbox}"
                except ValueError:
                    self.logger.text = "Error: Hitbox must be 0 or 1"
                try:
                    animation_delay = float(self.animation_delay_editor.text)
                    tile.animation_delay = animation_delay
                    self.logger.text = f"Set animation delay to {animation_delay}"
                except ValueError:
                    self.logger.text = "Error: Invalid animation delay"
        
        return super().handle_event(event)

    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        
        self.surface.fill(self.app.theme.colors["bg"])

        if self.app.tile_picker.selected != self.selected_tile and self.app.tile_picker.selected != -1:
            tile = self.app.level.tilemap.tileset.tiles[self.app.tile_picker.selected]
            self.bitmask_editor.text = str(tile.autotilebitmask)
            self.hitbox_editor.text = str(tile.hitbox)
            self.animation_delay_editor.text = str(tile.animation_delay)
            self.selected_tile = self.app.tile_picker.selected

        Frame.render(self, surface)


# ----- MiniMap Widget ----- #
class MiniMap(Frame):
    """A minimap widget to display a small overview of the map."""
    
    def __init__(self, parent, rect, map_canvas: MapCanvas):
        super().__init__(parent, rect)
        self.map_canvas = map_canvas
        self._minimap_surface = None
        self._scale = 1.0

    def reinit(self):
        """Reinitialize the minimap."""
        self._minimap_surface = None

    def update_minimap(self):
        """Update the minimap surface."""
        tm = self.app.level.tilemap
        tile_size = tm.tileset.tile_size
        map_w = tm.width * tile_size
        map_h = tm.height * tile_size

        # Calculate scale to fit in minimap rect
        scale_w = self.rect.width / map_w
        scale_h = self.rect.height / map_h
        self._scale = min(scale_w, scale_h)
        
        new_w = int(map_w * self._scale)
        new_h = int(map_h * self._scale)

        # Create a full tilemap surface and render to it
        full_surface = pygame.Surface((map_w, map_h), SRCALPHA)
        camera = Camera(Vector2(map_w // 2, map_h // 2), (map_w, map_h))
        TilemapRenderer.clear_cache()
        TilemapRenderer.render(tm, full_surface, camera, camera)
        
        # Scale the rendered tilemap
        scaled = pygame.transform.smoothscale(full_surface, (new_w, new_h))
        
        # Create the minimap display surface
        minimap_surf = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        minimap_surf.fill((0, 0, 0, 200))
        x = (self.rect.width - new_w) // 2
        y = (self.rect.height - new_h) // 2
        minimap_surf.blit(scaled, (x, y))
        
        self._minimap_surface = minimap_surf

    def center_camera(self, event: pygame.event.Event):
        """Center the MapCanvas camera on the minimap click."""
        if not self._minimap_surface:
            return
        
        mouse_pos = Vector2(event.pos) - Vector2(self.global_rect.topleft)
        tm = self.app.level.tilemap
        tile_size = tm.tileset.tile_size
        map_w = tm.width * tile_size
        map_h = tm.height * tile_size
        
        new_w = int(map_w * self._scale)
        new_h = int(map_h * self._scale)
        x_offset = (self.rect.width - new_w) // 2
        y_offset = (self.rect.height - new_h) // 2
        
        if x_offset <= mouse_pos.x <= x_offset + new_w and y_offset <= mouse_pos.y <= y_offset + new_h:
            relative_x = (mouse_pos.x - x_offset) / self._scale
            relative_y = (mouse_pos.y - y_offset) / self._scale
            self.map_canvas.scroll.x = max(0, min(relative_x - self.map_canvas.rect.width // 2, map_w - self.map_canvas.rect.width))
            self.map_canvas.scroll.y = max(0, min(relative_y - self.map_canvas.rect.height // 2, map_h - self.map_canvas.rect.height))

    def handle_event(self, event):
        if not self.displayed:
            return False
        
        if self.focus and event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.center_camera(event)
            return True
        
        if self.focus and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.center_camera(event)
            return True
        
        return super().handle_event(event)

    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        
        if self._minimap_surface is None:
            self.update_minimap()
        
        surface.blit(self._minimap_surface, self.rect.topleft)
        
        # Draw camera viewport rectangle
        if self._scale > 0:
            tm = self.app.level.tilemap
            tile_size = tm.tileset.tile_size
            map_w = tm.width * tile_size
            map_h = tm.height * tile_size
            new_w = int(map_w * self._scale)
            new_h = int(map_h * self._scale)
            x_offset = (self.rect.width - new_w) // 2
            y_offset = (self.rect.height - new_h) // 2
            
            viewport_w = int(self.map_canvas.rect.width * self._scale)
            viewport_h = int(self.map_canvas.rect.height * self._scale)
            viewport_x = int(self.map_canvas.scroll.x * self._scale) + x_offset + self.rect.x
            viewport_y = int(self.map_canvas.scroll.y * self._scale) + y_offset + self.rect.y
            
            pygame.draw.rect(
                surface,
                self.app.theme.colors["accent"],
                Rect(viewport_x, viewport_y, viewport_w, viewport_h),
                2
            )
        
        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(2, 2), 2)


# ----- Main Editor Application ----- #
class LevelEditor(UIApp):
    """The main level editor application."""
    
    def __init__(self, size=(1280, 800)):
        pygame.init()
        self.screen = display.set_mode(size)
        display.set_caption("SHIFT Map Editor")
        display.set_icon(pygame.image.load("icon.ico").convert())
        UIApp.__init__(self, size)
        self.running = True
        self.level = AssetsRegistry.load_level("empty", Engine())
        self.level.tilemap.name = "temp"
        self._setup_ui(size)

    def _setup_ui(self, size):
        main_layer = self.add_layer()
        overlay_layer = self.add_layer()

        # Menubar
        menubar = Menubar(None, width=size[0])
        overlay_layer.add(menubar)
        
        level_menu = menubar.add_dropdown("Level")
        level_menu.add_option("Open", self.open_level)
        level_menu.add_option("Save", lambda: self.save_level(self.level))
        level_menu.add_option("Save as", self.save_level_as)
        
        tilemap_menu = menubar.add_dropdown("Tilemap")
        tilemap_menu.add_option("Open", self.open_tilemap)
        tilemap_menu.add_option("Save", lambda: self.save_tilemap(self.level.tilemap))
        tilemap_menu.add_option("Save as", self.save_tilemap_as)
        
        tileset_menu = menubar.add_dropdown("Tileset")
        tileset_menu.add_option("Open", self.open_tileset)
        tileset_menu.add_option("Save", lambda: self.save_tileset(self.level.tilemap.tileset))
        tileset_menu.add_option("Save as", self.save_tileset_as)

        # Toolbar
        toolbar = Frame(parent=None, rect=Rect(0, 24, size[0], 48))
        main_layer.add(toolbar)
        
        IconButton(toolbar, Rect(0, 0, 48, 48), new_icon, self.new_level)
        IconButton(toolbar, Rect(48, 0, 48, 48), open_icon, self.open_level)
        IconButton(toolbar, Rect(96, 0, 48, 48), save_icon, self.save_file)

        self.tools_selector = Selector(
            toolbar, (240, 0),
            {"brush": brush_icon, "fill": fill_icon, "rect": rect_icon}
        )
        self.tools_selector.selected_index = 0

        edition = Selector(
            toolbar, (896, 0),
            {"tilemap": tilemap_icon, "entities": entity_icon, "layers": layer_icon}
        )
        edition.selected_index = 0

        # Main UI areas
        picker = TabbedFrame(parent=None, rect=Rect(0, 72, 240, 680), selector=edition)
        main_layer.add(picker)
        
        canvas = TabbedFrame(parent=None, rect=Rect(240, 72, 800, 680), selector=edition)
        main_layer.add(canvas)
        
        properties_editor = TabbedFrame(parent=None, rect=Rect(1040, 72, 240, 440), selector=edition)
        main_layer.add(properties_editor)

        infobar = Frame(parent=None, rect=Rect(0, 752, size[0], 48))
        main_layer.add(infobar)
        self.label_info = Label(infobar, (10, 10), "Ready.")
        
        # Setup tilemap editing
        self.tile_picker = TilePicker(picker, Rect(0, 0, 240, 680))
        picker.attach("tilemap", self.tile_picker)
        
        self.map_canvas = MapCanvas(canvas, Rect(0, 0, 800, 680))
        canvas.attach("tilemap", self.map_canvas)
        
        self.tile_properties = TilePropertiesEditor(properties_editor, Rect(0, 0, 240, 440))
        properties_editor.attach("tilemap", self.tile_properties)

        # Minimap
        self.minimap = MiniMap(None, Rect(1040, 512, 240, 240), self.map_canvas)
        main_layer.add(self.minimap)

    def new_level(self):
        """Create a new level."""
        popup = Popup(self, self.screen, Rect(0, 0, 1000, 700), "Create a new level")
        popup.rect.center = self.screen.get_rect().center
        
        Label(popup, (10, 20), "Name")
        level_name_entry = TextEntry(popup, Rect(100, 18, 300, 20), default_text="temp")
        
        Label(popup, (10, 70), "Tilemap")
        Label(popup, (30, 90), "* name")
        Label(popup, (30, 110), "* size")
        tilemap_name_entry = TextEntry(popup, Rect(150, 88, 300, 20), default_text="temp")
        tilemap_width_entry = TextEntry(popup, Rect(150, 108, 70, 20), default_text="40")
        Label(popup, (230, 110), "X")
        tilemap_height_entry = TextEntry(popup, Rect(250, 108, 70, 20), default_text="23")
        
        Label(popup, (30, 130), "* tileset")
        tileset_list = DropdownList(popup, (150, 130), list(AssetsRegistry.list_assets("tileset")))
        
        Label(popup, (10, 180), "Systems")
        systems_list = DualListToggle(popup, Rect(10, 210, 500, 280), config.SYSTEM_PRIORITY)
        
        def close():
            popup.title = "create"
            popup.close()
        Button(popup, Rect(750, 600, 200, 50), "Créer", close)
        popup.run()
        
        if popup.title == "create":
            level_name = level_name_entry.text or "temp"
            tilemap_name = tilemap_name_entry.text or "temp"
            try:
                tilemap_width = int(tilemap_width_entry.text)
            except ValueError:
                tilemap_width = 40
            try:
                tilemap_height = int(tilemap_height_entry.text)
            except ValueError:
                tilemap_height = 23

            self.level.name = level_name
            self.level.systems = list(systems_list.get())
            self.level.tilemap.name = tilemap_name
            self.level.tilemap.tileset = AssetsRegistry.load_tileset(tileset_list.get_text())
            self.level.tilemap.width = tilemap_width
            self.level.tilemap.height = tilemap_height
            self.level.tilemap.grid = [[-1 for _ in range(tilemap_width)] for _ in range(tilemap_height)]
            self.level.tilemap.entities = []
            
            self.map_canvas.reinit()
            self.minimap.reinit()
            self.label_info.text = f"Level '{level_name}' created"

    def save_tileset(self, tileset: TilesetData):
        """Save tileset data."""
        tiles: list[TileData] = [tile for tile in tileset.tiles if tile.blueprint is not None]
        for tile in tiles:
            tile.blueprint.update({
                "hitbox": tile.hitbox,
                "type": tile.autotilebitmask,
                "animation_delay": tile.animation_delay
            })

        string: str = (
            "{" + "\n" +
            f'\t"tile_size": {tileset.tile_size},\n' +
            f'\t"files": {list({tile.blueprint["file"] for tile in tiles})},\n' +
            f'\t"tiles": [\n\t\t{",\n\t\t".join(inline_dict(tile.blueprint) for tile in tiles)}\n\t]\n' +
            "}"
        ).replace("'", "\"")

        with open(os.path.join(config.TILESET_DATA_FOLDER, f"{tileset.name}.json"), "w", encoding="utf-8") as f:
            f.write(string)
        
        self.label_info.text = "Tileset saved"

    def save_tilemap(self, tilemap: TilemapData):
        """Save tilemap data."""
        string = (
            "{" + "\n" +
            f'\t"size": {[tilemap.width, tilemap.height]},\n' +
            f'\t"bgm": "{tilemap.bgm}",\n' +
            f'\t"bgs": "{tilemap.bgs}",\n' +
            f'\t"tileset": "{tilemap.tileset.name}",\n' +
            f'\t"tiles": {format_grid(tilemap.grid, 1)},\n' +
            '\t"entities": [],\n' +
            '\t"parallax": []\n' +
            "}"
        ).replace("'", "\"")

        with open(os.path.join(config.TILEMAP_FOLDER, f"{tilemap.name}.json"), "w", encoding="utf-8") as f:
            f.write(string)
        
        self.label_info.text = "Tilemap saved"

    def save_level(self, level: Level):
        """Save level data."""
        with open(os.path.join(config.LEVELS_FOLDER, f"{level.name}.json"), "w", encoding="utf-8") as f:
            f.write(dumps({
                "tilemap": level.tilemap.name,
                "systems": level.systems,
                "player": level.player.overrides,
                "camera": {
                    "x": level.camera.centerx,
                    "y": level.camera.centery
                }
            }, indent=4))
        
        self.label_info.text = "Level saved"

    def save_file(self):
        """Save current level."""
        if self.level.name == "empty":
            self.level.name = "temp"
            self.level.tilemap.name = "temp"
        
        self.save_level(self.level)
        self.save_tilemap(self.level.tilemap)
        self.save_tileset(self.level.tilemap.tileset)
        self.label_info.text = f"Saved '{self.level.name}'"

    def save_tileset_as(self):
        """Save as tileset."""
        filepath = asksaveasfilename(initialdir=config.TILESET_DATA_FOLDER, defaultextension=".json")
        if filepath:
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap.tileset.name = name
            self.save_tileset(self.level.tilemap.tileset)

    def save_tilemap_as(self):
        """Save as tilemap."""
        filepath = asksaveasfilename(initialdir=config.TILEMAP_FOLDER, defaultextension=".json")
        if filepath:
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap.name = name
            self.save_tilemap(self.level.tilemap)

    def save_level_as(self):
        """Save as level."""
        filepath = asksaveasfilename(initialdir=config.LEVELS_FOLDER, defaultextension=".json")
        if filepath:
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.name = name
            self.save_level(self.level)

    def open_tileset(self):
        """Open a tileset."""
        filepath = askopenfilename(initialdir=config.TILESET_DATA_FOLDER, defaultextension=".json")
        if filepath:
            AssetsRegistry.clear_cache()
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap.tileset = AssetsRegistry.load_tileset(name)
            self.map_canvas.reinit()
            self.minimap.reinit()
            self.label_info.text = f"Loaded tileset '{name}'"

    def open_tilemap(self):
        """Open a tilemap."""
        filepath = askopenfilename(initialdir=config.TILEMAP_FOLDER, defaultextension=".json")
        if filepath:
            AssetsRegistry.clear_cache()
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap = AssetsRegistry.load_tilemap(name)
            self.map_canvas.reinit()
            self.minimap.reinit()
            self.label_info.text = f"Loaded tilemap '{name}'"

    def open_level(self):
        """Open a level."""
        filepath = askopenfilename(initialdir=config.LEVELS_FOLDER, defaultextension=".json")
        if filepath:
            AssetsRegistry.clear_cache()
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level = AssetsRegistry.load_level(name, Engine())
            self.map_canvas.reinit()
            self.minimap.reinit()
            self.label_info.text = f"Loaded level '{name}'"

    def run(self):
        """Run the application."""
        clock = time.Clock()
        while self.running:
            dt = clock.tick() / 1000
            
            for e in pygame.event.get():
                if e.type == QUIT:
                    self.running = False
                else:
                    self.handle_events(e)
            
            # Update tilesets animations
            tilesets = [AssetsRegistry.load_tileset(ts) for ts in AssetsRegistry.list_assets("tileset")]
            for tileset in tilesets:
                tileset.update_animation(dt)
            
            self.screen.fill((40, 40, 40))
            self.render(self.screen)
            display.flip()

        # Save before exit
        if self.level.name != "empty":
            self.save_file()


if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
    pygame.quit()
