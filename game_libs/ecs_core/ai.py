# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
ECS libs ai
version : 1.1
____________________________________________________________________________________________________
Contains ai of our game ecs
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from __future__ import annotations
import random


# import needed protocols of the package
from ..header import Engine


# ----- Base Logic of all AI ----- #
class Logic:
    """
    Base Logic of AI
    """
    def __init__(self: Logic, **kwargs: dict) -> None:
        pass

    def __call__(self, eid: int, engine: Engine, dt: float) -> None:
        raise NotImplementedError


# ----- IDLE logic ----- #
class Idle(Logic):
    """
    IDLE logic
    """
    def __call__(self, eid: int, engine: Engine, dt: float) -> None:
        state = engine.get_component(eid, "State")
        jump = engine.get_component(eid, "Jump")
        if random.random() >= 0.99 and state.has_flag("CAN_JUMP"):
            jump.direction = 90.0
            jump.time_left = jump.duration
