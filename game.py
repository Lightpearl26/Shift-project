#!venv\Scripts\python.exe
#-*- coding: utf-8 -*-

"""
SHIFT PROJECT
____________________________________________________________________________________________________
project name : Shift Project
authors      : Lafiteau Franck | Castaing Guillaume
version      : a0.1
____________________________________________________________________________________________________
This project is a fanmade game where two players are playing a platformer game. One of the player is
controlling the main character trying to pass the game and the other plays his sidekick that is here
to help him during his journey
____________________________________________________________________________________________________
copyrights: (c) Franck Lafiteau (code)
            (c) Guillaume Castaing (main idea, level design, graphics)
"""

import pygame

# import logger
from libs import logger, LoggerInterrupt
from libs import ecsComponents as C
from libs import level

def log_states(engine, eid):
    states = engine.get_component(eid, C.State).flags
    for state in C.EntityState.__dict__:
        if isinstance(getattr(C.EntityState, state), int):
            logger.info(f"State {state}: {bool(states & getattr(C.EntityState, state))}")

# Create main function of the script
def main() -> None:
    """
    Main function of the script
    this function is called when launching the script
    """
    try:
        # Here we execute code
        logger.info("Hello World !")

        pygame.init()
        screen = pygame.display.set_mode((48*21, 48*17), pygame.FULLSCREEN | pygame.SCALED)
        clock = pygame.time.Clock()

        # Crée moteur
        engine = level.Engine()
        engine.camera.rect.size = (48*21, 48*17)

        # Ajout des systèmes
        engine.add_system(
            # Tilemap systems
            "TileAnimationSystem",
            # Entity control systems
            "AISystem",
            "PlayerControlSystem",
            # Velocity changing systems
            "DragSystem",
            "GravitySystem",
            "JumpSystem",
            "MovementSystem",
            # Collisions with map systems
            "MovePredictionSystem",
            "MapCollisionSystem",
            # Apply changes on hitbox and position
            "UpdateHitboxAndPositionSystem",
            # Entity collision system
            "EntityCollisionsSystem",
            # State change systems
            "UpdateEntityStateSystem"
        )

        # Crée une entité joueur
        player = engine.new_entity("player", overrides={"Position": {"x":72, "y": 300}})

        # Boucle principale
        running = True

        while running:
            dt = clock.tick(60) / 1000  # durée en s

            if pygame.event.get(pygame.QUIT):
                running = False

            engine.update(dt)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        log_states(engine, player)

            # --- AFFICHAGE ---
            screen.fill((30, 30, 30))

            engine.tilemap_renderer.render(engine.tilemap, screen, engine.camera)

            hitbox = engine.get_component(player, C.Hitbox)

            # Joueur
            pygame.draw.rect(screen, (0, 255, 0), hitbox.rect)

            pygame.display.flip()

        pygame.quit()

    except LoggerInterrupt as e:
        logger.traceback(e.__traceback__)
    finally:
        logger.save()

if __name__ == "__main__":
    main()
