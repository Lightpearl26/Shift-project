# -*- coding: utf-8 -*-

"""
game_libs.scene.options
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines the MainMenu class.
    Displaying the main menu of the game before playing.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

# import built-in modules
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal
from os.path import join
import pygame

# import game_libs
from . import BaseScene
from ..transitions import FadeIn, FadeOut
from ..assets_cache import AssetsCache
from ..managers.options import OptionsManager
from ..managers.event import  KeyState
from .. import config
from .. import logger

# import type indentation
if TYPE_CHECKING:
    from pygame import Surface
    from pygame.font import Font


# ----- OptionScene -----
class OptionScene(BaseScene):
    """
    Option scene
    This scene is here to give player possibility to change its settings
    """
    def __init__(self) -> None:
        super().__init__("Options")
        self._main_menu_font: Optional[Font] = None
        self._sub_menu_font: Optional[Font] = None
        self.cursor_pos: tuple[int, int] = (0, 0)
        self._main_menu_options = ["Audio", "Video", "Controls"]
        self._sub_menu_options = {
            "Audio": ["Master", "BGM", "BGS", "ME", "SE"],
            "Video": ["Fullscreen", "Rendering process", "Framerate", "Luminosity", "Contrast", "Gamma", "Colorblind Mode"],
            "Controls": ["UP", "DOWN", "LEFT", "RIGHT", "JUMP", "PAUSE", "SPRINT"]
        }
        self._in_submenu: bool = False
        self._editing: bool = False
        self._waiting_for_key: bool = False
        self._control_key_slot: int = 0

    def init(self) -> None:
        self._main_menu_font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 48)
        self._sub_menu_font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 24)
        logger.info(f"Scene [{self.name}] successfully initialized")

    def on_enter(self) -> None:
        ...

    def on_exit(self) -> None:
        OptionsManager.save()

    def handle_events(self) -> None:
        if self._waiting_for_key:
            for event in pygame.event.get(pygame.KEYDOWN):
                if event.key != pygame.K_DELETE:
                    # Bind the key to the selected slot
                    action = self._current_option
                    current_keys = OptionsManager.get_action_keys(action)

                    # Add or replace key at the selected slot
                    if self._control_key_slot < len(current_keys):
                        # Replace existing key
                        current_keys[self._control_key_slot] = event.key
                    else:
                        # Add new key
                        current_keys.append(event.key)

                    OptionsManager.set_action_keys(action, current_keys)
                    logger.info(f"[{self.name}] Remapped '{action}' slot {self._control_key_slot} "
                                f"to {pygame.key.name(event.key)}")

                # Exit capture mode (whether ESC or valid key)
                self._waiting_for_key = False
                self.event_manager.update(0.0)
                return
            return

        events = self.event_manager.get_keys()
        if events.get("PAUSE") == KeyState.PRESSED:
            if self._in_submenu:
                if self._editing:
                    self._editing = False
                    return
                self._in_submenu = False
                return
            previous_scene = self.scene_manager.get_previous_scene().name
            self.scene_manager.change_scene(previous_scene,
                                            transition_in=FadeIn(500),
                                            transition_out=FadeOut(500))
            return
        if events.get("UP") == KeyState.PRESSED:
            if self._in_submenu:
                self._control_key_slot = 0
                if self._editing:
                    self.edit_current(-1)
                    return
                cursor_x, cursor_y = self.cursor_pos
                nb_choices = len(self._sub_menu_options[self._main_menu_options[cursor_x]])
                self.cursor_pos = (cursor_x, max(0, min(cursor_y - 1, nb_choices-1)))
                return
            return
        if events.get("DOWN") == KeyState.PRESSED:
            if self._in_submenu:
                self._control_key_slot = 0
                if self._editing:
                    self.edit_current(1)
                    return
                cursor_x, cursor_y = self.cursor_pos
                nb_choices = len(self._sub_menu_options[self._main_menu_options[cursor_x]])
                self.cursor_pos = (cursor_x, max(0, min(cursor_y + 1, nb_choices-1)))
                return
            return
        if events.get("LEFT") == KeyState.PRESSED:
            if not self._in_submenu:
                self.cursor_pos = (max(0, min(self.cursor_pos[0]-1, len(self._main_menu_options)-1)), self.cursor_pos[1])
                return
            if self._editing:
                self.edit_current(-1)
                return
            if self._main_menu_options[self.cursor_pos[0]] == "Controls":
                self._control_key_slot -= 1
                self._control_key_slot %= len(OptionsManager.get_key_bindings()[self._current_option])
                return
            return
        if events.get("RIGHT") == KeyState.PRESSED:
            if not self._in_submenu:
                self.cursor_pos = (max(0, min(self.cursor_pos[0]+1, len(self._main_menu_options)-1)), self.cursor_pos[1])
                return
            if self._editing:
                self.edit_current(1)
                return
            if self._main_menu_options[self.cursor_pos[0]] == "Controls":
                self._control_key_slot += 1
                self._control_key_slot %= len(OptionsManager.get_key_bindings()[self._current_option])
                return
            return
        if events.get("JUMP") == KeyState.PRESSED:
            # execute action in cursor pos
            if not self._in_submenu:
                self._in_submenu = True
                cursor_x, cursor_y = self.cursor_pos
                nb_choices = len(self._sub_menu_options[self._main_menu_options[cursor_x]])
                self.cursor_pos = (cursor_x, max(0, min(cursor_y, nb_choices-1)))
                return
            if not self._editing:
                self._editing = True
                return
            if self._main_menu_options[self.cursor_pos[0]] == "Controls" and not self._waiting_for_key:
                self._waiting_for_key = True
                pygame.event.clear() # cancel every event in queue to capture the next keydown
                return
            return

    def update(self, dt: float) -> None:
        self.event_manager.update(dt)

    def render(self, surface: Surface) -> None:
        self.render_header(surface)
        self.render_submenu(surface)

    @property
    def _current_option(self) -> str:
        return self._sub_menu_options[self._main_menu_options[self.cursor_pos[0]]][self.cursor_pos[1]]

    def edit_current(self, delta: Literal[1, -1]) -> None:
        """
        edit the current option
        """
        if self._current_option == "Master":
            old_vol = OptionsManager.master_volume()
            new_volume = max(0, min(old_vol + 0.05 * delta, 1.0))
            OptionsManager.set_master_volume(round(new_volume, 2))
            logger.info(f"Set master volume to {new_volume*100}")
        if self._current_option == "BGM":
            old_vol = OptionsManager.bgm_volume()
            new_volume = max(0, min(old_vol + 0.05 * delta, 1.0))
            OptionsManager.set_bgm_volume(round(new_volume, 2))
            logger.info(f"Set BGM volume to {new_volume*100}")
        if self._current_option == "BGS":
            old_vol = OptionsManager.bgs_volume()
            new_volume = max(0, min(old_vol + 0.05 * delta, 1.0))
            OptionsManager.set_bgs_volume(round(new_volume, 2))
            logger.info(f"Set BGS volume to {new_volume*100}")
        if self._current_option == "ME":
            old_vol = OptionsManager.me_volume()
            new_volume = max(0, min(old_vol + 0.05 * delta, 1.0))
            OptionsManager.set_me_volume(round(new_volume, 2))
            logger.info(f"Set ME volume to {new_volume*100}")
        if self._current_option == "SE":
            old_vol = OptionsManager.se_volume()
            new_volume = max(0, min(old_vol + 0.05 * delta, 1.0))
            OptionsManager.set_se_volume(round(new_volume, 2))
            logger.info(f"Set SE volume to {new_volume*100}")
        if self._current_option == "Fullscreen":
            OptionsManager.set_fullscreen(not OptionsManager.is_fullscreen())
            logger.info(f"Set fullscreen to {OptionsManager.is_fullscreen()}")
        if self._current_option == "Rendering process":
            options = ["cpu", "opengl"]
            current = options.index(OptionsManager.get_backend())
            OptionsManager.set_backend(options[(current+1)%2])
            logger.info(f"Set rendering process to '{OptionsManager.get_backend()}'")
        if self._current_option == "Framerate":
            available_framerate = [20, 30, 60, 120, 144, 180, 240, 300, 0]
            current_framerate = available_framerate.index(OptionsManager.get_fps_cap())
            OptionsManager.set_fps_cap(available_framerate[max(0, min(current_framerate+delta, len(available_framerate)-1))])
            logger.info(f"Set framerate to {"unlimited" if OptionsManager.get_fps_cap() == 0 else OptionsManager.get_fps_cap()}")
        if self._current_option == "Luminosity":
            old_lum = OptionsManager.get_luminosity()
            new_lum = max(0, min(old_lum + delta * 0.05, 1.0))
            OptionsManager.set_luminosity(round(new_lum, 2))
            logger.info(f"Set luminosity to {new_lum}")
        if self._current_option == "Contrast":
            old_con = OptionsManager.get_contrast()
            new_con = max(0, min(old_con + delta * 0.05, 1.0))
            OptionsManager.set_contrast(round(new_con, 2))
            logger.info(f"Set contrast to {new_con}")
        if self._current_option == "Gamma":
            old_gam = OptionsManager.get_gamma()
            new_gam = max(0.1, min(old_gam + delta * 0.1, 3.0))
            OptionsManager.set_gamma(round(new_gam, 1))
            logger.info(f"Set gamma to {new_gam}")
        if self._current_option == "Colorblind Mode":
            available_modes = ["none", "protanopia", "deuteranopia", "tritanopia"]
            current_mode = available_modes.index(OptionsManager.get_colorblind_mode())
            OptionsManager.set_colorblind_mode(available_modes[max(0, min(current_mode + delta, len(available_modes)-1))])
            logger.info(f"Set colorblind mode to '{OptionsManager.get_colorblind_mode()}'")

    def render_header(self, surface: Surface) -> None:
        """
        Render the header of the menu
        containing its title and the main options
        """
        width, height = surface.get_size()
        pygame.draw.rect(surface, (50, 0, 70), (0, 0, width, height // 5))
        surface.blit(self._main_menu_font.render("Options", True, (255, 255, 255)), (10, 10))
        step = width // 4
        for i, option in enumerate(self._main_menu_options, 1):
            if self.cursor_pos[0] == i-1:
                if self._in_submenu:
                    surface.blit(self._main_menu_font.render(option, True, (255, 155, 55)), (i*step, height//5-60))
                else:
                    surface.blit(self._main_menu_font.render(option, True, (155, 255, 55)), (i*step, height//5-60))
            else:
                surface.blit(self._main_menu_font.render(option, True, (255, 255, 255)), (i*step, height//5-60))

    def render_submenu(self, surface: Surface) -> None:
        """
        Render the given submenu
        """
        width, height = surface.get_size()
        pygame.draw.rect(surface, (0, 0, 0), (0, height//5, width, height//5 * 4))
        for i, option in enumerate(self._sub_menu_options[self._main_menu_options[self.cursor_pos[0]]]):
            if self._in_submenu:
                if self.cursor_pos[1] == i:
                    if self._editing:
                        surface.blit(self._main_menu_font.render(option, True, (255, 155, 55)), (100, 100 + height // 5 + i*100))
                    else:
                        surface.blit(self._main_menu_font.render(option, True, (155, 255, 55)), (100, 100 + height // 5 + i*100))
                else:
                    surface.blit(self._main_menu_font.render(option, True, (255, 255, 255)), (100, 100 + height // 5 + i*100))
            else:
                surface.blit(self._main_menu_font.render(option, True, (255, 255, 255)), (100, 100 + height // 5 + i*100))

        if self._main_menu_options[self.cursor_pos[0]] == "Audio":
            self.render_audio_submenu(surface)
        if self._main_menu_options[self.cursor_pos[0]] == "Video":
            self.render_video_submenu(surface)
        if self._main_menu_options[self.cursor_pos[0]] == "Controls":
            self.render_controls_submenu(surface)

    def render_audio_submenu(self, surface: Surface) -> None:
        """
        Render the Audio submenu
        """
        # draw master volume components
        width, height = surface.get_size()
        pygame.draw.rect(surface, (255, 255, 255), (width // 3, 123 + height // 5, width // 2, 2))
        percentage = OptionsManager.master_volume()
        pygame.draw.rect(surface, (155, 255, 55), (-10 + width // 3 + percentage * width // 2, 100 + height // 5, 20, 48))
        value = self._sub_menu_font.render(f"{percentage*100}", True, (255, 255, 255))
        value_rect = value.get_rect(midright=(width - 100, 124 + height // 5))
        surface.blit(value, value_rect)
        
        # draw bgm volume components
        width, height = surface.get_size()
        pygame.draw.rect(surface, (255, 255, 255), (width // 3, 223 + height // 5, width // 2, 2))
        percentage = OptionsManager.bgm_volume()
        pygame.draw.rect(surface, (155, 255, 55), (-10 + width // 3 + percentage * width // 2, 200 + height // 5, 20, 48))
        value = self._sub_menu_font.render(f"{percentage*100}", True, (255, 255, 255))
        value_rect = value.get_rect(midright=(width - 100, 224 + height // 5))
        surface.blit(value, value_rect)
        
        # draw bgs volume components
        width, height = surface.get_size()
        pygame.draw.rect(surface, (255, 255, 255), (width // 3, 323 + height // 5, width // 2, 2))
        percentage = OptionsManager.bgs_volume()
        pygame.draw.rect(surface, (155, 255, 55), (-10 + width // 3 + percentage * width // 2, 300 + height // 5, 20, 48))
        value = self._sub_menu_font.render(f"{percentage*100}", True, (255, 255, 255))
        value_rect = value.get_rect(midright=(width - 100, 324 + height // 5))
        surface.blit(value, value_rect)
        
        # draw me volume components
        width, height = surface.get_size()
        pygame.draw.rect(surface, (255, 255, 255), (width // 3, 423 + height // 5, width // 2, 2))
        percentage = OptionsManager.me_volume()
        pygame.draw.rect(surface, (155, 255, 55), (-10 + width // 3 + percentage * width // 2, 400 + height // 5, 20, 48))
        value = self._sub_menu_font.render(f"{percentage*100}", True, (255, 255, 255))
        value_rect = value.get_rect(midright=(width - 100, 424 + height // 5))
        surface.blit(value, value_rect)
        
        # draw se volume components
        width, height = surface.get_size()
        pygame.draw.rect(surface, (255, 255, 255), (width // 3, 523 + height // 5, width // 2, 2))
        percentage = OptionsManager.se_volume()
        pygame.draw.rect(surface, (155, 255, 55), (-10 + width // 3 + percentage * width // 2, 500 + height // 5, 20, 48))
        value = self._sub_menu_font.render(f"{percentage*100}", True, (255, 255, 255))
        value_rect = value.get_rect(midright=(width - 100, 524 + height // 5))
        surface.blit(value, value_rect)

    def render_video_submenu(self, surface: Surface) -> None:
        """
        Render the Video submenu
        """
        width, height = surface.get_size()

        # render fullscreen switch
        if OptionsManager.is_fullscreen():
            pygame.draw.rect(surface, (255, 255, 255), (width - 196, 100 + height // 5, 96, 48))
            pygame.draw.rect(surface, (0, 0, 0), (width - 146, 104 + height // 5, 40, 40))
        else:
            pygame.draw.rect(surface, (0, 0, 0), (width - 196, 100 + height // 5, 96, 48))
            pygame.draw.rect(surface, (255, 255, 255), (width - 192, 104 + height // 5, 40, 40))
        pygame.draw.rect(surface, (155, 255, 55), (width - 196, 100 + height // 5, 96, 48), width=2)
        
        # render backend selector
        text = self._sub_menu_font.render(OptionsManager.get_backend(), True, (0, 0, 0))
        pygame.draw.rect(surface, (255, 255, 255), (width-292, 200+height//5, 192, 48))
        text_rect = text.get_rect(center=(width-196, 224+height//5))
        surface.blit(text, text_rect)
        pygame.draw.rect(surface, (155, 255, 55), (width-292, 200+height//5, 192, 48), width=2)
        
        # render framerate selector
        text = "unlimited" if OptionsManager.get_fps_cap() == 0 else str(OptionsManager.get_fps_cap())
        text_surf = self._sub_menu_font.render(text, True, (0, 0, 0))
        pygame.draw.rect(surface, (255, 255, 255), (width-292, 300+height//5, 192, 48))
        text_rect = text_surf.get_rect(center=(width-196, 324+height//5))
        surface.blit(text_surf, text_rect)
        pygame.draw.rect(surface, (155, 255, 55), (width-292, 300+height//5, 192, 48), width=2)
        
        # render luminosity stuff
        pygame.draw.rect(surface, (255, 255, 255), (width // 3, 423 + height // 5, width // 2, 2))
        percentage = OptionsManager.get_luminosity()
        pygame.draw.rect(surface, (155, 255, 55), (-10 + width // 3 + percentage * width // 2, 400 + height // 5, 20, 48))
        value = self._sub_menu_font.render(f"{OptionsManager.get_luminosity()}", True, (255, 255, 255))
        value_rect = value.get_rect(midright=(width - 100, 424 + height // 5))
        surface.blit(value, value_rect)
        
        # render contrast stuff
        pygame.draw.rect(surface, (255, 255, 255), (width // 3, 523 + height // 5, width // 2, 2))
        percentage = OptionsManager.get_contrast()
        pygame.draw.rect(surface, (155, 255, 55), (-10 + width // 3 + percentage * width // 2, 500 + height // 5, 20, 48))
        value = self._sub_menu_font.render(f"{OptionsManager.get_contrast()}", True, (255, 255, 255))
        value_rect = value.get_rect(midright=(width - 100, 524 + height // 5))
        surface.blit(value, value_rect)
        
        # render gamma stuff
        pygame.draw.rect(surface, (255, 255, 255), (width // 3, 623 + height // 5, width // 2, 2))
        percentage = (OptionsManager.get_gamma() - 0.1) / 2.9
        pygame.draw.rect(surface, (155, 255, 55), (-10 + width // 3 + percentage * width // 2, 600 + height // 5, 20, 48))
        value = self._sub_menu_font.render(f"{OptionsManager.get_gamma()}", True, (255, 255, 255))
        value_rect = value.get_rect(midright=(width - 100, 624 + height // 5))
        surface.blit(value, value_rect)
        
        # render colorblind selector
        text = self._sub_menu_font.render(OptionsManager.get_colorblind_mode(), True, (0, 0, 0))
        pygame.draw.rect(surface, (255, 255, 255), (width-292, 700+height//5, 192, 48))
        text_rect = text.get_rect(center=(width-196, 724+height//5))
        surface.blit(text, text_rect)
        pygame.draw.rect(surface, (155, 255, 55), (width-292, 700+height//5, 192, 48), width=2)

    def render_controls_submenu(self, surface: Surface) -> None:
        """
        Render the Controls submenu
        """
        width, height = surface.get_size()
        for i, action in enumerate(self._sub_menu_options["Controls"]):
            for k, key in enumerate(OptionsManager.get_action_keys(action)):
                pygame.draw.rect(surface, (255, 255, 255), (width // 3 + k*250, 100 + i*100 + height // 5, 192, 48))
                if k == self._control_key_slot and action == self._current_option:
                    if self._waiting_for_key:
                        text = self._sub_menu_font.render(">   <", True, (0, 0, 0))
                    else:
                        text = self._sub_menu_font.render(pygame.key.name(key), True, (0, 0, 0))
                    pygame.draw.rect(surface, (155, 255, 55), (width // 3 + k*250, 100 + i*100 + height // 5, 192, 48), width=2)
                else:
                    text = self._sub_menu_font.render(pygame.key.name(key), True, (0, 0, 0))
                    pygame.draw.rect(surface, (55, 55, 55), (width // 3 + k*250, 100 + i*100 + height // 5, 192, 48), width=2)
                text_rect = text.get_rect(center=(width//3 + k*250 + 96, 124+i*100+height//5))
                surface.blit(text, text_rect)
                        
