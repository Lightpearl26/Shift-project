# -*- coding: utf-8 -*-

"""game_libs.managers.dialog
___________________________________________________________________________________________________
Dialog manager acting as a simple queue and I/O pipe.
___________________________________________________________________________________________________
(c) Lafiteau Franck 2026
"""

from __future__ import annotations
from typing import Optional


class DialogManager:
    """Global dialog queue with minimal state tracking."""

    _queue: list[str] = []
    _active: Optional[str] = None
    _done: set[str] = set()

    @classmethod
    def enqueue(cls, name: str, force: bool = False) -> bool:
        """Queue a dialog name. Returns True if queued or already active."""
        if not name:
            return False
        if cls._active == name or name in cls._queue:
            return True
        if force:
            cls._queue.insert(0, name)
        else:
            cls._queue.append(name)
        return True

    @classmethod
    def request_next(cls) -> Optional[str]:
        """Pop next dialog from the queue and mark it active."""
        if cls._active is not None:
            return None
        if not cls._queue:
            return None
        cls._active = cls._queue.pop(0)
        return cls._active

    @classmethod
    def mark_done(cls, name: str) -> None:
        """Mark a dialog as completed and clear active if matching."""
        if not name:
            return
        cls._done.add(name)
        if cls._active == name:
            cls._active = None

    @classmethod
    def is_done(cls, name: str) -> bool:
        """Check and consume the done flag for a dialog name."""
        if name in cls._done:
            cls._done.remove(name)
            return True
        return False

    @classmethod
    def clear(cls) -> None:
        """Clear queue and state."""
        cls._queue.clear()
        cls._done.clear()
        cls._active = None

    @classmethod
    def remove(cls, name: str) -> None:
        """Remove a dialog name from the queue."""
        if name in cls._queue:
            cls._queue = [n for n in cls._queue if n != name]
