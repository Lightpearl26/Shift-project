#!venv/Scripts/python
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

from game_libs import logger

DEBUG_MODE = True

# main function
def main():
    """Main function to run the game."""
    logger.info("======= Start Game =======")
    # Initialize pygame
    pygame.init()

    # Initialize managers
    logger.info("======= Initialize Managers =======")
    DisplayManager.init()
    AudioManager.init()
    SceneManager.init()
    OptionsManager.init()
    
    # set backend to cpu
    logger.info("======= Setup game =======")

    # load the first scene
    SceneManager.change_scene("Tests")

    fps_font = pygame.font.Font(None, 24)
    logger.info("======= Start Main Loop =======")

    # Main game loop
    running = True
    while running:
        # tick clock and get delta time
        DisplayManager.tick()
        dt = DisplayManager.get_delta_time()

        # check for QUIT event
        if pygame.event.peek(pygame.QUIT):
            running = False

        events: list = pygame.event.get(pygame.KEYDOWN)
        for event in events:
            if event.key == pygame.K_F11:
                DisplayManager.toggle_fullscreen()
            elif event.key == pygame.K_F12:
                DisplayManager.save_screenshot()
            elif event.key == pygame.K_F3:
                global DEBUG_MODE
                DEBUG_MODE = not DEBUG_MODE

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
            adj_text = fps_font.render(
                f"L:{OptionsManager.get_luminosity():.2f} C:{OptionsManager.get_contrast():.2f} G:{OptionsManager.get_gamma():.2f} CB:{OptionsManager.get_colorblind_mode()}",
                True,
                (0, 200, 255)
            )
            surface.blit(adj_text, (10, 30))

        # update display
        DisplayManager.flip()

    # Exit properly
    logger.info("======= Shutdown Game =======")
    DisplayManager.shutdown()
    OptionsManager.save()
    AudioManager.stop_all()
    pygame.quit()
    logger.info("======= Game Closed =======")

if __name__ == "__main__":
    main()
