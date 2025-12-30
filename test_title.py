# -*- coding: utf-8 -*-

"""
Test file for TitleScreen display
Displays the TitleScreen scene with basic game loop
Press JUMP (Space) to transition to next scene
Press ESC or close window to exit
"""

import pygame
import sys
from os.path import join

from game_libs.managers.scene import SceneManager
from game_libs.managers.event import EventManager
from game_libs.scenes.transitions import VideoTransition, CrossFade
from game_libs import config


class DummyPlayScene:
    """Dummy play scene for testing transition"""
    def __init__(self):
        self.name = "Game"
        self.scene_manager = None
        self.font = None
        
    def init(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 48)
        
    def handle_events(self, key_events):
        if key_events.get("PAUSE"):
            if self.scene_manager is not None:
                self.scene_manager.change_scene("Title",
                                                transition_out=CrossFade(500, old_scene=self, new_scene=self.scene_manager.get_scene("Title")),)
        
    def update(self, dt):
        pass
        
    def render(self, surface):
        surface.fill((20, 20, 40))
        if self.font:
            text = self.font.render("Game Scene", True, (100, 200, 255))
            x = (surface.get_width() - text.get_width()) // 2
            y = surface.get_height() // 2
            surface.blit(text, (x, y))


def main():
    # Initialize Pygame
    pygame.init()
    
    # Get window dimensions from config or use defaults
    width, height = config.SCREEN_SIZE
    
    screen = pygame.display.set_mode((width, height), config.SCREEN_FLAGS)
    pygame.display.set_caption("SHIFT PROJECT - Title Screen Test")
    
    clock = pygame.time.Clock()
    running = True
    
    # Initialize EventManager
    EventManager.update()
    SceneManager.init()
    
    # Register scenes
    play_scene = DummyPlayScene()
    
    SceneManager.add_scene(play_scene)
    
    # Set initial scene
    SceneManager.change_scene("Welcome",
                              transition_in=VideoTransition(join(config.VIDEOS_FOLDER, "Shift Intro.mp4")))
    
    # Game loop
    dt = 0.0
    
    while running:
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update EventManager (reads all key states)
        EventManager.update()
        
        # Handle scene events
        SceneManager.handle_events(EventManager.get_key_events())
        
        # Update at fixed timestep (example: 20 TPS for game logic)
        # For demo, we just update every frame
        SceneManager.update(dt)
        
        # Render
        SceneManager.render(screen)
        
        # render fps counter
        font = pygame.font.SysFont("Arial", 18)
        fps_text = font.render(f"FPS: {clock.get_fps():.2f}", True, (255, 255, 0))
        screen.blit(fps_text, (10, 10))
        pygame.display.flip()
        
        # Cap framerate and get dt
        dt = clock.tick() / 1000.0
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
