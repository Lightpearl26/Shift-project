#!venv/Scripts python
#-*- coding:utf-8 -*-

from game_libs.py_udp import UDPServer

# Initialize UDP server (for future use)
udp_server = UDPServer()

while True:
    # Update engine
    udp_server.tick()
