# -*- coding: utf-8 -*-

"""
game_libs.scene.game_test
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines the GameTestScene class,
    which is a test scene for the game.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import config, logger
from ..assets_registry import AssetsRegistry
from ..ecs_core.engine import Engine
from ..header import ComponentTypes as C
from ..rendering.entity_renderer import EntityRenderer
from ..rendering.level_renderer import LevelRenderer
from ..rendering.tilemap_renderer import TilemapRenderer
from .base import BaseScene

if TYPE_CHECKING:
    from pygame import Surface
    from ..level.entity import Player
    from ..level.level import Level


class GameTestScene(BaseScene):
    """Scene used to run the ECS pipeline on the test level."""

    def __init__(self) -> None:
        super().__init__(name="Tests")
        self.engine: Engine | None = None
        self.level: Level | None = None
        self.player: Player | None = None
        self._accumulator: float = 0.0
        self._alpha: float = 0.0
        self._fixed_dt: float = 1.0 / config.TPS_MAX if config.TPS_MAX > 0 else 0.0
        self._max_substeps: int = 5
        logger.info(f"[GameTestScene] Scene '{self.name}' initialized.")

    def _reset_render_state(self) -> None:
        """Reset render caches to avoid stale interpolation artifacts."""
        TilemapRenderer.clear_cache()
        LevelRenderer._last_camera_pos = None
        EntityRenderer._last_entity_pos.clear()

    def _apply_controls(self, keys: dict) -> None:
        """Push current input state into all controlled entities."""
        if not self.engine:
            return
        for eid in self.engine.get_entities_with(C.CONTROLLED):
            controlled = self.engine.get_component(eid, C.CONTROLLED)
            if controlled is not None:
                controlled.key_state = dict(keys)

    def _load_level(self) -> None:
        """Load or reload the test level and reset state."""
        if self.engine is None:
            self.engine = Engine()
        self.level = AssetsRegistry.load_level("Tests", self.engine)
        self.player = self.level.player
        self._accumulator = 0.0
        self._alpha = 0.0
        self._reset_render_state()
        LevelRenderer.update(self.level)

    def init(self) -> None:
        """Initialize the scene and preload the level."""
        self.engine = Engine()
        self._load_level()
        logger.info(f"[GameTestScene] Scene '{self.name}' init called.")

    def on_enter(self) -> None:
        """Reload state whenever the scene becomes active."""
        self._load_level()
        logger.info(f"[GameTestScene] Entered scene '{self.name}'.")

    def on_exit(self) -> None:
        """Log when leaving the scene."""
        logger.info(f"[GameTestScene] Exited scene '{self.name}'.")

    def update(self, dt: float) -> None:
        """Advance the ECS simulation using a fixed timestep."""
        if not self.level or not self.engine:
            return

        self._accumulator += dt

        if self._fixed_dt <= 0.0:
            self._apply_controls(self.event_manager.get_keys())
            LevelRenderer.update(self.level)
            self.engine.update(self.level, dt)
            self._alpha = 0.0
            self._accumulator = 0.0
            return

        substeps = 0
        while self._accumulator >= self._fixed_dt and substeps < self._max_substeps:
            self.event_manager.update(dt)
            keys = self.event_manager.get_keys()
            LevelRenderer.update(self.level)
            self._apply_controls(keys)
            self.engine.update(self.level, self._fixed_dt)
            self._accumulator -= self._fixed_dt
            substeps += 1

        self._alpha = min(self._accumulator / self._fixed_dt, 1.0)

    def render(self, surface: Surface) -> None:
        """Draw the current level using interpolated transforms."""
        if not self.level:
            return

        LevelRenderer.render(surface, self.level, self._alpha)

    def handle_events(self) -> None:
        """Handle scene-specific events (inputs are applied during update)."""
        return
