#!venv/Scripts python
#-*- coding:utf-8 -*-

# import components of the game
import pygame
from os.path import join
from game_libs.ecs_core.engine import Engine
from game_libs.assets_registry import AssetsRegistry
from game_libs.assets_cache import AssetsCache
from game_libs import config, logger
from game_libs.rendering.level_renderer import LevelRenderer
from game_libs.managers.event import EventManager

# initialize pygame display
logger.debug("Initializing Pygame")
pygame.init()

logger.debug("Setting up the display")
SCREEN = pygame.display.set_mode(config.SCREEN_SIZE, config.SCREEN_FLAGS)

# Create a simple test engine
logger.info("Creating game engine and loading level")
engine = Engine()
level = AssetsRegistry.load_level("Tests", engine)
EventManager.update(0.0)

# Main loop
running = True
INFO_MENU = True
clock = pygame.time.Clock()

# create fixed timer to run actions at a fixed rate
fixed_timer = 0.0
fixed_dt = 1.0 / config.TPS_MAX
logger.info("Starting main loop")

while running:
    dt = clock.tick() / 1000.0  # Delta time in seconds

    # Update engine
    fixed_timer += dt
    while fixed_timer >= fixed_dt:
        EventManager.update(fixed_dt)
        fixed_timer -= fixed_dt
        engine.get_component(level.player.eid, "Controlled").key_state = EventManager.get_keys()
        engine.update(level, fixed_dt)
        LevelRenderer.update(level)

    if pygame.event.peek(pygame.QUIT):
        running = False

    if events := pygame.event.get(pygame.KEYDOWN):
        if any(event.key == pygame.K_F3 for event in events):
            INFO_MENU = not INFO_MENU

    # Clear screen
    SCREEN.fill((0, 0, 0))

    # Render level
    alpha = min(1.0, max(0.0, fixed_timer / fixed_dt))
    LevelRenderer.render(SCREEN, level, alpha)

    # Render FPS
    if INFO_MENU:
        # FPS
        fps = 1/dt if dt > 0 else 0
        font = AssetsCache.load_font(join(config.FONT_FOLDER, "Pixel Game.otf"), 20)
        fps_text = font.render(f"FPS: {fps:.0f}", True, (255, 255, 255))
        SCREEN.blit(fps_text, (5, 5))
        # Player state
        player_state = engine.get_component(level.player.eid, "State")
        ## Can jump
        jump_text = font.render(f"Can jump: {player_state.has_flag('CAN_JUMP')}", True, (255, 255, 255))
        SCREEN.blit(jump_text, (5, 30))
        ## On ground
        on_ground_text = font.render(f"On ground: {player_state.has_flag('ON_GROUND')}", True, (255, 255, 255))
        SCREEN.blit(on_ground_text, (5, 55))
        ## Velocity
        player_velocity = engine.get_component(level.player.eid, "Velocity")
        velocity_text = font.render(f"Velocity: ({player_velocity.x:.2f}, {player_velocity.y:.2f}) px/s", True, (255, 255, 255))
        SCREEN.blit(velocity_text, (5, 80))
        ## Position
        player_hitbox = engine.get_component(level.player.eid, "Hitbox")
        position_text = font.render(f"Position: ({player_hitbox.rect.x}, {player_hitbox.rect.y}) px", True, (255, 255, 255))
        SCREEN.blit(position_text, (5, 105))
        ## Jumping
        player_jump = engine.get_component(level.player.eid, "Jump")
        jump_text = font.render(f"Jumping: {player_state.has_flag('JUMPING')}, Time left: {player_jump.time_left:.2f} s", True, (255, 255, 255))
        SCREEN.blit(jump_text, (5, 130))
        ## Wallsticking
        wallstick_text = font.render(f"Wallsticking: {player_state.has_flag('WALL_STICKING')}", True, (255, 255, 255))
        SCREEN.blit(wallstick_text, (5, 155))
        ## Camera deadzone
        camera_infos = engine.get_component(level.player.eid, "CameraFollow")
        rect = pygame.Rect(camera_infos.deadzone)
        rect.center = (level.camera.size[0] // 2, level.camera.size[1] // 2)
        pygame.draw.rect(SCREEN, (0, 0, 255), rect, 1)
        ## Camera position
        camera_text = font.render(f"Camera Pos: ({int(level.camera.pos.x)}, {int(level.camera.pos.y)}) px", True, (255, 255, 255))
        SCREEN.blit(camera_text, (5, 180))

    # Update display
    pygame.display.flip()
