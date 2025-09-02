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
        from . import ecs_components as C
        # Do nothing -> it's idle
        state = engine.get_component(eid, C.State)
        jump = engine.get_component(eid, C.Jump)
        if random.random() >= 0.99 and state.flags & C.EntityState.CAN_JUMP:
            jump.direction = 90.0
            jump.time_left = jump.duration
