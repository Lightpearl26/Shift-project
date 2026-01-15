# -*- coding: utf-8 -*-

"""
game_libs.scene.base
___________________________________________________________________________________________________
File infos:

    - Author: Justine Roux
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines the MainMenu class.
    Displaying the main menu of the game before playing.
___________________________________________________________________________________________________
@copyright: Justine Roux 2026
"""

# import needed built-in modules
from __future__ import annotations
from os.path import join
from typing import TYPE_CHECKING
import pygame
from ..managers.audio import AudioManager
from ..managers.event import KeyState
from ..transitions import FadeIn, FadeOut
from . import BaseScene
from ..assets_cache import AssetsCache
from ..import config

# import logger
from .. import logger

if TYPE_CHECKING:
    from pygame import Surface

# ----- MainMenuScene class ----- #
class MainMenuScene(BaseScene):
    """
    MainMenuScene object
    """

    def __init__(self) -> None:
        super().__init__('MainMenu')
        self.title = 'SHIFT PROJECT'
        self.options = ['Nouvelle partie',
                        'Charger une partie',
                        'Options',
                        'Crédits',
                        'Quitter']
        self.cursor = 0
        self._title_font = None
        self._options_font = None

    def init(self) -> None:
        """
        Initialize the scene.
        This method should be overridden by subclasses.
        """
        self._title_font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 64)
        self._options_font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 32)
        logger.info("[MainMenu] Scene initialized.")

    def on_enter(self) -> None:
        """
        Called when the scene is entered.
        This method should be overridden by subclasses.
        """
        self.cursor = 0

    def on_exit(self) -> None:
        """
        Called when the scene is exited.
        This method should be overridden by subclasses.
        """

    def update(self, dt: float) -> None:
        """
        Update the scene.

        Args:
            - dt (float): Time delta since the last update.
        This method should be overridden by subclasses.
        """
        self.event_manager.update(dt)

    def handle_events(self) -> None:
        """
        Handle input events for the scene.
        This method should be overridden by subclasses.
        """
        keys = self.event_manager.get_keys()
        if keys.get("UP") == KeyState.PRESSED:
            self.cursor = (self.cursor - 1) % len(self.options)
        elif keys.get("DOWN") == KeyState.PRESSED:
            self.cursor = (self.cursor + 1) % len(self.options)
        elif keys.get("JUMP") == KeyState.PRESSED:
            option = self.options[self.cursor]
            if option == 'Nouvelle partie' :
                self.scene_manager.change_scene('NewGame',
                                                transition_in=FadeIn(500),
                                                transition_out=FadeOut(500))
            elif option == 'Charger une partie' :
                self.scene_manager.change_scene('LoadGame',
                                                transition_in=FadeIn(500),
                                                transition_out=FadeOut(500))
            elif option == 'Options' :
                self.scene_manager.change_scene('Options',
                                                transition_in=FadeIn(500),
                                                transition_out=FadeOut(500))
            elif option == 'Crédits' :
                self.scene_manager.change_scene('Credits',
                                                transition_in=FadeIn(500),
                                                transition_out=FadeOut(500))
            elif option == 'Quitter' :
                pygame.event.post(pygame.event.Event(pygame.QUIT))


    def render(self, surface: Surface) -> None:
        """
        Render the scene onto the given surface.

        Args:
            - surface (Surface): The surface to render the scene on.
        This method should be overridden by subclasses.
        """
        surface.fill((50, 0, 70))
        # Render title
        if self._title_font:
            title_surf = self._title_font.render(self.title, True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 4))
            surface.blit(title_surf, title_rect)

        # Render options
        for i, option in enumerate(self.options):
            if i == self.cursor :
                text = self._options_font.render(option, True, (155, 255, 55))
            else:
                text = self._options_font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(topleft=(surface.get_width()* 2 // 3, surface.get_height() // 2 + i * 40))
            surface.blit(text, text_rect)
