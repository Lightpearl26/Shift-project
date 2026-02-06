# -*- coding: utf-8 -*-

"""ecs_core.ai.registry
___________________________________________________________________________________________________
Registries and decorators for AI commands and conditions.
___________________________________________________________________________________________________
(c) Lafiteau Franck 2026
"""

from __future__ import annotations
from typing import Callable
import inspect


AI_CMD_REGISTRY: dict[str, Callable] = {}
AI_COND_REGISTRY: dict[str, Callable] = {}
AI_CMD_ARGS: dict[str, list[str]] = {}
AI_COND_ARGS: dict[str, list[str]] = {}


def ai_command(name: str) -> Callable:
    """Decorator to register an AI command and its argument names."""
    def decorator(func: Callable) -> Callable:
        AI_CMD_REGISTRY[name] = func
        sig = inspect.signature(func)
        skip = {"eid", "engine", "level", "dt", "kwargs"}
        arg_names = [
            p.name
            for p in sig.parameters.values()
            if p.name not in skip and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
        ]
        AI_CMD_ARGS[name] = arg_names
        return func
    return decorator


def ai_condition(name: str) -> Callable:
    """Decorator to register an AI condition and its argument names."""
    def decorator(func: Callable) -> Callable:
        AI_COND_REGISTRY[name] = func
        sig = inspect.signature(func)
        skip = {"eid", "engine", "level", "dt", "kwargs"}
        arg_names = [
            p.name
            for p in sig.parameters.values()
            if p.name not in skip and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
        ]
        AI_COND_ARGS[name] = arg_names
        return func
    return decorator
