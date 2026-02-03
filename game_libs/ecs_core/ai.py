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
from typing import Callable, Any, TYPE_CHECKING
from operator import eq, ne, lt, le, gt, ge
from pygame import Vector2

from .. import logger

if TYPE_CHECKING:
    from ..ecs_core.engine import Engine
    from ..level.level import Level
    from ..ecs_core.components import Hitbox



# ----- AI registry ----- #
AI_CMD_REGISTRY: dict[str, Callable] = {}
AI_COND_REGISTRY: dict[str, Callable] = {}
AI_CMD_ARGS: dict[str, list[str]] = {}
AI_COND_ARGS: dict[str, list[str]] = {}


# ----- Decorators ----- #

import inspect
import re

def ai_command(name: str) -> Callable:
    """
    Decorator to register an AI command and its argument names
    """
    def decorator(func: Callable) -> Callable:
        AI_CMD_REGISTRY[name] = func
        # Enregistre les noms d'arguments (hors eid, engine, level, dt, **kwargs)
        sig = inspect.signature(func)
        skip = {"eid", "engine", "level", "dt", "kwargs"}
        arg_names = [p.name for p in sig.parameters.values()
                     if p.name not in skip and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
        AI_CMD_ARGS[name] = arg_names
        return func
    return decorator

def ai_condition(name: str) -> Callable:
    """
    Decorator to register an AI condition and its argument names
    """
    def decorator(func: Callable) -> Callable:
        AI_COND_REGISTRY[name] = func
        # Enregistre les noms d'arguments (hors eid, engine, level, **kwargs)
        sig = inspect.signature(func)
        skip = {"eid", "engine", "level", "dt", "kwargs"}
        arg_names = [p.name for p in sig.parameters.values()
                     if p.name not in skip and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
        AI_COND_ARGS[name] = arg_names
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
    
    @classmethod
    def from_dict(cls, data: dict) -> "AICondition":
        return cls(
            type=data["type"],
            params=data.get("params", {})
        )

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
    
    @classmethod
    def from_dict(cls, data: dict) -> "AICommand":
        return cls(
            cmd=data["cmd"],
            kargs=data.get("kargs", {})
        )

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

    @classmethod
    def from_dict(cls, data: dict) -> "AIPage":
        return cls(
            condition=AICondition.from_dict(data["condition"]),
            commands=[AICommand.from_dict(cmd) for cmd in data["commands"]]
        )


class AIPageLogic(Logic):
    """
    AI Page Logic
    """
    def __init__(self: AIPageLogic, pages: list[AIPage], **kwargs: dict) -> None:
        super().__init__(**kwargs)
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
            
    @classmethod
    def from_dict(cls, data: dict) -> "AIPageLogic":
        pages = [AIPage.from_dict(page) for page in data["pages"]]
        return cls(pages=pages)


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
    Déplace l'entité vers (x, y) avec accélération/décélération naturelle.
    - S'arrête progressivement à proximité.
    - Gère la direction et la vitesse.
    - Retourne 1 si la cible est atteinte (tolérance), sinon 0.
    """
    hitbox: Hitbox = engine.get_component(eid, "Hitbox")
    pos: Vector2 = hitbox.pos
    vel = engine.get_component(eid, "Velocity")
    walk = engine.get_component(eid, "Walk")
    xdir = engine.get_component(eid, "XDirection")
    state = engine.get_component(eid, "State")

    target = Vector2(x, y)
    delta = target - pos
    tolerance = 2.0  # px
    max_speed = walk.walk_speed
    accel = max_speed * 4  # px/s²
    decel = max_speed * 6  # px/s²

    # Si on est proche de la cible, on stoppe
    if abs(delta.x) <= tolerance:
        vel.x = 0
        state.remove_flag("WALKING")
        hitbox.pos.x = x  # Snap pour éviter l'oscillation
        return 1

    # Détermination de la direction
    xdir.value = 1 if delta.x > 0 else -1
    state.add_flag("WALKING")

    # Décélération si on approche de la cible
    stopping_dist = (vel.x ** 2) / (2 * decel) if decel > 0 else 0
    if abs(delta.x) < abs(stopping_dist):
        # Décélère
        vel.x -= decel * dt * xdir.value
        # Clamp la vitesse
        if xdir.value > 0:
            vel.x = max(0, min(vel.x, max_speed))
        else:
            vel.x = min(0, max(vel.x, -max_speed))
    else:
        # Accélère
        vel.x += accel * dt * xdir.value
        # Clamp la vitesse
        if xdir.value > 0:
            vel.x = min(vel.x, max_speed)
        else:
            vel.x = max(vel.x, -max_speed)

    return 0

@ai_command("move_to_player")
def ai_move_to_player(eid: int, engine: Engine, level: Level, dt: float) -> int:
    """
    Move the Entity to the player
    """
    pos = engine.get_component(level.player.eid, "Hitbox").pos
    x, y = pos.x, pos.y
    return ai_move_to(eid, engine, level, dt, x, y)
    

@ai_command("if")
def ai_if(eid: int, engine: Engine, level: Level, dt: float, condition: dict, then: list, otherwise: list = None) -> int:
    """
    Commande conditionnelle :
    - 'condition' : dict décrivant la condition (ex: {"type": ..., "params": {...}})
    - 'then' : liste de commandes à exécuter si vrai
    - 'otherwise' : liste de commandes à exécuter si faux (optionnel)
    """
    cond = AICondition.from_dict(condition)
    cmds = then if cond.resolve(eid, engine, level) else (otherwise or [])
    # On exécute chaque commande de la branche choisie
    for cmd_dict in cmds:
        cmd = AICommand.from_dict(cmd_dict)
        result = cmd.run(eid, engine, level, dt)
        if result == 0:
            return 0  # Attendre la fin de la sous-commande
    return 1  # Branche terminée

@ai_command("jump")
def ai_jump(eid: int, engine: Engine, level: Level, dt: float) -> int:
    """
    Initialize a jump
    """
    jump = engine.get_component(eid, "Jump")
    state = engine.get_component(eid,"State")
    ai_state = engine.get_component(eid, "AI")._ai_state
    jumping = ai_state.get("jump", False)
    if not jumping:
        if state.has_flag("CAN_JUMP"):
            jump.direction = 90.0
            jump.time_left = jump.duration
            ai_state["jump"] = True
        return 0
    else:
        if state.has_flag("ON_GROUND"):
            ai_state["jump"] = False
            return 1
        return 0

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


# ----- AI Script Parser ----- #

class AIScriptParseError(Exception):
    pass

def parse_args_block(lines: list[str]) -> dict[str, dict[str, Any]]:
    """
    Parse le bloc args: en dict {nom: {type, default, doc}}
    """
    args = {}
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        # Ex: target_x: int = 100  # doc
        m = re.match(r"(\w+):\s*(\w+)(?:\s*=\s*([^#]+))?(?:\s*#\s*(.*))?", line.strip())
        if m:
            name, typ, default, doc = m.groups()
            args[name] = {
                'type': typ,
                'default': default.strip() if default else None,
                'doc': doc.strip() if doc else ''
            }
    return args

def _try_cast_number(val):
    """Essaie de caster val en int ou float si possible, sinon laisse en str."""
    try:
        if isinstance(val, str) and '.' in val:
            return float(val)
        return int(val)
    except Exception:
        return val

def parse_condition(line: str) -> dict[str, Any]:
    """
    Parse une condition sous forme: nom(param1, param2, ...)
    Utilise AI_COND_ARGS pour mapper les arguments positionnels sur les bons noms.
    """
    m = re.match(r"([\w_]+)\((.*)\)", line.strip())
    if m:
        name, params = m.groups()
        params = params.strip()
        # Supporte True/False sans parenthèses
        if not params:
            return {'type': name, 'params': {}}
        # Ex: distance_to_player(<100)
        # On tente de parser opérateur et valeur
        if name in AI_COND_ARGS:
            arg_names = AI_COND_ARGS[name]
            param_list = [p.strip() for p in re.split(r',\s*', params) if p.strip()]
            kargs = {}
            # Cas spécial : si le premier paramètre attendu est 'operator' et qu'on reçoit une valeur de la forme <200
            if len(arg_names) >= 2 and arg_names[0] == 'operator' and arg_names[1] == 'distance' and len(param_list) == 1:
                op_val = re.match(r"([<>!=]=?|==)\s*([\w$\.]+)", param_list[0])
                if not op_val:
                    op_val = re.match(r"([<>!=]=?|==)([\w$\.]+)", param_list[0])
                if op_val:
                    op, val = op_val.groups()
                    kargs['operator'] = op
                    kargs['distance'] = _try_cast_number(val)
                    return {'type': name, 'params': kargs}
            # Cas général
            for i, val in enumerate(param_list):
                if i < len(arg_names):
                    kargs[arg_names[i]] = val
                else:
                    kargs.setdefault('args', []).append(val)
            return {'type': name, 'params': kargs}
        # Fallback: opérateur et valeur pour les conditions classiques
        op_val = re.match(r"([<>!=]=?|==)\s*([\w$\.]+)", params)
        if not op_val:
            # Essaye sans espace (ex: <200)
            op_val = re.match(r"([<>!=]=?|==)([\w$\.]+)", params)
        if op_val:
            op, val = op_val.groups()
            return {'type': name, 'params': {'operator': op, 'distance': _try_cast_number(val)}}
        # Autres cas: split par virgule
        param_list = [p.strip() for p in params.split(',') if p.strip()]
        return {'type': name, 'params': {'args': param_list}}
    # Cas True/False sans parenthèses
    if line.strip() in ('True', 'False'):
        return {'type': line.strip(), 'params': {}}
    raise AIScriptParseError(f"Condition invalide: {line}")

def parse_command(line: str) -> dict[str, Any]:
    """
    Parse une commande simple: nom arg1 arg2 ...
    Utilise AI_CMD_ARGS pour mapper les arguments positionnels sur les bons noms.
    """
    parts = line.strip().split()
    if not parts:
        return None
    cmd = parts[0]
    args = parts[1:]
    kargs = {}
    if cmd in AI_CMD_ARGS and args:
        arg_names = AI_CMD_ARGS[cmd]
        for i, val in enumerate(args):
            if i < len(arg_names):
                kargs[arg_names[i]] = val
            else:
                # Arguments surnuméraires, on les met dans 'args'
                kargs.setdefault('args', []).append(val)
    elif args:
        kargs['args'] = args
    return {'cmd': cmd, 'kargs': kargs}

def parse_commands_block(lines: list[str], start: int = 0, indent: int = 8) -> tuple[list[dict[str, Any]], int]:
    """
    Parse un bloc de commandes, gère if/else imbriqués.
    Retourne (liste de commandes, index de fin)
    """
    commands = []
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith('#'):
            i += 1
            continue
        current_indent = len(line) - len(line.lstrip())
        if current_indent < indent:
            break
        lstr = line.strip()
        if lstr.startswith('if '):
            # Bloc if/else
            cond = lstr[3:].rstrip(':')
            i += 1
            then_cmds, i = parse_commands_block(lines, i, indent + 4)
            # Cherche un else:
            else_cmds = []
            if i < len(lines) and lines[i].strip().startswith('else:'):
                i += 1
                else_cmds, i = parse_commands_block(lines, i, indent + 4)
            commands.append({
                'cmd': 'if',
                'kargs': {
                    'condition': parse_condition(cond),
                    'then': then_cmds,
                    'otherwise': else_cmds
                }
            })
        else:
            commands.append(parse_command(lstr))
            i += 1
    return commands, i

def parse_ai_script(script: str) -> dict[str, Any]:
    """
    Parse un script .ai en dict {args, pages}
    """
    lines = script.splitlines()
    args = {}
    pages = []
    i = 0
    while i < len(lines):
        line = lines[i]
        lstr = line.strip()
        if not lstr or lstr.startswith('#'):
            i += 1
            continue
        if lstr.startswith('args:'):
            # Bloc args
            arg_lines = []
            i += 1
            while i < len(lines) and (lines[i].strip() == '' or lines[i].startswith('    ')):
                arg_lines.append(lines[i])
                i += 1
            args = parse_args_block(arg_lines)
            continue
        if lstr.startswith('page:'):
            # Bloc page
            page = {}
            i += 1
            # Cherche condition
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            if i < len(lines) and lines[i].strip().startswith('condition:'):
                cond_line = lines[i].strip()[len('condition:'):].strip()
                page['condition'] = parse_condition(cond_line)
                i += 1
            # Cherche commands
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            if i < len(lines) and lines[i].strip().startswith('commands:'):
                i += 1
                cmds, i = parse_commands_block(lines, i)
                page['commands'] = cmds
            pages.append(page)
            continue
        i += 1
    return {'args': args, 'pages': pages}

def decode_ai_script_dict(data: dict, arg_values: dict = None) -> list:
    """
    Convertit un dict issu du parser en liste d'AIPage (structure AIPageLogic),
    avec substitution des variables $var et conversion de type.
    arg_values : valeurs d'initialisation des arguments (sinon valeurs par défaut)
    """
    args_decl = data.get('args', {})
    # Prépare les valeurs d'arguments (utilise arg_values ou les valeurs par défaut)
    values = {}
    for k, meta in args_decl.items():
        v = None
        if arg_values and k in arg_values:
            v = arg_values[k]
        elif meta.get('default') is not None:
            v = meta['default']
        # Conversion de type
        typ = meta.get('type', 'str')
        if v is not None:
            if typ == 'int':
                v = int(v)
            elif typ == 'float':
                v = float(v)
            elif typ == 'bool':
                v = str(v).lower() in ('1', 'true', 'yes')
            else:
                v = str(v)
        values[k] = v

    def substitute(val):
        # Remplace $var par sa valeur (str/int/float)
        if isinstance(val, str) and val.startswith('$'):
            var = val[1:]
            return values.get(var, val)
        return val

    def substitute_dict(d):
        # Substitution récursive dans un dict
        return {k: substitute_dict(v) if isinstance(v, dict) else
                    [substitute_dict(x) if isinstance(x, dict) else substitute(x) for x in v] if isinstance(v, list)
                    else substitute(v)
                for k, v in d.items()}

    def decode_condition(cond_dict):
        params = substitute_dict(cond_dict.get('params', {}))
        return AICondition(type=cond_dict['type'], params=params)

    def decode_command(cmd_dict):
        cmd = cmd_dict['cmd']
        kargs = substitute_dict(cmd_dict.get('kargs', {}))
        # Gestion récursive pour les if/else
        if cmd == 'if':
            cond = decode_condition(kargs['condition'])
            then_cmds = [decode_command(c) for c in kargs.get('then',[])]
            otherwise_cmds = [decode_command(c) for c in kargs.get('otherwise',[])]
            return AICommand(cmd='if', kargs={
                'condition': {'type': cond.type, 'params': cond.params},
                'then': [c.__dict__ for c in then_cmds],
                'otherwise': [c.__dict__ for c in otherwise_cmds]
            })
        return AICommand(cmd=cmd, kargs=kargs)

    pages = []
    for page_dict in data.get('pages', []):
        cond = decode_condition(page_dict['condition'])
        cmds = [decode_command(c) for c in page_dict.get('commands',[])]
        pages.append(AIPage(condition=cond, commands=cmds))
    return pages

def decode_ai_script(script: str, **arg_values) -> list[AIPage]:
    """
    Parse un script .ai en AIPageLogic, avec substitution des variables $var et conversion de type.
    arg_values : valeurs d'initialisation des arguments (sinon valeurs par défaut)
    """
    data = parse_ai_script(script)
    pages = decode_ai_script_dict(data, arg_values)
    return pages
