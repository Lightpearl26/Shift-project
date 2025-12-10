# -*- coding: utf-8 -*-

"""
SHIFT PROJECT - Map Editor
____________________________________________________________________________________________________
Main Editor Application (UI Layout)
____________________________________________________________________________________________________
"""

from __future__ import annotations

import os
from typing import Optional
from json import dumps

from tkinter.filedialog import asksaveasfilename, askopenfilename

import pygame
from pygame import MOUSEBUTTONDOWN, NOFRAME, QUIT, Rect, Vector2, display, time

from game_libs import config
from game_libs.assets_registry import AssetsRegistry
from game_libs.ecs_core.engine import Engine
from game_libs.level.components import Camera
from game_libs.level.tilemap import TilesetData, TilemapData, FixedParallaxData, TilemapParallaxData
from game_libs.rendering.tilemap_renderer import TilemapRenderer, TileRenderer
from game_libs.header import (Level, TileData)
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


# ----- usefull functions ----- #
def inline_dict(value: dict) -> str:
    """
    Format a dictionary into a single-line string for display.
    Strings are quoted.
    """
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
    """
    Format a 2D grid into a string for display.
    """
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


# ----- TilePicker ----- #
class TilePicker(Frame):
    """
    A tile picker widget to select tiles from a tileset.
    Peut fonctionner avec n'importe quelle tilemap (None = tilemap principale).
    """
    def __init__(self, parent: Optional[UIWidget], rect: Rect, tilemap=None):
        super().__init__(parent, rect)
        self.logger = self.app.label_info
        self.selected: int = -1
        self.hovered: int = -1
        self.tilemap = tilemap  # None = tilemap principale
        self._update_size()

    def set_tilemap(self, tilemap):
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
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)

    def handle_event(self, event):
        if not self.displayed:
            return False
        tilemap = self.get_tilemap()
        tile_size = tilemap.tileset.tile_size
        tiles_per_row = max(1, self.rect.width // tile_size)
        n_tiles = len(tilemap.tileset.tiles)

        # Calcul de la position de la souris dans la surface interne (avec scroll)
        if self.hover and event.type == pygame.MOUSEMOTION:
            pos = Vector2(event.pos) - Vector2(self.global_rect.topleft) + self.scroll
            x = int(pos.x // tile_size)
            y = int(pos.y // tile_size)
            idx = int(y * tiles_per_row + x)
            if 0 <= idx < n_tiles:
                self.hovered = idx
            else:
                self.hovered = -1
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

        # Met à jour la taille si besoin
        self._update_size()

        # Efface la surface interne
        self.surface.fill(self.app.theme.colors["bg"])

        # Blit les tiles sur la surface interne
        for idx, tile in enumerate(tilemap.tileset.tiles):
            x = (idx % tiles_per_row) * tile_size
            y = (idx // tiles_per_row) * tile_size
            self.surface.blit(TileRenderer.render(tile, [False]*8), (x, y))
            rect_tile = pygame.Rect(x, y, tile_size, tile_size)
            if idx == self.selected:
                pygame.draw.rect(
                    self.surface,
                    self.app.theme.colors["accent"],
                    rect_tile,
                    2
                )
            elif idx == self.hovered:
                pygame.draw.rect(
                    self.surface,
                    self.app.theme.colors["hover"],
                    rect_tile,
                    2
                )

        # Le reste (scrollbars, bordure) est déjà géré par Frame.render()
        surface_rect = Rect(self.scroll, self.rect.size)
        surface.blit(self.surface.subsurface(surface_rect), self.rect)

        self.draw_scrollbars(surface)
        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(2, 2), 2)


# ----- MapCanvas ----- #
class MapCanvas(Frame):
    """
    A map canvas widget to display and edit a tilemap.
    Peut fonctionner avec n'importe quelle tilemap (None = tilemap principale).
    """
    def __init__(self, parent: Optional[UIWidget], rect: Rect, tilemap=None):
        Frame.__init__(self, parent, rect)
        self.logger = self.app.label_info
        self.tilemap = tilemap  # None = tilemap principale
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

    def set_tilemap(self, tilemap):
        self.tilemap = tilemap
        self.reinit()

    def get_tilemap(self):
        return self.tilemap if self.tilemap is not None else self.app.level.tilemap

    def reinit(self):
        """
        Reinit map canvas
        """
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

    @property
    def camera(self) -> Camera:
        return Camera(
            Vector2(self.scroll.x + self.rect.width // 2, self.scroll.y + self.rect.height // 2),
            (self.rect.width, self.rect.height)
        )

    def fill(self, event: pygame.event.Event):
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
            self.logger.text = f"Filled {len(filled)} tiles with tile {replacement_tile}"

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
                    x1 = min(self.rect_start.x, x)
                    x2 = max(self.rect_start.x, x)
                    y1 = min(self.rect_start.y, y)
                    y2 = max(self.rect_start.y, y)
                    if self.tile_picker.selected != -1:
                        for iy in range(int(y1), int(y2)+1):
                            for ix in range(int(x1), int(x2)+1):
                                tm.grid[iy][ix] = self.tile_picker.selected
                        self.logger.text = f"Painted rectangle from ({int(x1)}, {int(y1)}) to ({int(x2)}, {int(y2)}) with tile {self.tile_picker.selected}"
                self.estimating_rect = False
                self.rect_start = None
                self.app.minimap.update_minimap()

        if self.focus and event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.erasing = False

        if self.painting:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
            y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
            if 0 <= x < tm.width and 0 <= y < tm.height:
                if self.tile_picker.selected != -1:
                    tm.grid[y][x] = self.tile_picker.selected
                    self.logger.text = f"Painted tile {self.tile_picker.selected} at ({x}, {y})"
            self.app.minimap.update_minimap()

        if self.erasing:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
            y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
            if 0 <= x < tm.width and 0 <= y < tm.height:
                tm.grid[y][x] = -1
                self.logger.text = f"Erased tile at ({x}, {y})"
            self.app.minimap.update_minimap()
        return super().handle_event(event)

    def render(self, surface):
        if not self.displayed:
            return
        tm = self.get_tilemap()
        self.surface.fill((0, 0, 0, 0))
        TilemapRenderer.clear_cache()
        TilemapRenderer.render(tm, self.surface, self.camera, 0.0)
        surface.blit(self.surface, self.rect)

        # Render tile highlighter
        if self.estimating_rect and self.rect_start is not None:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            x = int((mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size)
            y = int((mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size)
            if 0 <= x < tm.width and 0 <= y < tm.height:
                x1 = min(self.rect_start.x, x)
                x2 = max(self.rect_start.x, x)
                y1 = min(self.rect_start.y, y)
                y2 = max(self.rect_start.y, y)
                pygame.draw.rect(
                    surface,
                    self.app.theme.colors["accent"],
                    Rect(
                        Vector2(x1, y1) * tm.tileset.tile_size - Vector2(self.scroll) + Vector2(self.rect.topleft),
                        ((x2 - x1 + 1) * tm.tileset.tile_size, (y2 - y1 + 1) * tm.tileset.tile_size)
                    ),
                    2
                )
        else:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            x = int(
                (mouse_pos.x - self.global_rect.left + self.scroll.x) // tm.tileset.tile_size
            )
            y = int(
                (mouse_pos.y - self.global_rect.top + self.scroll.y) // tm.tileset.tile_size
            )
            if 0 <= x < tm.width and 0 <= y < tm.height:
                pygame.draw.rect(
                    surface,
                    self.app.theme.colors["accent"],
                    Rect(
                        Vector2(x, y) * tm.tileset.tile_size - Vector2(self.scroll) + Vector2(self.rect.topleft),
                        (tm.tileset.tile_size, tm.tileset.tile_size)
                    ),
                    2
                )

        self.draw_scrollbars(surface)


# ----- Tile Properties Editor ----- #
class TilePropertiesEditor(Frame):
    """
    A properties editor for tiles.
    """
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
                        raise ValueError("Invalid bitmask value")
                    if bitmask != tile.autotilebitmask:
                        tile.autotilebitmask = bitmask
                        self.logger.text = f"Set bitmask of tile {self.selected_tile} to {bitmask}"
                except ValueError:
                    self.logger.text = "Error: Invalid bitmask value: must"
                    self.logger.text += " be in ['unique', 'field', 'fall', 'wall']"
                try:
                    hitbox = int(self.hitbox_editor.text)
                    if hitbox not in [0, 1]:
                        raise ValueError("Hitbox must be 0 or 1")
                    if hitbox != tile.hitbox:
                        tile.hitbox = hitbox
                        self.logger.text = "Set hitbox of"
                        self.logger.text += f" tile {self.selected_tile} to {tile.hitbox}"
                except ValueError:
                    self.logger.text = "Error: Hitbox must be an integer (0 or 1)"
                try:
                    animation_delay = float(self.animation_delay_editor.text)
                    if animation_delay != tile.animation_delay:
                        tile.animation_delay = animation_delay
                        self.logger.text = "Set animation delay of tile "
                        self.logger.text += f"{self.selected_tile} to {animation_delay}"
                except ValueError:
                    self.logger.text = "Error: Animation delay must be a float number"
            TileRenderer.clear_cache()  # Clear cache to force re-render
        return super().handle_event(event)

    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        self.surface.fill(self.app.theme.colors["bg"])

        if self.app.tile_picker.selected != self.selected_tile:
            tile = self.app.level.tilemap.tileset.tiles[self.app.tile_picker.selected]
            self.bitmask_editor.text = str(tile.autotilebitmask)
            self.bitmask_editor.cursor_pos = len(self.bitmask_editor.text)
            self.hitbox_editor.text = str(tile.hitbox)
            self.hitbox_editor.cursor_pos = len(self.hitbox_editor.text)
            self.animation_delay_editor.text = str(tile.animation_delay)
            self.animation_delay_editor.cursor_pos = len(self.animation_delay_editor.text)
            self.selected_tile = self.app.tile_picker.selected

        Frame.render(self, surface)


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
        names += [f"Parallax {i+1}" for i in range(len(self.app.level.tilemap.parallax))]
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
        for i, parallax in enumerate(self.app.level.tilemap.parallax):
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
        name_entry_tilemap = TextEntry(tilemap_frame, Rect(60, 8, 200, 24), default_text=f"Parallax {len(self.app.level.tilemap.parallax)+1}")
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
                name = name_entry_tilemap.text or f"Parallax {len(self.app.level.tilemap.parallax)+1}"
                width = int(width_entry.text or "40")
                height = int(height_entry.text or "23")
                tileset = AssetsRegistry.load_tileset(tileset.get_text())
                tilemap = TilemapData(name, width, height, tileset, "", "", [[-1 for _ in range(width)] for _ in range(height)], [], [])
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


# ----- LayerCanvas (placeholder) ----- #
class LayerCanvas(Frame):
    """
    A canvas to display the selected layer in the LayerPicker.
    """
    def __init__(self, parent: Optional[UIWidget], rect: Rect):
        super().__init__(parent, rect)
        self.tabbed = TabbedFrame(self, Rect(0, 0, rect.width, rect.height), self.app.layerpicker.listview)
        self.refresh()
        
    def refresh(self):
        """
        Refresh the canvases based on the selected layer.
        """
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


# ----- MiniMap ----- #
class MiniMap(Frame):
    """
    A minimap widget to display a small overview of the map, ratio preserved and centered.
    """
    def __init__(self, parent, rect, map_canvas: MapCanvas):
        super().__init__(parent, rect)
        self.map_canvas = map_canvas
        self.app_ref = self.map_canvas.app
        tile_size = self.app.level.tilemap.tileset.tile_size
        width = self.app.level.tilemap.width * tile_size
        height = self.app.level.tilemap.height * tile_size
        self._cache = None

        # Camera covering the entire map, centered
        self.camera = Camera(
            Vector2(width // 2, height // 2),
            (width, height)
        )
        self._minimap_surface = None

    def reinit(self):
        """
        Reinit minimap
        """
        tile_size = self.app.level.tilemap.tileset.tile_size
        width = self.app.level.tilemap.width * tile_size
        height = self.app.level.tilemap.height * tile_size
        self._cache = None

        # Camera covering the entire map, centered
        self.camera = Camera(
            Vector2(width // 2, height // 2),
            (width, height)
        )
        self._minimap_surface = None

    def update_minimap(self):
        """
        Update the minimap surface by rendering the full map scaled to fit the minimap rect.
        """
        tile_size = self.app.level.tilemap.tileset.tile_size
        map_w = self.app.level.tilemap.width * tile_size
        map_h = self.app.level.tilemap.height * tile_size

        # Calculate scale ratio to fit the minimap rect
        scale_w = self.rect.width / map_w
        scale_h = self.rect.height / map_h
        scale = min(scale_w, scale_h)
        new_w = int(map_w * scale)
        new_h = int(map_h * scale)
        self._cache = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        TilemapRenderer.clear_cache()
        TilemapRenderer.render(self.app.level.tilemap, self._cache, self.camera, 0.0)
        self._cache = pygame.transform.smoothscale(self._cache, (new_w, new_h))

        # Create the minimap surface and center the scaled map
        minimap_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        x = (self.rect.width - new_w) // 2
        y = (self.rect.height - new_h) // 2
        minimap_surf.blit(self._cache, (x, y))
        self._minimap_surface = minimap_surf

    def center_camera(self, event: pygame.event.Event):
        """
        Center the MapCanvas camera on the clicked position in the minimap.
        """
        mouse_pos = Vector2(event.pos) - Vector2(self.global_rect.topleft)
        tile_size = self.app.level.tilemap.tileset.tile_size
        map_w = self.app.level.tilemap.width * tile_size
        map_h = self.app.level.tilemap.height * tile_size
        scale_w = self.rect.width / map_w
        scale_h = self.rect.height / map_h
        scale = min(scale_w, scale_h)
        new_w = int(map_w * scale)
        new_h = int(map_h * scale)
        x_offset = (self.rect.width - new_w) // 2
        y_offset = (self.rect.height - new_h) // 2
        if x_offset <= mouse_pos.x <= x_offset + new_w and y_offset <= mouse_pos.y <= y_offset + new_h:
            # Calculate the position in the full map coordinates
            relative_x = (mouse_pos.x - x_offset) / scale
            relative_y = (mouse_pos.y - y_offset) / scale
            # Center the MapCanvas camera on that position
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
        tile_size = self.app.level.tilemap.tileset.tile_size
        map_w = self.app.level.tilemap.width * tile_size
        map_h = self.app.level.tilemap.height * tile_size
        scale_w = self.rect.width / map_w
        scale_h = self.rect.height / map_h
        scale = min(scale_w, scale_h)
        new_w = int(map_w * scale)
        new_h = int(map_h * scale)
        x = (self.rect.width - new_w) // 2
        y = (self.rect.height - new_h) // 2
        pygame.draw.rect(
            surface,
            self.app.theme.colors["accent"],
            Rect(
                self.map_canvas.camera.topleft*scale + Vector2(x, y),
                Vector2(self.map_canvas.camera.size)*scale
            ).move(self.rect.topleft),
            2
        )
        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(2, 2), 2)


# ----- MapEditor Application ----- #
class LevelEditor(UIApp):
    """
    The main level editor application."""
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
        menubar = Menubar(None, width=1280)
        overlay_layer.add(menubar)
        level = menubar.add_dropdown("Level")
        level.add_option("Open", self.open_level)
        level.add_option("Save", lambda: self.save_level(self.level))
        level.add_option("Save as", self.save_level_as)
        tilemap = menubar.add_dropdown("Tilemap")
        tilemap.add_option("Open", self.open_tilemap)
        tilemap.add_option("Save", lambda: self.save_tilemap(self.level.tilemap))
        tilemap.add_option("Save as", self.save_tilemap_as)
        tileset = menubar.add_dropdown("Tileset")
        tileset.add_option("Open", self.open_tileset)
        tileset.add_option("Save", lambda: self.save_tileset(self.level.tilemap.tileset))
        tileset.add_option("Save as", self.save_tileset_as)

        # Toolbar
        toolbar = Frame(parent=None, rect=Rect(0, 24, size[0], 48))
        main_layer.add(toolbar)
        # File management buttons
        IconButton(toolbar, Rect(0, 0, 48, 48), new_icon, self.new_level)
        IconButton(toolbar, Rect(48, 0, 48, 48), open_icon, self.open_level)
        IconButton(toolbar, Rect(96, 0, 48, 48), save_icon, self.save_file)

        # Tools selector (brush, fill, rect)
        self.tools_selector = Selector(
            toolbar,
            (240, 0),
            {"brush":brush_icon, "fill": fill_icon, "rect": rect_icon}
        )
        self.tools_selector.selected_index = 0

        # Edition tabs (tilemap, entities, layers)
        edition = Selector(
            toolbar,
            (896, 0),
            {"tilemap": tilemap_icon, "entities": entity_icon, "layers": layer_icon}
        )
        edition.selected_index = 0


        # Main area frames
        # Picker (left)
        picker = TabbedFrame(
            parent=None,
            rect=Rect(0, 72, 240, 680),
            selector=edition
        )
        main_layer.add(picker)
        # Canvas (center)
        canvas = TabbedFrame(
            parent=None,
            rect=Rect(240, 72, 800, 680),
            selector=edition
        )
        main_layer.add(canvas)
        # PropertiesEditor (right)
        properties_editor = TabbedFrame(
            parent=None,
            rect=Rect(1040, 72, 240, 440),
            selector=edition
        )
        main_layer.add(properties_editor)

        # InfoBar (bottom)
        infobar = Frame(parent=None, rect=Rect(0, 752, size[0], 48))
        main_layer.add(infobar)
        self.label_info = Label(infobar, (10, 10), "Ready.")
        
        # Edition tilemap
        self.tile_picker = TilePicker(picker, Rect(0, 0, 240, 680))
        picker.attach("tilemap", self.tile_picker)
        self.map_canvas = MapCanvas(canvas, Rect(0, 0, 800, 680))
        canvas.attach("tilemap", self.map_canvas)
        self.tile_properties = TilePropertiesEditor(properties_editor, Rect(0, 0, 240, 440))
        properties_editor.attach("tilemap", self.tile_properties)

        # Edition layers
        self.layerpicker = LayerPicker(picker, Rect(0, 0, 240, 680))
        picker.attach("layers", self.layerpicker)
        self.layer_properties = LayerProperties(properties_editor, Rect(0, 0, 240, 440))
        properties_editor.attach("layers", self.layer_properties)
        self.layer_canvas = LayerCanvas(canvas, Rect(0, 0, 800, 680))
        canvas.attach("layers", self.layer_canvas)

        # MiniMap (right, below properties)
        self.minimap = MiniMap(None, Rect(1040, 512, 240, 240), self.map_canvas)
        main_layer.add(self.minimap)

    def new_level(self):
        """
        Create a new level
        """
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
        tileset_list = DropdownList(popup, (150, 130), AssetsRegistry.list_assets("tileset"))
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
            self.map_canvas.reinit()
            self.minimap.reinit()
            self.layerpicker.refresh()
            self.label_info.text = f"Level {level_name} succesfully created"

    def save_tileset(self, tileset: TilesetData):
        """
        Save the tileset data to its JSON file.
        """
        tiles: list[TileData] = [tile for tile in tileset.tiles if tile.blueprint is not None]
        for tile in tiles:
            tile.blueprint.update(
                {
                    "hitbox": tile.hitbox,
                    "type": tile.autotilebitmask,
                    "animation_delay": tile.animation_delay
                }
            )

        string: str = (
            "{" + "\n" +
            f'\t"tile_size": {tileset.tile_size},\n' +
            f'\t"files": {list({
                tile.blueprint["file"]
                for tile in tileset.tiles
                if tile.blueprint is not None
            })},\n' +
            f"\t\"tiles\": [\n\t\t{",\n\t\t".join(
                inline_dict(tile.blueprint) for tile in tiles
            )}" + "\n\t" + "]\n" +
            "}"
        ).replace("'", "\"")

        with open(os.path.join(config.TILESET_DATA_FOLDER, f"{tileset.name}.json"),
                  "w", encoding="utf-8") as file:
            file.write(string)

        self.label_info.text = "Successfully saved Tileset"

    def save_tilemap(self, tilemap: TilemapData):
        """
        Save the tilemap data to its JSON file.
        """
        string = (
            "{" + "\n" +
            f'\t\"size\": {[tilemap.width, tilemap.height]},\n' +
            f'\t"bgm": "{tilemap.bgm}",\n' +
            f'\t"bgs": "{tilemap.bgs}",\n' +
            f'\t"tileset": "{tilemap.tileset.name}",\n' +
            f'\t"tiles": {format_grid(tilemap.grid, 1)},\n' +
            "\t\"entities\": [" + "\n\t\t" * int(len(tilemap.entities) > 0) +
            f"{",\n\t\t".join(
                inline_dict(e) for e in tilemap.entities
            )}" + "\n\t" * int(len(tilemap.entities) > 0) + "],\n" +
            "\t\"parallax\": [" + "\n\t\t" * int(len(tilemap.parallax) > 0) +
            f"{",\n\t\t".join(
                inline_dict(p.blueprint) for p in tilemap.parallax
            )}" + "\n\t" * int(len(tilemap.parallax) > 0) + "]\n" +
            "}"
        ).replace("'", "\"")

        with open(os.path.join(config.TILEMAP_FOLDER, f"{tilemap.name}.json"),
                  "w", encoding="utf-8") as file:
            file.write(string)

        self.label_info.text = "Successfully saved Tilemap"

    def save_level(self, level: Level):
        """
        Save the level data to its JSON file.
        """
        with open(os.path.join(config.LEVELS_FOLDER, f"{level.name}.json"),
                  "w", encoding="utf-8") as file:
            file.write(dumps({
                "tilemap": level.tilemap.name,
                "systems": level.systems,
                "player": level.player.overrides,
                "camera": {
                    "x": level.camera.centerx,
                    "y": level.camera.centery
                }
            }, indent=4))

        self.label_info.text = "Successfully saved Level"

    def save_file(self):
        """
        Save the current level to its opened file
        if level name is "empty", create a temp.json file
        """
        if self.level.name == "empty":
            self.level.name = "temp"
            self.level.tilemap.name = "temp"
            self.level.tilemap.tileset.name = "temp"
        self.save_level(self.level)
        for parallax in self.level.tilemap.parallax:
            if hasattr(parallax, "tm"):
                self.save_tilemap(parallax.tm)
        self.save_tilemap(self.level.tilemap)
        self.save_tileset(self.level.tilemap.tileset)
        self.label_info.text = f"Level '{self.level.name}' saved."

    def save_tileset_as(self):
        """
        Ask Save As to save the tileset in the chosen file
        """
        filepath = asksaveasfilename(initialdir=config.TILESET_DATA_FOLDER,defaultextension=".json")
        if filepath:
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap.tileset.name = name
            self.save_tileset(self.level.tilemap.tileset)

    def save_tilemap_as(self):
        """
        Ask Save As to save the tilemap in the chosen file
        """
        filepath = asksaveasfilename(initialdir=config.TILEMAP_FOLDER, defaultextension=".json")
        if filepath:
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap.name = name
            self.save_tilemap(self.level.tilemap)

    def save_level_as(self):
        """
        Ask Save As to save the level in the chosen file
        """
        filepath = asksaveasfilename(initialdir=config.LEVELS_FOLDER, defaultextension=".json")
        if filepath:
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.name = name
            self.save_level(self.level)

    def open_tileset(self):
        """
        Ask to open a Tileset
        """
        filepath = askopenfilename(initialdir=config.TILESET_DATA_FOLDER,defaultextension=".json")
        if filepath:
            AssetsRegistry.clear_cache()
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap.tileset = AssetsRegistry.load_tileset(name)
            self.map_canvas.reinit()
            self.minimap.reinit()
            self.layerpicker.refresh()
            self.label_info.text = f"Successfully load Tileset {name}"

    def open_tilemap(self):
        """
        Ask to open a Tilemap
        """
        filepath = askopenfilename(initialdir=config.TILEMAP_FOLDER, defaultextension=".json")
        if filepath:
            AssetsRegistry.clear_cache()
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level.tilemap = AssetsRegistry.load_tilemap(name)
            self.map_canvas.reinit()
            self.minimap.reinit()
            self.layerpicker.refresh()
            self.label_info.text = f"Successfully load Tilemap {name}"

    def open_level(self):
        """
        Ask to open a Level
        """
        filepath = askopenfilename(initialdir=config.LEVELS_FOLDER, defaultextension=".json")
        if filepath:
            AssetsRegistry.clear_cache()
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.level = AssetsRegistry.load_level(name, Engine())
            self.map_canvas.reinit()
            self.minimap.reinit()
            self.layerpicker.refresh()
            self.label_info.text = f"Successfully load Level {name}"

    def run(self):
        """
        Run the app
        """
        clock = time.Clock()
        while self.running:
            dt = clock.tick() / 1000
            for e in pygame.event.get():
                if e.type == QUIT:
                    self.running = False
                else:
                    self.handle_events(e)
            tilesets = [AssetsRegistry.load_tileset(ts) for ts in AssetsRegistry.list_assets("tileset")]
            for tileset in tilesets:
                tileset.update_animation(dt)
            self.screen.fill((40, 40, 40))
            self.render(self.screen)
            display.flip()

        self.level.name = "temp"
        self.level.tilemap.name = "temp"
        self.save_file()


if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
    pygame.quit()
