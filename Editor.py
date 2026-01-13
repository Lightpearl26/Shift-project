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
from game_libs.level.entity import Player
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
        
        self.tile_picker: Optional[TilePicker] = None
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
            replacement_tile = self.tile_picker.selected if self.tile_picker else -1
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
                    if self.tile_picker and self.tile_picker.selected != -1:
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
                if self.tile_picker and self.tile_picker.selected != -1 and tm.grid[y][x] != self.tile_picker.selected:
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
        
        # Create a viewport-sized surface
        viewport_surface = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        viewport_surface.fill((0, 0, 0, 0))
        
        TilemapRenderer.clear_cache()
        
        # Create camera for this viewport
        camera = self.viewport_camera
        TilemapRenderer.render(tm, viewport_surface, camera, camera)
        
        # Blit the viewport directly to the destination
        surface.blit(viewport_surface, self.rect.topleft)

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


# ----- LayerPicker ----- #
class LayerPicker(Frame):
    """
    Liste des layers (tilemap principale + parallax) avec gestion ajout/suppression/déplacement.
    """
    def __init__(self, parent: Optional[UIWidget], rect: Rect):
        super().__init__(parent, rect)
        self.logger = self.app.label_info

        # ListView pour les layers
        self.listview = ListView(self, Rect(10, 50, rect.width-20, rect.height-360), self.get_layer_names())
        self.listview.selected_index = 0
        
        # TabbedFrame pour les TilePicker / vide
        self.tilepickers = TabbedFrame(self, Rect(0, rect.height-300, rect.width, 300), self.listview)
        self.refresh()

        # Boutons
        self.add_btn = Button(self, Rect(10, 10, 60, 30), "Add", self.add_layer)
        self.remove_btn = Button(self, Rect(80, 10, 60, 30), "Remove", self.remove_layer)
        self.up_btn = Button(self, Rect(150, 10, 30, 30), "↑", self.move_up)
        self.down_btn = Button(self, Rect(190, 10, 30, 30), "↓", self.move_down)

    def get_layer_names(self):
        names = ["Tilemap principale"]
        names += [f"Parallax {i+1}" for i in range(len(self.app.level.tilemap.parallax or []))]
        return names

    def refresh(self):
        old_index = self.listview.selected_index
        self.listview.items = self.get_layer_names()
        self.listview.selected_index = min(old_index, len(self.listview.items) - 1)

        self.tilepickers.frames.clear()
        # Tilemap principale
        self.tilepickers.attach(
            "Tilemap principale",
            TilePicker(self.tilepickers,
                       Rect(0, 0, self.tilepickers.rect.width, self.tilepickers.rect.height))
            )
        # Parallax
        for i, parallax in enumerate(self.app.level.tilemap.parallax or []):
            if hasattr(parallax, "tm"):  # À adapter selon ta structure
                self.tilepickers.attach(
                    f"Parallax {i+1}",
                    TilePicker(self.tilepickers,
                               Rect(0,
                                    0,
                                    self.tilepickers.rect.width,
                                    self.tilepickers.rect.height),
                               tilemap=parallax.tm)
                    )
            else:
                self.tilepickers.attach(
                    f"Parallax {i+1}",
                    Frame(self.tilepickers,
                          Rect(0,
                               0,
                               self.tilepickers.rect.width,
                               self.tilepickers.rect.height))
                    )  # Vide
        if hasattr(self.app, "layer_properties"):
            self.app.layer_properties.refresh()
        if hasattr(self.app, "layer_canvas"):
            self.app.layer_canvas.refresh()
        if hasattr(self.app, "minimap"):
            self.app.minimap.update_minimap()

    def add_layer(self):
        # Popup pour choisir le type de parallax et ses propriétés
        popup = Popup(self.app, self.app.screen, Rect(0, 0, 500, 400), "Nouveau Parallax")
        popup.rect.center = self.app.screen.get_rect().center

        # Selector + TabbedFrame pour le type de parallax
        type_selector = Selector(popup, (10, 10), {"Statique": rect_icon, "Tilemap": layer_icon})
        tabbed = TabbedFrame(popup, Rect(50, 100, 400, 250), selector=type_selector)

        # Frame pour Statique
        static_frame = Frame(tabbed, Rect(0, 0, 400, 250))
        Label(static_frame, (10, 10), "Image")
        image_entry = TextEntry(static_frame, Rect(10, 48, 380, 24), default_text="parallax.png")
        def open_file():
            filename = askopenfilename(
                title="Ouvrir une image",
                initialdir="assets/Parallax",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All files", "*.*")]
            )
            if filename:
                rel_path = os.path.relpath(filename)
                image_entry.text = rel_path.replace("\\", "/")
                image_entry.cursor_pos = len(image_entry.text)
        Button(static_frame, Rect(10, 80, 200, 24), "Ouvrir une image", open_file)
        tabbed.attach("Statique", static_frame)

        # Frame pour Tilemap
        tilemap_frame = Frame(tabbed, Rect(0, 0, 400, 250))
        Label(tilemap_frame, (10, 10), "Nom")
        name_entry_tilemap = TextEntry(tilemap_frame, Rect(60, 8, 200, 24), default_text=f"Parallax {len(self.app.level.tilemap.parallax or [])+1}")
        Label(tilemap_frame, (10, 50), "Taille")
        width_entry = TextEntry(tilemap_frame, Rect(70, 48, 60, 24), default_text="40")
        Label(tilemap_frame, (135, 50), "x")
        height_entry = TextEntry(tilemap_frame, Rect(150, 48, 60, 24), default_text="23")
        Label(tilemap_frame, (10, 90), "Tileset")
        tileset = DropdownList(tilemap_frame, (80, 88), list(AssetsRegistry.list_assets("tileset")))
        tabbed.attach("Tilemap", tilemap_frame)

        def close():
            popup.title = "create"
            popup.close()
        Button(popup, Rect(390, 360, 100, 30), "Créer", close)
        popup.run()

        if popup.title == "create":
            if type_selector.selected_name == "Statique":
                image = image_entry.text or "parallax.png"
                parallax = FixedParallaxData(img=pygame.image.load(image).convert_alpha(), blueprint={"type": "img", "img": image})
                self.logger.text = f"Create static parallax with image {image}"
                
            else:
                name = name_entry_tilemap.text or f"Parallax {len(self.app.level.tilemap.parallax or [])+1}"
                width = int(width_entry.text or "40")
                height = int(height_entry.text or "23")
                tileset_obj = AssetsRegistry.load_tileset(tileset.get_text())
                tilemap = TilemapData(name, width, height, tileset_obj, "", "", [[-1 for _ in range(width)] for _ in range(height)], [], [])
                parallax = TilemapParallaxData(tm=tilemap, blueprint={"type": "tilemap", "name": tilemap.name})
                self.logger.text = f"Create tilemap parallax with tilemap {name} ({width}x{height})"
            self.app.level.tilemap.parallax.append(parallax)
            self.refresh()

    def remove_layer(self):
        idx = self.listview.selected_index
        if idx == 0:
            self.app.label_info.text = "Impossible de supprimer la tilemap principale"
            return
        del self.app.level.tilemap.parallax[idx-1]
        self.refresh()

    def move_up(self):
        idx = self.listview.selected_index
        if idx <= 1:
            return
        parallax = self.app.level.tilemap.parallax
        parallax[idx-2], parallax[idx-1] = parallax[idx-1], parallax[idx-2]
        self.listview.selected_index -= 1
        self.refresh()

    def move_down(self):
        idx = self.listview.selected_index
        parallax = self.app.level.tilemap.parallax
        if idx == 0 or idx >= len(parallax):
            return
        parallax[idx-1], parallax[idx] = parallax[idx], parallax[idx-1]
        self.listview.selected_index += 1
        self.refresh()


