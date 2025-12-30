#-*- coding: utf-8 -*-

"""
SHIFT PROJECT game_libs
____________________________________________________________________________________________________
game_libs.managers.event
version : 1.0
____________________________________________________________________________________________________
This Package contains the event manager lib
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# Importing the pygame event module
from __future__ import annotations
from pygame.key import ScancodeWrapper, get_pressed

# Importing config file
from .. import config

# Importing the logger
from .. import logger


# Create event mapping object
class EventMapping:
    """
    EventMapping class to map event names to key codes
    """

    # Define key mappings
    UP: set[int] = config.KEYS_UP
    DOWN: set[int] = config.KEYS_DOWN
    LEFT: set[int] = config.KEYS_LEFT
    RIGHT: set[int] = config.KEYS_RIGHT
    JUMP: set[int] = config.KEYS_JUMP
    SPRINT: set[int] = config.KEYS_SPRINT
    PAUSE: set[int] = config.KEYS_PAUSE

    @classmethod
    def from_dict(cls, mapping_dict: dict[str, set[int]]) -> EventMapping:
        """
        Create an EventMapping instance from a dictionary

        :param mapping_dict: A dictionary mapping event names to key code sets
        :return: An EventMapping instance
        """
        instance = cls()
        for key, value in mapping_dict.items():
            if hasattr(instance, key):
                setattr(instance, key, set(value))
            else:
                logger.warning(f"Unknown event mapping key: {key}")
        return instance

    def serialize(self, key_state: ScancodeWrapper) -> dict[str, bool]:
        """
        Serialize the current state of the event mappings based on the provided key state

        :param key_state: A ScancodeWrapper representing the current state of keys
        :return: A dictionary mapping event names to their pressed state (True/False)
        """
        return {
            "UP": any(key_state[key] for key in self.UP),
            "DOWN": any(key_state[key] for key in self.DOWN),
            "LEFT": any(key_state[key] for key in self.LEFT),
            "RIGHT": any(key_state[key] for key in self.RIGHT),
            "JUMP": any(key_state[key] for key in self.JUMP),
            "SPRINT": any(key_state[key] for key in self.SPRINT),
            "PAUSE": any(key_state[key] for key in self.PAUSE)
        }


# Create EventManager class
class EventManager:
    """
    EventManager class to manage game events
    """
    key_mappings: EventMapping = EventMapping()
    key_events: dict[str, bool] = {}

    @classmethod
    def load_key_mappings(cls, mapping_dict: dict[str, set[int]]):
        """
        Load key mappings from a dictionary

        :param mapping_dict: A dictionary mapping event names to key code sets
        """
        cls.key_mappings = EventMapping.from_dict(mapping_dict)
        logger.info("Key mappings loaded into EventManager")

    @classmethod
    def get_key_mappings(cls) -> EventMapping:
        """
        Get the current key mappings

        :return: The current EventMapping instance
        """
        return cls.key_mappings

    @classmethod
    def get_key_events(cls) -> dict[str, bool]:
        """
        Get the current key events state

        :return: A dictionary mapping event names to their pressed state (True/False)
        """
        return cls.key_events

    @classmethod
    def update(cls) -> None:
        """
        Update the key events based on the current key state
        """
        key_state = get_pressed()
        cls.key_events = cls.key_mappings.serialize(key_state)
        logger.debug(f"Key events updated: {cls.key_events}")
