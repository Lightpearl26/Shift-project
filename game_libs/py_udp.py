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

def decode(data: bytes) -> ScancodeWrapper:
    """
    Decode data from UDP transmission
    """
    bits = []
    for byte in data:
        for bit_index in range(8):
            bits.append((byte >> bit_index) & 1 == 1)
    return ScancodeWrapper(bits)

# ----- P2PClient ----- #
class P2PClient:
    """
    UDP P2P Client
    """
    def __init__(self,
                 address: Address = DEFAULT_ADDRESS,
                 buffer_size: int = DEFAULT_BUFFER_SIZE
                ) -> None:
        self.address: Address = address
        self.buffer_size: int = buffer_size
        self.socket: SocketType = SocketType(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(2.0)
        self.socket.setblocking(False)
        logger.info(f"UDP Client initialized with address {self.address} and buffer size {self.buffer_size}")

    def send(self, data: bytes) -> None:
        """
        Send data to the other Peer
        """
        self.socket.sendto(data, self.address)
        logger.debug(f"Sent data to {self.address}")

    def receive(self) -> Optional[bytes]:
        """
        Receive data from the other peer
        """
        try:
            data, _ = self.socket.recvfrom(self.buffer_size)
            logger.debug(f"Received data from {self.address}")
            return data
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            return None