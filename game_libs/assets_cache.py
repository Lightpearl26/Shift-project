#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
Assets cache lib
version : 1.0
____________________________________________________________________________________________________
Contains assets cache systems
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from pygame import Surface, font
from pygame.image import load as img_load
from pygame.mixer import Sound

# import logger
from . import logger


# ----- GraphicsCache ----- #
class AssetsCache:
    """
    Cache of all loaded graphics
    """
    _images: dict[str, Surface] = {}
    _sounds: dict[str, Sound] = {}
    _fonts: dict[tuple[str, int], font.Font] = {}

    @classmethod
    def load_image(cls, filepath: str) -> Surface:
        """
        Load an image and put it in cache if not already loaded
        If the filepath has already been loaded then returns the corresponding Surface
        """
        if not filepath in cls._images:
            cls._images[filepath] = img_load(filepath).convert_alpha()
            logger.info(f"Image loaded and cached: {filepath}")

        logger.debug(f"Image loaded from cache: {filepath}")

        return cls._images[filepath]

    @classmethod
    def load_sound(cls, filepath: str) -> Sound:
        """
        Load a sound and put it in cache if not already loaded
        If the filepath has already been loaded then returns the corresponding Sound
        """
        if not filepath in cls._sounds:
            cls._sounds[filepath] = Sound(filepath)
            logger.info(f"Sound loaded and cached: {filepath}")

        logger.debug(f"Sound loaded from cache: {filepath}")

        return cls._sounds[filepath]

    @classmethod
    def load_font(cls, filepath: str, size: int) -> font.Font:
        """
        Load a font and put it in cache if not already loaded
        If the (filepath, size) has already been loaded then returns the corresponding Font
        """
        if not font.get_init():
            font.init()
        key = (filepath, size)
        if key not in cls._fonts:
            cls._fonts[key] = font.Font(filepath, size)
            logger.info(f"Font loaded and cached: {filepath} (size: {size})")

        logger.debug(f"Font loaded from cache: {filepath} (size: {size})")

        return cls._fonts[key]
