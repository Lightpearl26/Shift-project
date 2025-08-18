#!venv\Scripts\python.exe
#-*- coding: utf-8 -*-

"""
SHIFT PROJECT - MapEditor
____________________________________________________________________________________________________
project name : Shift Project
authors      : Lafiteau Franck
version      : a0.1
____________________________________________________________________________________________________
This program is a map editor for the game of Shift-Project. All features are open-source and
dedicated to the game. The maps created by this editor can only be loaded by the Shift-Project game.
____________________________________________________________________________________________________
copyrights: (c) Franck Lafiteau
"""

# import external modules
from dataclasses import dataclass
from os import listdir
from os.path import join, basename
from queue import Queue
from tkinter.filedialog import askopenfilename
import math
import pygame

# import ui modules
from libs import logger
from libs.level import EntityLoader
from libs.tile_map import TileMap, TileMapRenderer, AutoTileRenderer, TilesetData
from libs.ecs_components import Camera
from libs.pygame_ui import Frame, UIWidget, SelectorButton, Button, Selector, Popup, Label, TextEntry, TextList


# create constants of the script:
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
ICONS = {
    "brush": pygame.image.load("assets//Editor//brush.png"),
    "fill": pygame.image.load("assets//Editor//fill.png"),
    "rectangle": pygame.image.load("assets//Editor//rectangle.png"),
    "new": pygame.image.load("assets//Editor//new.png"),
    "open": pygame.image.load("assets//Editor//open.png"),
    "save": pygame.image.load("assets//Editor//save.png")
}


# create objects of the script
@dataclass
class EntityData:
    """
    Base of all entity data
    """
    blueprint: str
    sprite: pygame.Surface
    overrides: dict[str, dict] | None = None

    def to_dict(self) -> dict:
        """
        returns dict of the entity to save in map file
        """
        return {
            "name": self.blueprint,
            "overrides": self.overrides
        }


@dataclass
class MapData:
    """
    Map Data class
    """
    tile_map: TileMap
    entities: list[EntityData]
    entity_loader: EntityLoader = EntityLoader(join("assets", "blueprints"))

    @classmethod
    def load(cls, name: str):
        """
        loads map data from map name
        """
        tile_map = TileMap.load(name)
        entities = [
            EntityData(entity["name"], None, entity["overrides"])
            for entity in tile_map.entities
        ]
        return cls(tile_map, entities)

    def save(self) -> None:
        """
        Save map data in filename
        """
        filename = join("assets", "Tilemaps", f"{self.tile_map.name}.json")
        with open(filename, "w", encoding="utf-8") as file:
            data = {
                "size": [self.tile_map.width, self.tile_map.height],
                "bgm": self.tile_map.bgm,
                "bgs": self.tile_map.bgs,
                "tileset": self.tile_map.tileset.name,
                "tiles": self.tile_map.grid,
                "entities": [entity.to_dict() for entity in self.entities]
            }
            file.write("{\n")
            file.write(f"\t\"size\": {data["size"]},\n")
            file.write(f"\t\"bgm\": \"{data["bgm"]}\",\n")
            file.write(f"\t\"bgs\": \"{data["bgs"]}\",\n")
            file.write(f"\t\"tileset\": \"{data["tileset"]}\",\n")
            file.write("\t\"tiles\": ")
            formated = (
                "[\n\t\t"
                + ",\n\t\t".join(
                    "[" + ", ".join(f"{t:2d}" for t in line) + "]"
                    for line in data["tiles"]
                )
                + "\n\t],\n"
            )
            file.write(formated)
            file.write("\t\"entities\": [")
            if data["entities"]:
                file.write("\n")
                for i, entity in enumerate(data["entities"]):
                    if i == len(data["entities"])-1:
                        file.write(f"\t\t{entity}\n")
                    else:
                        file.write(f"\t\t{entity},\n")
                file.write("\t]\n")
            else:
                file.write("]\n")
            file.write("}")
        logger.info(f"Map [{self.tile_map.name}] succesfully saved")


