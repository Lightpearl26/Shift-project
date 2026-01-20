# -*- coding: utf-8 -*-

"""
SHIFT PROJECT Scenes Package
____________________________________________________________________________________________________
Game scenes (title, level, pause, options, game over) and transitions
version : 1.0
____________________________________________________________________________________________________
Welcome Scene of the game. Rendering the title of the game and a prompt to start.
____________________________________________________________________________________________________
(c) Franck Lafiteau
"""

# import needed built-in modules
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from os.path import join

# import assets
from ..assets_cache import AssetsCache

# Import AudioManager
from ..managers.audio import AudioManager

# import base scene
from .base import BaseScene

# import KeyStates
from ..managers.event import KeyState

# Import Fade transitions
from ..transitions import DisintegrateRight, IntegrateRight
from ..transitions.easing import ease_in_out_expo

# import logger
from .. import logger

# import config
from .. import config

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.font import Font


# ----- WelcomeScene class ----- #
class WelcomeScene(BaseScene):
    """
    WelcomeScene object
    """
    def __init__(self):
        super().__init__("Welcome") # Nom unique de la scène
        self.title = "SHIFT PROJECT"
        self.prompt = "Press JUMP to start"

        # initialize fonts
        self._title_font: Optional[Font] = None
        self._prompt_font: Optional[Font] = None

        self._elapsed_time: float = 0.0
        self._blink_interval: float = 1.0  # Intervalle de clignotement en secondes

    def init(self):
        """
        Initialize fonts and other resources for the welcome scene.
        """
        self._title_font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 64)
        self._prompt_font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 32)
        logger.info("[WelcomeScene] Scene initialized.")

    def on_enter(self):
        """Appelé à chaque fois qu'on entre dans la scène"""
        self._elapsed_time = 0.0
        AudioManager.play_bgm("welcome_theme", loops=-1, fadein_ms=1000)

    def on_exit(self):
        """Appelé à chaque fois qu'on quitte la scène"""
        # Nettoyer, arrêter la musique, etc.
        AudioManager.stop_bgm(fadeout_ms=500)

    def handle_events(self):
        """
        Handle user inputs for the welcome scene.
        """
        keys = self.event_manager.get_keys()

        if keys.get("JUMP") == KeyState.PRESSED:
            # Change scene to the main menu with fade transitions
            AudioManager.play_se("cursor_select")
            self.scene_manager.change_scene(
                "MainMenu",
                transition_in=IntegrateRight(1500, easing_func=ease_in_out_expo),
                transition_out=DisintegrateRight(1500, easing_func=ease_in_out_expo)
            )

    def update(self, dt: float):
        """
        Update the Scene logic.
        """
        self.event_manager.update(dt)
        self._elapsed_time += dt

    def render(self, surface: Surface):
        """
        Render Sscene on given surface.
        """
        # Dessiner tout sur la surface
        surface.fill((50, 0, 70))

        # Render title
        if self._title_font:
            title_surf = self._title_font.render(self.title, True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(surface.get_width() // 2,
                                                     surface.get_height() // 3))
            surface.blit(title_surf, title_rect)

        # Render prompt with blinking effect
        if self._prompt_font:
            if self._elapsed_time % self._blink_interval < 0.7 * self._blink_interval:
                prompt_surf = self._prompt_font.render(self.prompt, True, (255, 255, 255))
                prompt_rect = prompt_surf.get_rect(center=(surface.get_width() // 2,
                                                           surface.get_height() * 2 // 3))
                surface.blit(prompt_surf, prompt_rect)
