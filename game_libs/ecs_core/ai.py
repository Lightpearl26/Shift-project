# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
# pylint: disable=protected-access

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
from dataclasses import dataclass
from typing import Callable, Any
from operator import eq, ne, lt, le, gt, ge
from pygame import Vector2


# import needed protocols of the package
from ..header import Engine, Level, Hitbox

# import logger
from .. import logger


# ----- AI registry ----- #
AI_CMD_REGISTRY: dict[str, Callable] = {}
AI_COND_REGISTRY: dict[str, Callable] = {}


# ----- Decorators ----- #
def ai_command(name: str) -> Callable:
    """
    Decorator to register an AI command
    """
    def decorator(func: Callable) -> Callable:
        AI_CMD_REGISTRY[name] = func
        return func
    return decorator


def ai_condition(name: str) -> Callable:
    """
    Decorator to register an AI condition
    """
    def decorator(func: Callable) -> Callable:
        AI_COND_REGISTRY[name] = func
        return func
    return decorator


# ----- Default logic of entities ----- #
class Logic:
    """
    Base Logic of AI
    """
    def __init__(self: Logic, **kwargs: dict) -> None:
        pass

    def __call__(self, eid: int, engine: Engine, level: Level, dt: float) -> None:
        raise NotImplementedError


class Idle(Logic):
    """
    IDLE logic
    """
    def __call__(self, eid: int, engine: Engine, level: Level, dt: float) -> None:
        pass
        # Do nothing


# ----- AI page system logic ----- #
@dataclass
class AICondition:
    """
    AI condition
    """
    type: str
    params: dict[str, Any]

    def resolve(self: AICondition, eid: int, engine: Engine, level: Level) -> bool:
        """
        Resolve the condition
        """
        func = AI_COND_REGISTRY.get(self.type)
        if func:
            return func(eid, engine, level, **self.params)
        raise ValueError(f"AI Condition '{self.type}' not found in registry.")


@dataclass
class AICommand:
    """
    AI command
    """
    cmd: str
    kargs: dict[str, Any]

    def run(self: AICommand, eid: int, engine: Engine, level: Level, dt: float) -> int:
        """
        Run the command
        """
        func = AI_CMD_REGISTRY.get(self.cmd)
        if func:
            return func(eid, engine, level, dt, **self.kargs)
        raise ValueError(f"AI Command '{self.cmd}' not found in registry.")


@dataclass
class AIPage:
    """
    AI command page
    """
    condition: AICondition
    commands: list[AICommand]


class AIPageLogic(Logic):
    """
    AI Page Logic
    """
    def __init__(self: AIPageLogic, pages: list[AIPage], **kwargs: dict) -> None:
        Logic.__init__(**kwargs)
        self.pages = pages
        self.current_page = 0
        self.command_index = 0

    def __call__(self: AIPageLogic, eid: int, engine: Engine, level: Level, dt: float) -> None:
        active_page = next(
            (i for i, page in enumerate(self.pages)
             if page.condition.resolve(eid, engine, level)), -1
        )

        if active_page != self.current_page:
            self.current_page = active_page
            self.command_index = 0

        if self.current_page == -1:
            return  # No active page found

        page = self.pages[self.current_page]
        if self.command_index < len(page.commands):
            command = page.commands[self.command_index]
            result = command.run(eid, engine, level, dt)
            if result == 1:
                self.command_index += 1
        else:
            self.command_index = 0  # Reset for next call


# ----- AI commands ----- #
@ai_command("idle")
def ai_idle(eid: int, engine: Engine, level: Level, dt: float, **kwargs: dict) -> int:
    """
    AI idle command
    """
    return 1  # Always complete immediately

@ai_command("wait")
def ai_wait(eid: int, engine: Engine, level: Level, dt: float, duration: float=1.0) -> int:
    """
    AI wait command
    """
    ai_comp = engine.get_component(eid, "AI")
    timer = ai_comp._ai_state.setdefault("wait_timer", 0.0)
    timer += dt
    ai_comp._ai_state["wait_timer"] = timer
    if timer >= duration:
        ai_comp._ai_state["wait_timer"] = 0.0  # Reset timer
        return 1  # Complete
    return 0  # Not complete yet

@ai_command("jump_to")
def ai_jump_to(eid: int, engine: Engine, level: Level, dt: float, commandline: int) -> int:
    """
    AI jump to command
    """
    ai_comp = engine.get_component(eid, "AI")
    ai_comp.page_logic.command_index = commandline
    return 1  # Complete

