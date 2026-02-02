# -*- coding: utf-8 -*-
#pylint: disable=broad-except, unsubscriptable-object

"""game_libs.managers.display
=================================

Lightweight display manager for the game.

This module exposes the `DisplayManager` class which centralizes window
creation and presentation for the game. It supports two post-processing
backends:

- "opengl": GPU-based post-process pipeline using a GLSL shader (preferred).
- "cpu": CPU LUT-based post-process (provided but disabled for realtime by
    default due to performance constraints).

Key responsibilities
- Initialize and configure the pygame display (windowed or fullscreen).
- Optionally setup an OpenGL shader, texture and quad for GPU post-processing.
- Provide a surface for game rendering (`get_surface()`), handle scaling for
    fullscreen, and present frames with `flip()`.
- Manage simple display settings: caption, icon, cursor visibility, vsync,
    FPS cap, and basic color adjustments (luminosity / contrast / gamma) as
    shader uniforms or via a generated LUT.

Usage
-----
Call `DisplayManager.init(...)` once at startup. Use `get_surface()` to draw
each frame, `flip()` to present the frame, and `shutdown()` before exiting.

Notes
-----
- If PyOpenGL is not available or shader setup fails, the manager falls back
    to the CPU backend automatically.
- CPU post-processing is intentionally disabled for realtime gameplay; the
    GLSL pipeline is the recommended path for interactive applications.

Copyright
---------
Copyright (c) Franck Lafiteau 2026
"""

from __future__ import annotations
from typing import Literal
from pathlib import Path
from datetime import datetime
import ctypes
import numpy as np
try:
    # OpenGL imports (optional, used when GPU post-process is enabled)
    from OpenGL.GL import (
        glCreateShader, glShaderSource, glCompileShader, glGetShaderiv, glGetShaderInfoLog,
        GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_COMPILE_STATUS,
        glCreateProgram, glAttachShader, glLinkProgram, glGetProgramiv, glGetProgramInfoLog,
        GL_LINK_STATUS, glUseProgram, glGetUniformLocation, glUniform1f, glUniform1i,
        glGenTextures, glBindTexture, glTexImage2D, glTexSubImage2D, glTexParameteri,
        GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE, GL_LINEAR, GL_CLAMP_TO_EDGE,
        GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
        glViewport, glClearColor,
        glGenVertexArrays, glBindVertexArray,
        glGenBuffers, glBindBuffer, glBufferData, GL_ARRAY_BUFFER,
        glEnableVertexAttribArray, glVertexAttribPointer, GL_FLOAT,
        glDrawArrays, GL_TRIANGLES,
        glActiveTexture, GL_TEXTURE0, GL_STATIC_DRAW
    )
    _OPENGL_AVAILABLE = True
except Exception as e:
    _OPENGL_AVAILABLE = False

# Import pygame
from pygame import Surface
from pygame import display as pygame_display
from pygame import image as pygame_image
from pygame import mouse as pygame_mouse
from pygame import time as pygame_time
from pygame import transform as pygame_transform
from pygame import FULLSCREEN, OPENGL, DOUBLEBUF

# Import config
from .. import config

# Import logger
from .. import logger

# Import AssetsCache
from ..assets_cache import AssetsCache


