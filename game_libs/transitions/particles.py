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

# import logger
from .. import logger

if TYPE_CHECKING:
    pass

# DEBUG NOTE:
# The screen ratio is approx 1.77 (1920/1080).
# To ensure the transition feels like it takes the exact same amount of time
# vertically as it does horizontally, vertical speeds are scaled down by ~1.77.

# 1. HORIZONTAL SETTINGS (Reference Width ~1920px)
SPEED_OUT_H = 20.0  # Base speed for the exiting scene (chased by the new scene)
SPEED_IN_H = 35.0   # Base speed for the entering scene (faster to eat the void)
CHAOS_H = 15.0      # Amplitude of random speed variance (creates debris effect)

# 2. VERTICAL SETTINGS (Reference Height ~1080px)
# DEBUG: Calculated as Horizontal / 1.77
SPEED_OUT_V = 11.25 # Slower than H to traverse a shorter distance in same time
SPEED_IN_V = 19.75
CHAOS_V = 8.5       # Reduced chaos to maintain consistent debris density visually

TILE_SIZE = 20
DURATION = 1500

# --- CHAOS DELAY SETTINGS ---
# Controls the shape of the "wave" vs the "random popping".
# DEBUG: If the line looks too straight, increase DELAY_NOISE.
# DEBUG: If the wave is too slow/fast, adjust DELAY_GRADIENT.
DELAY_GRADIENT = 0.45
DELAY_NOISE = 0.25

# ==============================================================================
# 1. DIRECTION: RIGHT (Wipe Left -> Right)
# ==============================================================================

class DisintegrateRightParticle:
    """
    Represents a single tile of the EXITING scene moving towards the RIGHT.
    Simulates a debris particle detaching from the main image.
    """
    def __init__(self, image, x, y, delay, screen_width):
        """
        Initialize the particle.
        
        Args:
            image (Surface): The cropped tile image.
            x, y (int): Starting coordinates.
            delay (float): Time to wait before moving (0.0 to 1.0).
            screen_width (int): Boundary for culling.
        """
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y
        self.screen_width = screen_width
        
        # DEBUG: Velocity = Base Speed + Random Chaos.
        # This variance ensures tiles don't move as a solid block.
        self.velocity = SPEED_OUT_H + random.uniform(0, CHAOS_H)
        self.delay = delay

    def update(self, progress):
        """
        Updates position based on transition progress.
        Logic: Wait for delay -> Move horizontally.
        """
        if progress < self.delay :
            return
        self.x += self.velocity
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        """Draws the particle only if it hasn't left the screen boundary."""
        if self.x < self.screen_width:
            surface.blit(self.image, self.rect)

class IntegrateRightParticle:
    """
    Represents a single tile of the ENTERING scene moving towards the RIGHT.
    Simulates a chaotic storm reforming into a solid image.
    """
    def __init__(self, image, target_x, target_y, delay):
        """
        Args:
            target_x, target_y: The final resting position of the tile.
        """
        self.image = image
        self.rect = image.get_rect()
        self.target_x = target_x
        self.target_y = target_y
        # Start position: Just outside the left edge of the screen
        self.start_x = -TILE_SIZE
        self.x = self.start_x
        self.y = target_y
        # DEBUG: We use Chaos here too so the entry looks organic, not rigid.
        self.velocity = SPEED_IN_H + random.uniform(0, CHAOS_H)
        self.delay = delay
        self.arrived = False

    def update(self, progress):
        """
        Moves the particle towards its target. 
        Snaps to the exact pixel once it reaches or passes the target.
        """
        if progress < self.delay :
            return
        if self.arrived :
            return
        self.x += self.velocity
        # SNAP LOGIC: We are moving Right (positive), so if x >= target, stop.
        if self.x >= self.target_x:
            self.x = self.target_x
            self.arrived = True
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        """Draws only if the particle has entered the screen (passed start_x)."""
        if self.x > self.start_x:
            surface.blit(self.image, self.rect)

