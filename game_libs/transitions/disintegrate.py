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

# import pygame modules
from pygame import Rect

# import base transition
from .base import BaseTransition

if TYPE_CHECKING:
    from pygame import Surface

DEFAULT_TILE_SIZE = 20
DEFAULT_SPEED = 25     # Vitesse de déplacement

class SlideOutParticle:
    """Gère un morceau de la vieille scène qui part vers la droite"""
    def __init__(self, image, x, y, delay, width):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y
        self.width = width
        
        # Vitesse constante vers la droite
        self.velocity = random.uniform(DEFAULT_SPEED, DEFAULT_SPEED + 5)
        
        self.delay = delay
        self.active = False

    def update(self, progress):
        if progress < self.delay:
            return

        self.active = True
        self.x += self.velocity
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface: Surface):
        # On dessine tant que c'est sur l'écran
        if self.x < surface.get_width():
            surface.blit(self.image, self.rect)


class SlideInParticle:
    """Gère un morceau de la NOUVELLE scène qui arrive de la gauche"""
    def __init__(self, image, target_x, target_y, delay):
        self.image = image
        self.rect = image.get_rect()
        
        self.target_x = target_x
        self.target_y = target_y
        
        # DÉPART : Hors écran à GAUCHE
        # On ajoute un petit random (-50) pour que la ligne de coupure ne soit pas trop droite
        self.start_x = -random.uniform(DEFAULT_TILE_SIZE, DEFAULT_TILE_SIZE * 3)
        self.x = self.start_x
        self.y = target_y
        
        # VITESSE : Doit être rapide pour rattraper le retard du délai
        self.velocity = random.uniform(DEFAULT_SPEED + 5, DEFAULT_SPEED + 15)
        
        self.delay = delay
        self.arrived = False

    def update(self, progress):
        if progress < self.delay:
            return

        if self.arrived:
            return

        # Mouvement vers la droite
        self.x += self.velocity
        
        # "Snapping" : Si on dépasse la cible, on se gare
        if self.x >= self.target_x:
            self.x = self.target_x
            self.arrived = True
        
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        # On ne dessine que si ça a commencé à entrer sur l'écran
        if self.x > self.start_x:
            surface.blit(self.image, self.rect)


class Disintegrate(BaseTransition):
    def __init__(self, duration: float, tile_size: int = DEFAULT_TILE_SIZE):
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
                
                # DÉLAI : De Gauche (0.0) à Droite (0.5)
                # Cela crée l'effet de vague qui part
                norm_x = x / width
                delay = norm_x * 0.5 
                
                self.particles.append(SlideOutParticle(sub, x, y, delay, width))
        self.generated = True

    def render(self, surface):
        if not self.generated:
            self._generate(surface)
            return
        
        surface.fill((0, 0, 0)) # Fond noir derrière les blocs qui partent
        for p in self.particles:
            p.update(self.progress)
            p.draw(surface)


class Integrate(BaseTransition):
    def __init__(self, duration: float, tile_size: int = DEFAULT_TILE_SIZE):
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
                
                # DÉLAI : De Gauche (0.0) à Droite (0.5)
                # Important : La gauche arrive en premier pour combler le vide
                norm_x = x / width
                delay = norm_x * 0.5
                
                self.particles.append(SlideInParticle(sub, x, y, delay))
        self.generated = True

    def render(self, surface):
        if not self.generated:
            self._generate(surface)
            return
        
        surface.fill((0, 0, 0)) # Fond noir en attendant que les blocs arrivent
        for p in self.particles:
            p.update(self.progress)
            p.draw(surface)