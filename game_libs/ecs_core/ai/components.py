# -*- coding: utf-8 -*-

"""ecs_core.ai.components
___________________________________________________________________________________________________
AI structures and script parsing utilities.
___________________________________________________________________________________________________
(c) Lafiteau Franck 2026
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
import re

from .registry import AI_CMD_ARGS, AI_COND_ARGS

if TYPE_CHECKING:
    from ..engine import Engine
    from ...level.level import Level
    from .runtime import AIRuntime


# ----- Default logic of entities ----- #
class Logic:
    """Base Logic of AI."""
    def __init__(self: Logic, **kwargs: dict) -> None:
        pass

    def __call__(self, eid: int, engine: Engine, level: Level, dt: float, runtime: AIRuntime) -> None:
        raise NotImplementedError


class Idle(Logic):
    """IDLE logic."""
    def __call__(self, eid: int, engine: Engine, level: Level, dt: float, runtime: AIRuntime) -> None:
        pass


# ----- AI page system logic ----- #
@dataclass
class AICondition:
    """AI condition."""
    type: str
    params: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict) -> "AICondition":
        return cls(
            type=data["type"],
            params=data.get("params", {})
        )

    def resolve(self: AICondition, runtime: AIRuntime, eid: int, engine: Engine, level: Level) -> bool:
        """Resolve the condition using the runtime."""
        return runtime.resolve_condition(self.type, self.params, eid, engine, level)


@dataclass
class AICommand:
    """AI command."""
    cmd: str
    kargs: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict) -> "AICommand":
        return cls(
            cmd=data["cmd"],
            kargs=data.get("kargs", {})
        )

    def run(self: AICommand, runtime: AIRuntime, eid: int, engine: Engine, level: Level, dt: float) -> int:
        """Run the command using the runtime."""
        return runtime.run_command(self.cmd, self.kargs, eid, engine, level, dt)


@dataclass
class AIPage:
    """AI command page."""
    condition: AICondition
    commands: list[AICommand]

    @classmethod
    def from_dict(cls, data: dict) -> "AIPage":
        return cls(
            condition=AICondition.from_dict(data["condition"]),
            commands=[AICommand.from_dict(cmd) for cmd in data["commands"]]
        )


class AIPageLogic(Logic):
    """AI Page Logic."""
    def __init__(self: AIPageLogic, pages: list[AIPage], **kwargs: dict) -> None:
        super().__init__(**kwargs)
        self.pages = pages
        self.current_page = 0
        self.command_index = 0

    def __call__(self: AIPageLogic, eid: int, engine: Engine, level: Level, dt: float, runtime: AIRuntime) -> None:
        active_page = next(
            (i for i, page in enumerate(self.pages)
             if page.condition.resolve(runtime, eid, engine, level)), -1
        )

        if active_page != self.current_page:
            self.current_page = active_page
            self.command_index = 0

        if self.current_page == -1:
            return

        page = self.pages[self.current_page]
        if self.command_index < len(page.commands):
            command = page.commands[self.command_index]
            result = command.run(runtime, eid, engine, level, dt)
            if result == 1:
                self.command_index += 1
        else:
            self.command_index = 0

    @classmethod
    def from_dict(cls, data: dict) -> "AIPageLogic":
        pages = [AIPage.from_dict(page) for page in data["pages"]]
        return cls(pages=pages)


# ----- AI Script Parser ----- #
class AIScriptParseError(Exception):
    pass


def parse_args_block(lines: list[str]) -> dict[str, dict[str, Any]]:
    """Parse the args block into a dict of argument metadata."""
    args = {}
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
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
    """Try to cast to int/float if possible, otherwise keep as str."""
    try:
        if isinstance(val, str) and '.' in val:
            return float(val)
        return int(val)
    except Exception:
        return val


def _try_cast_literal(val):
    """Try to cast booleans and numbers, otherwise keep as str."""
    if isinstance(val, str):
        lowered = val.lower()
        if lowered in ("true", "false"):
            return lowered == "true"
    return _try_cast_number(val)


def parse_condition(line: str) -> dict[str, Any]:
    """Parse a condition line into a dict for runtime resolution."""
    m = re.match(r"([\w_]+)\((.*)\)", line.strip())
    if m:
        name, params = m.groups()
        params = params.strip()
        if not params:
            return {'type': name, 'params': {}}
        if name in AI_COND_ARGS:
            arg_names = AI_COND_ARGS[name]
            param_list = [p.strip() for p in re.split(r',\s*', params) if p.strip()]
            kargs = {}
            if (
                len(arg_names) >= 2
                and arg_names[0] == 'operator'
                and arg_names[1] == 'distance'
                and len(param_list) == 1
            ):
                op_val = re.match(r"([<>!=]=?|==)\s*([\w$\.]+)", param_list[0])
                if not op_val:
                    op_val = re.match(r"([<>!=]=?|==)([\w$\.]+)", param_list[0])
                if op_val:
                    op, val = op_val.groups()
                    kargs['operator'] = op
                    kargs['distance'] = _try_cast_number(val)
                    return {'type': name, 'params': kargs}
            if len(arg_names) >= 3 and len(param_list) == 1:
                inline = re.match(r"([\w$\.]+)\s*([<>!=]=?|==)\s*([\w$\.]+)", param_list[0])
                if inline:
                    left, op, right = inline.groups()
                    kargs[arg_names[0]] = left
                    kargs[arg_names[1]] = op
                    kargs[arg_names[2]] = _try_cast_literal(right)
                    return {'type': name, 'params': kargs}
            for i, val in enumerate(param_list):
                if i < len(arg_names):
                    key = arg_names[i]
                    if key in ("value", "distance", "expected_value"):
                        kargs[key] = _try_cast_literal(val)
                    else:
                        kargs[key] = val
                else:
                    kargs.setdefault('args', []).append(val)
            return {'type': name, 'params': kargs}
        op_val = re.match(r"([<>!=]=?|==)\s*([\w$\.]+)", params)
        if not op_val:
            op_val = re.match(r"([<>!=]=?|==)([\w$\.]+)", params)
        if op_val:
            op, val = op_val.groups()
            return {'type': name, 'params': {'operator': op, 'distance': _try_cast_number(val)}}
        param_list = [p.strip() for p in params.split(',') if p.strip()]
        return {'type': name, 'params': {'args': param_list}}
    if line.strip() in ('True', 'False'):
        return {'type': line.strip(), 'params': {}}
    raise AIScriptParseError(f"Condition invalide: {line}")


def parse_command(line: str) -> dict[str, Any]:
    """Parse a single command line into a dict for runtime resolution."""
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
                if isinstance(val, str) and val.startswith('$'):
                    kargs[arg_names[i]] = val
                else:
                    kargs[arg_names[i]] = _try_cast_literal(val)
            else:
                kargs.setdefault('args', []).append(_try_cast_literal(val))
    elif args:
        kargs['args'] = [_try_cast_literal(val) for val in args]
    return {'cmd': cmd, 'kargs': kargs}


def parse_commands_block(lines: list[str], start: int = 0, indent: int = 8) -> tuple[list[dict[str, Any]], int]:
    """Parse a commands block and return (commands, end_index)."""
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
            cond = lstr[3:].rstrip(':')
            i += 1
            then_cmds, i = parse_commands_block(lines, i, indent + 4)
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
    """Parse a .ai script into a dict of args/pages."""
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
            arg_lines = []
            i += 1
            while i < len(lines) and (lines[i].strip() == '' or lines[i].startswith('    ')):
                arg_lines.append(lines[i])
                i += 1
            args = parse_args_block(arg_lines)
            continue
        if lstr.startswith('page:'):
            page = {}
            i += 1
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            if i < len(lines) and lines[i].strip().startswith('condition:'):
                cond_line = lines[i].strip()[len('condition:'):].strip()
                page['condition'] = parse_condition(cond_line)
                i += 1
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


def decode_ai_script_dict(data: dict, arg_values: dict = None) -> list[AIPage]:
    """Decode parsed AI script data into AIPage structures."""
    args_decl = data.get('args', {})
    values = {}
    for k, meta in args_decl.items():
        v = None
        if arg_values and k in arg_values:
            v = arg_values[k]
        elif meta.get('default') is not None:
            v = meta['default']
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
        if isinstance(val, str) and val.startswith('$'):
            var = val[1:]
            return values.get(var, val)
        return val

    def substitute_dict(d):
        return {
            k: substitute_dict(v) if isinstance(v, dict) else
            [substitute_dict(x) if isinstance(x, dict) else substitute(x) for x in v] if isinstance(v, list)
            else substitute(v)
            for k, v in d.items()
        }

    def decode_condition(cond_dict):
        params = substitute_dict(cond_dict.get('params', {}))
        return AICondition(type=cond_dict['type'], params=params)

    def decode_command(cmd_dict):
        cmd = cmd_dict['cmd']
        kargs = substitute_dict(cmd_dict.get('kargs', {}))
        if cmd == 'if':
            cond = decode_condition(kargs['condition'])
            then_cmds = [decode_command(c) for c in kargs.get('then', [])]
            otherwise_cmds = [decode_command(c) for c in kargs.get('otherwise', [])]
            return AICommand(cmd='if', kargs={
                'condition': {'type': cond.type, 'params': cond.params},
                'then': [c.__dict__ for c in then_cmds],
                'otherwise': [c.__dict__ for c in otherwise_cmds]
            })
        return AICommand(cmd=cmd, kargs=kargs)

    pages = []
    for page_dict in data.get('pages', []):
        cond = decode_condition(page_dict['condition'])
        cmds = [decode_command(c) for c in page_dict.get('commands', [])]
        pages.append(AIPage(condition=cond, commands=cmds))
    return pages


def decode_ai_script(script: str, **arg_values) -> list[AIPage]:
    """Parse and decode a .ai script into AIPage structures."""
    data = parse_ai_script(script)
    pages = decode_ai_script_dict(data, arg_values)
    return pages