class DisintegrateRight(BaseTransition):
    """
    Transition Effect: Disintegrates the old scene from Left to Right.
    Looks like the screen is turning to dust.
    """
    def __init__(self, duration: float = DURATION, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size; self.particles = []; self.generated = False

    def start(self): 
        """Resets the transition state."""
        super().start(); self.generated = False; self.particles = []

    def _generate(self, surface):
        """
        Slices the input surface into tiles and assigns Delay/Velocity.
        """
        width, height = surface.get_size()
        cols, rows = width // self.tile_size, height // self.tile_size
        src = surface.copy()
        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try: sub = src.subsurface(rect).copy()
                except ValueError: continue
                
                # DEBUG: Delay Calculation
                # norm_x (0.0 to 1.0) * GRADIENT creates the wave direction.
                # + random(NOISE) adds the "crumbling" effect.
                norm_x = x / width
                delay = (norm_x * DELAY_GRADIENT) + random.uniform(0, DELAY_NOISE)
                
                self.particles.append(DisintegrateRightParticle(sub, x, y, delay, width))
        self.generated = True

    def render(self, surface):
        """Main render loop: Generate -> Clear Screen -> Update Particles."""
        if not self.generated: self._generate(surface); surface.fill((0,0,0)); return
        surface.fill((0, 0, 0))
        for p in self.particles: p.update(self.progress); p.draw(surface)

class IntegrateRight(BaseTransition):
    """
    Transition Effect: Reassembles the new scene from Left to Right.
    Looks like a chaotic storm solidifying into the new image.
    """
    def __init__(self, duration: float = DURATION, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size; self.particles = []; self.generated = False
    
    def start(self): 
        super().start(); self.generated = False; self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols, rows = width // self.tile_size, height // self.tile_size
        src = surface.copy()
        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try: sub = src.subsurface(rect).copy()
                except ValueError: continue
                
                norm_x = x / width
                # DEBUG: The '+ 0.05' offset ensures the "In" particles start slightly 
                # after the "Out" particles to prevent visual clipping at frame 0.
                delay = (norm_x * DELAY_GRADIENT) + random.uniform(0, DELAY_NOISE) + 0.05
                
                self.particles.append(IntegrateRightParticle(sub, x, y, delay))
        self.generated = True

    def render(self, surface):
        if not self.generated: self._generate(surface); surface.fill((0,0,0)); return
        surface.fill((0, 0, 0))
        for p in self.particles: p.update(self.progress); p.draw(surface)


# ==============================================================================
# 2. DIRECTION: LEFT (Wipe Right -> Left)
# ==============================================================================

class DisintegrateLeftParticle:
    """Exiting particle moving LEFT (Negative Velocity)."""
    def __init__(self, image, x, y, delay, screen_width):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y
        # DEBUG: Negative speed to move Left. Uses Horizontal constants.
        self.velocity = -(SPEED_OUT_H + random.uniform(0, CHAOS_H))
        self.delay = delay

    def update(self, progress):
        if progress < self.delay: return
        self.x += self.velocity
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        # DEBUG: Only draw if the tile is still physically on screen (x + size > 0)
        if self.x + TILE_SIZE > 0:
            surface.blit(self.image, self.rect)

class IntegrateLeftParticle:
    """Entering particle moving LEFT (Negative Velocity)."""
    def __init__(self, image, target_x, target_y, delay, screen_width):
        self.image = image
        self.rect = image.get_rect()
        self.target_x = target_x
        self.target_y = target_y
        self.start_x = screen_width # Start outside Right edge
        self.x = self.start_x
        self.y = target_y
        # DEBUG: Negative speed to move Left.
        self.velocity = -(SPEED_IN_H + random.uniform(0, CHAOS_H))
        self.delay = delay
        self.arrived = False

    def update(self, progress):
        if progress < self.delay: return
        if self.arrived: return
        self.x += self.velocity
        
        # SNAP LOGIC: Moving Left (negative), so if x <= target, stop.
        if self.x <= self.target_x:
            self.x = self.target_x
            self.arrived = True
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.x < self.start_x:
            surface.blit(self.image, self.rect)

class DisintegrateLeft(BaseTransition):
    """Transition: Disintegrates Right to Left."""
    def __init__(self, duration: float = DURATION, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size; self.particles = []; self.generated = False
    def start(self): super().start(); self.generated = False; self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols, rows = width // self.tile_size, height // self.tile_size
        src = surface.copy()
        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try: sub = src.subsurface(rect).copy()
                except ValueError: continue
                
                norm_x = x / width
                # DEBUG: Wave direction inverted (1.0 - norm_x) for Right-to-Left
                delay = ((1.0 - norm_x) * DELAY_GRADIENT) + random.uniform(0, DELAY_NOISE)
                
                self.particles.append(DisintegrateLeftParticle(sub, x, y, delay, width))
        self.generated = True

    def render(self, surface):
        if not self.generated: self._generate(surface); surface.fill((0,0,0)); return
        surface.fill((0, 0, 0))
        for p in self.particles: p.update(self.progress); p.draw(surface)

class IntegrateLeft(BaseTransition):
    """Transition: Reassembles Right to Left."""
    def __init__(self, duration: float = DURATION, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size; self.particles = []; self.generated = False
    def start(self): super().start(); self.generated = False; self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols, rows = width // self.tile_size, height // self.tile_size
        src = surface.copy()
        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try: sub = src.subsurface(rect).copy()
                except ValueError: continue
                
                norm_x = x / width
                # DEBUG: Chaotic delay with inverted direction + offset
                delay = ((1.0 - norm_x) * DELAY_GRADIENT) + random.uniform(0, DELAY_NOISE) + 0.05
                
                self.particles.append(IntegrateLeftParticle(sub, x, y, delay, width))
        self.generated = True

    def render(self, surface):
        if not self.generated: self._generate(surface); surface.fill((0,0,0)); return
        surface.fill((0, 0, 0))
        for p in self.particles: p.update(self.progress); p.draw(surface)


# ==============================================================================
# 3. DIRECTION: DOWN (Wipe Top -> Bottom)
# ==============================================================================

class DisintegrateDownParticle:
    """Exiting particle moving DOWN (Positive Y)."""
    def __init__(self, image, x, y, delay, screen_height):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y
        self.screen_height = screen_height
        
        # DEBUG: Uses VERTICAL speed/chaos settings (Scaled by 1.77)
        self.velocity = SPEED_OUT_V + random.uniform(0, CHAOS_V) 
        self.delay = delay

    def update(self, progress):
        if progress < self.delay: return
        self.y += self.velocity
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.y < self.screen_height:
            surface.blit(self.image, self.rect)

class IntegrateDownParticle:
    """Entering particle moving DOWN (Positive Y)."""
    def __init__(self, image, target_x, target_y, delay):
        self.image = image
        self.rect = image.get_rect()
        self.target_x = target_x
        self.target_y = target_y
        self.start_y = -TILE_SIZE # Start just above Top edge
        self.x = target_x
        self.y = self.start_y
        
        # DEBUG: Vertical Speed + Vertical Chaos
        self.velocity = SPEED_IN_V + random.uniform(0, CHAOS_V)
        self.delay = delay
        self.arrived = False

    def update(self, progress):
        if progress < self.delay: return
        if self.arrived: return
        self.y += self.velocity
        
        # SNAP LOGIC: Moving Down (positive), so if y >= target, stop.
        if self.y >= self.target_y:
            self.y = self.target_y
            self.arrived = True
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.y > self.start_y:
            surface.blit(self.image, self.rect)

class DisintegrateDown(BaseTransition):
    """Transition: Disintegrates Top to Bottom."""
    def __init__(self, duration: float = DURATION, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size; self.particles = []; self.generated = False
    def start(self): super().start(); self.generated = False; self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols, rows = width // self.tile_size, height // self.tile_size
        src = surface.copy()
        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try: sub = src.subsurface(rect).copy()
                except ValueError: continue
                
                # DEBUG: norm_y is used for Vertical direction
                norm_y = y / height
                delay = (norm_y * DELAY_GRADIENT) + random.uniform(0, DELAY_NOISE)
                
                self.particles.append(DisintegrateDownParticle(sub, x, y, delay, height))
        self.generated = True

    def render(self, surface):
        if not self.generated: self._generate(surface); surface.fill((0,0,0)); return
        surface.fill((0, 0, 0))
        for p in self.particles: p.update(self.progress); p.draw(surface)

class IntegrateDown(BaseTransition):
    """Transition: Reassembles Top to Bottom."""
    def __init__(self, duration: float = DURATION, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size; self.particles = []; self.generated = False
    def start(self): super().start(); self.generated = False; self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols, rows = width // self.tile_size, height // self.tile_size
        src = surface.copy()
        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try: sub = src.subsurface(rect).copy()
                except ValueError: continue
                
                norm_y = y / height
                # DEBUG: Chaotic delay with vertical gradient + offset
                delay = (norm_y * DELAY_GRADIENT) + random.uniform(0, DELAY_NOISE) + 0.05
                
                self.particles.append(IntegrateDownParticle(sub, x, y, delay))
        self.generated = True

    def render(self, surface):
        if not self.generated: self._generate(surface); surface.fill((0,0,0)); return
        surface.fill((0, 0, 0))
        for p in self.particles: p.update(self.progress); p.draw(surface)


# ==============================================================================
# 4. DIRECTION: UP (Wipe Bottom -> Top)
# ==============================================================================

class DisintegrateUpParticle:
    """Exiting particle moving UP (Negative Y)."""
    def __init__(self, image, x, y, delay, screen_height):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y
        # DEBUG: Vertical Speed (Negative) + Vertical Chaos
        self.velocity = -(SPEED_OUT_V + random.uniform(0, CHAOS_V))
        self.delay = delay

    def update(self, progress):
        if progress < self.delay: return
        self.y += self.velocity
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.y + TILE_SIZE > 0:
            surface.blit(self.image, self.rect)

class IntegrateUpParticle:
    """Entering particle moving UP (Negative Y)."""
    def __init__(self, image, target_x, target_y, delay, screen_height):
        self.image = image
        self.rect = image.get_rect()
        self.target_x = target_x
        self.target_y = target_y
        self.start_y = screen_height # Start just below Bottom edge
        self.x = target_x
        self.y = self.start_y
        
        # DEBUG: Vertical Speed (Negative) + Vertical Chaos
        self.velocity = -(SPEED_IN_V + random.uniform(0, CHAOS_V))
        self.delay = delay
        self.arrived = False

    def update(self, progress):
        if progress < self.delay: return
        if self.arrived: return
        self.y += self.velocity
        
        # SNAP LOGIC: Moving Up (negative), so if y <= target, stop.
        if self.y <= self.target_y:
            self.y = self.target_y
            self.arrived = True
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.y < self.start_y:
            surface.blit(self.image, self.rect)

class DisintegrateUp(BaseTransition):
    """Transition: Disintegrates Bottom to Top."""
    def __init__(self, duration: float = DURATION, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size; self.particles = []; self.generated = False
    def start(self): super().start(); self.generated = False; self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols, rows = width // self.tile_size, height // self.tile_size
        src = surface.copy()
        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try: sub = src.subsurface(rect).copy()
                except ValueError: continue
                
                # DEBUG: Wave direction inverted (1.0 - norm_y) for Bottom-to-Top
                norm_y = y / height
                delay = ((1.0 - norm_y) * DELAY_GRADIENT) + random.uniform(0, DELAY_NOISE)
                
                self.particles.append(DisintegrateUpParticle(sub, x, y, delay, height))
        self.generated = True

    def render(self, surface):
        if not self.generated: self._generate(surface); surface.fill((0,0,0)); return
        surface.fill((0, 0, 0))
        for p in self.particles: p.update(self.progress); p.draw(surface)

class IntegrateUp(BaseTransition):
    """Transition: Reassembles Bottom to Top."""
    def __init__(self, duration: float = DURATION, tile_size: int = TILE_SIZE):
        super().__init__(duration)
        self.tile_size = tile_size; self.particles = []; self.generated = False
    def start(self): super().start(); self.generated = False; self.particles = []

    def _generate(self, surface):
        width, height = surface.get_size()
        cols, rows = width // self.tile_size, height // self.tile_size
        src = surface.copy()
        for row in range(rows):
            for col in range(cols):
                x, y = col * self.tile_size, row * self.tile_size
                rect = Rect(x, y, self.tile_size, self.tile_size)
                try: sub = src.subsurface(rect).copy()
                except ValueError: continue
                
                # DEBUG: Chaotic delay with inverted direction + offset
                norm_y = y / height
                delay = ((1.0 - norm_y) * DELAY_GRADIENT) + random.uniform(0, DELAY_NOISE) + 0.05
                
                self.particles.append(IntegrateUpParticle(sub, x, y, delay, height))
        self.generated = True

    def render(self, surface):
        if not self.generated: self._generate(surface); surface.fill((0,0,0)); return
        surface.fill((0, 0, 0))
        for p in self.particles: p.update(self.progress); p.draw(surface)