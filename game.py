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

# import logger
from libs import logger, LoggerInterrupt
import pygame
from pygame import Vector2, Rect
from libs import ecsComponents as C
from libs import level

print("Hello World")

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
            "TileAnimationSystem", # update Tilemap
            "AISystem", # initiate AI-entity movement
            "PlayerControlSystem", # initiate player movement
            "DragSystem", # needs to be first to change velocity
            "GravitySystem",
            "JumpSystem",
            "MovementSystem",
            "PhysicsSystem", # needs to be after velocity-changing systems
            "UpdateHitboxFromPositionSystem", # update entity hitbox with position
            "EntityCollisionsSystem", # collisions with entity update
            "MapCollisionsSystem", # collisions with map update
            "UpdatePositionFromHitboxSystem"
        )

        # Crée une entité joueur
        player = engine.new_entity("player", overrides={"Position": {"x":72, "y": 200}})

        enemi = engine.create_entity()
        engine.add_component(enemi, C.Position(Vector2(400, 524)))
        engine.add_component(enemi, C.Velocity(Vector2(0, 0)))
        engine.add_component(enemi, C.Mass(10.0))
        engine.add_component(enemi, C.XDirection(1.0))
        engine.add_component(enemi, C.Jump(strength=C.JUMP_STRENGTH*5.0, duration=0.1))
        engine.add_component(enemi, C.Hitbox(Rect(0, 0, 48, 48)))
        engine.add_component(enemi, C.EntityCollisions([]))
        engine.add_component(enemi, C.MapCollisions())
        engine.add_component(enemi, C.AI())

        state = C.State()
        state.flags |= C.EntityState.ON_GROUND
        engine.add_component(enemi, state)
        engine.add_component(enemi, C.Properties())


        # Boucle principale
        running = True

        while running:
            dt = clock.tick(60) / 1000  # durée en secondes

            if pygame.event.get(pygame.QUIT):
                running = False

            engine.update(dt)

            # --- AFFICHAGE ---
            screen.fill((30, 30, 30))

            engine.tilemap_renderer.render(engine.tilemap, screen, engine.camera)

            hitbox = engine.get_component(player, C.Hitbox)
            ehitbox = engine.get_component(enemi, C.Hitbox)

            # Joueur
            pygame.draw.rect(screen, (0, 255, 0), hitbox.rect)
            pygame.draw.rect(screen, (255, 0, 0), ehitbox.rect)

            pygame.display.flip()

        pygame.quit()

    except LoggerInterrupt as e:
        logger.traceback(e.__traceback__)
    finally:
        logger.save()

if __name__ == "__main__":
    main()
