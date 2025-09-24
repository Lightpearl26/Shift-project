from __future__ import annotations
from dataclasses import dataclass
from pygame import Rect, Vector2

from .. import config


@dataclass
class Camera:
    """
    Camera of the Level
    """
    pos: Vector2
    size: tuple[int, int]

    @classmethod
    def from_dict(cls, data: dict[str, float | int]) -> Camera:
        """
        Generate camera from a dict
        """
        x = data.get("x", 0.0)
        y = data.get("y", 0.0)
        width = data.get("width", config.CAMERA_SIZE[0])
        height = data.get("height", config.CAMERA_SIZE[1])
        return cls(Vector2(x, y), (width, height))

    @property
    def rect(self: Camera) -> Rect:
        """
        Get the pygame Rect of the Camera
        """
        topleft = self.pos - Vector2(self.size[0]/2, self.size[1]/2)
        return Rect(topleft, self.size)

    @rect.setter
    def rect(self: Camera, value: Rect) -> None:
        self.pos = Vector2(value.center)
        self.size = value.size

    def _get_prop(self: Camera, prop: str) -> float | Vector2:
        """
        Get a rect property of the Camera and convert it
        """
        p = getattr(self.rect, prop, None)
        if isinstance(p, int | float):
            return float(p)
        if isinstance(p, tuple):
            return Vector2(p)
        raise AttributeError(f"Attribut {prop} doesn't exists")

    def _set_prop(self: Camera, prop: str, value: float | Vector2) -> None:
        """
        Set a Rect property of the Camera
        """
        rect = self.rect
        setattr(rect, prop, value)
        self.pos = Vector2(rect.center)
        self.size = rect.size

    x = property(lambda obj, p="x": Camera._get_prop(obj, p),
                 lambda obj, value, p="x": Camera._set_prop(obj, p, value),
                 doc="Camera Rect x property")
    y = property(lambda obj, p="y": Camera._get_prop(obj, p),
                 lambda obj, value, p="y": Camera._set_prop(obj, p, value),
                 doc="Camera Rect y property")
    top = property(lambda obj, p="top": Camera._get_prop(obj, p),
                   lambda obj, value, p="top": Camera._set_prop(obj, p, value),
                   doc="Camera Rect top property")
    bottom = property(lambda obj, p="bottom": Camera._get_prop(obj, p),
                      lambda obj, value, p="bottom": Camera._set_prop(obj, p, value),
                      doc="Hitboc Rect bottom property")
    left = property(lambda obj, p="left": Camera._get_prop(obj, p),
                    lambda obj, value, p="left": Camera._set_prop(obj, p, value),
                    doc="Camera Rect left property")
    right = property(lambda obj, p="right": Camera._get_prop(obj, p),
                     lambda obj, value, p="right": Camera._set_prop(obj, p, value),
                     doc="Camera rect right property")
    center = property(lambda obj, p="center": Camera._get_prop(obj, p),
                      lambda obj, value, p="center": Camera._set_prop(obj, p, value),
                      doc="Camera Rect center property")
    centerx = property(lambda obj, p="centerx": Camera._get_prop(obj, p),
                       lambda obj, value, p="centerx": Camera._set_prop(obj, p, value),
                       doc="Camera rect centerx property")
    centery = property(lambda obj, p="centery": Camera._get_prop(obj, p),
                       lambda obj, value, p="centery": Camera._set_prop(obj, p, value),
                       doc="Camera rect centery property")
    topleft = property(lambda obj, p="topleft": Camera._get_prop(obj, p),
                       lambda obj, value, p="topleft": Camera._set_prop(obj, p, value),
                       doc="Camera rect topleft property")
    topright = property(lambda obj, p="topright": Camera._get_prop(obj, p),
                        lambda obj, value, p="topright": Camera._set_prop(obj, p, value),
                        doc="=Camera rect topright property")
    bottomleft = property(lambda obj, p="bottomleft": Camera._get_prop(obj, p),
                          lambda obj, value, p="bottomleft": Camera._set_prop(obj, p, value),
                          doc="Camera Rect bottomleft property")
    bottomright = property(lambda obj, p="bottomright": Camera._get_prop(obj, p),
                           lambda obj, value, p="bottomright": Camera._set_prop(obj, p, value),
                           doc="Camera Rect bottomright property")
    width = property(lambda obj, p="width": Camera._get_prop(obj, p),
                     lambda obj, value, p="width": Camera._set_prop(obj, p, value),
                     doc="Camera Rect width property")
    height = property(lambda obj, p="height": Camera._get_prop(obj, p),
                      lambda obj, value, p="height": Camera._set_prop(obj, p, value),
                      doc="Camera Rect height property")
