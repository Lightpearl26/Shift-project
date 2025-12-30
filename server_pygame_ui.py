#-*- coding: utf-8 -*-
"""
SHIFT PROJECT - UDP Server Pygame UI
Interface de maintenance simple pour le serveur UDP
"""

import pygame
from pygame import Rect, QUIT
from pygame.event import get as get_events
from pygame.display import set_mode, flip
from pygame.time import Clock
from pygame_ui import UIApp, Frame, ListView, Button, Label, TextArea
from udp_server import UDPServer, logger

pygame.init()

# --- Paramètres UI ---
SCREEN_SIZE = (1200, 800)
BG_COLOR = (44, 44, 44)
THEME = {
    "bg": (44, 44, 44),
    "text": (228, 228, 228),
    "accent": (179, 156, 208),
    "hover": (168, 218, 220),
}

class ServerPygameUI:
    def __init__(self, server_instance: UDPServer):
        pygame.init()
        self.screen = set_mode(SCREEN_SIZE)
        pygame.scrap.init()
        pygame.display.set_caption("Shift Project - UDP Server Maintenance")
        pygame.display.set_icon(pygame.image.load("icon.ico").convert_alpha())
        self.clock = Clock()
        self.udp_server = server_instance
        self.app = UIApp(SCREEN_SIZE)
        self.app.theme.colors.update(THEME)

        # Frame principal
        self.frame = Frame(None, Rect(0, 0, *SCREEN_SIZE))
        self.app.add_layer().add(self.frame)

        # Label titre
        self.title = Label(self.frame, (30, 30), "Shift Project - UDP Server Maintenance")
        self.frame.children.append(self.title)

        # TextArea logs (non éditable, scrollable, sélectionnable)
        self.logs_view = TextArea(self.frame, Rect(30, 70, 1140, 300), text="")
        self.logs_view.editable = False
        self.last_log_count = 0

        # ListView rooms
        self.rooms_view = ListView(self.frame, Rect(30, 400, 1140, 300), items=[])

        # Boutons
        self.stop_btn = Button(self.frame, Rect(840, 730, 150, 40), "Arrêter", self.stop_server)
        self.restart_btn = Button(self.frame, Rect(1020, 730, 150, 40), "Redémarrer", self.restart_server)

    def stop_server(self):
        self.udp_server.shutdown()

    def restart_server(self):
        self.last_log_count = 0
        self.udp_server.restart()

    def update_logs(self):
        # Affiche les 500 derniers logs dans la TextArea, mais n'ajoute que les nouvelles lignes
        logs = logger.logs[-500:]
        if not hasattr(self, 'last_log_count'):
            self.last_log_count = 0
        if len(logger.logs) != self.last_log_count:
            # Si le nombre de logs a changé, on ne met à jour que les nouvelles lignes
            new_text = "\n".join(logger.get_strflog(log) for log in logs)
            if self.last_log_count == 0 or len(logs) < self.last_log_count:
                # Premier affichage ou reset, on remplace tout
                self.logs_view.text = "\n".join(logger.get_strflog(log) for log in logs)
            else:
                self.logs_view.text += "\n" + new_text
            self.last_log_count = len(logger.logs)

    def update_rooms(self):
        self.rooms_view.items = []
        for room_id, room in self.udp_server.rooms.items():
            players = [str(pid) for pid in room.clients.values() if pid]
            self.rooms_view.items.append(f"Room {room_id} - Players: {', '.join(players)}")

    def run(self):
        while self.udp_server.running:
            for event in get_events():
                if event.type == QUIT:
                    self.stop_server()
                self.app.handle_events(event)
            self.update_logs()
            self.update_rooms()
            self.screen.fill(BG_COLOR)
            self.app.render(self.screen)
            flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    udp_server = UDPServer()
    udp_server.start()
    logger.info("UDP Server started and listening for connections.")
    ui = ServerPygameUI(udp_server)
    ui.run()
    udp_server.join()
