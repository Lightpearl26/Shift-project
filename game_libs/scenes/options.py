# -*- coding: utf-8 -*-
#pylint: disable=broad-exception-caught

"""
SHIFT PROJECT Scenes
____________________________________________________________________________________________________
Options scene
version : 1.0
____________________________________________________________________________________________________
Simple title screen with a blinking 'Press Jump to Start' prompt.
Transitions to a target scene on input.
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from os.path import join

from ..managers.event import KeyState
from ..assets_cache import AssetsCache
from .. import config
from .. import logger
from .base import BaseScene

if TYPE_CHECKING:
    from pygame import Surface

# ----- Options Scene ----- #
class OptionsScene(BaseScene):
    """
    Options Scene
    
    Displays options menu.
    """
    def __init__(self):
        BaseScene.__init__(self, "Options")
        self.option_list: list[str] = [
            "Audio Settings",
            "Video Settings",
            "Controls",
            "Gameplay",
            "Back"
        ]
        self.cursor_pos: int = 0

    def init(self):
        """Initialize the Options scene"""
        self.cursor_pos = 0

    def handle_events(self, key_events: dict[str, KeyState]):
        """Handle input events"""
        if key_events.get("UP") == KeyState.PRESSED:
            self.cursor_pos = (self.cursor_pos - 1) % len(self.option_list)
        elif key_events.get("DOWN") == KeyState.PRESSED:
            self.cursor_pos = (self.cursor_pos + 1) % len(self.option_list)
        elif key_events.get("JUMP") == KeyState.PRESSED:
            selected_option = self.option_list[self.cursor_pos]
            if selected_option == "Back":
                # Return to Title Screen
                title_scene = self.scene_manager.get_scene("Title")
                if title_scene is not None:
                    self.scene_manager.change_scene("Title")
            else:
                logger.info("T'es intelligent toi ! J'ai pas encore implémenté ça !")

    def update(self, dt: float):
        """Update the scene state"""

    def render(self, surface: Surface):
        """Render the scene to the given surface"""
        surface.fill((0, 0, 0))
        # Simple text rendering for options (placeholder)
        font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 24)
        for index, option in enumerate(self.option_list):
            color = (255, 255, 0) if index == self.cursor_pos else (255, 255, 255)
            text_surf = font.render(option, True, color)
            surface.blit(text_surf, (100, 100 + index * 50))