# ----- Layer Properties ----- #
class LayerProperties(Frame):
    """
    Properties display for the selected layer.
    """
    def __init__(self, parent: Optional[UIWidget], rect: Rect):
        super().__init__(parent, rect)
        self.logger = self.app.label_info
        self.frame = TabbedFrame(self, Rect(0, 0, rect.width, rect.height), self.app.layerpicker.listview)
        self.refresh()

    def refresh(self):
        """
        Refresh the properties display based on the selected layer.
        """
        self.frame.frames.clear()
        for layer in self.app.layerpicker.listview.items:
            if layer == "Tilemap principale":
                tilemap = self.app.level.tilemap
                frame = Frame(self.frame, Rect(0, 0, self.frame.rect.width, self.frame.rect.height))
                Label(frame, (10, 10), "Tilemap Properties")
                Label(frame, (10, 50), f"Size: {tilemap.width} x {tilemap.height}")
                Label(frame, (10, 90), f"Tileset: {tilemap.tileset.name}")
                Label(frame, (10, 130), f"BGM: {tilemap.bgm if tilemap.bgm else 'None'}")
                Label(frame, (10, 170), f"BGS: {tilemap.bgs if tilemap.bgs else 'None'}")
                self.frame.attach(layer, frame)
            else:
                idx = int(layer.split()[-1]) - 1
                parallax = self.app.level.tilemap.parallax[idx]
                frame = Frame(self.frame, Rect(0, 0, self.frame.rect.width, self.frame.rect.height))
                Label(frame, (10, 10), f"{layer} Properties")
                if hasattr(parallax, "img"):
                    Label(frame, (10, 50), "Type: Static")
                    Label(frame, (10, 90), f"Image: {parallax.img}")
                elif hasattr(parallax, "tm"):
                    tm = parallax.tm
                    Label(frame, (10, 50), "Type: Tilemap")
                    Label(frame, (10, 90), f"Size: {tm.width} x {tm.height}")
                    Label(frame, (10, 130), f"Tileset: {tm.tileset.name}")
                else:
                    Label(frame, (10, 50), "Unknown Parallax Type")
                self.frame.attach(layer, frame)


