#!venv/Scripts/python
#-*- coding: utf-8 -*-
# pylint: disable=unused-argument,protected-access,broad-except

"""
SHIFT PROJECT udp_server
"""

# Import socket module components
from __future__ import annotations
from typing import Optional
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from uuid import uuid4, UUID
from time import time
from miniupnpc import UPnP

# Importing config file
from game_libs import config

# Importing the logger
from game_libs import Logger


# Initialize logger
logger = Logger(folder=config.SERVER_LOG_FOLDER)

# Create command decorator
def command(cmd_name: str):
    """
    Decorator to register a command in the UDPServer commands dictionary
    """
    def decorator(func):
        # On marque la fonction avec un attribut pour l'enregistrement différé
        func._command_name = cmd_name
        return func
    return decorator


# Create Room class
class Room:
    """
    Room class to manage a game room
    """
    def __init__(self, room_id: int, server: UDPServer) -> None:
        """
        Initialize the Room

        :param room_id: The ID of the room
        """
        self.room_id = room_id
        self.server = server
        self.running: bool = True
        self.clients: dict[str, Optional[UUID]] = {
            "player1": None,
            "player2": None
        }

    def close(self) -> None:
        """
        Close the room and its socket
        """
        if self.clients["player1"] is not None:
            self.server.socket.sendto(f"UCONN;You got unconected from room {self.room_id}".encode(),
                               self.server.players[self.clients["player1"]]["addr"])
        if self.clients["player2"] is not None:
            self.server.socket.sendto(f"UCONN;You got unconected from room {self.room_id}".encode(),
                               self.server.players[self.clients["player2"]]["addr"])
        self.running = False
        logger.info(f"Room {self.room_id} closed.")

    def __contains__(self, player_uuid: UUID) -> bool:
        """
        Check if a player is in the room

        :param player_uuid: The UUID of the player
        :return: True if the player is in the room, False otherwise
        """
        return player_uuid in self.clients.values()

    def is_empty(self) -> bool:
        """
        Check if the room is empty

        :return: True if the room has no players, False otherwise
        """
        return all(client is None for client in self.clients.values())


