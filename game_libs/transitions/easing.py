# -*- coding: utf-8 -*-

"""
game_libs.transition.easing
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module defines easing functions for scene transitions.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

# import built-in modules
from math import sin, cos, pi


# ----- Easing linear functions ----- #
def linear(t: float) -> float:
    """
    Linear easing function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return t

# ----- Easing quadratic functions ----- #
def ease_in_quad(t: float) -> float:
    """
    Quadratic ease-in function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return pow(t, 2)

def ease_out_quad(t: float) -> float:
    """
    Quadratic ease-out function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return t * (2 - t)

def ease_in_out_quad(t: float) -> float:
    """
    Quadratic ease-in-out function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2 * t) * t

# ----- Easing sine functions ----- #
def ease_sin_in(t: float) -> float:
    """
    Sine ease-in function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return 1 - cos((t * pi) / 2)

def ease_sin_out(t: float) -> float:
    """
    Sine ease-out function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return sin((t * pi) / 2)

def ease_sin_in_out(t: float) -> float:
    """
    Sine ease-in-out function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return -(cos(pi * t) - 1) / 2

# ----- Easing cubic functions ----- #
def ease_in_cubic(t: float) -> float:
    """
    Cubic ease-in function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return t ** 3

def ease_out_cubic(t: float) -> float:
    """
    Cubic ease-out function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return (t - 1) ** 3 + 1

def ease_in_out_cubic(t: float) -> float:
    """
    Cubic ease-in-out function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    if t < 0.5:
        return 4 * t ** 3
    else:
        return (t - 1) * (2 * t - 2) ** 2 + 1

# ----- Easing circular functions ----- #
def ease_in_circle(t: float) -> float:
    """
    Circular ease-in function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return 1 - pow(1 - t * t, 0.5)

def ease_out_circle(t: float) -> float:
    """
    Circular ease-out function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    return pow(1 - (t - 1) * (t - 1), 0.5)

def ease_in_out_circle(t: float) -> float:
    """
    Circular ease-in-out function.

    Args:
        t (float): Progress value between 0.0 and 1.0.

    Returns:
        float: Eased progress value.
    """
    if t < 0.5:
        return (1 - pow(1 - 4 * t * t, 0.5)) / 2
    else:
        return (pow(1 - (2 * t - 2) * (2 * t - 2), 0.5) + 1) / 2

# ----- Easing exponential functions ----- #
def ease_in_expo(t: float) -> float:
    """
    Exponential ease-in function.
    Args:
        t (float): Progress value between 0.0 and 1.0.
    Returns:
        float: Eased progress value.
    """
    return 0 if t == 0 else pow(2, 10 * (t - 1))

def ease_out_expo(t: float) -> float:
    """
    Exponential ease-out function.
    Args:
        t (float): Progress value between 0.0 and 1.0.
    Returns:
        float: Eased progress value.
    """
    return 1 if t == 1 else 1 - pow(2, -10 * t)

def ease_in_out_expo(t: float) -> float:
    """
    Exponential ease-in-out function.
    Args:
        t (float): Progress value between 0.0 and 1.0.
    Returns:
        float: Eased progress value.
    """
    if t == 0:
        return 0
    if t == 1:
        return 1
    if t < 0.5:
        return pow(2, 20 * t - 10) / 2
    else:
        return (2 - pow(2, -20 * t + 10)) / 2