# ----- LayerCanvas ----- #
class LayerCanvas(Frame):
    """
    A canvas to display the selected layer in the LayerPicker.
    """
    def __init__(self, parent: Optional[UIWidget], rect: Rect):
        super().__init__(parent, rect)
        self.tabbed = None
        
    def initialize(self):
        """Initialize tabbed frame after layerpicker is created."""
        if self.tabbed is None:
            self.tabbed = TabbedFrame(self, Rect(0, 0, self.rect.width, self.rect.height), self.app.layerpicker.listview)
            self.refresh()
        
    def refresh(self):
        """
        Refresh the canvases based on the selected layer.
        """
        if self.tabbed is None:
            self.initialize()
        
        self.tabbed.frames.clear()
        self.tabbed.children.clear()
        for layer in self.app.layerpicker.listview.items:
            if layer == "Tilemap principale":
                tilemap = self.app.level.tilemap
                canvas = MapCanvas(self.tabbed, Rect(0, 0, self.tabbed.rect.width, self.tabbed.rect.height), tilemap=tilemap)
                canvas.tile_picker = self.app.layerpicker.tilepickers.frames[layer]
                self.tabbed.attach(layer, canvas)
            else:
                idx = int(layer.split()[-1]) - 1
                parallax = self.app.level.tilemap.parallax[idx]
                if hasattr(parallax, "tm"):
                    tm = parallax.tm
                    canvas = MapCanvas(self.tabbed, Rect(0, 0, self.tabbed.rect.width, self.tabbed.rect.height), tilemap=tm)
                    canvas.tile_picker = self.app.layerpicker.tilepickers.frames[layer]
                    self.tabbed.attach(layer, canvas)
                else:
                    frame = Frame(self.tabbed, Rect(0, 0, self.tabbed.rect.width, self.tabbed.rect.height))
                    Label(frame, (10, 10), "No canvas for static parallax")
                    # create a frame to display the image
                    self.tabbed.attach(layer, frame)


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


# ----- Entity Picker ----- #
class EntityPicker(Frame):
    """A widget to select entity blueprints to place on the map."""
    
    def __init__(self, parent: Optional[UIWidget], rect: Rect):
        super().__init__(parent, rect)
        self.logger = self.app.label_info
        
        Label(self, (10, 10), "Entity Blueprints")
        
        # Get available blueprints and add Player as special option
        blueprint_names = ["[PLAYER]"] + list(AssetsRegistry.list_assets("blueprint"))
        self.blueprint_list = ListView(self, Rect(10, 40, self.rect.width - 20, self.rect.height - 50), blueprint_names)
        self.blueprint_list.selected_index = 0 if blueprint_names else -1
        
        # Update label with initial selection
        if self.selected_blueprint:
            self.logger.text = f"Selected: {self.selected_blueprint}"
    
    @property
    def selected_blueprint(self):
        """Get the currently selected blueprint."""
        if self.blueprint_list.selected_index >= 0 and self.blueprint_list.selected_index < len(self.blueprint_list.items):
            return self.blueprint_list.items[self.blueprint_list.selected_index]
        return None
        
    def handle_event(self, event):
        if not self.displayed:
            return False
        
        # Just let the list handle its own events
        result = super().handle_event(event)
        
        # Update label when selection changes
        if self.selected_blueprint:
            self.logger.text = f"Selected blueprint: {self.selected_blueprint}"
        
        return result
    
    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        
        self.surface.fill(self.app.theme.colors["bg"])
        Frame.render(self, surface)


