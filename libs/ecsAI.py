from . import logger
import random
from typing import Any

class AILogic:
    def __init__(self, **kwargs) -> None:
        # optional if AI needs attributs
        pass

    def __call__(self, eid: int, engine: Any, dt: float) -> None:
        logger.fatal("Not Implemented: AILogic")
    

class Idle(AILogic):
    def __call__(self, eid: int, engine: Any, dt: float) -> None:
        from . import ecsComponents as C
        # Do nothing -> it's idle
        state = engine.get_component(eid, C.State)
        jump = engine.get_component(eid, C.Jump)
        xdir = engine.get_component(eid, C.XDirection)
        if random.random() >= 0.99 and state.flags & C.EntityState.CAN_JUMP:
            jump.direction = 90.0
            jump.time_left = jump.duration
        if random.random() >= 0.8:
            xdir.value = random.choice([-1.0, 1.0])
        if random.random() >= 0.9:
            if state.flags & C.EntityState.WALKING:
                state.flags &= ~C.EntityState.WALKING
                state.flags |= C.EntityState.RUNNING
            elif state.flags & C.EntityState.RUNNING:
                state.flags &= ~C.EntityState.RUNNING
            else:
                state.flags |= C.EntityState.WALKING