# Create UDPServer class
class UDPServer(Thread):
    """
    UDPServer class to handle UDP communication
    """
    commands: dict[str, callable] = {}

    def __init__(self, host: str = "0.0.0.0", port: int = config.UDP_LISTENING_PORT) -> None:
        """
        Initialize the UDP server

        :param host: The host address to bind the server to
        :param port: The port number to bind the server to
        """
        Thread.__init__(self, name="UDPServerThread")
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((host, port))
        self.socket.setblocking(False)
        self.running: bool = True

        # Manage UPnP port forwarding
        try:
            self.upnp = UPnP()
            self.upnp.discoverdelay = 200
            self.upnp.discover()
            self.upnp.selectigd()
            self.upnp.addportmapping(port,
                                     'UDP',
                                     self.upnp.lanaddr,
                                     port,
                                     'Shift Project UDP Server',
                                     '')
            logger.info(f"UPnP port forwarding set for port {port} "\
                f"binded to {self.upnp.externalipaddress()}")
        except Exception as e:
            logger.warning(f"Failed to set UPnP port forwarding: {e}")

        # Initialize rooms dictionary
        self.rooms: dict[UUID, Room] = {}
        self.players: dict[UUID, dict[str, float | tuple[str, int]]] = {}

        # register commands
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_command_name"):
                cmd_name = getattr(attr, "_command_name")
                self.commands[cmd_name] = attr
                logger.info(f"Registered command: {cmd_name:5} | {attr.__doc__}")

    def get_player_id(self, addr: tuple[str, int]) -> Optional[UUID]:
        """
        Get the player UUID from the address

        :param addr: The address tuple (IP, port)
        :return: The UUID of the player if found, None otherwise
        """
        for player_id, player_dict in self.players.items():
            if player_dict["addr"] == addr:
                return player_id
        return None

    # Adding commands
    @command("CROOM")
    def create_room(self, player_id: UUID=None, player_msg: str=None) -> UUID:
        """ Create a new game room """
        room_id = uuid4()
        self.rooms[room_id] = Room(room_id, self)
        self.rooms[room_id].clients["player1"] = player_id
        self.rooms[room_id].start()
        self.socket.sendto(f"JROOM;{room_id}".encode(), self.players[player_id]["addr"])
        logger.info(f"Created new room with ID: {room_id}")
        return room_id

    @command("SDOWN")
    def shutdown(self, player_id: UUID=None, player_msg: str=None) -> None:
        """ Shutdown the UDP server and all rooms """
        self.running = False
        for room in self.rooms.values():
            room.close()
            room.join()
        self.socket.close()
        self.upnp.deleteportmapping(config.UDP_LISTENING_PORT, 'UDP')
        logger.info("UDP Server shutdown complete.")
        logger.save()

    @command("RSTRT")
    def restart(self, player_id: UUID=None, player_msg: str=None) -> None:
        """ Restart the UDP server and all rooms """
        self.shutdown()
        logger.__init__(folder=config.SERVER_LOG_FOLDER)
        logger.info("Restarting UDP Server...")
        self.__init__(self.host, self.port)
        self.start()
        logger.info("UDP Server restart complete.")

    @command("JROOM")
    def join_room(self, player_id: UUID=None, player_msg: str=None) -> None:
        """Join an existing game room"""
        room_id = UUID(player_msg)
        room = self.rooms.get(room_id)
        if room and room.clients["player2"] is None:
            room.clients["player2"] = player_id
            logger.info(f"Player {player_id} joined room {room_id}")
            self.socket.sendto(f"JROOM;{room_id}".encode(), self.players[player_id]["addr"])
        elif room:
            logger.warning(f"Room {room_id} is full. Player {player_id} cannot join.")
            self.socket.sendto(f"ERR;Room {room_id} is full.".encode(), self.players[player_id]["addr"])
        else:
            logger.warning(f"Room {room_id} does not exist. Player {player_id} cannot join.")
            self.socket.sendto(f"ERR;Room {room_id} does not exist.".encode(), self.players[player_id]["addr"])

    @command("UCONN")
    def unconnect(self, player_id: UUID=None, player_msg: str=None) -> None:
        """ Unconnect a player from the server """
        if player_id in self.players:
            del self.players[player_id]
            logger.info(f"Player {player_id} unconnected from server.")
            # Remove player from any rooms
            for room in self.rooms.values():
                if player_id in room:
                    for key, value in room.clients.items():
                        if value == player_id:
                            room.clients[key] = None
                            logger.info(f"Player {player_id} removed from room {room.room_id}.")
                            break
        else:
            logger.warning(f"Player {player_id} not found for unconnection.")

    @command("SENDM")
    def send_message(self, player_id: UUID=None, player_msg: str=None) -> None:
        """ Send a message to all players in the same room except the sender """
        for room in self.rooms.values():
            if player_id in room:
                for _, value in room.clients.items():
                    if value is not None and value != player_id:
                        self.socket.sendto(f"MSG;{player_msg}".encode(), self.players[value]["addr"])
                        logger.info(f"Sent message from player {player_id} to player {value} in room {room.room_id}")
                break

    @command("SENDK")
    def send_keystate(self, player_id: UUID=None, player_msg: str=None) -> None:
        """ Send keystate to all players in the same room except the sender """
        for room in self.rooms.values():
            if player_id in room:
                for _, value in room.clients.items():
                    if value is not None and value != player_id:
                        self.socket.sendto(f"KEYS;{player_msg}".encode(), self.players[value]["addr"])
                        logger.info(f"Sent keystate from player {player_id} to player {value} in room {room.room_id}")
                break

    @command("PING")
    def ping(self, player_id: UUID=None, player_msg: str=None) -> None:
        """ Respond to a ping from a player """
        self.socket.sendto(b"PONG", self.players[player_id]["addr"])
        self.players[player_id]["last_seen"] = time()
        logger.info(f"Responded to PING from player {player_id}")

    # Run method
    def run(self) -> None:
        """
        Run the UDP server to listen for incoming messages
        """
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                if not addr in (v["addr"] for v in self.players.values()):
                    player_uuid = uuid4()
                    self.players[player_uuid] = {"addr": addr, "last_seen": time()}
                    self.socket.sendto(f"CONNA;{player_uuid}".encode(), addr)
                    logger.info(f"New player connected: {player_uuid} from {addr}")
                message = data.decode()
                cmd, *params = message.split(';')
                if cmd in self.commands:
                    logger.info(f"Execute command {cmd} from {addr} with params {params}")
                    self.commands[cmd](player_id=self.get_player_id(addr), player_msg=';'.join(params))
                else:
                    self.socket.sendto(b"MSG;Roger that!", addr)
                logger.info(f"Received message from {addr}: {message}")
            except BlockingIOError:
                continue
            except WindowsError as e:
                if e.winerror == 10035:  # WSAEWOULDBLOCK
                    continue
                else:
                    logger.error(f"Socket error: {e}")
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
            finally:
                # Delete empty rooms
                for room_id in self.rooms.copy():
                    room = self.rooms[room_id]
                    if room.is_empty():
                        room.close()
                        room.join()
                        del self.rooms[room_id]
                        logger.info(f"Deleted empty room with ID: {room_id}")
                # Kick players not seen for a while
                current_time = time()
                for player_id, player_dict in list(self.players.items()):
                    if current_time - player_dict["last_seen"] > config.PLAYER_TIMEOUT:
                        self.socket.sendto("TIMEOUT;You have been kicked due to inactivity.".encode(), player_dict["addr"])
                        self.unconnect(player_id=player_id)
                        logger.info(f"Kicked inactive player: {player_id}")
