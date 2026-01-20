# -*- coding: utf-8 -*-

"""
game_libs.transitions.particles_simple
___________________________________________________________________________________________________
File infos:
    - Author: Justine Roux
    - Version: 2.2 (Ultra-simplified)
___________________________________________________________________________________________________
Description:
    Minimalist particle transitions without particle classes.
    Pure data + logic approach for maximum simplicity.
___________________________________________________________________________________________________
@copyright: Justine Roux 2026 (patch by Franck Lafiteau)
"""

# Import built-in modules
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, NamedTuple
from random import uniform
from enum import Enum

# Import pygame components
from pygame.display import get_init
from pygame import Rect

# Import Basetransition
from . import BaseTransition

# Import logger
from .. import logger

if TYPE_CHECKING:
    from pygame import Surface

# ----- Enums & Constants ----- #
Tile = NamedTuple("Tile", [("src_rect", Rect), ("delay", float)])
class Direction(Enum):
    """
    Direction Enum for particle movement.
    """
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    DOWN = (0, 1)
    UP = (0, -1)


# ----- Particle Transition Base Class ----- #
class Particletransition(BaseTransition):
    """
    Base class for particle transitions.
    """
    def __init__(self,
                 direction: Direction = Direction.RIGHT,
                 mode: str = "out",
                 duration: float = 1500,
                 tile_size: int = 10,
                 easing_func: Callable[[float], float] = lambda t: t):
        BaseTransition.__init__(self, duration)
        self.direction = direction
        self.mode = mode
        self.tile_size = tile_size
        self.easing_func = easing_func
        self.tiles: list[Tile] = []
        self.atlas: Surface = None
        logger.info(f"[Particletransition] Initialized with mode: {self.mode},"
                    f" direction: {self.direction},"
                    f" tile_size: {self.tile_size},"
                    f" duration: {self.duration}ms")

    def start(self):
        BaseTransition.start(self)
        self.tiles.clear()
        self.atlas = None

    def _generate(self, surface: Surface):
        """
        Generate particles from surface content.
        """
        if not get_init():
            logger.error("[Particletransition] Pygame display not initialized.")
            return

        self.atlas = surface.convert_alpha()

        width, height = self.atlas.get_size()
        cols = (width + self.tile_size - 1) // self.tile_size
        rows = (height + self.tile_size - 1) // self.tile_size

        for row in range(rows):
            for col in range(cols):
                x = col * self.tile_size
                y = row * self.tile_size
                w = min(self.tile_size, width - x)
                h = min(self.tile_size, height - y)
                src_rect = Rect(x, y, w, h)

                # Calculate delay based on position and randomness
                dx, dy = self.direction.value
                norm = abs(dx) * (x / width) + abs(dy) * (y / height)
                pos_factor = 1.0 - norm if (dx < 0 or dy < 0) else norm
                delay = pos_factor * 0.45 + uniform(0, 0.25)

                self.tiles.append(Tile(src_rect, delay))

        logger.info(f"[Particletransition] Generated {len(self.tiles)} tiles.")

    def render(self, surface):
        """
        Render the particle transition on the given surface.
        """
        if not self._is_playing:
            return

        if not self.atlas:
            self._generate(surface)

        surface.fill((0, 0, 0))  # Clear surface

        for tile in self.tiles:
            t = (self.progress - tile.delay) / (1.0 - tile.delay) if tile.delay < 1.0 else 1.0
            t = max(0.0, min(1.0, t))

            if self.mode == "out" and t == 1.0:
                continue
            if self.mode == "in" and t == 0.0:
                continue

            t = self.easing_func(t)
            dx, dy = self.direction.value
            ox, oy = tile.src_rect.topleft
            if self.mode == "out":
                end_x = (surface.get_width() if dx > 0 else -self.tile_size) if dx != 0 else ox
                end_y = (surface.get_height() if dy > 0 else -self.tile_size) if dy != 0 else oy
                x = ox + (end_x - ox) * t
                y = oy + (end_y - oy) * t
            else:  # mode == "in"
                start_x = (-self.tile_size if dx > 0 else surface.get_width()) if dx != 0 else ox
                start_y = (-self.tile_size if dy > 0 else surface.get_height()) if dy != 0 else oy
                x = start_x + (ox - start_x) * t
                y = start_y + (oy - start_y) * t

            surface.blit(self.atlas, (x, y), tile.src_rect)


# ----- Convienience Subclasses ----- #
class DisintegrateRight(Particletransition):
    """
    Particle transition for 'out' mode.
    """
    def __init__(self,
                 duration: float = 1500,
                 easing_func: Callable[[float], float] = lambda t: t):
        super().__init__(Direction.RIGHT, "out", duration, 10, easing_func)
        logger.info("[DisintegrateRight] Initialized.")

class IntegrateRight(Particletransition):
    """
    Particle transition for 'in' mode.
    """
    def __init__(self,
                 duration: float = 1500,
                 easing_func: Callable[[float], float] = lambda t: t):
        super().__init__(Direction.RIGHT, "in", duration, 10, easing_func)
        logger.info("[IntegrateRight] Initialized.")

class DisintegrateLeft(Particletransition):
    """
    Particle transition for 'out' mode.
    """
    def __init__(self,
                 duration: float = 1500,
                 easing_func: Callable[[float], float] = lambda t: t):
        super().__init__(Direction.LEFT, "out", duration, 10, easing_func)
        logger.info("[DisintegrateLeft] Initialized.")

class IntegrateLeft(Particletransition):
    """
    Particle transition for 'in' mode.
    """
    def __init__(self,
                 duration: float = 1500,
                 easing_func: Callable[[float], float] = lambda t: t):
        super().__init__(Direction.LEFT, "in", duration, 10, easing_func)
        logger.info("[IntegrateLeft] Initialized.")

class DisintegrateDown(Particletransition):
    """
    Particle transition for 'out' mode.
    """
    def __init__(self,
                 duration: float = 1500,
                 easing_func: Callable[[float], float] = lambda t: t):
        super().__init__(Direction.DOWN, "out", duration, 10, easing_func)
        logger.info("[DisintegrateDown] Initialized.")

class IntegrateDown(Particletransition):
    """
    Particle transition for 'in' mode.
    """
    def __init__(self,
                 duration: float = 1500,
                 easing_func: Callable[[float], float] = lambda t: t):
        super().__init__(Direction.DOWN, "in", duration, 10, easing_func)
        logger.info("[IntegrateDown] Initialized.")

class DisintegrateUp(Particletransition):
    """
    Particle transition for 'out' mode.
    """
    def __init__(self,
                 duration: float = 1500,
                 easing_func: Callable[[float], float] = lambda t: t):
        super().__init__(Direction.UP, "out", duration, 10, easing_func)
        logger.info("[DisintegrateUp] Initialized.")

class IntegrateUp(Particletransition):
    """
    Particle transition for 'in' mode.
    """
    def __init__(self,
                 duration: float = 1500,
                 easing_func: Callable[[float], float] = lambda t: t):
        super().__init__(Direction.UP, "in", duration, 10, easing_func)
        logger.info("[IntegrateUp] Initialized.")
