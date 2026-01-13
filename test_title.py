# -*- coding: utf-8 -*-

"""
Test file for TitleScreen display
Displays the TitleScreen scene with basic game loop
Press JUMP (Space) to transition to next scene
Press ESC or close window to exit
"""

from os.path import join
import sys
import pygame

from game_libs.managers.scene import SceneManager
from game_libs.managers.event import EventManager
from game_libs.managers.audio import AudioManager
from game_libs.scenes.transitions import VideoTransition
from game_libs.assets_cache import AssetsCache
from game_libs import config

def main():
    # Initialize Pygame
    pygame.init()
    
    # Get window dimensions from config or use defaults
    width, height = config.SCREEN_SIZE
    
    screen = pygame.display.set_mode((width, height), config.SCREEN_FLAGS)
    pygame.display.set_caption("SHIFT PROJECT - Title Screen Test")
    
    clock = pygame.time.Clock()
    running = True
    
    # Initialize Managers
    AudioManager.init()
    EventManager.update(0.0)
    SceneManager.init()
    
    # Set initial scene
    SceneManager.change_scene("Options",
                              transition_in=VideoTransition(join(config.VIDEOS_FOLDER, "Shift Intro.mp4")))
    
    # Game loop
    dt = 0.0
    
    while running:
        # Handle pygame events
        if pygame.event.peek(pygame.QUIT):
            running = False
        
        # Update EventManager (reads all key states)
        EventManager.update(dt)
        
        # Handle scene events
        SceneManager.handle_events(EventManager.get_keys())
        
        # Update at fixed timestep (example: 20 TPS for game logic)
        # For demo, we just update every frame
        SceneManager.update(dt)
        
        # Render
        SceneManager.render(screen)
        
        # render fps counter
        font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 16)
        fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, (255, 255, 0))
        screen.blit(fps_text, (10, 10))
        pygame.display.flip()
        
        # Cap framerate and get dt
        dt = clock.tick() / 1000.0
        pygame.event.pump()
        AudioManager.cleanup()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
