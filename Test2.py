#!venv/Scripts python
#-*- coding:utf-8 -*-

# Import components of the game
import pygame
from game_libs.ecs_core.engine import Engine
from game_libs.assets_registry import AssetsRegistry
from game_libs import config, logger
from game_libs.rendering.level_renderer import LevelRenderer
from game_libs.level.components import Camera
from game_libs.py_udp import UDPClient, decode, encode

# initialize pygame display
logger.debug("Initializing Pygame")
pygame.init()

logger.debug("Setting up the display")
SCREEN = pygame.display.set_mode(config.SCREEN_SIZE, config.SCREEN_FLAGS)

# Create a simple test engine
logger.info("Creating game engine and loading level")
engine = Engine()
level = AssetsRegistry.load_level("Tests", engine)
last_pos = pygame.Vector2(engine.get_component(level.player.eid, "Hitbox").rect.topleft)
last_camera_pos = pygame.Vector2(level.camera.pos)

# Initialize UDP server (for future use)
udp_client = UDPClient()


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
        fixed_timer -= fixed_dt
        logger.debug("Server ticked")
        key_state: bytes = udp_client.receive()
        if key_state:
            engine.get_component(level.player.eid, "Controlled").key_state = decode(key_state)[0]
        else:
            engine.get_component(level.player.eid, "Controlled").key_state = pygame.key.get_pressed()
        udp_client.send(encode(pygame.key.get_pressed()))
        logger.debug("Client ticked")
        engine.update(level, fixed_dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                INFO_MENU = not INFO_MENU

    # Clear screen
    SCREEN.fill((0, 0, 0))

    # Render level
    alpha = min(1.0, max(0.0, fixed_timer / fixed_dt))
    LevelRenderer.render(SCREEN, level, alpha)

    # Render player
    player_hitbox = engine.get_component(level.player.eid, "Hitbox")
    
    prev_pos = last_pos
    curr_pos = pygame.Vector2(player_hitbox.rect.topleft)
    interp_pos = prev_pos.lerp(curr_pos, alpha)
    last_pos = pygame.Vector2(int(interp_pos.x), int(interp_pos.y))
    
    prev_pos = last_camera_pos or pygame.Vector2(level.camera.pos)
    curr_pos = pygame.Vector2(level.camera.pos)
    interp_camera_pos = prev_pos.lerp(curr_pos, alpha)
    interp_camera = Camera(interp_camera_pos, level.camera.size)
    last_camera_pos = pygame.Vector2(int(interp_camera_pos.x), int(interp_camera_pos.y))
    
    # Position réelle du joueur (interpolée)
    player_screen_pos = interp_pos - pygame.Vector2(interp_camera.rect.topleft)
    player_hitbox_rect = pygame.Rect(player_screen_pos, player_hitbox.size)
    pygame.draw.rect(SCREEN, (0, 255, 0), player_hitbox_rect)

    # Render FPS
    if INFO_MENU:
        # FPS
        fps = clock.get_fps()
        font = pygame.font.SysFont("Arial", 24)
        fps_text = font.render(f"FPS: {fps:.0f}", True, (255, 255, 255))
        SCREEN.blit(fps_text, (10, 10))
        # Player state
        player_state = engine.get_component(level.player.eid, "State")
        ## Can jump
        jump_text = font.render(f"Can jump: {player_state.has_flag('CAN_JUMP')}", True, (255, 255, 255))
        SCREEN.blit(jump_text, (10, 40))
        ## On ground
        on_ground_text = font.render(f"On ground: {player_state.has_flag('ON_GROUND')}", True, (255, 255, 255))
        SCREEN.blit(on_ground_text, (10, 70))
        ## Velocity
        player_velocity = engine.get_component(level.player.eid, "Velocity")
        velocity_text = font.render(f"Velocity: ({player_velocity.x:.2f}, {player_velocity.y:.2f}) px/s", True, (255, 255, 255))
        SCREEN.blit(velocity_text, (10, 100))
        ## Position
        player_hitbox = engine.get_component(level.player.eid, "Hitbox")
        position_text = font.render(f"Position: ({player_hitbox.rect.x}, {player_hitbox.rect.y}) px", True, (255, 255, 255))
        SCREEN.blit(position_text, (10, 130))
        ## Jumping
        player_jump = engine.get_component(level.player.eid, "Jump")
        jump_text = font.render(f"Jumping: {player_state.has_flag('JUMPING')}, Time left: {player_jump.time_left:.2f} s", True, (255, 255, 255))
        SCREEN.blit(jump_text, (10, 160))
        ## Wallsticking
        wallstick_text = font.render(f"Wallsticking: {player_state.has_flag('WALL_STICKING')}", True, (255, 255, 255))
        SCREEN.blit(wallstick_text, (10, 190))
        ## Camera deadzone
        camera_infos = engine.get_component(level.player.eid, "CameraFollow")
        rect = pygame.Rect(camera_infos.deadzone)
        rect.center = (level.camera.size[0] // 2, level.camera.size[1] // 2)
        pygame.draw.rect(SCREEN, (0, 0, 255), rect, 1)
        ## Camera position
        camera_text = font.render(f"Camera Pos: ({int(level.camera.pos.x)}, {int(level.camera.pos.y)}) px", True, (255, 255, 255))
        SCREEN.blit(camera_text, (10, 220))
        ## Camera interpolated position
        interp_camera_text = font.render(f"Interp Camera Pos: ({int(interp_camera.pos.x)}, {int(interp_camera.pos.y)}) px", True, (255, 255, 255))
        SCREEN.blit(interp_camera_text, (10, 250))
        ## player interpolated position
        interp_player_text = font.render(f"Interp Player Pos: ({int(interp_pos.x)}, {int(interp_pos.y)}) px", True, (255, 255, 255))
        SCREEN.blit(interp_player_text, (10, 280))

    # Update display
    pygame.display.flip()