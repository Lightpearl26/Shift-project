#-*- coding: utf-8 -*-
#pylint: disable=unused-argument

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
ECS libs Actions
version : 1.0
____________________________________________________________________________________________________
Contient les actions d'entités pour le système ECS
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

from typing import Callable, Dict

from ..header import ComponentTypes as C

# Registre global des actions
ENTITY_ACTIONS: Dict[str, Callable] = {}

def register_action(name: str):
    """registry of all actions"""
    def decorator(func: Callable):
        ENTITY_ACTIONS[name] = func
        return func
    return decorator


@register_action("idle")
def idle_action(*args, **kwargs):
    """Do Nothing"""


# Action de poussée de bloc
@register_action("push_block")
def push_block_action(eid, engine, level, dt, **kwargs):
    """
    Push an entity horinzontally if it's colliding with something on its left or right side.
    The push force can be customized via the "push_force" parameter in kwargs (default: 4000.0).
    The actual force applied is inversely proportional to the entity's mass.
    """
    block_vel = engine.get_component(eid, C.VELOCITY)
    block_mass = engine.get_component(eid, C.MASS)
    block_collision = engine.get_component(eid, C.ENTITYCOLLISION)
    block_state = engine.get_component(eid, C.STATE)
    if not block_collision.collided_entities:
        block_vel.x = 0.0
        block_state.remove_flag("MOVING")
        return

    # On prend la première collision latérale détectée
    for _, directions in block_collision.collided_entities:
        left, right, _, _ = directions
        if left or right:
            break

    direction = -1 if right else 1
    push_force = kwargs.get("push_force", 4000.0)
    mass_value = getattr(block_mass, "value", 1.0)
    force_applied = direction * push_force / max(mass_value, 0.1)
    block_vel.x = force_applied
    block_state.add_flag("MOVING")
