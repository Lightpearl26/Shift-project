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
from libs import ecs_components as C
from libs import level

# Create main function of the script
def main() -> None:
    """
    Main function of the script
    this function is called when launching the script
    """
    try:
        # Here we execute code

        pygame.init()
        screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
        clock = pygame.time.Clock()

        # Crée moteur
        engine = level.Engine()
        engine.load_tilemap("Caves")
        engine.camera.size = (1920, 1080)

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
            "UpdateEntityStateSystem",
            # update Camera
            "CameraSystem"
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

            # --- AFFICHAGE ---
            screen.fill((30, 30, 30))

            engine.tilemap_renderer.render(engine.tilemap, screen, engine.camera)

            for eid in engine.get_entities_with(C.Hitbox):
                hitbox = engine.get_component(eid, C.Hitbox)
                adapted_hitbox = pygame.Rect(engine.camera.transform_coords(hitbox.topleft), hitbox.size)
                pygame.draw.rect(screen, (0, 255, 255), adapted_hitbox)

            hitbox = engine.get_component(player, C.Hitbox)
            adapted_hitbox = pygame.Rect(engine.camera.transform_coords(hitbox.topleft), hitbox.size)

            # Joueur
            dirx = engine.get_component(player, C.XDirection)
            jumping = engine.get_component(player, C.State).flags & C.EntityState.JUMPING
            if jumping:
                pygame.draw.rect(screen, (0, 0, 255), adapted_hitbox)
            else:
                if dirx.value == 1.0:
                    pygame.draw.rect(screen, (0, 255, 0), adapted_hitbox)
                else:
                    pygame.draw.rect(screen, (255, 0, 0), adapted_hitbox)

            pygame.display.flip()

        pygame.quit()

    except LoggerInterrupt as e:
        logger.traceback(e.__traceback__)
    finally:
        logger.save()

if __name__ == "__main__":
    main()
