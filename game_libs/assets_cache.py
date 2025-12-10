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
from pygame import Surface
from pygame.image import load as img_load

# import logger
from . import logger


# ----- GraphicsCache ----- #
class AssetsCache:
    """
    Cache of all loaded graphics
    """
    _images: dict[str, Surface] = {}

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
