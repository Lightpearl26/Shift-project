#!venv/Scripts/python.exe
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
        screen = pygame.display.set_mode((800, 600))
        clock = pygame.time.Clock()

        # Crée moteur
        engine = level.Engine()

        # Ajout des systèmes
        engine.add_system(
            "PlayerControlSystem",
            "AISystem",
            "DragSystem",
            "GravitySystem",
            "JumpSystem",
            "PhysicsSystem",
            "EntityUpdateSystem",
        )

        # Crée une entité joueur
        player = engine.create_entity()
        engine.add_component(player, C.Position(Vector2(400, 500)))
        engine.add_component(player, C.Velocity(Vector2(0, 0)))
        engine.add_component(player, C.Mass(5.0))
        engine.add_component(player, C.Drag(8.0))
        engine.add_component(player, C.XDirection(1.0))
        engine.add_component(player, C.Jump(strength=C.JUMP_STRENGTH*5.0, duration=0.15))
        engine.add_component(player, C.Hitbox(Rect(0, 0, 32, 64)))
        engine.add_component(player, C.PlayerControlled())

        state = C.State()
        state.flags |= C.EntityState.CAN_JUMP
        engine.add_component(player, state)
        engine.add_component(player, C.Properties())

        enemi = engine.create_entity()
        engine.add_component(enemi, C.Position(Vector2(200, 516)))
        engine.add_component(enemi, C.Velocity(Vector2(0, 0)))
        engine.add_component(enemi, C.Mass(10.0))
        engine.add_component(enemi, C.Drag(8.0))
        engine.add_component(enemi, C.XDirection(1.0))
        engine.add_component(enemi, C.Jump(strength=C.JUMP_STRENGTH*10.0, duration=0.1))
        engine.add_component(enemi, C.Hitbox(Rect(0, 0, 32, 32)))
        engine.add_component(enemi, C.AI())

        state = C.State()
        state.flags |= C.EntityState.CAN_JUMP
        engine.add_component(enemi, state)
        engine.add_component(enemi, C.Properties())


        # Boucle principale
        running = True
        GROUND_Y = 500  # sol fictif

        while running:
            dt = clock.tick(60) / 1000  # durée en secondes

            if pygame.event.get(pygame.QUIT):
                running = False

            engine.update(dt)


            # --- GESTION DU SOL ---
            pos = engine.get_component(player, C.Position)
            vel = engine.get_component(player, C.Velocity)
            state = engine.get_component(player, C.State)

            if pos.value.y >= GROUND_Y:
                pos.value.y = GROUND_Y
                vel.value.y = 0
                state.flags |= C.EntityState.ON_GROUND
                state.flags |= C.EntityState.CAN_JUMP
            else:
                state.flags &= ~C.EntityState.ON_GROUND

            epos = engine.get_component(enemi, C.Position)
            evel = engine.get_component(enemi, C.Velocity)
            estate = engine.get_component(enemi, C.State)

            if epos.value.y >= GROUND_Y+16:
                epos.value.y = GROUND_Y+16
                evel.value.y = 0
                estate.flags |= C.EntityState.ON_GROUND
                estate.flags |= C.EntityState.CAN_JUMP
            else:
                estate.flags &= ~C.EntityState.ON_GROUND

            # --- AFFICHAGE ---
            screen.fill((30, 30, 30))

            # Joueur
            hitbox = engine.get_component(player, C.Hitbox)
            ehitbox = engine.get_component(enemi, C.Hitbox)
            pygame.draw.rect(screen, (0, 255, 0), hitbox.rect)
            pygame.draw.rect(screen, (255, 0, 0), ehitbox.rect)

            # Sol fictif
            pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(0, GROUND_Y + 32, 800, 600 - GROUND_Y))

            pygame.display.flip()

        pygame.quit()

    except LoggerInterrupt as e:
        logger.traceback(e.__traceback__)
    finally:
        logger.save()

if __name__ == "__main__":
    main()
