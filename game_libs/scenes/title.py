# -*- coding: utf-8 -*-
#pylint: disable=broad-exception-caught

"""
SHIFT PROJECT Scenes
____________________________________________________________________________________________________
TitleScreen scene
version : 1.0
____________________________________________________________________________________________________
Simple title screen with a blinking 'Press Jump to Start' prompt.
Transitions to a target scene on input.
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from __future__ import annotations

from os.path import join

import pygame
from pygame import Surface

from .base import BaseScene
from .transitions.fade import FadeOut, FadeIn, CrossFade
from .transitions.polygon import LeftHexagonTransition, RightHexagonReverseTransition

from .. import config
from ..assets_cache import AssetsCache
from ..managers.event import KeyState


class WelcomeScreen(BaseScene):
    """
    Welcome Screen Scene
    
    Displays a welcome message and waits for user input to proceed.
    If no input is received, we blink a "press jump to start" prompt.
    If jump is pressed, we trasition to the main TitleScreen scene.
    If pause is pressed, we exit the game.
    """
    def __init__(self):
        super().__init__("Welcome")
        # internal state
        self._time: float = 0.0
        self.blink_timer: float = 0.8 

        # visual elements
        self.font_large: pygame.font.Font | None = None
        self.font_small: pygame.font.Font | None = None

    def init(self):
        """Initialize the Welcome Screen scene"""
        if not pygame.font.get_init():
            pygame.font.init()

        self.font_large = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 64)
        self.font_small = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 32)

    def handle_events(self, key_events: dict[str, KeyState]):
        """Handle input events"""
        if key_events.get("JUMP") == KeyState.PRESSED:
            # Transition to Title Screen
            if self.scene_manager is not None:
                title_scene = self.scene_manager.get_scene("Title")
                if title_scene is not None:
                    self.scene_manager.change_scene(
                        "Title",
                        transition_in=CrossFade(1000, self, title_scene)
                    )
        elif key_events.get("PAUSE") == KeyState.PRESSED:
            # Exit the game
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float):
        """Update the scene logic"""
        self._time += dt

    def render(self, surface: Surface):
        """Render the scene"""
        if self.font_large is None or self.font_small is None:
            return

        surface.fill((10, 10, 30))

        # Render welcome message
        welcome_text = self.font_large.render("SHIFT PROJECT", True, (200, 200, 255))
        x = (surface.get_width() - welcome_text.get_width()) // 2
        y = surface.get_height() // 3
        surface.blit(welcome_text, (x, y))

        # Render blinking prompt
        phase = self._time % self.blink_timer
        percentage = phase / self.blink_timer
        if percentage < 0.6: # Show prompt for 60% of the time
            prompt_text = self.font_small.render("Press JUMP to Start", True, (150, 150, 255))
            px = (surface.get_width() - prompt_text.get_width()) // 2
            py = y + welcome_text.get_height() + 50
            surface.blit(prompt_text, (px, py))


class TitleScreen(BaseScene):
    """
    Title Screen Scene
    
    Displays the main title screen with options to
    start the game, load a save, enter options configuration, or exit.
    Transitions to the appropriate scene based on user input.
    """
    def __init__(self):
        super().__init__("Title")
        # visual elements
        self.font_large: pygame.font.Font | None = None
        self.font_small: pygame.font.Font | None = None
        self._cursor_pos: int = 0  # Index of the currently selected menu option

    def init(self):
        """Initialize the Title Screen scene"""
        if not pygame.font.get_init():
            pygame.font.init()

        self.font_large = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 64)
        self.font_small = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 32)

    def handle_events(self, key_events: dict[str, KeyState]):
        """Handle input events"""
        if key_events.get("UP") == KeyState.PRESSED:
            self._cursor_pos = (self._cursor_pos - 1) % 4  # Assuming 4 options
        elif key_events.get("DOWN") == KeyState.PRESSED:
            self._cursor_pos = (self._cursor_pos + 1) % 4
        elif key_events.get("JUMP") == KeyState.PRESSED:
            # Handle selection based on cursor position
            if self.scene_manager is not None:
                if self._cursor_pos == 0:
                    # Start Game
                    play_scene = self.scene_manager.get_scene("Play")
                    if play_scene is not None:
                        self.scene_manager.change_scene(
                            "Play",
                            transition_in=CrossFade(1000, self, play_scene)
                        )
                elif self._cursor_pos == 1:
                    # Load Game
                    pass  # Implement load game logic
                elif self._cursor_pos == 2:
                    # Options
                    options_scene = self.scene_manager.get_scene("Options")
                    if options_scene is not None:
                        self.scene_manager.change_scene(
                            "Options",
                            transition_in=CrossFade(1000, self, options_scene)
                        )
                elif self._cursor_pos == 3:
                    # Exit
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float):
        """Update the scene logic"""

    def render(self, surface: Surface):
        """Render the scene"""
        if self.font_large is None or self.font_small is None:
            return

        surface.fill((0, 0, 50))

        # Render title message
        title_text = self.font_large.render("SHIFT PROJECT", True, (255, 255, 255))
        x = (surface.get_width() - title_text.get_width()) // 2
        y = surface.get_height() // 4
        surface.blit(title_text, (x, y))

        # Render options
        options = ["Start Game", "Load Game", "Options", "Exit"]
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self._cursor_pos else (200, 200, 200)
            option_text = self.font_small.render(option, True, color)
            ox = (surface.get_width() - option_text.get_width()) // 2
            oy = y + 100 + i * 50
            surface.blit(option_text, (ox, oy))
