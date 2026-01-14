# -*- coding: utf-8 -*-
#pylint: disable=broad-except

"""
game_libs.managers.display
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module manages the display and window for the game.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
from datetime import datetime

# Import pygame
from pygame import display as pygame_display
from pygame import image as pygame_image
from pygame import mouse as pygame_mouse
from pygame import time as pygame_time
from pygame import FULLSCREEN, SCALED

# Import config
from .. import config

# Import logger
from .. import logger

# Import AssetsCache
from ..assets_cache import AssetsCache

if TYPE_CHECKING:
    from pygame import Surface


# ----- DisplayManager class ----- #
class DisplayManager:
    """
    DisplayManager object
    
    This object manages the game window and display surface.
    
    Properties:
        surface (Surface): The main display surface
        width (int): Window width
        height (int): Window height
        size (tuple[int, int]): Window size (width, height)
        fullscreen (bool): Whether fullscreen is active
    
    Methods:
        init(width: int, height: int, caption: str, fullscreen: bool, flags: int) -> None
        get_surface() -> Surface
        get_width() -> int
        get_height() -> int
        get_size() -> tuple[int, int]
        is_fullscreen() -> bool
        toggle_fullscreen() -> None
        set_caption(caption: str) -> None
        set_icon(icon_path: str | None) -> None
        show_cursor(visible: bool) -> None
        save_screenshot(filename: str | None) -> None
        flip() -> None
        shutdown() -> None
    """

    _display: Surface | None = None
    _width: int = 1920
    _height: int = 1080
    _fullscreen: bool = False
    _caption: str = "Game Window"
    _flags: int = 0
    _vsync: bool = True
    _max_framerate: int = 0  # 0 means unlimited
    _clock: pygame_time.Clock | None = None
    _delta_time: float = 0.0

    @classmethod
    def init(cls,
             width: int | None = None,
             height: int | None = None,
             caption: str | None = None,
             fullscreen: bool = False,
             flags: int | None = None) -> None:
        """
        Initialize the display manager and create the game window.
        
        Args:
            - width (int | None): Window width (uses config if None)
            - height (int | None): Window height (uses config if None)
            - caption (str | None): Window caption/title (uses config if None)
            - fullscreen (bool): Whether to start in fullscreen mode
            - flags (int | None): Additional pygame display flags (uses config if None)
        """
        # Use config values if not provided
        cls._width = width if width is not None else config.WINDOW_WIDTH
        cls._height = height if height is not None else config.WINDOW_HEIGHT
        cls._caption = caption if caption is not None else config.WINDOW_CAPTION
        cls._fullscreen = fullscreen
        cls._flags = flags if flags is not None else config.WINDOW_FLAGS

        # Build display flags
        display_flags = cls._flags
        if cls._fullscreen:
            display_flags |= FULLSCREEN | SCALED

        # Create the display with vsync
        cls._display = pygame_display.set_mode(
            (cls._width, cls._height),
            display_flags,
            vsync=int(cls._vsync)
        )
        pygame_display.set_caption(cls._caption)

        # Try to set icon from config
        try:
            cls.set_icon(config.ICON_PATH)
        except Exception as e:
            logger.warning(f"[DisplayManager] Could not load icon from {config.ICON_PATH}: {e}")

        cls.show_cursor(config.SHOW_CURSOR)

        # Initialize clock
        cls._clock = pygame_time.Clock()
        cls._delta_time = 0.0

        logger.info(f"[DisplayManager] Display initialized: {cls._width}x{cls._height}, "
                   f"fullscreen={cls._fullscreen}, caption='{cls._caption}'")

    @classmethod
    def get_surface(cls) -> Surface:
        """
        Get the main display surface.
        
        Returns:
            - Surface: The pygame display surface
        
        Raises:
            - RuntimeError: If display not initialized
        """
        if cls._display is None:
            logger.error("[DisplayManager] Display not initialized! Call init() first.")
            raise RuntimeError("DisplayManager not initialized")
        return cls._display

    @classmethod
    def get_width(cls) -> int:
        """
        Get the window width.
        
        Returns:
            - int: Window width in pixels
        """
        return cls._width

    @classmethod
    def get_height(cls) -> int:
        """
        Get the window height.
        
        Returns:
            - int: Window height in pixels
        """
        return cls._height

    @classmethod
    def get_size(cls) -> tuple[int, int]:
        """
        Get the window size.
        
        Returns:
            - tuple[int, int]: (width, height) in pixels
        """
        return (cls._width, cls._height)

    @classmethod
    def is_fullscreen(cls) -> bool:
        """
        Check if the window is in fullscreen mode.
        
        Returns:
            - bool: True if fullscreen, False otherwise
        """
        return cls._fullscreen

    @classmethod
    def toggle_fullscreen(cls) -> None:
        """
        Toggle between fullscreen and windowed mode.
        """
        if cls._display is None:
            logger.error("[DisplayManager] Cannot toggle fullscreen - display not initialized")
            return

        cls._fullscreen = not cls._fullscreen

        # Build display flags (remove fullscreen flags first, then add if needed)
        display_flags = cls._flags & ~(FULLSCREEN | SCALED)
        if cls._fullscreen:
            display_flags |= FULLSCREEN | SCALED

        # Quit the current display and recreate with new flags
        try:
            pygame_display.quit()
            cls._display = pygame_display.set_mode(
                (cls._width, cls._height),
                display_flags,
                vsync=int(cls._vsync))
            pygame_display.set_caption(cls._caption)
            cls.show_cursor(config.SHOW_CURSOR)
            cls.set_icon(config.ICON_PATH)
            logger.info(f"[DisplayManager] Fullscreen toggled: {cls._fullscreen}")
        except Exception as e:
            # If toggle fails, revert the state
            cls._fullscreen = not cls._fullscreen
            logger.error(f"[DisplayManager] Fullscreen toggle failed: {e}")

    @classmethod
    def set_caption(cls, caption: str) -> None:
        """
        Set the window caption/title.
        
        Args:
            - caption (str): New window title
        """
        cls._caption = caption
        pygame_display.set_caption(caption)
        logger.info(f"[DisplayManager] Caption set to: '{caption}'")

    @classmethod
    def flip(cls) -> None:
        """
        Update the display (flip buffers).
        
        This should be called once per frame after all rendering is done.
        """
        pygame_display.flip()

    @classmethod
    def set_icon(cls, icon_path: str | None = None) -> None:
        """
        Set the window icon.
        
        Args:
            - icon_path (str | None): Path to the icon image file (uses config if None)
        
        Raises:
            - FileNotFoundError: If icon file does not exist
        """
        if icon_path is None:
            icon_path = config.ICON_PATH

        if not Path(icon_path).exists():
            raise FileNotFoundError(f"Icon file not found: {icon_path}")

        try:
            icon = AssetsCache.load_image(icon_path)
            pygame_display.set_icon(icon)
            logger.info(f"[DisplayManager] Icon set from: {icon_path}")
        except Exception as e:
            logger.error(f"[DisplayManager] Failed to set icon: {e}")
            raise

    @classmethod
    def show_cursor(cls, visible: bool = True) -> None:
        """
        Show or hide the mouse cursor.
        
        Args:
            - visible (bool): True to show cursor, False to hide
        """
        pygame_mouse.set_visible(visible)
        state = "visible" if visible else "hidden"
        logger.info(f"[DisplayManager] Cursor is now {state}")

    @classmethod
    def save_screenshot(cls, filename: str | None = None) -> None:
        """
        Save a screenshot of the current display.
        
        Args:
            - filename (str | None): Custom filename (uses timestamp if None)
        
        Raises:
            - RuntimeError: If display not initialized
        """
        if cls._display is None:
            logger.error("[DisplayManager] Cannot save screenshot - display not initialized")
            raise RuntimeError("DisplayManager not initialized")

        # Create screenshots folder if needed
        screenshots_dir = Path(config.SCREENSHOTS_FOLDER)
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        filepath = screenshots_dir / filename

        try:
            pygame_image.save(cls._display, str(filepath))
            logger.info(f"[DisplayManager] Screenshot saved to: {filepath}")
        except Exception as e:
            logger.error(f"[DisplayManager] Failed to save screenshot: {e}")
            raise

    @classmethod
    def shutdown(cls) -> None:
        """
        Cleanup and shutdown the display manager.
        
        Should be called before exiting the game.
        """
        if cls._display is not None:
            try:
                pygame_display.quit()
                cls._display = None
                logger.info("[DisplayManager] Display shutdown complete")
            except Exception as e:
                logger.error(f"[DisplayManager] Error during shutdown: {e}")

    @classmethod
    def set_vsync(cls, enabled: bool) -> None:
        """
        Enable or disable vertical sync.
        
        Note: Requires display recreation to take effect.
        
        Args:
            - enabled (bool): True to enable vsync, False to disable
        """
        if cls._vsync == enabled:
            return

        cls._vsync = enabled

        # Recreate display to apply vsync change
        if cls._display is not None:
            display_flags = cls._flags
            if cls._fullscreen:
                display_flags |= FULLSCREEN | SCALED

            try:
                pygame_display.quit()
                cls._display = pygame_display.set_mode(
                    (cls._width, cls._height),
                    display_flags,
                    vsync=int(cls._vsync)
                )
                pygame_display.set_caption(cls._caption)
                cls.show_cursor(config.SHOW_CURSOR)
                cls.set_icon(config.ICON_PATH)
                logger.info(f"[DisplayManager] VSync {'enabled' if enabled else 'disabled'}")
            except Exception as e:
                # If vsync change fails, revert
                cls._vsync = not enabled
                logger.error(f"[DisplayManager] VSync change failed: {e}")

    @classmethod
    def is_vsync_enabled(cls) -> bool:
        """
        Check if vertical sync is enabled.
        
        Returns:
            - bool: True if vsync enabled, False otherwise
        """
        return cls._vsync

    @classmethod
    def tick(cls) -> None:
        """
        Update the clock and calculate delta time.
        
        Should be called once per frame at the beginning of the game loop.
        Respects the max framerate setting.
        """
        if cls._clock is None:
            logger.error("[DisplayManager] Clock not initialized! Call init() first.")
            return

        # Tick with fps cap (0 means unlimited)
        ms = cls._clock.tick(cls._max_framerate)
        cls._delta_time = ms / 1000.0  # Convert to seconds

    @classmethod
    def get_delta_time(cls) -> float:
        """
        Get the time elapsed since the last frame in seconds.
        
        Returns:
            - float: Delta time in seconds
        """
        return cls._delta_time

    @classmethod
    def set_fps_cap(cls, fps: int) -> None:
        """
        Set the maximum framerate cap.
        
        Args:
            - fps (int): Maximum FPS (0 for unlimited)
        """
        cls._max_framerate = max(0, fps)
        logger.info(f"[DisplayManager] FPS cap set to: {'unlimited' if fps == 0 else fps}")

    @classmethod
    def get_fps_cap(cls) -> int:
        """
        Get the current FPS cap.
        
        Returns:
            - int: FPS cap (0 means unlimited)
        """
        return cls._max_framerate

    @classmethod
    def get_fps(cls) -> float:
        """
        Get the current frames per second.
        
        Returns:
            - float: Current FPS
        """
        if cls._clock is None:
            return 0.0
        return cls._clock.get_fps()
