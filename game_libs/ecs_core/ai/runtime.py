# -*- coding: utf-8 -*-

"""ecs_core.ai.runtime
___________________________________________________________________________________________________
AI command and condition runtime implementations.
___________________________________________________________________________________________________
(c) Lafiteau Franck 2026
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from operator import eq, ne, lt, le, gt, ge
from pygame import Vector2

from .registry import AI_CMD_REGISTRY, AI_COND_REGISTRY, ai_command, ai_condition
from .components import AICondition, AICommand
from ...managers.dialog import DialogManager
from ...managers.audio import AudioManager

if TYPE_CHECKING:
    from ..engine import Engine
    from ...level.level import Level
    from ..components import Hitbox


def _cast_literal(value: Any) -> Any:
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in ("true", "false"):
            return lowered == "true"
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
    return value


class AIRuntime:
    """Runtime wrapper for executing AI commands and conditions."""

    def resolve_condition(self,
                          cond_type: str,
                          params: dict,
                          eid: int,
                          engine: Engine,
                          level: Level) -> bool:
        func = AI_COND_REGISTRY.get(cond_type)
        if func:
            return func(eid, engine, level, **params)
        raise ValueError(f"AI Condition '{cond_type}' not found in registry.")

    def run_command(self,
                    cmd: str,
                    kargs: dict,
                    eid: int,
                    engine: Engine,
                    level: Level,
                    dt: float) -> int:
        func = AI_CMD_REGISTRY.get(cmd)
        if func:
            return func(eid, engine, level, dt, **kargs)
        raise ValueError(f"AI Command '{cmd}' not found in registry.")


# ----- AI commands ----- #
@ai_command("idle")
def ai_idle(eid: int, engine: Engine, level: Level, dt: float, **kwargs: dict) -> int:
    """AI idle command."""
    return 1


@ai_command("wait")
def ai_wait(eid: int, engine: Engine, level: Level, dt: float, duration: float = 1.0) -> int:
    """AI wait command."""
    ai_comp = engine.get_component(eid, "AI")
    timer = ai_comp._ai_state.setdefault("wait_timer", 0.0)
    timer += dt
    ai_comp._ai_state["wait_timer"] = timer
    if timer >= duration:
        ai_comp._ai_state["wait_timer"] = 0.0
        return 1
    return 0


@ai_command("dialog")
def ai_dialog(eid: int, engine: Engine, level: Level, dt: float, name: str, force: bool = False) -> int:
    """Request a dialog through the global manager and wait for completion."""
    DialogManager.enqueue(name, force=force)
    return 1 if DialogManager.is_done(name) else 0


@ai_command("jump_to")
def ai_jump_to(eid: int, engine: Engine, level: Level, dt: float, commandline: int) -> int:
    """AI jump to command."""
    ai_comp = engine.get_component(eid, "AI")
    ai_comp.page_logic.command_index = commandline
    return 1


@ai_command("move_to")
def ai_move_to(eid: int, engine: Engine, level: Level, dt: float, x: int, y: int) -> int:
    """Move the entity to (x, y) with acceleration/deceleration."""
    hitbox: Hitbox = engine.get_component(eid, "Hitbox")
    pos: Vector2 = hitbox.pos
    vel = engine.get_component(eid, "Velocity")
    walk = engine.get_component(eid, "Walk")
    xdir = engine.get_component(eid, "XDirection")
    state = engine.get_component(eid, "State")

    target = Vector2(x, y)
    delta = target - pos
    tolerance = 2.0
    max_speed = walk.walk_speed
    accel = max_speed * 4
    decel = max_speed * 6

    if abs(delta.x) <= tolerance:
        vel.x = 0
        state.remove_flag("WALKING")
        hitbox.pos.x = x
        return 1

    xdir.value = 1 if delta.x > 0 else -1
    state.add_flag("WALKING")

    stopping_dist = (vel.x ** 2) / (2 * decel) if decel > 0 else 0
    if abs(delta.x) < abs(stopping_dist):
        vel.x -= decel * dt * xdir.value
        if xdir.value > 0:
            vel.x = max(0, min(vel.x, max_speed))
        else:
            vel.x = min(0, max(vel.x, -max_speed))
    else:
        vel.x += accel * dt * xdir.value
        if xdir.value > 0:
            vel.x = min(vel.x, max_speed)
        else:
            vel.x = max(vel.x, -max_speed)

    return 0


@ai_command("move_to_player")
def ai_move_to_player(eid: int, engine: Engine, level: Level, dt: float) -> int:
    """Move the entity to the player."""
    pos = engine.get_component(level.player.eid, "Hitbox").pos
    x, y = pos.x, pos.y
    return ai_move_to(eid, engine, level, dt, x, y)


@ai_command("if")
def ai_if(
    eid: int,
    engine: Engine,
    level: Level,
    dt: float,
    condition: dict,
    then: list,
    otherwise: list = None
) -> int:
    """Conditional command for AI scripts."""
    ai_comp = engine.get_component(eid, "AI")
    runtime = ai_comp.runtime
    cond = AICondition.from_dict(condition)
    cmds = then if cond.resolve(runtime, eid, engine, level) else (otherwise or [])
    for cmd_dict in cmds:
        cmd = AICommand.from_dict(cmd_dict)
        result = cmd.run(runtime, eid, engine, level, dt)
        if result == 0:
            return 0
    return 1


@ai_command("jump")
def ai_jump(eid: int, engine: Engine, level: Level, dt: float) -> int:
    """Initialize a jump and wait until landing."""
    jump = engine.get_component(eid, "Jump")
    state = engine.get_component(eid, "State")
    ai_state = engine.get_component(eid, "AI")._ai_state
    jumping = ai_state.get("jump", False)
    if not jumping:
        if state.has_flag("CAN_JUMP"):
            jump.direction = 90.0
            jump.time_left = jump.duration
            ai_state["jump"] = True
            player_distance = engine.get_component(eid, "Hitbox").pos.distance_to(
                engine.get_component(level.player.eid, "Hitbox").pos
            )
            max_distance = 1000.0 # 10m (1m = 100px)
            volume = max(0.0, min(1.0, 1 - (player_distance / max_distance)))
            AudioManager.play_se("JUMP", volume_modifier=volume)
        return 0
    if state.has_flag("ON_GROUND"):
        ai_state["jump"] = False
        return 1
    return 0


@ai_command("move_left")
def ai_move_left(eid: int, engine: Engine, level: Level, dt: float) -> int:
    """Move the entity to the left."""
    pos = engine.get_component(level.player.eid, "Hitbox").pos
    return ai_move_to(eid, engine, level, dt, pos.x - 48, pos.y)


@ai_command("move_right")
def ai_move_right(eid: int, engine: Engine, level: Level, dt: float) -> int:
    """Move the entity to the right."""
    pos = engine.get_component(level.player.eid, "Hitbox").pos
    return ai_move_to(eid, engine, level, dt, pos.x + 48, pos.y)


@ai_command("change_state")
def ai_change_state(eid: int, engine: Engine, level: Level, dt: float, flag: str, value: str = "add") -> int:
    """Add or remove a state flag."""
    state = engine.get_component(eid, "State")
    if state:
        if value == "remove":
            state.remove_flag(flag)
        else:
            state.add_flag(flag)
    return 1


@ai_command("set_variable")
def ai_set_variable(eid: int, engine: Engine, level: Level, dt: float, name: str, value: any) -> int:
    """Set an AI state variable."""
    ai_comp = engine.get_component(eid, "AI")
    if ai_comp:
        ai_comp._ai_state[name] = value
    return 1


@ai_command("initiate_jump")
def ai_initiate_jump(eid: int, engine: Engine, level: Level, dt: float) -> int:
    """Initiate a jump without blocking."""
    jump = engine.get_component(eid, "Jump")
    state = engine.get_component(eid, "State")
    if state and state.has_flag("CAN_JUMP") and jump:
        jump.direction = 90.0
        jump.time_left = jump.duration
        # adjust channel sound with player distance
        player_distance = engine.get_component(eid, "Hitbox").pos.distance_to(
            engine.get_component(level.player.eid, "Hitbox").pos
        )
        max_distance = 1000.0 # 10m (1m = 100px)
        volume = max(0.0, min(1.0, 1 - (player_distance / max_distance)))
        AudioManager.play_se("JUMP", volume_modifier=volume)
    return 1


@ai_command("play_sound")
def ai_play_sound(eid: int, engine: Engine, level: Level, dt: float, name: str) -> int:
    """Play a sound effect."""
    AudioManager.play_se(name)
    return 1


# ----- AI conditions ----- #
@ai_condition("True")
def ai_condition_true(eid: int, engine: Engine, level: Level, **kwargs: dict) -> bool:
    """AI condition that is always true."""
    return True


@ai_condition("False")
def ai_condition_false(eid: int, engine: Engine, level: Level, **kwargs: dict) -> bool:
    """AI condition that is always false."""
    return False


@ai_condition("not")
def ai_condition_not(eid, engine, level, condition: dict) -> bool:
    """Negate another condition."""
    runtime = engine.get_component(eid, "AI").runtime
    cond = AICondition(**condition)
    return not cond.resolve(runtime, eid, engine, level)


@ai_condition("and")
def ai_condition_and(eid: int, engine: Engine, level: Level, conditions: list[dict]) -> bool:
    """Check if all conditions are true."""
    runtime = engine.get_component(eid, "AI").runtime
    return all(AICondition(**cond).resolve(runtime, eid, engine, level) for cond in conditions)


@ai_condition("or")
def ai_condition_or(eid: int, engine: Engine, level: Level, conditions: list[dict]) -> bool:
    """Check if at least one condition is true."""
    runtime = engine.get_component(eid, "AI").runtime
    return any(AICondition(**cond).resolve(runtime, eid, engine, level) for cond in conditions)


@ai_condition("component_value")
def ai_condition_component_value(
    eid: int,
    engine: Engine,
    level: Level,
    component_path: str,
    expected_value: Any = None,
    operator: str = "="
) -> bool:
    """Test a component attribute with a dotted path."""
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
def ai_condition_has_component(
    eid: int,
    engine: Engine,
    level: Level,
    component_name: str,
    **kwargs: dict
) -> bool:
    """Check if the entity has a specific component."""
    comp = engine.get_component(eid, component_name)
    return comp is not None


@ai_condition("variable")
def ai_condition_variable(
    eid: int,
    engine: Engine,
    level: Level,
    name: str,
    operator: str,
    value: Any
) -> bool:
    """Check a variable stored in AI state."""
    ai_comp = engine.get_component(eid, "AI")
    var_value = ai_comp._ai_state.get(name)
    if not var_value:
        return False

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
    right = _cast_literal(value)
    left = var_value
    if operator in ("<", "<=", ">", ">="):
        left = _cast_literal(left)
    return op_func(left, right)


@ai_condition("distance_to_player")
def ai_condition_distance_to_player(
    eid: int,
    engine: Engine,
    level: Level,
    operator: str,
    distance: float
) -> bool:
    """Check distance from entity to player."""
    player_eid = level.player.eid
    entity_pos_comp: Vector2 = engine.get_component(eid, "Hitbox").pos
    player_pos_comp: Vector2 = engine.get_component(player_eid, "Hitbox").pos

    dist = entity_pos_comp.distance_to(player_pos_comp)
    distance = _cast_literal(distance)
    if isinstance(distance, str):
        try:
            distance = float(distance)
        except ValueError:
            return False

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


@ai_condition("has_flag")
def ai_condition_has_flag(eid: int, engine: Engine, level: Level, flag: str) -> bool:
    """Check if the entity has a specific state flag."""
    state = engine.get_component(eid, "State")
    if state:
        return state.has_flag(flag)
    return False


@ai_condition("line_of_sight")
def ai_condition_line_of_sight(
    eid: int,
    engine: Engine,
    level: Level,
    target_eid: int = None
) -> bool:
    """Line of sight condition (not implemented yet)."""
    if target_eid is None:
        target_eid = level.player.eid
    raise NotImplementedError


@ai_condition("collision_at")
def ai_condition_collision_at(
    eid: int,
    engine: Engine,
    level: Level,
    direction: str
) -> bool:
    """Check collision in a given direction."""
    col = engine.get_component(eid, "MapCollision")
    return getattr(col, direction, False)
