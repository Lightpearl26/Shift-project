#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
Assets registry lib
version : 1.0
____________________________________________________________________________________________________
Contains assets registry systems
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from __future__ import annotations
from typing import TYPE_CHECKING
from os import listdir
from os.path import join, splitext
from json import load
from pygame import Surface, Rect, Vector2

# import header
from .header import ComponentTypes as C

# import tilemap components
from .level.tilemap import (
    TileData,
    TilesetData,
    TilemapData,
    TilemapParallaxData,
    FixedParallaxData,
    ParallaxData
)

# import entity components
from .level.entity import EntityBlueprint, EntityData, Player

# import level
from .level.level import Level

# import camera
from .level.components import Camera

# import AssetsCache
from .assets_cache import AssetsCache

# import config
from . import config

# import logger
from . import logger

# import ai script parser
from .ecs_core.ai import parse_ai_script

if TYPE_CHECKING:
    from .ecs_core.engine import Engine


# ----- AssetsRegistry ----- #
class AssetsRegistry:
    """
    Registry of all assets of the game
    """
    _tilesets: dict[str, TilesetData] = {}
    _tilemaps: dict[str, TilemapData] = {}
    _parallax: dict[tuple, ParallaxData] = {}
    _blueprints: dict[str, EntityBlueprint] = {}
    _levels: dict[str, Level] = {}
    _ai_scripts: dict[str, dict] = {}

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear registry cache
        """
        cls._tilesets.clear()
        cls._tilemaps.clear()
        cls._parallax.clear()
        cls._levels.clear()
        cls._blueprints.clear()
        cls._ai_scripts.clear()

        logger.debug("AssetsRegistry cache cleared")

    @classmethod
    def load_tileset(cls, tileset_name: str) -> TilesetData:
        """
        Load and return the Tileset named by tileset_name
        If already loaded once return it from cache
        """

        if tileset_name not in cls._tilesets:
            tiles = []
            with open(join(config.TILESET_DATA_FOLDER,f"{tileset_name}.json"),
                    "r",
                    encoding="utf-8") as file:
                data: dict = load(file)
                tsize = data.get("tile_size", 48)
                images = {
                    f: AssetsCache.load_image(join(config.TILESET_GRAPHICS_FOLDER, f))
                    for f in data.get("files")
                }
                tile: dict
                for tile in data.get("tiles"):
                    graphics = tuple(
                        images[tile.get("file")].subsurface(
                            Rect(
                                Vector2(frame)*tsize,
                                Vector2(config.AUTOTILING_SHAPES[tile.get("type", "unique")])*tsize
                            )
                        )
                        for frame in tile.get("frames")
                    )
                    tiles.append(
                        TileData(
                            graphics,
                            size=tsize,
                            hitbox=tile.get("hitbox"),
                            autotilebitmask=tile.get("type"),
                            animation_delay=tile.get("animation_delay", 0.333),
                            blueprint=tile
                        )
                    )
                    logger.debug(f"Tile loaded: {tile}")

            cls._tilesets[tileset_name] = TilesetData(tileset_name, tiles, tsize)
            logger.info(f"Tileset [{tileset_name}] loaded and cached")

        logger.info(f"Tileset [{tileset_name}] loaded successfully")
        return cls._tilesets[tileset_name]

    @classmethod
    def load_parallax(cls, parallax_key: dict) -> ParallaxData:
        """
        Load a parallax with its dict identity
        If already loaded once return it from cache
        """
        key = tuple(parallax_key.items())
        if key not in cls._parallax:
            parallax_type = parallax_key.get("type")

            if parallax_type == "img":
                img: Surface = AssetsCache.load_image(parallax_key.get("path"))
                cls._parallax[key] = FixedParallaxData(img, parallax_key)
            elif parallax_type == "tilemap":
                tm: TilemapData = cls.load_tilemap(parallax_key.get("name"))
                cls._parallax[key] = TilemapParallaxData(tm, parallax_key)
                
            logger.info(f"Parallax [{parallax_key}] loaded and cached")

        logger.info(f"Parallax [{parallax_key}] loaded successfully")
        return cls._parallax[key]

    @classmethod
    def load_tilemap(cls, tilemap_name: str) -> TilemapData:
        """
        Load and return the Tileamp named by tilemap_name
        If already loaded once return it from cache
        """
        if tilemap_name not in cls._tilemaps:
            with open(join(config.TILEMAP_FOLDER, f"{tilemap_name}.json"),
                      "r",
                      encoding="utf-8") as file:
                data: dict = load(file)
                width, height = data.get("size")
                bgm = data.get("bgm")
                bgs = data.get("bgs")
                tileset = cls.load_tileset(data.get("tileset"))
                grid = data.get("tiles")
                parallax = [cls.load_parallax(d) for d in data.get("parallax", [])]

            cls._tilemaps[tilemap_name] = TilemapData(
                tilemap_name,
                width, height,
                tileset,
                bgm,
                bgs,
                grid,
                parallax
            )
            logger.info(f"Tilemap [{tilemap_name}] loaded and cached")

        logger.info(f"Tilemap [{tilemap_name}] loaded successfully")
        return cls._tilemaps[tilemap_name]

    @classmethod
    def load_blueprint(cls, blueprint_name: str) -> EntityBlueprint:
        """
        Load and return the Blueprint named blueprint_name
        If already loaded return it from cache
        """
        if blueprint_name not in cls._blueprints:
            with open(join(config.BLUEPRINTS_FOLDER, f"{blueprint_name}.json"),
                      "r",
                      encoding="utf-8") as file:
                data = load(file)
            cls._blueprints[blueprint_name] = EntityBlueprint(
                blueprint_name,
                data.get("components", []),
                data.get("overrides", {})
            )
            logger.info(f"Blueprint [{blueprint_name}] loaded and cached")

        logger.info(f"Blueprint [{blueprint_name}] loaded successfully")
        return cls._blueprints[blueprint_name]

    @classmethod
    def load_level(cls, level_name: str, engine: Engine) -> Level:
        """
        Load and return the Level named level_name
        If already loaded return it from cache
        """
        with open(join(config.LEVELS_FOLDER, f"{level_name}.json"),
                      "r",
                      encoding="utf-8") as file:
            data: dict = load(file)
        if level_name not in cls._levels:
            tilemap = cls.load_tilemap(data.get("tilemap"))
            systems = data.get("systems", config.SYSTEM_PRIORITY)
            cls._levels[level_name] = Level(
                level_name,
                engine,
                tilemap,
                None,
                None,
                systems,
                []
            )
            logger.info(f"Level [{level_name}] loaded and cached")

        level = cls._levels[level_name]
        engine.reset()
        level.entities.clear()
        level.camera = Camera.from_dict(data.get("camera"))
        level.player = cls.new_entity(
            engine,
            {"name": "player", "sprite": "player", "overrides": data.get("player", {})},
            is_player=True
        )
        for entity_data in data.get("entities", []):
            entity = cls.new_entity(engine, entity_data)
            level.entities.append(entity)

        logger.info(f"Level [{level_name}] loaded successfully")
        return level

    @classmethod
    def new_entity(cls, engine: Engine, entity_data: dict, is_player: bool=False) -> EntityData:
        """
        Create a EntityData from entity_data
        if is_player is True return a Player instance instead
        """
        entity_blueprint = cls.load_blueprint(entity_data.get("name"))
        logger.info(f"Creating entity from blueprint: {entity_blueprint.name}")
        eid = engine.new_entity()
        sprite = None # TODO: sprite handling

        for comp_name in entity_blueprint.components:
            overrides = {
                **entity_blueprint.overrides.get(comp_name, {}),
                **entity_data.get("overrides", {}).get(comp_name, {})
            }
            logger.info(f"Adding component {comp_name} to entity {eid} with overrides {overrides}")
            engine.add_component(eid, C.from_str(comp_name), overrides)

        logger.info(f"Entity [{entity_blueprint.name}] created with eid {eid}")
        if is_player:
            return Player(eid, engine, sprite, entity_data.get("overrides", {}))
        return EntityData(eid, engine, sprite, entity_data.get("overrides", {}))

    @classmethod
    def list_assets(cls, asset_type: str) -> list[str]:
        """
        Return a list of available assets by type (from filesystem).
        asset_type: "tileset" | "tilemap" | "blueprint" | "level"
        """
        if asset_type == "tileset":
            folder = config.TILESET_DATA_FOLDER
            ext = ".json"
        elif asset_type == "tilemap":
            folder = config.TILEMAP_FOLDER
            ext = ".json"
        elif asset_type == "blueprint":
            folder = config.BLUEPRINTS_FOLDER
            ext = ".json"
        elif asset_type == "level":
            folder = config.LEVELS_FOLDER
            ext = ".json"
        else:
            raise ValueError(f"Unknown asset type: {asset_type}")

        return [
            splitext(f)[0]
            for f in listdir(folder)
            if f.endswith(ext)
        ]

    @classmethod
    def list_all_assets(cls) -> dict[str, list[str]]:
        """
        Return the mapping of all avaiable assets
        """
        return {
            asset_type: cls.list_assets(asset_type)
            for asset_type in ["tileset", "tilemap", "blueprint", "level", "ai_script"]
        }

    @classmethod
    def load_ai_script(cls, script_name: str) -> dict:
        """
        Load and return the AI script named by script_name
        If already loaded once return it from cache
        """
        if script_name not in cls._ai_scripts:
            with open(join(config.AI_SCRIPTS_FOLDER, f"{script_name}.ai"),
                    "r",
                    encoding="utf-8") as file:
                script_content = file.read()
                parsed = parse_ai_script(script_content)
                cls._ai_scripts[script_name] = parsed
                logger.debug(f"AI script '{script_name}' loaded and cached")
        return cls._ai_scripts[script_name]
