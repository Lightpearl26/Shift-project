#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
TCP lib
version : 1.0
____________________________________________________________________________________________________
This Lib contains all server-client objects of the game
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from threading import Thread, Lock
from json import dumps, loads, JSONDecodeError
from socket import socket as SocketType, AF_INET, SOCK_STREAM, timeout
from queue import Queue
from uuid import uuid4, UUID

# get main logger of the game
from . import logger

# create module types
address = tuple[str, int]

# create module constants
LOCALHOST = ("localhost", 12345)

# create module objects
class ClientHandler(Thread):
    """
    ClientHandler object

    This object handle the socket connection of a client

    attributs:
        - uuid: UUID = unique user id of the client
        - socket: socket = socket of the client
        - queue: Queue[tuple[UUID, dict[str, bool]]] = queue where client data are stored
        - running: bool = state of the thread
    """
    def __init__(self, uuid: UUID, client_socket: SocketType, listen_queue: Queue, conn_infos: address) -> None:
        Thread.__init__(self, name=f"Thread-of-client-{str(uuid)}")
        self.uuid: UUID = uuid
        self.socket: SocketType = client_socket
        self.queue: Queue[tuple[UUID, dict[str, bool]]] = listen_queue
        self.running: bool = True
        logger.debug(f"ClientHandler of client {str(uuid)} with address {conn_infos} initialized")

    def run(self) -> None:
        """
        method called when thread is running
        """
        try:
            while self.running:
                data: bytes = self.socket.recv(2048)
                if not data:
                    logger.warning(f"Client closed connection")
                    self.running = False
                    break
                try:
                    logger.debug(f"Received '{data.decode()}'")
                    inputs: dict[str, bool] = loads(data.decode())
                    self.queue.put((self.uuid, inputs))
                except JSONDecodeError:
                    logger.warning(f"Invalid data | failed to decode")
        except (ConnectionAbortedError, ConnectionResetError, OSError):
            logger.error(f"Client lost connection")
        except Exception as e:
            logger.fatal(f"Unexpected error occurs: {e}")
        finally:
            self.socket.close()
            logger.debug("Close connection with client")

class ServerSocket(SocketType):
    """
    """
    def __init__(self, host: address=LOCALHOST) -> None:
        SocketType.__init__(self, AF_INET, SOCK_STREAM)
        self.host: address = host
        self.clients: dict[UUID, ClientHandler] = {}
        self.queue: Queue = Queue()
        self.connection_handler: ConnectionHandler = ConnectionHandler(self)
        self.running: bool = True
        self.client_lock: Lock = Lock()
        logger.info(f"Server initialized on {host}")

    def shutdown(self) -> None:
        """
        method called to shutdown the server properly
        """
        logger.info("Server shutdown initiated")
        self.running = False

        for handler in self.clients.values():
            handler.running = False

            try:
                handler.socket.shutdown(2)
                handler.socket.close()
            except OSError:
                pass

            handler.join()

        logger.debug("All client threads terminated")

        self.clients.clear()
        logger.debug("Client list cleared")

        self.connection_handler.running = False
        self.connection_handler.join()

        try:
            self.close()
            logger.debug("Server socket is now closed")
        except OSError as e:
            logger.error(f"Server socket seems to be already closed: {e}")

    def send_to(self, uuid: UUID, msg: str) -> None:
        self.clients[uuid].socket.sendall(msg.encode())

    def sendall(self, msg: str) -> None:
        for client in self.clients.values():
            client.socket.sendall(msg.encode())

    def run(self) -> None:
        """
        runs the server
        """
        self.bind(self.host)
        self.settimeout(0.5)
        self.listen(5)

        self.connection_handler.start()

        while self.running:
            with self.client_lock:
                to_remove = [uuid for uuid, handler in self.clients.items() if not handler.running]
                for uuid in to_remove:
                    self.clients.pop(uuid)
                    logger.info(f"Client {uuid} removed from client list")

        self.shutdown()

class ConnectionHandler(Thread):
    """
    """
    def __init__(self, server: ServerSocket) -> None:
        Thread.__init__(self, name="Thread-of-ConnectionHandler")
        self.server: ServerSocket = server
        self.running: bool = True

    def run(self):
        """
        method called when thread is running
        """
        try:
            while self.running:
                try:
                    conn, addr = self.server.accept()
                    handler = ClientHandler(uuid4(), conn, self.server.queue, addr)
                    with self.server.client_lock:
                        self.server.clients[handler.uuid] = handler
                    handler.start()
                except timeout:
                    continue
        except Exception as e:
            logger.fatal(f"Unexpected error occurs: {e}")
        finally:
            logger.debug("Connection thread aborted")
