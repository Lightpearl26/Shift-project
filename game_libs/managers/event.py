# -*- coding : utf-8 -*-
#pylint: disable=broad-except, invalid-name

"""
game_libs.managers.event
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 1.0
___________________________________________________________________________________________________
Description:
    This module manages event functionalities for the game,
    it handles user inputs and system events then translate it into game actions.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

from __future__ import annotations
from typing import TYPE_CHECKING

# Import enum
from enum import IntFlag, auto

# Import pygame
from pygame.key import get_pressed as key_state
from pygame.joystick import (
    Joystick,
    init as joystick_init,
    get_count,
)

# Import config
from .. import config

# Import logger
from .. import logger

if TYPE_CHECKING:
    from pygame.key import ScancodeWrapper
    from pygame.joystick import JoystickType

# ------ KeyState enum -----
class KeyState(IntFlag):
    """
    KeyState enum to handle key states.
    """
    RELEASED = 0
    PRESSED = auto()
    HELD = auto()


# ----- KeyMapping class -----
class KeyMapping:
    """
    KeyMapping class to handle key mappings using pygame.key.get_pressed().
    """
    def __init__(self) -> None:
        """
        Initialize the KeyMapping with default key mappings from config.
        """
        # Define key mappings
        self.UP: set[int] = config.KEYS_UP
        self.DOWN: set[int] = config.KEYS_DOWN
        self.LEFT: set[int] = config.KEYS_LEFT
        self.RIGHT: set[int] = config.KEYS_RIGHT
        self.JUMP: set[int] = config.KEYS_JUMP
        self.SPRINT: set[int] = config.KEYS_SPRINT
        self.PAUSE: set[int] = config.KEYS_PAUSE

        # Track which keys were down last frame
        self._last_key_state: set[int] = set()

    def serialize(self, keys: ScancodeWrapper) -> dict[str, KeyState]:
        """
        Get the current key states from get_pressed().

        Args:
            - keys (ScancodeWrapper): Result from pygame.key.get_pressed()

        Returns:
            - dict[str, KeyState]: Dictionary mapping action names to their current KeyState.
        """
        state: dict[str, KeyState] = {
            "UP": KeyState.RELEASED,
            "DOWN": KeyState.RELEASED,
            "LEFT": KeyState.RELEASED,
            "RIGHT": KeyState.RELEASED,
            "JUMP": KeyState.RELEASED,
            "SPRINT": KeyState.RELEASED,
            "PAUSE": KeyState.RELEASED,
        }

        # Get all currently pressed keys
        current_down: set[int] = set()

        for action, mapping in {
            "UP": self.UP,
            "DOWN": self.DOWN,
            "LEFT": self.LEFT,
            "RIGHT": self.RIGHT,
            "JUMP": self.JUMP,
            "SPRINT": self.SPRINT,
            "PAUSE": self.PAUSE,
        }.items():
            for scancode in mapping:
                try:
                    if keys[scancode]:
                        current_down.add(scancode)
                        # Check if key was pressed in previous frame
                        if scancode in self._last_key_state:
                            state[action] = KeyState.HELD
                        else:
                            state[action] = KeyState.PRESSED
                        break
                except IndexError:
                    # Scancode out of range, skip it
                    continue
        
        # Update last key state for next frame
        self._last_key_state = current_down
        return state

    # class method to load a key_mapping from a dictionary
    @classmethod
    def from_dict(cls, mapping_dict: dict[str, list[int]]) -> KeyMapping:
        """
        Load key mappings from a dictionary.

        Args:
            - mapping_dict: Dictionary mapping action names to lists of key codes.
        """
        inst = cls()
        for action, keys in mapping_dict.items():
            if hasattr(inst, action):
                # Validate that all keys are valid integers (pygame key codes can be > 512)
                if any(not isinstance(k, int) or k < 0 for k in keys):
                    logger.error(f"[KeyMapping] Invalid key codes in action '{action}'")
                    raise KeyError(f"Invalid key codes in action '{action}'")
                setattr(inst, action, set(keys))
            else:
                logger.warning(f"[KeyMapping] Unknown action '{action}' in mapping dictionary")
        logger.info("[EventManager] Key mappings loaded from dictionary")
        return inst


# ----- GamepadMapping class -----
class GamepadMapping:
    """
    GamepadMapping class to handle gamepad mappings.

    - Reads D-Pad via hat (preferred) or left stick with a threshold.
    - Maps buttons to ACTION/CANCEL/PAUSE/SHIFT/WHEEL.
    - Serializes into the same action keys as keyboard.
    """

    def __init__(self) -> None:
        # Default button indices (common layout; can be remapped via from_dict)
        self.JUMP: set[int] = {0}  # A / Cross
        self.SPRINT: set[int] = {10}  # LB / L1
        self.PAUSE: set[int] = {5, 1}   # Start / Cross

        # Direction config: D-Pad buttons (ZEROPLUS Pro5: UP=11, DOWN=12, LEFT=13, RIGHT=14)
        self._dpad_up: set[int] = {11}
        self._dpad_down: set[int] = {12}
        self._dpad_left: set[int] = {13}
        self._dpad_right: set[int] = {14}
        
        # Trigger axes (L2=axis 4, R2=axis 5)
        self._l2_axis: int = 4
        self._r2_axis: int = 5
        self._axis_threshold: float = 0.5
        
        # Fallback to left stick if D-Pad buttons not available
        self._use_left_stick_for_dir: bool = True

        # Joystick state
        self._initialized: bool = False
        self._joystick: JoystickType | None = None

        # Last down flags per action for HELD/PRESSED detection
        self._last_down: dict[str, bool] = {
            "UP": False,
            "DOWN": False,
            "LEFT": False,
            "RIGHT": False,
            "JUMP": False,
            "SPRINT": False,
            "PAUSE": False,
        }

    def _ensure_init(self) -> None:
        if self._initialized:
            return
        try:
            joystick_init()
            count = get_count()
            if count > 0:
                self._joystick = Joystick(0)
                self._joystick.init()
                logger.info(f"[GamepadMapping] Gamepad detected: {self._joystick.get_name()}")
                logger.info(f"[GamepadMapping] Hat count: {self._joystick.get_numhats()}, Axes: {self._joystick.get_numaxes()}, Buttons: {self._joystick.get_numbuttons()}")
            else:
                logger.info("[GamepadMapping] No gamepad detected")
            self._initialized = True
        except Exception as exc:
            logger.error(f"[GamepadMapping] Initialization error: {exc}")
            self._initialized = True

    def _read_buttons_down(self) -> dict[str, bool]:
        down: dict[str, bool] = {
            "JUMP": False,
            "SPRINT": False,
            "PAUSE": False,
        }
        if not self._joystick:
            return down
        try:
            for btn in self.PAUSE:
                if self._joystick.get_button(btn):
                    down["PAUSE"] = True
                    break
            for btn in self.JUMP:
                if self._joystick.get_button(btn):
                    down["JUMP"] = True
                    break
            for btn in self.SPRINT:
                if self._joystick.get_button(btn):
                    down["SPRINT"] = True
                    break
        except Exception as exc:
            logger.error(f"[GamepadMapping] Button read error: {exc}")
        return down

    def _read_direction_down(self) -> dict[str, bool]:
        dpad: dict[str, bool] = {
            "UP": False,
            "DOWN": False,
            "LEFT": False,
            "RIGHT": False,
        }
        if not self._joystick:
            return dpad
        try:
            # Read D-Pad buttons
            for btn in self._dpad_up:
                if self._joystick.get_button(btn):
                    dpad["UP"] = True
                    break
            for btn in self._dpad_down:
                if self._joystick.get_button(btn):
                    dpad["DOWN"] = True
                    break
            for btn in self._dpad_left:
                if self._joystick.get_button(btn):
                    dpad["LEFT"] = True
                    break
            for btn in self._dpad_right:
                if self._joystick.get_button(btn):
                    dpad["RIGHT"] = True
                    break
            
            # Fall back to left stick if no D-Pad button press detected
            if not any(dpad.values()) and self._use_left_stick_for_dir and self._joystick.get_numaxes() >= 2:
                ax_x = self._joystick.get_axis(0)
                ax_y = self._joystick.get_axis(1)
                thr = self._axis_threshold
                dpad["LEFT"] = ax_x < -thr
                dpad["RIGHT"] = ax_x > thr
                dpad["UP"] = ax_y < -thr
                dpad["DOWN"] = ax_y > thr
        except Exception as exc:
            logger.error(f"[GamepadMapping] Direction read error: {exc}")
        return dpad

    def serialize(self) -> dict[str, KeyState]:
        """
        Read current joystick state and produce KeyState per action.
        """
        self._ensure_init()

        # Read current down flags
        dir_down = self._read_direction_down()
        btn_down = self._read_buttons_down()
        now_down: dict[str, bool] = {**self._last_down}
        now_down.update(dir_down)
        now_down.update(btn_down)

        states: dict[str, KeyState] = {}
        for action, is_down in now_down.items():
            last = self._last_down.get(action, False)
            if is_down:
                states[action] = KeyState.HELD if last else KeyState.PRESSED
            else:
                states[action] = KeyState.RELEASED
        # Update last
        self._last_down = now_down
        return states

    @classmethod
    def from_dict(cls, mapping_dict: dict[str, list[int]]) -> GamepadMapping:
        """
        Load button mappings from a dictionary (actions -> list of button indices).
        Note: Directions use hat/stick and are not remapped via buttons.
        """
        inst = cls()
        for action, btns in mapping_dict.items():
            if hasattr(inst, action):
                if any(not isinstance(b, int) or b < 0 for b in btns):
                    logger.error(f"[GamepadMapping] Invalid button codes in action '{action}'")
                    raise KeyError(f"Invalid button codes in action '{action}'")
                setattr(inst, action, set(btns))
            else:
                logger.warning(f"[GamepadMapping] Unknown action '{action}' in mapping dictionary")
        logger.info("[GamepadMapping] Gamepad button mappings loaded from dictionary")
        return inst


# ----- EventManager class -----
class EventManager:
    """
    EventManager class to handle events.
    """
    # adding default key mapping
    key_mapping: KeyMapping = KeyMapping()
    gamepad_mapping: GamepadMapping = GamepadMapping()
    key_states: dict[str, KeyState] = {}

    # adding timers dictionary
    _timers: dict[str, tuple[float, float, bool, bool]] = {
    } # name: (time_left, duration, repeat, paused)
    _triggered: set[str] = set()  # timers triggered this frame
    _paused: bool = False  # pause all timers

    # - mapping methods
    @classmethod
    def set_key_mapping(cls, mapping: dict[str, list[int]]) -> None:
        """
        Set a new key mapping.

        Args:
            - mapping (KeyMapping): New key mapping to set.
        """
        cls.key_mapping = KeyMapping.from_dict(mapping)
        logger.info("[EventManager] Key mapping updated")

    @classmethod
    def set_gamepad_mapping(cls, mapping: dict[str, list[int]]) -> None:
        """
        Set a new gamepad mapping.

        Args:
            - mapping (GamepadMapping): New gamepad mapping to set.
        """
        cls.gamepad_mapping = GamepadMapping.from_dict(mapping)
        logger.info("[EventManager] Gamepad mapping updated")

    # - timer IO methods
    @classmethod
    def add_timer(cls, name: str, duration: float, repeat: bool = False) -> None:
        """
        Add a new timer.

        Args:
            - name (str): Name of the timer.
            - duration (float): Duration of the timer in seconds.
            - repeat (bool): Whether the timer should repeat.
        """
        cls._timers[name] = (duration, duration, repeat, False)
        logger.info(f"[EventManager] Timer '{name}' added: duration {duration}s, repeat={repeat}")

    @classmethod
    def kill_timer(cls, name: str) -> None:
        """
        Kill a timer.

        Args:
            - name (str): Name of the timer to kill.
        """
        if name in cls._timers:
            del cls._timers[name]
            logger.info(f"[EventManager] Timer '{name}' killed")
        else:
            logger.warning(f"[EventManager] Timer '{name}' not found to kill")

    @classmethod
    def has_timer(cls, name: str) -> bool:
        """
        Check if a timer exists.

        Args:
            - name (str): Name of the timer.

        Returns:
            - bool: True if timer exists, False otherwise.
        """
        return name in cls._timers

    @classmethod
    def pause_timers(cls) -> None:
        """
        Pause all timers.
        """
        cls._paused = True
        logger.info("[EventManager] All timers paused")

    @classmethod
    def resume_timers(cls) -> None:
        """
        Resume all timers.
        """
        cls._paused = False
        logger.info("[EventManager] All timers resumed")

    @classmethod
    def pause_timer(cls, name: str) -> None:
        """
        Pause a specific timer by name.
        """
        if name in cls._timers:
            time_left, original_duration, repeat, _ = cls._timers[name]
            cls._timers[name] = (time_left, original_duration, repeat, True)
            logger.info(f"[EventManager] Timer '{name}' paused")
        else:
            logger.warning(f"[EventManager] Timer '{name}' not found to pause")

    # class method to resume a specific timer
    @classmethod
    def resume_timer(cls, name: str) -> None:
        """
        Resume a specific paused timer.
        """
        if name in cls._timers:
            time_left, original_duration, repeat, _ = cls._timers[name]
            cls._timers[name] = (time_left, original_duration, repeat, False)
            logger.info(f"[EventManager] Timer '{name}' resumed")
        else:
            logger.warning(f"[EventManager] Timer '{name}' not found to resume")

    # - update method
    @classmethod
    def update(cls, dt: float) -> None:
        """
        Update the current key states.
        """
        # update key_state
        keys = key_state()
        kb_states = cls.key_mapping.serialize(keys)
        gp_states = cls.gamepad_mapping.serialize()

        merged: dict[str, KeyState] = {}
        for action, kb in kb_states.items():
            gp = gp_states.get(action, KeyState.RELEASED)
            # Merge precedence: PRESSED > HELD > RELEASED
            if KeyState.PRESSED in (kb, gp):
                merged[action] = KeyState.PRESSED
            elif KeyState.HELD in (kb, gp):
                merged[action] = KeyState.HELD
            else:
                merged[action] = KeyState.RELEASED

        cls.key_states = merged

        # update timers
        cls._triggered.clear()
        to_remove = []
        for name, (time_left, original_duration, repeat, paused) in cls._timers.items():
            if not cls._paused and not paused:
                time_left -= dt
            if time_left <= 0:
                logger.info(f"[EventManager] Timer '{name}' triggered")
                cls._triggered.add(name)
                if repeat:
                    cls._timers[name] = (original_duration, original_duration, repeat, paused)
                else:
                    to_remove.append(name)
            else:
                cls._timers[name] = (time_left, original_duration, repeat, paused)

        for name in to_remove:
            cls.kill_timer(name)

        logger.debug(f"[EventManager] Updated key states and timers with dt={dt}s")

    # - state access methods
    @classmethod
    def get_keys(cls) -> dict[str, KeyState]:
        """
        Get the current key states.

        Returns:
            - dict[str, KeyState]: Dictionary mapping action names to their current KeyState.
        """
        return cls.key_states

    @classmethod
    def get_timer(cls, name: str) -> bool:
        """
        Check if a timer was triggered this frame.

        Args:
            - name (str): Name of the timer to check.

        Returns:
            - bool: True if timer was triggered, False otherwise.
        """
        return name in cls._triggered

    @classmethod
    def get_timer_remaining(cls, name: str) -> float | None:
        """
        Get the remaining time of a timer.

        Args:
            - name (str): Name of the timer.

        Returns:
            - float | None: Remaining time in seconds, or None if timer does not exist.
        """
        if name in cls._timers:
            return cls._timers[name][0]
        return None

    # - reset method
    @classmethod
    def reset(cls) -> None:
        """
        Reset the EventManager to its initial state.
        """
        cls.key_states = {}
        cls._timers.clear()
        cls._triggered.clear()
        cls._paused = False
        logger.info("[EventManager] Reset to initial state")
