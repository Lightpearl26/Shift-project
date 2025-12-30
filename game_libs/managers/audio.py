#-*- coding: utf-8 -*-

"""
SHIFT PROJECT game_libs
____________________________________________________________________________________________________
game_libs.managers.audio
version : 1.0
____________________________________________________________________________________________________
This Package contains the audio manager lib
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# Importing the pygame mixer module
from os.path import join
from pygame.mixer_music import (
    load,
    play,
    fadeout,
    set_volume
)
from pygame.mixer import Sound

# Importing the AssetsCache for audio file management
from ..assets_cache import AssetsCache

# Importing config file
from .. import config

# Importing the logger
from .. import logger

# Create utils functions
def setup_audio() -> None:
    """
    Setuping the audio manager with base files
    """
    # Load titlescreen audio
    AudioManager.load_bgm("Titlescreen", join(config.MUSICS_FOLDER, "titlescreen.ogg"))
    AudioManager.load_se("Cursor", join(config.SOUNDS_FOLDER, "cursor.wav"))
    AudioManager.load_se("Decision", join(config.SOUNDS_FOLDER, "decision.wav"))
    AudioManager.load_se("Cancel", join(config.SOUNDS_FOLDER, "cancel.wav"))

# Create AudioManager class
class AudioManager:
    """
    AudioManager class to manage audio playback
    """

    # Initialize volume levels
    _bgm_volume: float = 1.0
    _bgs_volume: float = 1.0
    _me_volume: float = 1.0
    _se_volume: float = 1.0

    # Initialize sounds and musics dictionaries
    bgm: dict[str, str] = {}
    bgs: dict[str, str] = {}
    me: dict[str, str] = {}
    se: dict[str, str] = {}

    # Create properties for volume control
    @property
    def bgm_volume(self) -> float:
        """
        Get the background music volume
        """
        return self._bgm_volume

    @bgm_volume.setter
    def bgm_volume(self, volume: float):
        """
        Set the background music volume
        """
        self._bgm_volume = max(0.0, min(1.0, volume))
        set_volume(self._bgm_volume)

    @property
    def bgs_volume(self) -> float:
        """
        Get the background sound volume
        """
        return self._bgs_volume

    @bgs_volume.setter
    def bgs_volume(self, volume: float):
        """
        Set the background sound volume
        """
        self._bgs_volume = max(0.0, min(1.0, volume))

    @property
    def me_volume(self) -> float:
        """
        Get the music effect volume
        """
        return self._me_volume

    @me_volume.setter
    def me_volume(self, volume: float):
        """
        Set the music effect volume
        """
        self._me_volume = max(0.0, min(1.0, volume))

    @property
    def se_volume(self) -> float:
        """
        Get the sound effect volume
        """
        return self._se_volume

    @se_volume.setter
    def se_volume(self, volume: float):
        """
        Set the sound effect volume
        """
        self._se_volume = max(0.0, min(1.0, volume))

    # Adding methods to load and store audio files
    @classmethod
    def load_bgm(cls, name: str, filepath: str):
        """
        Load a background music file
        """
        cls.bgm[name] = filepath

    @classmethod
    def load_bgs(cls, name: str, filepath: str):
        """
        Load a background sound file
        """
        cls.bgs[name] = filepath

    @classmethod
    def load_me(cls, name: str, filepath: str):
        """
        Load a music effect file
        """
        cls.me[name] = filepath

    @classmethod
    def load_se(cls, name: str, filepath: str):
        """
        Load a sound effect file
        """
        cls.se[name] = filepath

    # Adding methods to play audio files
    @classmethod
    def play_bgm(cls, name: str, loops: int = -1, start: float = 0.0):
        """
        Play a background music file
        """
        if name in cls.bgm:
            load(cls.bgm[name])
            set_volume(cls._bgm_volume)
            play(loops=loops, start=start)
        else:
            logger.warning(f"No Background Music (BGM) [{name}] found. Maybe load it before use")

    @classmethod
    def play_bgs(cls, name: str, loops: int = -1):
        """
        Play a background sound file
        """
        if name in cls.bgs:
            sound: Sound = AssetsCache.load_sound(cls.bgs[name])
            sound.set_volume(cls._bgs_volume)
            sound.play(loops=loops)
        else:
            logger.warning(f"No Background Sound (BGS) [{name}] found. Maybe load it before use")

    @classmethod
    def play_me(cls, name: str):
        """
        Play a music effect file
        """
        if name in cls.me:
            sound: Sound = AssetsCache.load_sound(cls.me[name])
            sound.set_volume(cls._me_volume)
            sound.play()
        else:
            logger.warning(f"No Music Effect (ME) [{name}] found. Maybe load it before use")

    @classmethod
    def play_se(cls, name: str):
        """
        Play a sound effect file
        """
        if name in cls.se:
            sound: Sound = AssetsCache.load_sound(cls.se[name])
            sound.set_volume(cls._se_volume)
            sound.play()
        else:
            logger.warning(f"No Sound Effect (SE) [{name}] found. Maybe load it before use")

    # Addinf methods to stop audio files
    @classmethod
    def stop_bgm(cls, fadeout_time: int = 500) -> None:
        """
        Fadeout the bgm then stop it
        """
        fadeout(fadeout_time)

    @classmethod
    def stop_bgs(cls, name: str, fadeout_time: int = 500) -> None:
        """
        Fadeout the bgs then stop it
        """
        if name in cls.bgs:
            bgs: Sound = AssetsCache.load_sound(cls.bgs[name])
            bgs.fadeout(fadeout_time)
        else:
            logger.warning(f"No Background Sound (BGS) [{name}] found. Maybe load it before use")
