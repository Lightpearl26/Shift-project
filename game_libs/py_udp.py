#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
Assets registry lib
version : 1.0
____________________________________________________________________________________________________
Contains udp server of the game
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import other components
from __future__ import annotations
from typing import Optional
from socket import (
    socket as SocketType,
    gethostbyname,
    gethostname,
    AF_INET,
    SOCK_DGRAM
)
from pygame.key import ScancodeWrapper
from miniupnpc import UPnP

# import logger
from . import logger

# create module types
Address = tuple[str, int]

# create module constants
LOCALHOST: str = gethostbyname(gethostname())
PORT: int = 2802
DEFAULT_ADDRESS: Address = (LOCALHOST, PORT)
DEFAULT_BUFFER_SIZE: int = 1024

# create encode/decode functions
def encode(data: ScancodeWrapper) -> bytes:
    """
    Encode data for UDP transmission
    """
    bits = list(data)
    n_bytes = (len(bits) + 7) // 8
    key_bytes = bytearray(n_bytes)

    for i, bit in enumerate(bits):
        if bit:
            byte_index = i // 8
            bit_index = i % 8
            key_bytes[byte_index] |= 1 << bit_index

    return bytes(key_bytes)

def decode(data: bytes) -> list[ScancodeWrapper]:
    """
    Decode data from UDP transmission
    """
    bits = []
    for byte in data:
        for bit_index in range(8):
            bits.append((byte >> bit_index) & 1 == 1)
    return [ScancodeWrapper(bits[i:i+512]) for i in range(0, len(bits), 512)]

# ----- UDPClient ----- #
class UDPClient:
    """
    UDP Client for network communication
    """
    def __init__(self, address: Address = DEFAULT_ADDRESS) -> None:
        self._socket: SocketType = SocketType(AF_INET, SOCK_DGRAM)
        self._socket.connect(address)
        self._socket.setblocking(False)
        logger.info(f"UDP Client initialized with address {address}")

    def send(self, data: bytes) -> None:
        """
        Send data to the server
        """
        try:
            self._socket.send(data)
            logger.debug(f"Sent data: {data}")
        except Exception as e:
            logger.error(f"Error sending data: {e}")

    def receive(self, buffer_size: int = DEFAULT_BUFFER_SIZE) -> bytes:
        """
        Receive data from the server
        """
        try:
            data = self._socket.recv(buffer_size)
            logger.debug(f"Received data: {data}")
            return data
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            return b""

    def close(self) -> None:
        """
        Close the UDP socket
        """
        self._socket.close()
        logger.info("UDP Client socket closed")

# ----- UDPServer ----- #
class UDPServer:
    """
    UDP Server for network communication
    """
    def __init__(self, address: Address = DEFAULT_ADDRESS) -> None:
        self._address: Address = address
        self._socket: SocketType = SocketType(AF_INET, SOCK_DGRAM)
        self._socket.bind(address)
        self._socket.setblocking(False)
        self._next_player_id: int = 0
        self.clients: dict[int, tuple[Address, bytes]] = {}

        self.upnp = UPnP()
        self.external_ip: Optional[str] = None

        self.try_upnp()

        logger.info(f"UDP Server initialized and bound to address {address}")

    def try_upnp(self) -> None:
        """
        Try to set up UPnP port forwarding
        """
        try:
            self.upnp.discoverdelay = 1000
            self.upnp.discover()

            self.upnp.selectigd()
            self.upnp.addportmapping(self._address[1], "UDP", self.upnp.lanaddr, self._address[1], "GameUDP", "")

            self.external_ip = self.upnp.externalipaddress()

            logger.info(f"UPnP success — Public: {self.external_ip}:{self._address[1]}")
        except Exception as e:
            logger.warning(f"UPnP failed: {e}")
            self.external_ip = None

    def tick(self, buffer_size: int = DEFAULT_BUFFER_SIZE) -> None:
        """
        check for incoming data from clients
        """
        try:
            data, client_address = self._socket.recvfrom(buffer_size)
            if not any(addr == client_address for addr, _ in self.clients.values()):
                logger.info(f"New client connected: {client_address} assigned ID {self._next_player_id}")
                self.clients[self._next_player_id] = (client_address, data)
                self._next_player_id += 1
            else:
                for pid, (addr, _) in self.clients.items():
                    if addr == client_address:
                        self.clients[pid] = (addr, data)
                        break

            logger.debug(f"Received data from {client_address}: {data}")

            payload: bytes = b"".join(self.clients[pid][1] for pid in sorted(self.clients.keys()))
            for addr, _ in self.clients.values():
                self._socket.sendto(payload, addr)
                logger.debug(f"Sent data to {addr}: {payload}")
        except (BlockingIOError, OSError) as e:
            if not (isinstance(e, OSError) and getattr(e, "winerror", None) == 10035) and not (isinstance(e, BlockingIOError)):
                logger.error(f"Socket error: {e}")
        except Exception as e:
            logger.error(f"Error in UDP Server tick: {e}")

    def close(self) -> None:
        """
        Close the UDP socket
        """
        self._socket.close()
        self.upnp.deleteportmapping(self._address[1], "UDP")
        logger.info("UDP Server socket closed")
