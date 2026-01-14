# -*- coding: utf-8 -*-
#pylint: disable=no-member

"""
SHIFT PROJECT Scenes
____________________________________________________________________________________________________
video transitions
version : 1.0
____________________________________________________________________________________________________
video transitions between scenes
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import cv2
import numpy as np
from pygame import Surface, surfarray

from .base import BaseTransition

if TYPE_CHECKING:
    from ..scenes import BaseScene
    from pathlib import Path


class VideoTransition(BaseTransition):
    """
    Play a video as a transition between scenes.
    Supports common formats: .mp4, .avi, .mov, .webm
    """

    def __init__(self, video_path: Path, loop: bool = False) -> None:
        """
        Args:
            video_path: Path to video file
            loop: If True, loop video until duration is reached
        """
        super().__init__(0)  # Duration sera calculée depuis la vidéo

        self.video_path = video_path
        self.loop = loop
        self._capture: cv2.VideoCapture | None = None
        self._fps: float = 30.0
        self._frame_duration: float = 0.0
        self._total_frames: int = 0
        self._current_frame: int = 0

    def play(self) -> None:
        """Start the video transition."""
        super().start()

        # Ouvrir la vidéo
        self._capture = cv2.VideoCapture(str(self.video_path))

        if not self._capture.isOpened():
            raise RuntimeError(f"Failed to open video: {self.video_path}")

        # Récupérer les propriétés de la vidéo
        self._fps = self._capture.get(cv2.CAP_PROP_FPS) or 30.0
        self._frame_duration = 1.0 / self._fps  # seconds per frame
        self._total_frames = int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculer la durée totale en secondes (stockage interne)
        self._duration = self._total_frames * self._frame_duration
        self._current_frame = 0

    def update(self, dt: float) -> None:
        """Update video playback."""
        if not self._is_playing:
            return

        super().update(dt)

        # Calculer quelle frame afficher en fonction du temps écoulé
        target_frame = int(self._elapsed / self._frame_duration)

        # Gérer le loop si activé
        if self.loop and target_frame >= self._total_frames:
            target_frame = target_frame % self._total_frames
            self._capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            self._current_frame = target_frame

        # Ne pas dépasser le nombre de frames
        if target_frame >= self._total_frames:
            target_frame = self._total_frames - 1
            if not self.loop:
                self._is_complete = True

    def render(self, surface: Surface) -> None:
        """Render the current video frame."""
        if not self._is_playing or not self._capture:
            return

        # Lire la frame actuelle
        ret, frame = self._capture.read()

        if not ret:
            # Fin de la vidéo
            if self.loop:
                # Recommencer depuis le début
                self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self._capture.read()
            else:
                self._is_complete = True
                return

        if frame is None:
            return

        # Convertir BGR (OpenCV) en RGB (Pygame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Redimensionner la frame à la taille de la surface
        target_size = (surface.get_width(), surface.get_height())
        frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)

        # Créer une surface Pygame depuis le numpy array
        # Rotation de 90° et flip nécessaires pour l'orientation correcte
        frame = np.rot90(frame)
        frame = np.flipud(frame)

        video_surface = surfarray.make_surface(frame)

        # Afficher la vidéo par-dessus
        surface.blit(video_surface, (0, 0))

    def __del__(self) -> None:
        """Cleanup: release video capture."""
        if self._capture is not None:
            self._capture.release()
