# -*- coding: utf-8 -*-

"""dialog.runtime
___________________________________________________________________________________________________
Simple runtime for auto-advancing dialogs during gameplay.
___________________________________________________________________________________________________
(c) Lafiteau Franck 2026
"""

from __future__ import annotations
from typing import Callable, Optional
from os.path import join

from pygame import Surface, Rect, SRCALPHA
from pygame.draw import rect as draw_rect

from .. import config, logger
from ..assets_cache import AssetsCache
from .component import Dialog, DialogParagraph, DialogOption, DialogGoto


class DialogRuntime:
    """Runtime that auto-advances dialog paragraphs without choices."""

    def __init__(
        self,
        dialog_loader: Callable[[str], Dialog],
        seconds_per_line: float = 1.6,
        padding: int = 24,
        font_name: str = "Pixel Game.otf",
        font_size: int = 36,
    ) -> None:
        self._dialog_loader = dialog_loader
        self._seconds_per_line = seconds_per_line
        self._padding = padding
        self._font = AssetsCache.load_font(join(config.FONT_FOLDER, font_name), font_size)
        self._panel_color = (0, 0, 0, 180)
        self._border_color = (255, 255, 255, 120)
        self._current: Optional[Dialog] = None
        self._lines: list[str] = []
        self._time_left: float = 0.0
        self._char_time_left: float = 0.0
        self._seconds_per_char: float = 0.02
        self._char_index: int = 0
        self._active: bool = False
        self._dialog_name: Optional[str] = None

    @property
    def active(self) -> bool:
        """Return True when a dialog is running."""
        return self._active

    def start_autorun(self, dialog_name: str) -> None:
        """Start an autorun dialog by name."""
        self._dialog_name = dialog_name
        self._current = self._dialog_loader(dialog_name)
        self._active = True
        self._lines = []
        self._time_left = 0.0
        self._char_time_left = 0.0
        self._char_index = 0
        self._prepare_current()

    def stop(self) -> None:
        """Stop the current dialog."""
        self._active = False
        self._current = None
        self._lines = []
        self._time_left = 0.0
        self._char_time_left = 0.0
        self._char_index = 0
        self._dialog_name = None

    def update(self, dt: float) -> None:
        """Advance dialog time and move to the next paragraph when needed."""
        if not self._active:
            return
        if self._current is None:
            self.stop()
            return
        if not self._lines:
            self._prepare_current()
            if not self._active:
                return
        if self._seconds_per_char > 0.0:
            self._char_time_left -= dt
            while self._char_time_left <= 0.0 and self._char_index < self._total_chars():
                self._char_index += 1
                self._char_time_left += self._seconds_per_char
        self._time_left -= dt
        if self._time_left <= 0.0:
            self._advance()

    def render(self, surface: Surface) -> None:
        """Render the dialog overlay."""
        if not self._active or not self._lines:
            return
        width, height = surface.get_size()
        panel_height = max(int(height * 0.2), 140)
        panel_width = max(int(width * 0.6), 400)
        panel_rect = Rect(
            (width - panel_width - self._padding) / 2,
            height - panel_height - self._padding,
            panel_width,
            panel_height,
        )

        panel = Surface(panel_rect.size, SRCALPHA)
        panel.fill(self._panel_color)
        draw_rect(panel, self._border_color, panel.get_rect(), width=2)
        surface.blit(panel, panel_rect.topleft)

        max_text_width = panel_rect.width - self._padding * 2
        line_height = self._font.get_linesize()
        max_lines = max(1, (panel_rect.height - self._padding * 2) // line_height)

        rendered_lines: list[str] = []
        remaining = self._char_index
        for line in self._lines:
            line_text = line
            if remaining < len(line_text):
                line_text = line_text[:remaining]
            remaining -= len(line)
            if remaining < 0:
                remaining = 0
            if line_text or rendered_lines:
                rendered_lines.extend(self._wrap_line(line_text, max_text_width))
            if remaining == 0:
                break
        rendered_lines = rendered_lines[:max_lines]

        y = panel_rect.top + self._padding
        for line in rendered_lines:
            text_surf = self._font.render(line, True, (255, 255, 255))
            surface.blit(text_surf, (panel_rect.left + self._padding, y))
            y += line_height

    def _wrap_line(self, text: str, max_width: int) -> list[str]:
        if not text:
            return [""]
        words = text.split(" ")
        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if self._font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def _advance(self) -> None:
        if self._current is None:
            self.stop()
            return
        node = self._current.node
        if isinstance(node, DialogParagraph):
            if not self._current.children:
                self.stop()
                return
            if len(self._current.children) > 1:
                logger.warning(f"Dialog runtime hit branch paragraph in auto mode for {self._dialog_name}")
                self.stop()
                return
            self._current = self._current.children[0]
            self._lines = []
            self._char_index = 0
            self._prepare_current()
            return
        if isinstance(node, DialogOption):
            logger.warning(f"Dialog runtime hit choice in auto mode for {self._dialog_name}")
            self.stop()
            return
        if isinstance(node, DialogGoto):
            self._lines = []
            self._char_index = 0
            self._prepare_current()
            return
        self.stop()

    def _prepare_current(self) -> None:
        if self._current is None:
            self.stop()
            return
        resolved = self._resolve_goto(self._current)
        if resolved is None:
            self.stop()
            return
        self._current = resolved
        node = self._current.node
        if node is None:
            self.stop()
            return
        if isinstance(node, DialogParagraph):
            self._lines = list(node.lines)
            line_count = max(1, len(self._lines))
            self._time_left = self._seconds_per_line * line_count
            total_chars = self._total_chars()
            if total_chars > 0:
                self._char_time_left = self._seconds_per_char
            else:
                self._char_time_left = 0.0
            self._char_index = 0
            return
        if isinstance(node, DialogOption):
            logger.warning(f"Dialog runtime hit choice in auto mode for {self._dialog_name}")
            self.stop()
            return
        if isinstance(node, DialogGoto):
            self._lines = []
            self._char_index = 0
            self._prepare_current()
            return
        self.stop()

    def _total_chars(self) -> int:
        return sum(len(line) for line in self._lines)

    def _resolve_goto(self, dialog: Dialog) -> Optional[Dialog]:
        hop_limit = 16
        current = dialog
        hops = 0
        while isinstance(current.node, DialogGoto):
            hops += 1
            if hops > hop_limit:
                logger.warning(f"Dialog runtime exceeded goto hop limit for {self._dialog_name}")
                return None
            current = self._dialog_loader(current.node.target_name)
        return current