@ai_command("move_to")
def ai_move_to(eid: int, engine: Engine, level: Level, dt: float, x: int, y: int) -> int:
    """
    Move the Entity to the point (x, y)
    This will not handle jumping nor collision but only X movement on ground
    0 = not finished
    1 = finished
    """
    hitbox: Hitbox = engine.get_component(eid, "Hitbox")
    pos: Vector2 = hitbox.pos
    speed_comp = engine.get_component(eid, "Walk").walk_speed
    if pos.x != x:
        xdir = engine.get_component(eid, "XDirection")
        xdir.value = 1 if x > pos.x else -1
        vel = engine.get_component(eid, "Velocity")
        vel.x = xdir.value * speed_comp
        return 0  # Not finished yet
    else:
        vel = engine.get_component(eid, "Velocity")
        vel.x = 0
        return 1  # Finished

# ----- AI conditions ----- #
@ai_condition("True")
def ai_condition_true(eid: int, engine: Engine, level: Level, **kwargs: dict) -> bool:
    """
    AI condition that is always true
    """
    return True

@ai_condition("False")
def ai_condition_false(eid: int, engine: Engine, level: Level, **kwargs: dict) -> bool:
    """
    AI condition that is always false
    """
    return False

@ai_condition("not")
def ai_condition_not(eid, engine, level, condition: dict) -> bool:
    """
    Negates another condition
    """
    cond = AICondition(**condition)
    return not cond.resolve(eid, engine, level)

@ai_condition("and")
def ai_condition_and(eid: int, engine: Engine, level: Level, conditions: list[dict]) -> bool:
    """
    Checks if all conditions are true
    """
    return all(AICondition(**cond).resolve(eid, engine, level) for cond in conditions)

@ai_condition("or")
def ai_condition_or(eid: int, engine: Engine, level: Level, conditions: list[dict]) -> bool:
    """
    Checks if at least one condition is true
    """
    return any(AICondition(**cond).resolve(eid, engine, level) for cond in conditions)

@ai_condition("component_value")
def ai_condition_component_value(eid: int,
                                 engine: Engine,
                                 level: Level,
                                 component_path: str,
                                 expected_value: Any = None,
                                 operator: str = "=") -> bool:
    """
    Teste la valeur d'un attribut (éventuellement imbriqué) d'un composant via une notation pointée.
    Ex: "Mass.value", "Hitbox.rect.x"
    """
    ops = {
        "=": eq, "==": eq,
        "!=": ne,
        "<": lt,
        "<=": le,
        ">": gt,
        ">=": ge,
    }
    if component_path is None or expected_value is None:
        return False

    parts = component_path.split(".")
    comp = engine.get_component(eid, parts[0])
    if not comp:
        return False

    value = comp
    for attr in parts[1:]:
        value = getattr(value, attr)
    op_func = ops.get(operator)
    if not op_func:
        raise ValueError(f"Unknown operator '{operator}' in component_value condition.")
    return op_func(value, expected_value)

@ai_condition("has_component")
def ai_condition_has_component(eid: int,
                               engine: Engine,
                               level: Level,
                               component_name: str,
                               **kwargs: dict) -> bool:
    """
    Vérifie si l'entité possède un composant spécifique.
    """
    comp = engine.get_component(eid, component_name)
    return comp is not None

@ai_condition("variable")
def ai_condition_variable(eid: int,
                          engine: Engine,
                          level: Level,
                          name: str,
                          operator: str,
                          value: Any) -> bool:
    """
    Vérifie une variable stockée dans l'état de l'AI.
    """
    ai_comp = engine.get_component(eid, "AI")
    var_value = ai_comp._ai_state.get(name)

    ops = {
        "=": eq, "==": eq,
        "!=": ne,
        "<": lt,
        "<=": le,
        ">": gt,
        ">=": ge,
    }
    op_func = ops.get(operator)
    if not op_func:
        raise ValueError(f"Unknown operator '{operator}' in variable condition.")
    return op_func(var_value, value)

@ai_condition("distance_to_player")
def ai_condition_distance_to_player(eid: int,
                                    engine: Engine,
                                    level: Level,
                                    operator: str,
                                    distance: float) -> bool:
    """
    Vérifie la distance entre l'entité et le joueur.
    """
    player_eid = level.player.eid
    entity_pos_comp: Vector2 = engine.get_component(eid, "Hitbox").pos
    player_pos_comp: Vector2 = engine.get_component(player_eid, "Hitbox").pos

    dist = entity_pos_comp.distance_to(player_pos_comp)

    ops = {
        "=": eq, "==": eq,
        "!=": ne,
        "<": lt,
        "<=": le,
        ">": gt,
        ">=": ge,
    }
    op_func = ops.get(operator)
    if not op_func:
        raise ValueError(f"Unknown operator '{operator}' in distance_to_player condition.")
    return op_func(dist, distance)
