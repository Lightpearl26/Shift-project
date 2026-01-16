# -*- coding: utf-8 -*-

"""
game_libs.transition.fade
___________________________________________________________________________________________________
File infos:

    - Author: Justine Roux
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines Particles as scene transition.
___________________________________________________________________________________________________
@copyright: Justine Roux 2026
"""
# import needed built-in modules
from __future__ import annotations
from typing import TYPE_CHECKING
import random
import math

# import pygame modules
from pygame import Rect

# import base transition
from .base import BaseTransition

# import logger
from .. import logger

if TYPE_CHECKING:
    pass


TILE_SIZE = 20      
WIND_SPEED = 20     
TURBULENCE_AMP = 20 # Amplitude de l'ondulation (plus grand = moins "carré")

class DustParticleOut:
    def __init__(self, image, x, y, delay, screen_width):
        self.image = image
        self.rect = image.get_rect()
        self.x = x
        self.y = y
        self.start_y = y
        
        # VITESSE : Très variée pour étaler le nuage
        self.vx = random.uniform(WIND_SPEED, WIND_SPEED + 15)
        
        # ONDULATION : Désynchronisée
        self.freq = random.uniform(0.05, 0.15)
        self.phase = random.uniform(0, 6.28)
        
        self.delay = delay
        self.screen_width = screen_width
        self.alpha = 255
        self.visible = True

    def update(self, progress):
        if progress < self.delay:
            return

        # Temps écoulé depuis activation
        t = (progress - self.delay) * 15

        # Mouvement
        self.x += self.vx 
        # On ajoute du chaos vertical pour casser l'alignement des grilles
        self.y = self.start_y + math.sin(t * self.freq + self.phase) * TURBULENCE_AMP
        
        # Fade Out
        self.alpha -= 10 # Disparition plus rapide pour alléger le CPU
        if self.alpha <= 0:
            self.alpha = 0
            self.visible = False
        
        self.image.set_alpha(self.alpha)
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.visible and self.x < self.screen_width:
            surface.blit(self.image, self.rect)


class DustParticleIn:
    def __init__(self, image, target_x, target_y, delay):
        self.image = image
        self.rect = image.get_rect()
        self.target_x = target_x
        self.target_y = target_y
        
        # DÉPART : Étale sur la gauche hors écran
        self.start_x = -random.uniform(50, 500)
        self.x = self.start_x
        # On fait arriver les particules de hauteurs différentes pour effet tempête
        self.y = target_y + random.uniform(-50, 50) 
        
        self.vx = random.uniform(25, 40)
        
        self.delay = delay
        self.arrived = False
        self.alpha = 0
        self.image.set_alpha(0)

    def update(self, progress):
        if progress < self.delay:
            return
        
        if self.arrived:
            return

        # Mouvement
        self.x += self.vx
        
        # Lissage Y : On revient vers la ligne cible
        dy = self.target_y - self.y
        self.y += dy * 0.1
        
        # Apparition
        self.alpha += 15
        if self.alpha > 255: self.alpha = 255
        self.image.set_alpha(self.alpha)
        
        # Arrivée (Snapping)
        if self.x >= self.target_x:
            self.x = self.target_x
            self.y = self.target_y
            self.arrived = True
            self.image.set_alpha(255)
        
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.x > self.start_x:
            surface.blit(self.image, self.rect)


class DustOut(BaseTransition):
    def __init__(self, duration: float, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size
        self.particles = []
        self.generated = False

    def start(self):
        super().start()
        self.generated = False
        self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols = width // self.tile_size
        rows = height // self.tile_size
        src = surface.copy()

        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try:
                    sub = src.subsurface(rect).copy()
                except ValueError:
                    continue
                
                # Délai Gauche -> Droite
                norm_x = x / width
                delay = norm_x * 0.4 + random.uniform(0, 0.05)
                
                self.particles.append(DustParticleOut(sub, x, y, delay, width))
        self.generated = True

    def render(self, surface):
        if not self.generated:
            self._generate(surface)
            return
        
        # Fond Noir
        surface.fill((0, 0, 0))
        
        # Optimisation : On ne dessine pas tout aveuglément
        for p in self.particles:
            p.update(self.progress)
            p.draw(surface)


class DustIn(BaseTransition):
    def __init__(self, duration: float, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size
        self.particles = []
        self.generated = False

    def start(self):
        super().start()
        self.generated = False
        self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols = width // self.tile_size
        rows = height // self.tile_size
        src = surface.copy()

        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try:
                    sub = src.subsurface(rect).copy()
                except ValueError:
                    continue
                
                # Délai Gauche -> Droite
                norm_x = x / width
                delay = norm_x * 0.4 + random.uniform(0, 0.05)
                
                self.particles.append(DustParticleIn(sub, x, y, delay))
        self.generated = True

    def render(self, surface):
        if not self.generated:
            self._generate(surface)
            return
        
        # IMPORTANT : On couvre TOUT de noir avant de dessiner les particules
        # C'est ce qui évite de voir le menu "Nouvelle Partie" derrière en fantôme.
        surface.fill((0, 0, 0))
        
        for p in self.particles:
            p.update(self.progress)
            p.draw(surface)