class MapCanvas(Frame):
    """
    Instance of map canvas widget
    """
    def __init__(self, parent: UIWidget, rect: pygame.Rect, map_data: MapData) -> None:
        Frame.__init__(self, parent, rect, bg_color=(57, 61, 71))
        self.map_data = map_data
        self.map_renderer: TileMapRenderer = TileMapRenderer()
        self.map_camera: Camera = Camera(rect=pygame.Rect(0, 0, 0, 0))
        self.painting = False
        self.erasing = False
        self.reload_surface()

    def reload_surface(self) -> None:
        """
        reload surface with new map infos
        """
        width = max(self.rect.width,
                    self.map_data.tile_map.width*self.map_data.tile_map.tileset.tile_size)
        height = max(self.rect.height,
                     self.map_data.tile_map.height*self.map_data.tile_map.tileset.tile_size)
        self.size = (width, height)
        self.surface = pygame.Surface(self.size, pygame.HWSURFACE)

    def load_map(self, name: str) -> None:
        """
        load a man from name
        """
        self.map_data = MapData.load(name)
        self.reload_surface()

    def update(self, dt: float) -> None:
        """
        appli brush if painting
        """
        pos = pygame.mouse.get_pos()
        tile_size = self.map_data.tile_map.tileset.tile_size
        if self.hover:
            new_pos = (pos[0]-self.rect.x + self.scroll.x,
                       pos[1]-self.rect.y + self.scroll.y)
            tile_x = int(new_pos[0] // tile_size)
            tile_y = int(new_pos[1] // tile_size)
            if 0 <= tile_x < self.map_data.tile_map.width and\
            0 <= tile_y < self.map_data.tile_map.height:
                if self.painting:
                    self.map_data.tile_map.grid[tile_y][tile_x] = self.parent.tile_picker.tile_selected
                if self.erasing:
                    self.map_data.tile_map.grid[tile_y][tile_x] = -1

    def fill(self):
        """
        do fill algorithm
        """
        tiles = Queue()
        pos = pygame.mouse.get_pos()
        tile_size = self.map_data.tile_map.tileset.tile_size
        tile_x = int((pos[0]-self.rect.x+self.scroll.x)//tile_size)
        tile_y = int((pos[1]-self.rect.y+self.scroll.y)//tile_size)
        target = int(self.map_data.tile_map.grid[tile_y][tile_x])
        tiles.put((tile_x, tile_y))

        while not tiles.empty():
            tile_x, tile_y = tiles.get()
            if 0 <= tile_x < self.map_data.tile_map.width and\
               0 <= tile_y < self.map_data.tile_map.height:
                if self.map_data.tile_map.grid[tile_y][tile_x] == target:
                    self.map_data.tile_map.grid[tile_y][tile_x] = self.parent.tile_picker.tile_selected
                    tiles.put((tile_x-1, tile_y))
                    tiles.put((tile_x+1, tile_y))
                    tiles.put((tile_x, tile_y-1))
                    tiles.put((tile_x, tile_y+1))

    def handle_mouse_event(self, event):
        Frame.handle_mouse_event(self, event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            if self.parent.tool_bar.selected == "brush":
                self.painting = True

            elif self.parent.tool_bar.selected == "fill":
                self.fill()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.hover:
            if self.parent.tool_bar.selected == "brush":
                self.erasing = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.painting = False
            self.erasing = False

    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        self.surface.fill(self.bg_color)
        map_width = self.map_data.tile_map.width*self.map_data.tile_map.tileset.tile_size
        map_height = self.map_data.tile_map.height*self.map_data.tile_map.tileset.tile_size
        map_rect = pygame.Rect(0, 0, map_width, map_height)
        self.surface.fill((255, 255, 255), map_rect)
        self.map_renderer.render(self.map_data.tile_map, self.surface, self.map_camera)

        surface_rect = pygame.Rect(self.scroll, self.rect.size)
        surface.blit(self.surface.subsurface(surface_rect), self.rect)

        self.draw_scrollbar(surface)

        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(2, 2), width=2)


class TilePicker(Frame):
    """
    Instance of the tile picker widget
    """
    def __init__(self, parent: UIWidget, rect: pygame.Rect, map_data: MapData):
        self.map_data = map_data
        self.tile_selected: int = -1
        self.tile_renderer: AutoTileRenderer = AutoTileRenderer()
        Frame.__init__(self, parent, rect, bg_color=(57, 61, 71))
        self.reload_surface()

    def reload_surface(self) -> None:
        """
        reload surface with map data
        """
        self.widgets.clear()
        tiles = self.map_data.tile_map.tileset.tiles
        tile_size = self.map_data.tile_map.tileset.tile_size
        cols = max(1, self.rect.width // tile_size)
        rows = math.ceil(len(tiles) / cols)
        width = max(cols * tile_size, self.rect.width)
        height = max(rows * tile_size, self.rect.height)
        self.size = (width, height)
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)

        for tile_id, tile in enumerate(tiles):
            name = str(tile_id)
            icon = self.tile_renderer.render(tile, [0, 0, 0, 0, 0, 0, 0, 0])
            pos = (
                tile_id % cols * tile_size,
                tile_id // cols * tile_size
            )
            SelectorButton(
                self,
                pygame.Rect(pos, (tile_size, tile_size)),
                name,
                icon,
                self.select_tile,
                hover_color=None,
                active_color=None
            )

    def select_tile(self, tile_id: str) -> None:
        """
        select a tile
        """
        self.tile_selected = int(tile_id)
        for btn in self.widgets:
            if isinstance(btn, SelectorButton):
                btn.active = btn.name == tile_id
        logger.info(f"Tile {tile_id} selected")

    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return
        self.surface.fill(self.bg_color)

        for btn in self.widgets:
            btn.render(self.surface)
            if btn.active:
                halo = pygame.Surface((self.map_data.tile_map.tileset.tile_size,)*2,
                                      pygame.SRCALPHA)
                halo.fill((155, 255, 55, 80))
                self.surface.blit(halo, btn.rect)
                pygame.draw.rect(
                    self.surface,
                    (0, 0, 0),
                    btn.rect,
                    width=2
                )
            elif btn.hover:
                pygame.draw.rect(
                    self.surface,
                    (0, 0, 0),
                    btn.rect,
                    width=2
                )

        surface_rect = pygame.Rect(self.scroll, self.rect.size)
        surface.blit(self.surface.subsurface(surface_rect), self.rect)

        self.draw_scrollbar(surface)

        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(2, 2), width=2)



class MapEditor(Frame):
    """
    Instance of the map editor
    """
    def __init__(self, map_name: str) -> None:
        # initialize screen
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE, pygame.SRCALPHA)
        pygame.display.set_caption("Shift project - MapEditor")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # loading map
        self.map_data: MapData = MapData.load(map_name)

        # create editor states
        self.running: bool = True

        # create ui
        Frame.__init__(self, None, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.icon_bar: Frame = Frame(self, pygame.Rect(0, 0, SCREEN_WIDTH, 48), bg_color=(218, 112, 214))
        self.map_canvas: MapCanvas = MapCanvas(self, pygame.Rect(3*48, 48, SCREEN_WIDTH-3*48, SCREEN_HEIGHT-48), self.map_data)
        self.tile_picker: TilePicker = TilePicker(self, pygame.Rect(0, 48, 3*48, SCREEN_HEIGHT-48), self.map_data)

        self.file_bar: Frame = Frame(self.icon_bar, pygame.Rect(0, 0, 120, 48))
        self.new_button: Button = Button(
            self.file_bar,
            (8, 8),
            bg_pressed_color=(106, 0, 102),
            bg_image=ICONS["new"].convert_alpha(),
            bg_hover_image=ICONS["new"].convert_alpha(),
            bg_pressed_image=ICONS["new"].convert_alpha(),
            callback=(self.new_map, {})
        )
        self.open_button: Button = Button(
            self.file_bar,
            (48, 8),
            bg_pressed_color=(106, 0, 102),
            bg_image=ICONS["open"].convert_alpha(),
            bg_hover_image=ICONS["open"].convert_alpha(),
            bg_pressed_image=ICONS["open"].convert_alpha(),
            callback=(self.load_map, {})
        )
        self.save_button: Button = Button(
            self.file_bar,
            (88, 8),
            bg_pressed_color=(106, 0, 102),
            bg_image=ICONS["save"].convert_alpha(),
            bg_hover_image=ICONS["save"].convert_alpha(),
            bg_pressed_image=ICONS["save"].convert_alpha(),
            callback=(self.map_data.save, {})
        )
        self.tool_bar: Selector = Selector(self.icon_bar,
                                           pygame.Rect(160, 0, 600, 48),
                                           [
                                               ("brush", ICONS["brush"].convert_alpha()),
                                               ("fill", ICONS["fill"].convert_alpha()),
                                               ("rectangle", ICONS["rectangle"].convert_alpha())
                                            ],
                                           orientation="horizontal",
                                           bg_color=(218, 112, 214))

    def handle_events(self):
        """
        handle pygame events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.handle_event(event)

    def load_map(self) -> None:
        """
        loads an existing map
        """
        filename = askopenfilename(initialdir=join("assets", "Tilemaps"))
        name = basename(filename)[:-5]
        self.map_data = MapData.load(name)
        self.map_canvas.map_data = self.map_data
        self.map_canvas.reload_surface()
        self.tile_picker.map_data = self.map_data
        self.save_button.callback = self.map_data.save

    def new_map(self) -> None:
        """
        Create a new map
        """
        tileset_names = listdir(join("assets", "Tilesets"))
        popup_rect = pygame.Rect(0, 0, 1000, 700)
        popup_rect.center = self.screen.get_rect().center
        font = pygame.font.SysFont(None, 24)
        map_infos_popup = Popup(self.screen,
                                rect=popup_rect,
                                title="Nouvelle Map")

        Label(map_infos_popup, (50, 50), "Nom :", font, (0, 0, 0))
        name_entry = TextEntry(map_infos_popup, pygame.Rect(110, 40, 300, 30), font)
        Label(map_infos_popup, (50, 100), "Taille :", font, (0, 0, 0))
        width_entry = TextEntry(map_infos_popup, pygame.Rect(120, 90, 100, 30), font)
        Label(map_infos_popup, (230, 100), "x", font, (0, 0, 0))
        height_entry = TextEntry(map_infos_popup, pygame.Rect(250, 90, 100, 30), font)
        Label(map_infos_popup, (50, 150), "Tileset :", font, (0, 0, 0))
        tileset_list = TextList(map_infos_popup, (120, 145), 300, tileset_names, font)
        Button(map_infos_popup, (850, 500), "Créer", (100, 50), font, (255, 255, 255), (255, 255, 255), (0, 0, 0), (155, 255, 55), (255, 155, 55), (200, 200, 200), callback=(lambda: setattr(map_infos_popup, "running", False), {}))

        map_infos_popup.run()

        width = int(width_entry.text)
        height = int(height_entry.text)
        tileset = TilesetData.load(tileset_list.selected_text)
        tile_map = TileMap(name_entry.text, width, height, tileset, "", "", [[-1 for _ in range(width)]for _ in range(height)], [])
        self.map_data = MapData(tile_map, [])
        self.map_canvas.map_data = self.map_data
        self.map_canvas.reload_surface()
        self.tile_picker.map_data = self.map_data
        self.save_button.callback = self.map_data.save

    def update(self, dt: float) -> None:
        """
        update editor logic
        """
        # update tile animation
        for tile in self.map_data.tile_map.tileset.tiles:
            tile.animation_time_left -= dt
            if tile.animation_time_left <= 0:
                tile.animation_frame = (tile.animation_frame + 1) % len(tile.graphics)
                tile.animation_time_left += tile.animation_delay

        # update map canvas
        self.map_canvas.update(dt)

    def run(self) -> None:
        """
        runs editor
        """
        while self.running:
            dt: float = self.clock.tick(60) / 1000
            self.handle_events()
            self.update(dt)
            self.screen.fill((0, 0, 0))
            for widget in self.widgets:
                widget.render(self.screen)
            pygame.display.flip()


# create functions of the script
def main() -> None:
    """
    Main function of the script
    """
    logger.info("Starting Editor")
    editor = MapEditor("empty")
    logger.info("Initialization of Editor completed")
    editor.run()


# launching script
if __name__ == "__main__":
    main()
