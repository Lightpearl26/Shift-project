# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs - Header
Minimal runtime header. Only ComponentTypes is defined here.
All other types are defined in their respective modules.
Type annotations should use string literals or from __future__ import annotations.
"""

from __future__ import annotations

from enum import Enum


class ComponentTypes(str, Enum):
    """Enum for mapping any component name"""
    AI = "AI"
    CAMERAFOLLOW = "CameraFollow"
    COLLISIONACTION = "CollisionAction"
    CONTROLLED = "Controlled"
    ENTITYCOLLISION = "EntityCollision"
    HITBOX = "Hitbox"
    JUMP = "Jump"
    MAPCOLLISION = "MapCollision"
    MASS = "Mass"
    NEXTPOSITION = "NextPosition"
    PROPERTIES = "Properties"
    STATE = "State"
    VELOCITY = "Velocity"
    WALK = "Walk"
    WALLSTICKING = "WallSticking"
    XDIRECTION = "XDirection"

    @classmethod
    def from_str(cls, name: str) -> ComponentTypes:
        """Convert a string to a ComponentTypes enum member."""
        for member in cls:
            if member.value == name:
                return member
        raise ValueError(f"No ComponentTypes member with value '{name}' found.")


__all__ = ["ComponentTypes"]