# ----- Entity Canvas ----- #
class EntityCanvas(Frame):
    """A canvas to place and edit entities on the tilemap."""
    
    def __init__(self, parent: Optional[UIWidget], rect: Rect):
        super().__init__(parent, rect)
        self.logger = self.app.label_info
        self.tilemap = None
        self.selected_entity_idx: int = -1
        self.dragging_entity_idx: int = -1
        self.tile_size = 32  # Default, will be updated
        self.scroll = Vector2(0, 0)
        
    def get_tilemap(self):
        return self.app.level.tilemap
    
    def reinit(self):
        """Reinitialize canvas with tilemap data."""
        tm = self.get_tilemap()
        self.tilemap = tm
        self.tile_size = tm.tileset.tile_size
        width = tm.width * self.tile_size
        height = tm.height * self.tile_size
        self.size = (width, height)
    
    def handle_event(self, event):
        if not self.displayed:
            return False
        
        tm = self.get_tilemap()
        level = self.app.level
        
        if self.focus and event.type == MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicking on selected entity to start drag
            if self.selected_entity_idx == -2:  # -2 means player is selected
                mouse_pos = Vector2(event.pos)
                world_x = int(mouse_pos.x - self.global_rect.left + self.scroll.x)
                world_y = int(mouse_pos.y - self.global_rect.top + self.scroll.y)
                
                player_x = level.player.overrides.get("Hitbox", {}).get("x", 0) if level.player else 0
                player_y = level.player.overrides.get("Hitbox", {}).get("y", 0) if level.player else 0
                
                if abs(player_x - world_x) < self.tile_size and abs(player_y - world_y) < self.tile_size:
                    self.dragging_entity_idx = -2  # -2 for player
                    return True
            elif self.selected_entity_idx >= 0:
                mouse_pos = Vector2(event.pos)
                world_x = int(mouse_pos.x - self.global_rect.left + self.scroll.x)
                world_y = int(mouse_pos.y - self.global_rect.top + self.scroll.y)
                
                entity = tm.entities[self.selected_entity_idx]
                ex = entity.get("x", 0)
                ey = entity.get("y", 0)
                
                if abs(ex - world_x) < self.tile_size and abs(ey - world_y) < self.tile_size:
                    self.dragging_entity_idx = self.selected_entity_idx
                    return True
            
            # Otherwise place new entity or player
            if hasattr(self.app, 'entity_picker') and self.app.entity_picker.selected_blueprint:
                mouse_pos = Vector2(event.pos)
                # Convert screen coords to world coords
                world_x = int(mouse_pos.x - self.global_rect.left + self.scroll.x)
                world_y = int(mouse_pos.y - self.global_rect.top + self.scroll.y)
                
                blueprint = self.app.entity_picker.selected_blueprint
                
                if blueprint == "[PLAYER]":
                    # Place player
                    if level.player is None:
                        level.player = Player(0, level.engine, None, {})
                    level.player.overrides["Hitbox"] = {"x": world_x, "y": world_y}
                    self.logger.text = f"Placed Player at ({world_x}, {world_y})"
                else:
                    # Place regular entity
                    entity_data = {
                        "blueprint": blueprint,
                        "x": world_x,
                        "y": world_y,
                        "overrides": {}
                    }
                    tm.entities.append(entity_data)
                    self.logger.text = f"Placed {blueprint} at ({world_x}, {world_y})"
                
                if hasattr(self.app, 'entity_properties'):
                    self.app.entity_properties.refresh()
                return True
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Stop dragging
            if self.dragging_entity_idx == -2:  # Player
                player_x = self.app.level.player.overrides.get("Hitbox", {}).get("x", 0)
                player_y = self.app.level.player.overrides.get("Hitbox", {}).get("y", 0)
                self.logger.text = f"Moved Player to ({player_x}, {player_y})"
                self.dragging_entity_idx = -1
                if hasattr(self.app, 'entity_properties'):
                    self.app.entity_properties.refresh()
                return True
            elif self.dragging_entity_idx >= 0:
                entity = tm.entities[self.dragging_entity_idx]
                self.logger.text = f"Moved {entity.get('blueprint')} to ({entity.get('x')}, {entity.get('y')})"
                self.dragging_entity_idx = -1
                if hasattr(self.app, 'entity_properties'):
                    self.app.entity_properties.refresh()
                return True
        
        if self.focus and event.type == pygame.MOUSEMOTION and self.dragging_entity_idx == -2:
            # Drag player
            mouse_pos = Vector2(event.pos)
            world_x = int(mouse_pos.x - self.global_rect.left + self.scroll.x)
            world_y = int(mouse_pos.y - self.global_rect.top + self.scroll.y)
            
            if self.app.level.player:
                self.app.level.player.overrides["Hitbox"] = {"x": world_x, "y": world_y}
            return True
        
        if self.focus and event.type == pygame.MOUSEMOTION and self.dragging_entity_idx >= 0:
            # Drag entity
            mouse_pos = Vector2(event.pos)
            world_x = int(mouse_pos.x - self.global_rect.left + self.scroll.x)
            world_y = int(mouse_pos.y - self.global_rect.top + self.scroll.y)
            
            entity = tm.entities[self.dragging_entity_idx]
            entity["x"] = world_x
            entity["y"] = world_y
            return True
        
        if self.focus and event.type == MOUSEBUTTONDOWN and event.button == 3:
            # Select entity at clicked position
            mouse_pos = Vector2(event.pos)
            world_x = int(mouse_pos.x - self.global_rect.left + self.scroll.x)
            world_y = int(mouse_pos.y - self.global_rect.top + self.scroll.y)
            
            # Check if clicking on player
            level = self.app.level
            if level.player:
                player_x = level.player.overrides.get("Hitbox", {}).get("x", 0)
                player_y = level.player.overrides.get("Hitbox", {}).get("y", 0)
                if abs(player_x - world_x) < self.tile_size and abs(player_y - world_y) < self.tile_size:
                    self.selected_entity_idx = -2  # -2 represents player
                    self.logger.text = f"Selected Player at ({player_x}, {player_y})"
                    if hasattr(self.app, 'entity_properties'):
                        self.app.entity_properties.refresh()
                    return True
            
            # Find entity at position (within 32 pixels)
            for i, entity in enumerate(tm.entities):
                ex = entity.get("x", 0)
                ey = entity.get("y", 0)
                if abs(ex - world_x) < self.tile_size and abs(ey - world_y) < self.tile_size:
                    self.selected_entity_idx = i
                    self.logger.text = f"Selected entity: {entity.get('blueprint')} at ({ex}, {ey})"
                    if hasattr(self.app, 'entity_properties'):
                        self.app.entity_properties.refresh()
                    return True
            
            self.selected_entity_idx = -1
            if hasattr(self.app, 'entity_properties'):
                self.app.entity_properties.refresh()
            return False
        
        # Handle scrolling
        if self.hover and event.type == pygame.MOUSEWHEEL:
            keys = pygame.key.get_mods()
            if keys & pygame.KMOD_SHIFT:
                # Horizontal scroll with Shift
                if event.y > 0:
                    self.scroll.x = max(0, self.scroll.x - 50)
                else:
                    max_scroll_x = max(0, self.size[0] - self.rect.width)
                    self.scroll.x = min(max_scroll_x, self.scroll.x + 50)
            else:
                # Vertical scroll
                if event.y > 0:
                    self.scroll.y = max(0, self.scroll.y - 50)
                else:
                    max_scroll_y = max(0, self.size[1] - self.rect.height)
                    self.scroll.y = min(max_scroll_y, self.scroll.y + 50)
            return True
        
        return super().handle_event(event)
    
    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        
        tm = self.get_tilemap()
        level = self.app.level
        self.surface.fill((50, 50, 50))
        
        # Render tilemap first
        viewport_surface = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        viewport_surface.fill((0, 0, 0, 0))
        
        TilemapRenderer.clear_cache()
        
        # Create camera for this viewport (pos is center, not top-left)
        center = self.scroll + Vector2(self.rect.width // 2, self.rect.height // 2)
        camera = Camera(center, (self.rect.width, self.rect.height))
        TilemapRenderer.render(tm, viewport_surface, camera, camera)
        
        # Blit the viewport directly to the destination
        self.surface.blit(viewport_surface, (0, 0))
        
        # Draw player on top of tilemap
        if level.player:
            player_x = level.player.overrides.get("Hitbox", {}).get("x", 0)
            player_y = level.player.overrides.get("Hitbox", {}).get("y", 0)
            
            # Convert world coords to surface coords
            surf_x = int(player_x - self.scroll.x)
            surf_y = int(player_y - self.scroll.y)
            
            # Only draw if in viewport
            if -self.tile_size < surf_x < self.rect.width and -self.tile_size < surf_y < self.rect.height:
                # Draw player as a larger circle or different shape
                color = self.app.theme.colors["accent"] if self.selected_entity_idx == -2 else (50, 150, 255)
                pygame.draw.circle(self.surface, color, (surf_x + self.tile_size // 2, surf_y + self.tile_size // 2), 10, 2)
                
                # Draw "P" for player
                text = self.app.theme.font.render("P", True, (50, 150, 255))
                self.surface.blit(text, (surf_x + 6, surf_y + 6))
        
        # Draw entities on top of tilemap
        for i, entity in enumerate(tm.entities):
            ex = entity.get("x", 0)
            ey = entity.get("y", 0)
            
            # Convert world coords to surface coords
            surf_x = int(ex - self.scroll.x)
            surf_y = int(ey - self.scroll.y)
            
            # Only draw if in viewport
            if -self.tile_size < surf_x < self.rect.width and -self.tile_size < surf_y < self.rect.height:
                # Draw entity as a circle
                color = self.app.theme.colors["accent"] if i == self.selected_entity_idx else (100, 200, 100)
                pygame.draw.circle(self.surface, color, (surf_x + self.tile_size // 2, surf_y + self.tile_size // 2), 8, 2)
                
                # Draw blueprint name
                blueprint = entity.get("blueprint", "?")
                text = self.app.theme.font.render(blueprint[:2], True, (200, 200, 200))
                self.surface.blit(text, (surf_x + 4, surf_y + 4))
        
        # Blit scrollable content to the display surface
        surface.blit(self.surface, self.rect.topleft)
        
        self.draw_scrollbars(surface)
        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(2, 2), 2)


# ----- Entity Properties ----- #
class EntityProperties(Frame):
    """Display and edit properties of selected entity."""
    
    def __init__(self, parent: Optional[UIWidget], rect: Rect):
        super().__init__(parent, rect)
        self.logger = self.app.label_info
        self.selected_idx: int = -1
        self.property_widgets: dict = {}
        
    def refresh(self):
        """Refresh properties display."""
        # Clear old widgets
        self.children.clear()
        self.property_widgets.clear()
        
        canvas = self.app.entity_canvas if hasattr(self.app, 'entity_canvas') else None
        if not canvas or canvas.selected_entity_idx < -1:
            Label(self, (10, 10), "No entity selected")
            return
        
        level = self.app.level
        tm = level.tilemap
        
        # Handle player
        if canvas.selected_entity_idx == -2:
            if not level.player:
                Label(self, (10, 10), "No player")
                return
            
            self.selected_idx = -2
            Label(self, (10, 10), "PLAYER")
            
            player_x = level.player.overrides.get("Hitbox", {}).get("x", 0)
            player_y = level.player.overrides.get("Hitbox", {}).get("y", 0)
            Label(self, (10, 50), f"Position: ({player_x}, {player_y})")
            
            # X position editor
            Label(self, (10, 90), "X:")
            x_entry = TextEntry(self, Rect(40, 88, 50, 24), default_text=str(player_x))
            self.property_widgets['x'] = x_entry
            
            # Y position editor
            Label(self, (10, 130), "Y:")
            y_entry = TextEntry(self, Rect(40, 128, 50, 24), default_text=str(player_y))
            self.property_widgets['y'] = y_entry
            
            # Delete button
            Button(self, Rect(10, 170, 100, 30), "Delete Player", self.delete_player)
            
            # Update button
            Button(self, Rect(120, 170, 100, 30), "Update", self.update_player)
            return
        
        # Handle regular entities
        if canvas.selected_entity_idx < 0:
            Label(self, (10, 10), "No entity selected")
            return
        
        entity = tm.entities[canvas.selected_entity_idx]
        self.selected_idx = canvas.selected_entity_idx
        
        Label(self, (10, 10), f"Entity #{self.selected_idx}")
        Label(self, (10, 50), f"Blueprint: {entity.get('blueprint', '?')}")
        Label(self, (10, 90), f"Position: ({entity.get('x', 0)}, {entity.get('y', 0)})")
        
        # X position editor
        Label(self, (10, 130), "X:")
        x_entry = TextEntry(self, Rect(40, 128, 50, 24), default_text=str(entity.get('x', 0)))
        self.property_widgets['x'] = x_entry
        
        # Y position editor
        Label(self, (10, 170), "Y:")
        y_entry = TextEntry(self, Rect(40, 168, 50, 24), default_text=str(entity.get('y', 0)))
        self.property_widgets['y'] = y_entry
        
        # Delete button
        Button(self, Rect(10, 210, 100, 30), "Delete Entity", self.delete_entity)
        
        # Update button
        Button(self, Rect(120, 210, 100, 30), "Update", self.update_entity)
    
    def delete_player(self):
        """Delete the player."""
        level = self.app.level
        if level.player:
            level.player = None
            self.logger.text = "Deleted player"
            canvas = self.app.entity_canvas
            canvas.selected_entity_idx = -1
            self.refresh()
    
    def delete_entity(self):
        """Delete the selected entity."""
        canvas = self.app.entity_canvas if hasattr(self.app, 'entity_canvas') else None
        if canvas and canvas.selected_entity_idx >= 0:
            tm = self.app.level.tilemap
            entity = tm.entities.pop(canvas.selected_entity_idx)
            self.logger.text = f"Deleted entity: {entity.get('blueprint')}"
            canvas.selected_entity_idx = -1
            self.refresh()
    
    def update_player(self):
        """Update player properties."""
        level = self.app.level
        if not level.player:
            return
        
        try:
            if 'x' in self.property_widgets:
                x = int(self.property_widgets['x'].text)
            else:
                x = level.player.overrides.get("Hitbox", {}).get("x", 0)
            
            if 'y' in self.property_widgets:
                y = int(self.property_widgets['y'].text)
            else:
                y = level.player.overrides.get("Hitbox", {}).get("y", 0)
            
            level.player.overrides["Hitbox"] = {"x": x, "y": y}
            self.logger.text = f"Updated player at ({x}, {y})"
        except ValueError:
            self.logger.text = "Error: Invalid position values"
    
    def update_entity(self):
        """Update entity properties."""
        canvas = self.app.entity_canvas if hasattr(self.app, 'entity_canvas') else None
        if not canvas or canvas.selected_entity_idx < 0:
            return
        
        tm = self.app.level.tilemap
        entity = tm.entities[canvas.selected_entity_idx]
        
        try:
            if 'x' in self.property_widgets:
                entity['x'] = int(self.property_widgets['x'].text)
            if 'y' in self.property_widgets:
                entity['y'] = int(self.property_widgets['y'].text)
            self.logger.text = f"Updated entity at ({entity['x']}, {entity['y']})"
        except ValueError:
            self.logger.text = "Error: Invalid position values"
    
    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        
        self.surface.fill(self.app.theme.colors["bg"])
        Frame.render(self, surface)


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
        # Ensure parallax list exists
        if self.level.tilemap.parallax is None:
            self.level.tilemap.parallax = []
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
            {"tilemap": tilemap_icon, "entities": entity_icon}
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
        self.layerpicker = LayerPicker(picker, Rect(0, 0, 240, 680))
        picker.attach("tilemap", self.layerpicker)
        
        self.entity_picker = EntityPicker(picker, Rect(0, 0, 240, 680))
        picker.attach("entities", self.entity_picker)
        
        self.layer_canvas = LayerCanvas(canvas, Rect(0, 0, 800, 680))
        self.layer_canvas.initialize()  # Initialize after layerpicker is created
        canvas.attach("tilemap", self.layer_canvas)
        
        self.entity_canvas = EntityCanvas(canvas, Rect(0, 0, 800, 680))
        self.entity_canvas.reinit()
        canvas.attach("entities", self.entity_canvas)
        
        self.entity_properties = EntityProperties(properties_editor, Rect(0, 0, 240, 440))
        self.entity_properties.refresh()
        properties_editor.attach("entities", self.entity_properties)

        # Minimap
        self.minimap = MiniMap(None, Rect(1040, 512, 240, 240), self.layer_canvas)
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
            self.level.tilemap.parallax = []
            
            self.layerpicker.refresh()
            self.layer_canvas.refresh()
            self.entity_canvas.reinit()
            self.entity_properties.refresh()
            self.minimap.update_minimap()
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
        # Format entities as JSON
        entities_json = "["
        for i, entity in enumerate(tilemap.entities):
            entities_json += f'\n\t\t{{"blueprint": "{entity.get("blueprint", "")}", "x": {entity.get("x", 0)}, "y": {entity.get("y", 0)}, "overrides": {{}}}}'
            if i < len(tilemap.entities) - 1:
                entities_json += ","
        entities_json += "\n\t]" if tilemap.entities else "[]"
        
        # Format parallax layers as JSON
        parallax_json = "["
        for i, parallax in enumerate(tilemap.parallax):
            if isinstance(parallax, FixedParallaxData):
                # Get image path from blueprint dict
                blueprint = parallax.blueprint or {}
                image_path = blueprint.get("img", "")
                parallax_json += f'\n\t\t{{"type": "img", "path": "{image_path}"}}'
            elif isinstance(parallax, TilemapParallaxData):
                # Get tilemap name from blueprint dict
                blueprint = parallax.blueprint or {}
                tilemap_name = blueprint.get("name", parallax.tm.name)
                parallax_json += f'\n\t\t{{"type": "tilemap", "name": "{tilemap_name}"}}'
            if i < len(tilemap.parallax) - 1:
                parallax_json += ","
        parallax_json += "\n\t]"
        if tilemap.parallax == []:
            parallax_json = "[]"
        
        string = (
            "{" + "\n" +
            f'\t"size": {[tilemap.width, tilemap.height]},\n' +
            f'\t"bgm": "{tilemap.bgm}",\n' +
            f'\t"bgs": "{tilemap.bgs}",\n' +
            f'\t"tileset": "{tilemap.tileset.name}",\n' +
            f'\t"tiles": {format_grid(tilemap.grid, 1)},\n' +
            f'\t"entities": {entities_json},\n' +
            f'\t"parallax": {parallax_json}\n' +
            "}"
        ).replace("'", "\"")

        with open(os.path.join(config.TILEMAP_FOLDER, f"{tilemap.name}.json"), "w", encoding="utf-8") as f:
            f.write(string)
        
        self.label_info.text = "Tilemap saved"

    def save_level(self, level: Level):
        """Save level data."""
        # Prepare player data
        player_data = None
        if level.player:
            player_data = level.player.overrides.copy() if level.player.overrides else {}
            # Ensure Hitbox is present
            if "Hitbox" not in player_data:
                player_data["Hitbox"] = {"x": 0, "y": 0}
        else:
            player_data = {"Hitbox": {"x": 0, "y": 0}}
        
        with open(os.path.join(config.LEVELS_FOLDER, f"{level.name}.json"), "w", encoding="utf-8") as f:
            f.write(dumps({
                "tilemap": level.tilemap.name,
                "systems": level.systems,
                "player": player_data,
                "camera": {
                    "x": level.camera.centerx if level.camera else 0,
                    "y": level.camera.centery if level.camera else 0
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
            self.layerpicker.refresh()
            self.layer_canvas.refresh()
            self.minimap.update_minimap()
            self.label_info.text = f"Loaded tileset '{name}'"

    def open_tilemap(self):
        """Open a tilemap."""
        filepath = askopenfilename(initialdir=config.TILEMAP_FOLDER, defaultextension=".json")
        if filepath:
            AssetsRegistry.clear_cache()
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap = AssetsRegistry.load_tilemap(name)
            self.layerpicker.refresh()
            self.layer_canvas.refresh()
            self.entity_canvas.reinit()
            self.entity_properties.refresh()
            self.minimap.update_minimap()
            self.label_info.text = f"Loaded tilemap '{name}'"

    def open_level(self):
        """Open a level."""
        filepath = askopenfilename(initialdir=config.LEVELS_FOLDER, defaultextension=".json")
        if filepath:
            AssetsRegistry.clear_cache()
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level = AssetsRegistry.load_level(name, Engine())
            # Ensure parallax list exists
            if self.level.tilemap.parallax is None:
                self.level.tilemap.parallax = []
            self.layerpicker.refresh()
            self.layer_canvas.refresh()
            self.entity_canvas.reinit()
            self.entity_properties.refresh()
            self.minimap.update_minimap()
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
