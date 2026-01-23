# -*- coding: utf-8 -*-

"""
game_libs.scene.base
___________________________________________________________________________________________________
File infos:

    - Author: Justienr Roux
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines the PauseMenuScene class,
    which enables the game to be paused and select various options.
___________________________________________________________________________________________________
@copyright: Justine Roux 2026
"""
# import needed built-in modules
from __future__ import annotations
from os.path import join
from typing import TYPE_CHECKING, Optional
import pygame
from ..managers.audio import AudioManager
from ..managers.event import KeyState
from ..transitions import FadeIn, FadeOut, DisintegrateLeft, IntegrateLeft, DisintegrateRight, IntegrateRight, DisintegrateDown, IntegrateDown, DisintegrateUp, IntegrateUp
from . import BaseScene
from ..assets_cache import AssetsCache
from ..import config

# import logger
from .. import logger

if TYPE_CHECKING:
    from ..managers.scene import SceneManager
    from ..managers.event import EventManager
    from pygame import Surface

# ----- PauseMenuScene class ----- #
class PauseMenuScene(BaseScene):
    """
    PauseMenuScene object

    This is the pause menu scene for the game.
    """

    def __init__(self) -> None:
        """
        Initialize the PauseMenuScene.

        Args:
            - name (str): The name of the scene.
        """
        super().__init__('PauseMenu')
        self.title = 'SHIFT PROJECT'
        self.options = ['Reprendre',
                        'Sauvegarder',
                        'Options',
                        'Retour au menu principal']
        self.cursor = 0
        self._title_font = None
        self._options_font = None
        logger.info(f"[PauseMenu] Initialized scene: {self.name}")

    def init(self) -> None:
        """
        Initialize the scene.
        This method should be overridden by subclasses.
        """
        self._title_font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 64)
        self._options_font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 32)
        logger.info("[PauseMenu] Scene initialized.")



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
        return

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
            if option == 'Reprendre' :
                self.scene_manager.change_scene('Tests',
                                                transition_in=FadeIn(500),
                                                transition_out=FadeOut(500))
            elif option == 'Sauvegarder' :
                self.scene_manager.change_scene('SaveSelect',
                                                transition_in=IntegrateUp(1500),
                                                transition_out=DisintegrateUp(1500))
            elif option == 'Options' :
                self.scene_manager.change_scene('Options',
                                                transition_in=IntegrateDown(1500),
                                                transition_out=DisintegrateDown(1500))
            elif option == 'Retour au menu principal' :
                self.scene_manager.change_scene('MainMenu',
                                                transition_in=IntegrateRight(1500),
                                                transition_out=DisintegrateRight(1500))


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
            title_rect = title_surf.get_rect(center=(surface.get_width() // 2,
                                                     surface.get_height() // 4))
            surface.blit(title_surf, title_rect)

        # Render options
        for i, option in enumerate(self.options):
            if i == self.cursor :
                text = self._options_font.render(option, True, (155, 255, 55))
            else:
                text = self._options_font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=(surface.get_width()// 2,
                                               surface.get_height() // 2 + i * 40))
            surface.blit(text, text_rect)
