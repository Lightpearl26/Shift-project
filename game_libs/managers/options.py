# -*- coding: utf-8 -*-
#pylint: disable=broad-except

"""
game_libs.managers.options
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module manages game options and settings, including persistence to disk.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

from __future__ import annotations
from pathlib import Path
import json

# Import config
from .. import config

# import game logger
from .. import logger

# import managers
from .audio import AudioManager
from .display import DisplayManager
from .event import EventManager


# ----- OptionsManager class ----- #
class OptionsManager:
    """
    OptionsManager object
    
    This object manages all game options and settings, including persistence.
    
    Properties (classmethods):
        master_volume (float): Master volume (0.0-1.0)
        bgm_volume (float): Background music volume (0.0-1.0)
        bgs_volume (float): Background sounds volume (0.0-1.0)
        me_volume (float): Music effects volume (0.0-1.0)
        se_volume (float): Sound effects volume (0.0-1.0)
        fullscreen (bool): Whether fullscreen is enabled
        vsync (bool): Whether vsync is enabled
        fps_cap (int): FPS cap (0 = unlimited, otherwise 20-300)
    
    Methods:
        set_master_volume(volume: float) -> None
        set_bgm_volume(volume: float) -> None
        set_bgs_volume(volume: float) -> None
        set_me_volume(volume: float) -> None
        set_se_volume(volume: float) -> None
        set_fullscreen(enabled: bool) -> None
        set_vsync(enabled: bool) -> None
        set_fps_cap(fps: int) -> None
        set_action_keys(action: str, keys: list[int]) -> None
        init() -> None
        save() -> None
        load() -> None
    """

    # Options file path
    _OPTIONS_FILE: Path = Path(".cache/settings.json")

    # Default options
    _options = {
        "master_volume": 1.0,
        "bgm_volume": 1.0,
        "bgs_volume": 1.0,
        "me_volume": 1.0,
        "se_volume": 1.0,
        "fullscreen": False,
        "vsync": True,
        "fps_cap": 0,  # 0 = unlimited
        "key_bindings": {
            "UP": list(config.KEYS_UP),
            "DOWN": list(config.KEYS_DOWN),
            "LEFT": list(config.KEYS_LEFT),
            "RIGHT": list(config.KEYS_RIGHT),
            "JUMP": list(config.KEYS_JUMP),
            "PAUSE": list(config.KEYS_PAUSE),
            "SPRINT": list(config.KEYS_SPRINT)
        }
    }

    # ----- Volume Properties ----- #
    @classmethod
    def master_volume(cls) -> float:
        """Get the master volume."""
        return cls._options["master_volume"]

    @classmethod
    def bgm_volume(cls) -> float:
        """Get the background music volume."""
        return cls._options["bgm_volume"]

    @classmethod
    def bgs_volume(cls) -> float:
        """Get the background sounds volume."""
        return cls._options["bgs_volume"]

    @classmethod
    def me_volume(cls) -> float:
        """Get the music effects volume."""
        return cls._options["me_volume"]

    @classmethod
    def se_volume(cls) -> float:
        """Get the sound effects volume."""
        return cls._options["se_volume"]

    # ----- Display Properties ----- #
    @classmethod
    def is_fullscreen(cls) -> bool:
        """Check if fullscreen is enabled."""
        return cls._options["fullscreen"]

    @classmethod
    def is_vsync_enabled(cls) -> bool:
        """Check if vsync is enabled."""
        return cls._options["vsync"]

    @classmethod
    def get_fps_cap(cls) -> int:
        """Get the FPS cap (0 = unlimited)."""
        return cls._options["fps_cap"]

    # ----- Key Bindings Properties ----- #
    @classmethod
    def get_key_bindings(cls) -> dict[str, list[int]]:
        """Get all key bindings."""
        return cls._options.get("key_bindings")

    @classmethod
    def get_action_keys(cls, action: str) -> list[int]:
        """Get the keys bound to an action."""
        bindings: dict[str, list[int]] = cls._options.get("key_bindings")
        return bindings.get(action)

    @classmethod
    def get_options(cls) -> dict:
        """Get all options."""
        return cls._options

    # ----- Volume Setters ----- #
    @classmethod
    def set_master_volume(cls, volume: float) -> None:
        """Set the master volume."""
        cls._options["master_volume"] = max(0.0, min(1.0, volume))
        # Sync with AudioManager
        AudioManager.set_master_volume(cls._options["master_volume"])

    @classmethod
    def set_bgm_volume(cls, volume: float) -> None:
        """Set the background music volume."""
        cls._options["bgm_volume"] = max(0.0, min(1.0, volume))
        AudioManager.set_bgm_volume(cls._options["bgm_volume"])

    @classmethod
    def set_bgs_volume(cls, volume: float) -> None:
        """Set the background sounds volume."""
        cls._options["bgs_volume"] = max(0.0, min(1.0, volume))
        AudioManager.set_bgs_volume(cls._options["bgs_volume"])

    @classmethod
    def set_me_volume(cls, volume: float) -> None:
        """Set the music effects volume."""
        cls._options["me_volume"] = max(0.0, min(1.0, volume))
        AudioManager.set_me_volume(cls._options["me_volume"])

    @classmethod
    def set_se_volume(cls, volume: float) -> None:
        """Set the sound effects volume."""
        cls._options["se_volume"] = max(0.0, min(1.0, volume))
        AudioManager.set_se_volume(cls._options["se_volume"])

    # ----- Display Setters ----- #
    @classmethod
    def set_fullscreen(cls, enabled: bool) -> None:
        """Set fullscreen state."""
        if cls._options["fullscreen"] != enabled:
            cls._options["fullscreen"] = enabled
        if DisplayManager.is_fullscreen() != enabled:
            DisplayManager.toggle_fullscreen()

    @classmethod
    def set_vsync(cls, enabled: bool) -> None:
        """Set vsync state."""
        cls._options["vsync"] = enabled
        DisplayManager.set_vsync(enabled)

    @classmethod
    def set_fps_cap(cls, fps: int) -> None:
        """Set the FPS cap (0 = unlimited)."""
        cls._options["fps_cap"] = max(0, fps)
        DisplayManager.set_fps_cap(cls._options["fps_cap"])
        logger.info(f"[OptionsManager] FPS cap set to: {cls._options['fps_cap']}")

    # ----- Key Bindings Setters ----- #
    @classmethod
    def set_action_keys(cls, action: str, keys: list[int]) -> None:
        """Set the keys bound to an action."""
        if action not in cls._options["key_bindings"]:
            logger.warning(f"[OptionsManager] Unknown action '{action}'")
            return
        cls._options["key_bindings"][action] = keys
        cls._sync_key_bindings()
        logger.info(f"[OptionsManager] Key bindings for '{action}' set to: {keys}")

    # ----- Persistence ----- #
    @classmethod
    def init(cls) -> None:
        """Initialize options manager by loading saved options."""
        logger.info("[OptionsManager] Initializing...")
        cls.load()
        cls._sync_with_managers()
        logger.info("[OptionsManager] Options loaded and synchronized with managers")

    @classmethod
    def save(cls) -> None:
        """Save options to file."""
        cls._sync_with_managers()
        try:
            cls._OPTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(cls._OPTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._options, f, indent=2)
            logger.info(f"[OptionsManager] Options saved to {cls._OPTIONS_FILE}")
        except Exception as e:
            logger.error(f"[OptionsManager] Failed to save options: {e}")

    @classmethod
    def load(cls) -> None:
        """Load options from file."""
        try:
            if cls._OPTIONS_FILE.exists():
                with open(cls._OPTIONS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle missing keys
                    cls._options.update(loaded)
                logger.info(f"[OptionsManager] Options loaded from {cls._OPTIONS_FILE}")
            else:
                logger.info("[OptionsManager] No saved options found, using defaults")
        except Exception as e:
            logger.error(f"[OptionsManager] Failed to load options: {e}")

    @classmethod
    def _sync_with_managers(cls) -> None:
        """Synchronize options with AudioManager and DisplayManager."""
        try:
            AudioManager.set_master_volume(cls._options["master_volume"])
            AudioManager.set_bgm_volume(cls._options["bgm_volume"])
            AudioManager.set_bgs_volume(cls._options["bgs_volume"])
            AudioManager.set_me_volume(cls._options["me_volume"])
            AudioManager.set_se_volume(cls._options["se_volume"])
            logger.info("[OptionsManager] Synchronized audio settings")
        except Exception as e:
            logger.warning(f"[OptionsManager] Could not sync audio: {e}")

        try:
            # Note: Fullscreen toggle and vsync need special handling
            # since they may need display recreation
            DisplayManager.set_vsync(cls._options["vsync"])
            DisplayManager.set_fps_cap(cls._options["fps_cap"])
            if DisplayManager.is_fullscreen() != cls._options["fullscreen"]:
                DisplayManager.toggle_fullscreen()
            logger.info("[OptionsManager] Synchronized display settings")
        except Exception as e:
            logger.warning(f"[OptionsManager] Could not sync display: {e}")

        cls._sync_key_bindings()

    @classmethod
    def _sync_key_bindings(cls) -> None:
        """Synchronize key bindings with EventManager."""
        try:
            bindings = cls._options.get("key_bindings")
            EventManager.set_key_mapping(bindings)
            logger.info("[OptionsManager] Synchronized key bindings")
        except Exception as e:
            logger.warning(f"[OptionsManager] Could not sync key bindings: {e}")
