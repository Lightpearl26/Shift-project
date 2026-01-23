#!venv/Script/python
#-*- coding: utf-8 -*-

"""
game.py
___________________________________________________________________________________________________
This file is not a module and is intended to be run as a script.
It contains the main game loop and handles user input, game state updates, and rendering.
___________________________________________________________________________________________________
(c) Lafiteau Franck 2026
"""

# import built-in modules

# import pygame
import pygame

# import game_libs
from game_libs.managers.audio import AudioManager
from game_libs.managers.scene import SceneManager
from game_libs.managers.display import DisplayManager
from game_libs.managers.options import OptionsManager

DEBUG_MODE = True

# main function
def main():
    """Main function to run the game."""
    # Initialize pygame
    pygame.init()

    # Initialize managers
    OptionsManager.init()
    DisplayManager.init()
    AudioManager.init()
    SceneManager.init()

    # load the first scene
    SceneManager.change_scene("Tests")

    fps_font = pygame.font.Font(None, 24)

    # Main game loop
    running = True
    while running:
        # tick clock and get delta time
        DisplayManager.tick()
        dt = DisplayManager.get_delta_time()

        # check for QUIT event
        if pygame.event.peek(pygame.QUIT):
            running = False

        # update managers
        AudioManager.update()
        SceneManager.update(dt)

        # handle events
        SceneManager.handle_events()

        # render scene
        surface = DisplayManager.get_surface()
        surface.fill((0, 0, 0))  # clear screen with black
        SceneManager.render(surface)

        # Debug fps
        if DEBUG_MODE:
            fps_text = fps_font.render(f"FPS: {DisplayManager.get_fps():.0f}", True, (255, 255, 0))
            surface.blit(fps_text, (10, 10))

        # update display
        DisplayManager.flip()

    # Exit properly
    DisplayManager.shutdown()
    OptionsManager.save()
    AudioManager.stop_all()
    pygame.quit()

if __name__ == "__main__":
    main()