# ----- DisplayManager class ----- #
class DisplayManager:
    """Manager that controls window, surface and presentation.

    This class implements a singleton-style manager (class methods only)
    responsible for creating the pygame window and providing a drawing
    surface for the rest of the engine. It abstracts differences between a
    pure pygame pipeline and an OpenGL-backed presentation pipeline.

    Important attributes (class-level)
    - `_display` : pygame display Surface or None (the actual OS window surface)
    - `_render_surface` : offscreen Surface used when OpenGL backend is enabled
    - `_gl_enabled` : whether the OpenGL GPU pipeline is active
    - `_post_backend` : "opengl" or "cpu" (requested backend)
    - `_lut` : precomputed 3D LUT if CPU post-process is used (may be None)
    - `_window_width`, `_window_height` : actual window size returned by SDL
    - `_width`, `_height` : requested logical render size (game resolution)

    Public behaviour
    - `init(...)` : initialize the display and optionally setup OpenGL
    - `get_surface()` : returns the surface that game code should draw to
    - `flip()` : present the current frame (applies post-processing)
    - `tick()` / `get_delta_time()` : simple timing helpers (uses pygame.Clock)
    - `set_post_backend()` : switch between CPU and OpenGL post-process backends

    Example
    -------
    >>> DisplayManager.init(width=1280, height=720, caption="My Game")
    >>> surf = DisplayManager.get_surface()
    >>> # draw to surf, then:
    >>> DisplayManager.flip()

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
    _window_width: int = config.WINDOW_WIDTH
    _window_height: int = config.WINDOW_HEIGHT
    _luminosity: float = config.DISPLAY_LUMINOSITY
    _contrast: float = config.DISPLAY_CONTRAST
    _gamma: float = config.DISPLAY_GAMMA
    _colorblind_mode: Literal["none", "protanopia", "deuteranopia", "tritanopia"] = "none"
    _frame_counter: int = 0  # For post-process frame skipping
    _post_backend: Literal["cpu", "opengl"] = "opengl"
    _gl_enabled: bool = False
    _render_surface: Surface | None = None
    _gl_tex: int = 0
    _gl_prog: int = 0
    _gl_vao: int = 0
    _gl_vbo: int = 0
    _u_tex: int = -1
    _u_l: int = -1
    _u_c: int = -1
    _u_g: int = -1
    _u_cb: int = -1
    _lut: np.ndarray | None = None  # 3D LUT for CPU post-processing
    _lut_size: int = 64  # LUT resolution (64x64x64 = good balance speed/quality)
    _lut_dirty: bool = True  # Flag to regenerate LUT when params change

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

        pygame_display.init()

        # Create display FIRST (with OpenGL flags if requested)
        cls._create_display()

        # THEN try to initialize OpenGL resources (after display context exists)
        if cls._post_backend == "opengl" and _OPENGL_AVAILABLE:
            cls._gl_enabled = cls._setup_opengl()
            if cls._gl_enabled:
                # Offscreen render surface for game drawing (same size as window)
                try:
                    cls._render_surface = Surface((cls._window_width, cls._window_height)).convert_alpha()
                except Exception:
                    cls._render_surface = Surface((cls._window_width, cls._window_height))
                logger.info("[DisplayManager] OpenGL backend enabled (GPU post-process active)")
            else:
                logger.warning("[DisplayManager] OpenGL backend requested but setup failed. Falling back to CPU.")
                cls._post_backend = "cpu"
        elif cls._post_backend == "opengl" and not _OPENGL_AVAILABLE:
            cls._post_backend = "cpu"
            logger.warning("[DisplayManager] PyOpenGL not available. Falling back to CPU backend.")

        if cls._post_backend == "cpu":
            # CPU backend
            cls._gl_enabled = False
            cls._render_surface = None
            cls._create_display() # Recreate display without OpenGL flags
            logger.info("[DisplayManager] CPU backend enabled (CPU post-process active)")

        if cls._display is None:
            logger.error("[DisplayManager] Failed to initialize display")
            raise RuntimeError("DisplayManager initialization failed")

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
    def _create_display(cls) -> None:
        """Create pygame display in windowed or fullscreen mode."""
        display_flags = cls._flags
        window_w = cls._width
        window_h = cls._height

        if cls._fullscreen:
            display_flags |= FULLSCREEN
            info = pygame_display.Info()
            window_w, window_h = info.current_w, info.current_h

        try:
            pygame_display.quit()
            # If OpenGL backend, request OPENGL|DOUBLEBUF
            if cls._post_backend == "opengl":
                display_flags |= OPENGL | DOUBLEBUF
            cls._display = pygame_display.set_mode((window_w, window_h), display_flags, vsync=int(cls._vsync))
            pygame_display.set_caption(cls._caption)
            win_size = pygame_display.get_window_size()
            cls._window_width = win_size[0]
            cls._window_height = win_size[1]
            logger.info(f"[DisplayManager] Display created: {cls._window_width}x{cls._window_height}")
        except Exception as e:
            logger.warning(f"[DisplayManager] Display creation failed: {e}")
            cls._display = None

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
        # When GL is enabled, return offscreen render surface for game drawing
        if cls._gl_enabled and cls._render_surface is not None:
            return cls._render_surface
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
    def get_luminosity(cls) -> float:
        """Get current luminosity factor."""
        return cls._luminosity

    @classmethod
    def get_contrast(cls) -> float:
        """Get current contrast factor."""
        return cls._contrast

    @classmethod
    def get_gamma(cls) -> float:
        """Get current gamma value."""
        return cls._gamma

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
        try:
            cls._create_display()
            cls.show_cursor(config.SHOW_CURSOR)
            cls.set_icon(config.ICON_PATH)
            # Recreate GL resources if using OpenGL backend
            if cls._post_backend == "opengl" and _OPENGL_AVAILABLE:
                cls._gl_enabled = cls._setup_opengl()
                if cls._gl_enabled:
                    try:
                        cls._render_surface = Surface((cls._window_width, cls._window_height)).convert_alpha()
                    except Exception:
                        cls._render_surface = Surface((cls._window_width, cls._window_height))
            logger.info(f"[DisplayManager] Fullscreen toggled: {cls._fullscreen}")
        except Exception as e:
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
    def set_luminosity(cls, value: float) -> None:
        """Set luminosity multiplier applied at flip (0.0+)."""
        new_val = max(0.0, float(value))
        if cls._luminosity != new_val:
            cls._luminosity = new_val
            cls._lut_dirty = True

    @classmethod
    def set_contrast(cls, value: float) -> None:
        """Set contrast multiplier applied at flip (0.0+)."""
        new_val = max(0.0, float(value))
        if cls._contrast != new_val:
            cls._contrast = new_val
            cls._lut_dirty = True

    @classmethod
    def set_gamma(cls, value: float) -> None:
        """Set gamma value applied at flip (>=0.01)."""
        new_val = max(0.01, float(value))
        if cls._gamma != new_val:
            cls._gamma = new_val
            cls._lut_dirty = True

    @classmethod
    def set_post_backend(cls, backend: Literal["cpu", "opengl"]) -> None:
        """Set the post-process backend and reinitialize display resources if needed."""
        if backend not in ("cpu", "opengl"):
            logger.warning(f"[DisplayManager] Invalid backend: {backend}")
            return
        if cls._post_backend == backend:
            return
        cls._post_backend = backend
        # Recreate display with appropriate flags and GL resources
        try:
            cls._create_display()
            cls.show_cursor(config.SHOW_CURSOR)
            cls.set_icon(config.ICON_PATH)
            if backend == "opengl" and _OPENGL_AVAILABLE:
                cls._gl_enabled = cls._setup_opengl()
                if cls._gl_enabled:
                    try:
                        cls._render_surface = Surface((cls._window_width, cls._window_height)).convert_alpha()
                    except Exception:
                        cls._render_surface = Surface((cls._window_width, cls._window_height))
                    logger.info("[DisplayManager] Backend switched to OpenGL")
                else:
                    logger.warning("[DisplayManager] OpenGL setup failed during backend switch; falling back to CPU")
                    cls._post_backend = "cpu"
                    cls._gl_enabled = False
                    cls._render_surface = None
            else:
                # CPU backend
                cls._gl_enabled = False
                cls._render_surface = None
                logger.info("[DisplayManager] Backend switched to CPU")
        except Exception as e:
            logger.error(f"[DisplayManager] Backend switch failed: {e}")

    @classmethod
    def flip(cls) -> None:
        """
        Update the display (flip buffers) with post-processing applied.
        """
        if cls._display is None:
            logger.error("[DisplayManager] Display not initialized! Call init() first.")
            raise RuntimeError("DisplayManager not initialized")

        surface = cls.get_surface()
        # Scale if fullscreen (use fast scale instead of smoothscale)
        if cls._window_width != cls._width or cls._window_height != cls._height:
            if not cls._gl_enabled:
                surface = pygame_transform.scale(cls._display, (cls._window_width, cls._window_height))
                cls._display.blit(surface, (0, 0))

        if cls._gl_enabled:
            # GPU path: upload render surface to GL texture, run post-process shader, present
            # Log once on first GPU present to confirm the active path
            if cls._frame_counter == 0:
                logger.info("[DisplayManager] Using GPU pipeline for flip()")
            cls._gl_present(surface)
            pygame_display.flip()
            cls._frame_counter += 1
            return
        else:
            # CPU path: apply post-process via LUT on surface pixels
            cls._apply_post_process(surface)

        pygame_display.flip()
        cls._frame_counter += 1

    # ----- OpenGL helpers -----
    @classmethod
    def _setup_opengl(cls) -> bool:
        """Initialize OpenGL resources (shader, quad, texture)."""
        try:
            # Build shader program
            vert_src = """
            #version 330 core
            layout(location = 0) in vec2 in_pos;
            layout(location = 1) in vec2 in_uv;
            out vec2 uv;
            void main() {
                uv = vec2(in_uv.x, 1.0 - in_uv.y);
                gl_Position = vec4(in_pos, 0.0, 1.0);
            }
            """
            frag_src = """
            #version 330 core
            uniform sampler2D u_tex;
            uniform float u_luminosity;
            uniform float u_contrast;
            uniform float u_gamma;
            uniform int u_cb_mode; // 0 none, 1 protanopia, 2 deuteranopia, 3 tritanopia
            in vec2 uv;
            out vec4 fragColor;

            vec3 apply_colorblind(vec3 c) {
                if (u_cb_mode == 1) {
                    c.r *= 0.567;
                    c.g += 0.433 * c.r;
                } else if (u_cb_mode == 2) {
                    c.g *= 0.625;
                    c.b += 0.375 * c.g;
                } else if (u_cb_mode == 3) {
                    c.b *= 0.95;
                }
                return c;
            }

            void main() {
                vec4 texel = texture(u_tex, uv);
                vec3 c = texel.rgb;
                // luminosity
                c *= u_luminosity;
                // contrast
                c = (c - 0.5) * u_contrast + 0.5;
                // gamma
                c = pow(clamp(c, 0.0, 1.0), vec3(1.0 / max(u_gamma, 0.001)));
                // colorblind
                c = apply_colorblind(c);
                fragColor = vec4(clamp(c, 0.0, 1.0), texel.a);
            }
            """
            vs = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vs, vert_src)
            glCompileShader(vs)
            status = glGetShaderiv(vs, GL_COMPILE_STATUS)
            if not status:
                err = glGetShaderInfoLog(vs).decode()
                logger.error(f"[DisplayManager] Vertex shader compile failed: {err}")
                return False

            fs = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fs, frag_src)
            glCompileShader(fs)
            status = glGetShaderiv(fs, GL_COMPILE_STATUS)
            if not status:
                err = glGetShaderInfoLog(fs).decode()
                logger.error(f"[DisplayManager] Fragment shader compile failed: {err}")
                return False

            prog = glCreateProgram()
            glAttachShader(prog, vs)
            glAttachShader(prog, fs)
            glLinkProgram(prog)
            link_ok = glGetProgramiv(prog, GL_LINK_STATUS)
            if not link_ok:
                err = glGetProgramInfoLog(prog).decode()
                logger.error(f"[DisplayManager] Program link failed: {err}")
                return False
            cls._gl_prog = prog

            # Full-screen quad (NDC)
            cls._gl_vao = glGenVertexArrays(1)
            glBindVertexArray(cls._gl_vao)
            cls._gl_vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, cls._gl_vbo)
            quad = np.array([
                # x, y,   u, v
                -1.0, -1.0, 0.0, 0.0,
                 1.0, -1.0, 1.0, 0.0,
                 1.0,  1.0, 1.0, 1.0,
                -1.0, -1.0, 0.0, 0.0,
                 1.0,  1.0, 1.0, 1.0,
                -1.0,  1.0, 0.0, 1.0,
            ], dtype=np.float32)
            glBufferData(GL_ARRAY_BUFFER, quad.nbytes, quad, GL_STATIC_DRAW)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, False, 16, ctypes.c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 2, GL_FLOAT, False, 16, ctypes.c_void_p(8))

            # Texture for uploaded surface
            cls._gl_tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, cls._gl_tex)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            # Allocate texture storage
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, cls._window_width, cls._window_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
            glBindTexture(GL_TEXTURE_2D, 0)

            glViewport(0, 0, cls._window_width, cls._window_height)
            glClearColor(0.0, 0.0, 0.0, 1.0)
            glUseProgram(cls._gl_prog)
            cls._u_tex = glGetUniformLocation(cls._gl_prog, "u_tex")
            cls._u_l = glGetUniformLocation(cls._gl_prog, "u_luminosity")
            cls._u_c = glGetUniformLocation(cls._gl_prog, "u_contrast")
            cls._u_g = glGetUniformLocation(cls._gl_prog, "u_gamma")
            cls._u_cb = glGetUniformLocation(cls._gl_prog, "u_cb_mode")
            glUseProgram(0)
            return True
        except Exception as e:
            logger.error(f"[DisplayManager] OpenGL setup failed: {e}")
            return False

    @classmethod
    def _gl_present(cls, surface: Surface) -> None:
        """Upload pygame surface to GL texture and render with shader."""
        try:
            # Convert surface to bytes for OpenGL upload (Y already flipped in shader)
            img_data = pygame_image.tostring(surface, "RGBA", False)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, cls._gl_tex)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, cls._window_width, cls._window_height, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

            # Draw full-screen quad
            glUseProgram(cls._gl_prog)
            glUniform1i(cls._u_tex, 0)
            glUniform1f(cls._u_l, float(cls._luminosity))
            glUniform1f(cls._u_c, float(cls._contrast))
            glUniform1f(cls._u_g, float(cls._gamma))
            mode_map = {"none": 0, "protanopia": 1, "deuteranopia": 2, "tritanopia": 3}
            glUniform1i(cls._u_cb, int(mode_map.get(cls._colorblind_mode, 0)))

            glBindVertexArray(cls._gl_vao)
            glBindTexture(GL_TEXTURE_2D, cls._gl_tex)
            glDrawArrays(GL_TRIANGLES, 0, 6)
            glBindTexture(GL_TEXTURE_2D, 0)
        except Exception as e:
            logger.warning(f"[DisplayManager] GL present failed: {e}")


    @classmethod
    def _generate_lut(cls) -> None:
        """
        Generate a 3D LUT (Look-Up Table) for fast post-processing.
        Pre-calculates all transformations (luminosity, contrast, gamma, colorblind).
        """
        try:
            size = cls._lut_size
            # Create coordinate grids for R, G, B (normalized 0-1)
            indices = np.linspace(0, 1, size, dtype=np.float32)
            r, g, b = np.meshgrid(indices, indices, indices, indexing='ij')
            
            # Stack into shape (size, size, size, 3)
            lut = np.stack([r, g, b], axis=-1)
            
            # Apply luminosity
            if cls._luminosity != 1.0:
                lut *= cls._luminosity
            
            # Apply contrast
            if cls._contrast != 1.0:
                lut = (lut - 0.5) * cls._contrast + 0.5
            
            # Apply gamma
            if cls._gamma != 1.0:
                lut = np.power(np.clip(lut, 0.0, 1.0), 1.0 / max(cls._gamma, 0.001))
            
            # Apply colorblind simulation
            if cls._colorblind_mode == "protanopia":
                lut[..., 0] *= 0.567
                lut[..., 1] += 0.433 * lut[..., 0]
            elif cls._colorblind_mode == "deuteranopia":
                lut[..., 1] *= 0.625
                lut[..., 2] += 0.375 * lut[..., 1]
            elif cls._colorblind_mode == "tritanopia":
                lut[..., 2] *= 0.95
            
            # Clamp to [0, 1] and convert to uint8 for fast lookup
            cls._lut = (np.clip(lut, 0.0, 1.0) * 255.0).astype(np.uint8)
            cls._lut_dirty = False
            logger.info(f"[DisplayManager] LUT generated ({size}x{size}x{size})")
        except Exception as e:
            logger.error(f"[DisplayManager] LUT generation failed: {e}")
            cls._lut = None

    @classmethod
    def _apply_post_process(cls, surface: Surface) -> None:
        """
        Apply post-processing using 3D LUT (Look-Up Table) for fast performance.
        NOTE: CPU post-processing is disabled for performance reasons.
        For real-time post-processing, use GPU backend (OpenGL).
        """
        # CPU post-processing is disabled - it's too slow for real-time gameplay
        # Post-processing only works with GPU backend (OpenGL)

    @classmethod
    def set_colorblind_mode(cls, mode: Literal["none", "protanopia", "deuteranopia", "tritanopia"] = "none") -> None:
        """
        Set the colorblind mode (applies simulation filter to post-process).
        
        Args:
            - mode: "none", "protanopia", "deuteranopia", or "tritanopia"
        """
        if mode not in ["none", "protanopia", "deuteranopia", "tritanopia"]:
            logger.warning(f"[DisplayManager] Invalid colorblind mode: {mode}")
            return
        if cls._colorblind_mode != mode:
            cls._colorblind_mode = mode
            cls._lut_dirty = True
        logger.info(f"[DisplayManager] Colorblind mode set to: {cls._colorblind_mode}")

    @classmethod
    def get_colorblind_mode(cls) -> str:
        """Get the current colorblind mode."""
        return cls._colorblind_mode

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
            pygame_image.save(cls.get_surface(), str(filepath))
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
            try:
                cls._create_display()
                cls.show_cursor(config.SHOW_CURSOR)
                cls.set_icon(config.ICON_PATH)
                logger.info(f"[DisplayManager] VSync {'enabled' if enabled else 'disabled'}")
            except Exception as e:
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
