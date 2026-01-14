# -*- coding : utf-8 -*-
#pylint: disable=broad-except

"""
game_libs.managers.audio
___________________________________________________________________________________________________
File infos:

    - Author: Franck Lafiteau
    - Version: 2.0
___________________________________________________________________________________________________
Description:
    This module manages audio functionalities for the game,
    including loading, playing, and controlling sound effects
    and background music using the pygame library.
___________________________________________________________________________________________________
@copyright: Franck Lafiteau 2026
"""

# Import os module
from os.path import join
from os import listdir

# Import pygame mixer objects
from pygame.mixer import (
    Sound,
    Channel,
    init as mixer_init,
    set_num_channels,
    pause as pause_mixer,
    unpause as unpause_mixer,
)
from pygame.mixer_music import (
    load as load_music,
    play as play_music,
    fadeout as fadeout_music,
    set_volume as set_music_volume,
    pause as pause_music,
    unpause as unpause_music,
    get_busy as busy_music,
    stop as stop_music,
)

# Import AssetsCache
from ..assets_cache import AssetsCache

# Import config
from .. import config

# Import logger
from .. import logger


# ----- AudioManager class ----- #
class AudioManager:
    """
    AudioManager object
    
    This object represent the audio manager of the game
    
    Properties (classmethods):
        busy (bool): Check if any audio is currently playing
        master_volume (float): Master volume
        bgm_volume (float): Background music volume
        bgs_volume (float): Background sounds volume
        me_volume (float): Music effects volume
        se_volume (float): Sound effects volume
    Methods:
        set_master_volume(volume: float) -> None
        set_bgm_volume(volume: float) -> None
        set_bgs_volume(volume: float) -> None
        set_me_volume(volume: float) -> None
        set_se_volume(volume: float) -> None
        load_bgm(name: str, path: str) -> None
        load_bgs(name: str, path: str) -> None
        load_me(name: str, path: str) -> None
        load_se(name: str, path: str) -> None
        play_bgm(name: str, loops: int = -1, start: float = 0.0, fadein_ms: int = 0) -> None
        pause_bgm() -> None
        resume_bgm() -> None
        stop_bgm(fadeout_ms: int = 0) -> None
        is_bgm_playing() -> bool
        play_bgs(name: str, loops: int = -1, fadein_ms: int = 0) -> Channel | None
        stop_bgs(name: str, fadeout_ms: int = 0) -> None
        stop_all_bgs(fadeout_ms: int = 0) -> None
        play_me(name: str, pause_bgm: bool = True) -> Channel | None
        stop_me(name: str, fadeout_ms: int = 0) -> None
        stop_all_me(fadeout_ms: int = 0) -> None
        play_se(name: str, volume_modifier: float = 1.0) -> Channel | None
        stop_se(name: str, fadeout_ms: int = 0) -> None
        stop_all_se(fadeout_ms: int = 0) -> None
        stop_all(fadeout_ms: int = 0) -> None
        init(frequency: int = 44100, size: int = -16, channels: int = 2, buffer: int = 512) -> None
        update() -> None
    """
    # volume attributes
    _master_volume: float = 1.0
    _bgm_volume: float = 1.0
    _bgs_volume: float = 1.0
    _me_volume: float = 1.0
    _se_volume: float = 1.0

    # sounds dictionnaries
    _bgm: dict[str, str] = {}
    _bgs: dict[str, str] = {}
    _me: dict[str, str] = {}
    _se: dict[str, str] = {}

    # channel tracking for memory management (support multiple concurrent plays per sound)
    _bgs_channels: dict[str, list[Channel]] = {}
    _me_channels: dict[str, list[Channel]] = {}
    _se_channels: dict[str, list[Channel]] = {}

    # audio state
    _bgm_paused: bool = False
    _current_bgm: str | None = None

    # protected methods
    @classmethod
    def _update_volumes(cls) -> None:
        """
        Update all volumes based on master volume and individual volumes
        """
        set_music_volume(cls._bgm_volume * cls._master_volume)
        for channels in cls._bgs_channels.values():
            for channel in channels:
                channel.set_volume(cls._bgs_volume * cls._master_volume)
        for channels in cls._me_channels.values():
            for channel in channels:
                channel.set_volume(cls._me_volume * cls._master_volume)
        for channels in cls._se_channels.values():
            for channel in channels:
                channel.set_volume(cls._se_volume * cls._master_volume)

    # busy properties
    @classmethod
    def busy(cls) -> bool:
        """
        Check if any audio is currently playing
        
        Returns:
            : bool: True if any audio is playing, False otherwise
        """
        if busy_music():
            return True
        for channels in cls._bgs_channels.values():
            for channel in channels:
                if channel.get_busy():
                    return True
        for channels in cls._me_channels.values():
            for channel in channels:
                if channel.get_busy():
                    return True
        for channels in cls._se_channels.values():
            for channel in channels:
                if channel.get_busy():
                    return True
        return False

    # volume properties
    @classmethod
    def master_volume(cls) -> float:
        """
        Get the master volume
        
        Returns:
            : float: Master volume
        """
        return cls._master_volume

    @classmethod
    def bgm_volume(cls) -> float:
        """
        Get the background music volume
        
        Returns:
            : float: Background music volume
        """
        return cls._bgm_volume

    @classmethod
    def bgs_volume(cls) -> float:
        """
        Get the background sounds volume
        
        Returns:
            : float: Background sounds volume
        """
        return cls._bgs_volume

    @classmethod
    def me_volume(cls) -> float:
        """
        Get the music effects volume
        
        Returns:
            : float: Music effects volume
        """
        return cls._me_volume

    @classmethod
    def se_volume(cls) -> float:
        """
        Get the sound effects volume
        
        Returns:
            : float: Sound effects volume
        """
        return cls._se_volume

    # class methods to control volumes
    @classmethod
    def set_master_volume(cls, volume: float) -> None:
        """
        Set the master volume
        
        Args:
            : volume (float): Master volume (0.0 to 1.0)
        """
        cls._master_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.debug(f"[AudioManager] Set master volume to {cls._master_volume}")

    @classmethod
    def set_bgm_volume(cls, volume: float) -> None:
        """
        Set the background music volume
        
        Args:
            : volume (float): Background music volume (0.0 to 1.0)
        """
        cls._bgm_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.debug(f"[AudioManager] Set BGM volume to {cls._bgm_volume}")

    @classmethod
    def set_bgs_volume(cls, volume: float) -> None:
        """
        Set the background sounds volume
        
        Args:
            : volume (float): Background sounds volume (0.0 to 1.0)
        """
        cls._bgs_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.debug(f"[AudioManager] Set BGS volume to {cls._bgs_volume}")

    @classmethod
    def set_me_volume(cls, volume: float) -> None:
        """
        Set the music effects volume
        
        Args:
            : volume (float): Music effects volume (0.0 to 1.0)
        """
        cls._me_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.debug(f"[AudioManager] Set ME volume to {cls._me_volume}")

    @classmethod
    def set_se_volume(cls, volume: float) -> None:
        """
        Set the sound effects volume
        
        Args:
            : volume (float): Sound effects volume (0.0 to 1.0)
        """
        cls._se_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.debug(f"[AudioManager] Set SE volume to {cls._se_volume}")

    # class methods to load audio files
    @classmethod
    def load_bgm(cls, name: str, path: str) -> None:
        """
        Load a background music file
        
        Args:
            : name (str): Name of the background music
            : path (str): Path to the background music file
        """
        cls._bgm[name] = path
        logger.info(f"[AudioManager] Loaded BGM <{name}> from path '{path}'")

    @classmethod
    def load_bgs(cls, name: str, path: str) -> None:
        """
        Load a background sound file
        
        Args:
            : name (str): Name of the background sound
            : path (str): Path to the background sound file
        """
        cls._bgs[name] = path
        logger.info(f"[AudioManager] Loaded BGS <{name}> from path '{path}'")

    @classmethod
    def load_me(cls, name: str, path: str) -> None:
        """
        Load a music effect file
        
        Args:
            : name (str): Name of the music effect
            : path (str): Path to the music effect file
        """
        cls._me[name] = path
        logger.info(f"[AudioManager] Loaded ME <{name}> from path '{path}'")

    @classmethod
    def load_se(cls, name: str, path: str) -> None:
        """
        Load a sound effect file
        
        Args:
            : name (str): Name of the sound effect
            : path (str): Path to the sound effect file
        """
        cls._se[name] = path
        logger.info(f"[AudioManager] Loaded SE <{name}> from path '{path}'")

    # - BGM playback methods
    @classmethod
    def play_bgm(cls, name: str, loops: int = -1, start: float = 0.0, fadein_ms: int = 0) -> None:
        """
        Play a background music file
        
        Args:
            name: Name of the BGM to play
            loops: Number of loops (-1 for infinite)
            start: Starting position in seconds
            fadein_ms: Fade in duration in milliseconds
        """
        if name not in cls._bgm:
            logger.warning(f"[AudioManager] BGM '{name}' not found")
            return

        try:
            load_music(cls._bgm[name])
            set_music_volume(cls._master_volume * cls._bgm_volume)
            if fadein_ms > 0:
                play_music(loops=loops, start=start, fade_ms=fadein_ms)
            else:
                play_music(loops=loops, start=start)
            cls._current_bgm = name
            cls._bgm_paused = False
            logger.info(f"[AudioManager] Playing BGM: {name}")
        except Exception as e:
            logger.error(f"[AudioManager] Failed to play BGM '{name}': {e}")

    @classmethod
    def pause_bgm(cls) -> None:
        """Pause the currently playing BGM"""
        if cls.is_bgm_playing():
            pause_music()
            cls._bgm_paused = True
            logger.debug("[AudioManager] BGM paused")

    @classmethod
    def resume_bgm(cls) -> None:
        """Resume the paused BGM"""
        if cls._bgm_paused:
            unpause_music()
            cls._bgm_paused = False
            logger.debug("[AudioManager] BGM resumed")

    @classmethod
    def stop_bgm(cls, fadeout_ms: int = 0) -> None:
        """
        Stop the currently playing BGM
        
        Args:
            fadeout_ms: Fadeout duration in milliseconds
        """
        if fadeout_ms > 0:
            fadeout_music(fadeout_ms)
        else:
            stop_music()
        cls._current_bgm = None
        cls._bgm_paused = False
        logger.info("[AudioManager] BGM stopped")

    @classmethod
    def is_bgm_playing(cls) -> bool:
        """Check if BGM is currently playing"""
        return busy_music() and not cls._bgm_paused

    # - BGS playback methods
    @classmethod
    def play_bgs(cls, name: str, loops: int = -1, fadein_ms: int = 0) -> Channel | None:
        """
        Play a background sound file
        
        Args:
            name: Name of the BGS to play
            loops: Number of loops (-1 for infinite)
            fadein_ms: Fade in duration in milliseconds
            
        Returns:
            The channel playing the sound, or None if failed
        """
        if name not in cls._bgs:
            logger.warning(f"[AudioManager] BGS '{name}' not found")
            return None

        try:
            # Stop existing BGS with same name
            if name in cls._bgs_channels:
                cls.stop_bgs(name)

            sound: Sound = AssetsCache.load_sound(cls._bgs[name])
            channel = sound.play(loops=loops, fade_ms=fadein_ms)

            if channel:
                channel.set_volume(cls._master_volume * cls._bgs_volume)
                if name not in cls._bgs_channels:
                    cls._bgs_channels[name] = []
                cls._bgs_channels[name].append(channel)
                logger.info(f"[AudioManager] Playing BGS: {name}")
                return channel
            else:
                logger.warning(f"[AudioManager] No available channel for BGS '{name}'")
                return None
        except Exception as e:
            logger.error(f"[AudioManager] Failed to play BGS '{name}': {e}")
            return None

    @classmethod
    def stop_bgs(cls, name: str, fadeout_ms: int = 0) -> None:
        """
        Stop a background sound
        
        Args:
            name: Name of the BGS to stop
            fadeout_ms: Fadeout duration in milliseconds
        """
        if name in cls._bgs_channels:
            for channel in cls._bgs_channels[name]:
                if channel and channel.get_busy():
                    if fadeout_ms > 0:
                        channel.fadeout(fadeout_ms)
                    else:
                        channel.stop()
            del cls._bgs_channels[name]
            logger.info(f"[AudioManager] BGS stopped: {name}")

    @classmethod
    def stop_all_bgs(cls, fadeout_ms: int = 0) -> None:
        """Stop all background sounds"""
        for name in list(cls._bgs_channels.keys()):
            cls.stop_bgs(name, fadeout_ms)
        logger.debug("[AudioManager] All BGS stopped")

    # - ME playback methods
    @classmethod
    def play_me(cls, name: str, pause_bgm: bool = True) -> Channel | None:
        """
        Play a music effect
        
        Args:
            name: Name of the ME to play
            pause_bgm: Whether to temporarily pause BGM while ME plays
                       It won't resume BGM after ME ends, caller must handle that.
            
        Returns:
            The channel playing the sound, or None if failed
        """
        if name not in cls._me:
            logger.warning(f"[AudioManager] ME '{name}' not found")
            return None

        try:
            if pause_bgm and busy_music():
                cls.pause_bgm()

            sound: Sound = AssetsCache.load_sound(cls._me[name])
            channel = sound.play()

            if channel:
                channel.set_volume(cls._master_volume * cls._me_volume)
                if name not in cls._me_channels:
                    cls._me_channels[name] = []
                cls._me_channels[name].append(channel)
                logger.info(f"[AudioManager] Playing ME: {name}")
                return channel
            else:
                logger.warning(f"[AudioManager] No available channel for ME '{name}'")
                return None
        except Exception as e:
            logger.error(f"[AudioManager] Failed to play ME '{name}': {e}")
            return None

    @classmethod
    def stop_me(cls, name: str, fadeout_ms: int = 0) -> None:
        """
        Stop a music effect
        
        Args:
            name: Name of the ME to stop
            fadeout_ms: Fadeout duration in milliseconds
        """
        if name in cls._me_channels:
            for channel in cls._me_channels[name]:
                if channel and channel.get_busy():
                    if fadeout_ms > 0:
                        channel.fadeout(fadeout_ms)
                    else:
                        channel.stop()
            del cls._me_channels[name]
            logger.info(f"[AudioManager] ME stopped: {name}")

    @classmethod
    def stop_all_me(cls, fadeout_ms: int = 0) -> None:
        """Stop all music effects"""
        for name in list(cls._me_channels.keys()):
            cls.stop_me(name, fadeout_ms)
        logger.debug("[AudioManager] All ME stopped")

    # - SE playback methods
    @classmethod
    def play_se(cls, name: str, volume_modifier: float = 1.0) -> Channel | None:
        """
        Play a sound effect
        
        Args:
            name: Name of the SE to play
            volume_modifier: Multiply SE volume by this value (0.0 to 1.0)
            
        Returns:
            The channel playing the sound, or None if failed
        """
        if name not in cls._se:
            logger.warning(f"[AudioManager] SE '{name}' not found")
            return None

        try:
            sound: Sound = AssetsCache.load_sound(cls._se[name])
            channel = sound.play()

            if channel:
                final_volume = cls._master_volume * cls._se_volume * max(0.0, min(1.0, volume_modifier))
                channel.set_volume(final_volume)
                if name not in cls._se_channels:
                    cls._se_channels[name] = []
                cls._se_channels[name].append(channel)
                logger.info(f"[AudioManager] Playing SE: {name}")
                return channel
            else:
                logger.debug(f"[AudioManager] No available channel for SE '{name}'")
                return None
        except Exception as e:
            logger.error(f"[AudioManager] Failed to play SE '{name}': {e}")
            return None

    @classmethod
    def stop_se(cls, name: str, fadeout_ms: int = 0) -> None:
        """
        Stop a sound effect
        
        Args:
            name: Name of the SE to stop
            fadeout_ms: Fadeout duration in milliseconds
        """
        if name in cls._se_channels:
            for channel in cls._se_channels[name]:
                if channel and channel.get_busy():
                    if fadeout_ms > 0:
                        channel.fadeout(fadeout_ms)
                    else:
                        channel.stop()
            del cls._se_channels[name]
            logger.info(f"[AudioManager] SE stopped: {name}")

    @classmethod
    def stop_all_se(cls, fadeout_ms: int = 0) -> None:
        """Stop all sound effects"""
        for name in list(cls._se_channels.keys()):
            cls.stop_se(name, fadeout_ms)
        logger.debug("[AudioManager] All SE stopped")

    # class methods to control all audio
    @classmethod
    def pause_all(cls) -> None:
        """Pause all audio (BGM and sound channels)"""
        cls.pause_bgm()
        pause_mixer()
        logger.info("[AudioManager] All audio paused")

    @classmethod
    def resume_all(cls) -> None:
        """Resume all paused audio"""
        cls.resume_bgm()
        unpause_mixer()
        logger.info("[AudioManager] All audio resumed")

    @classmethod
    def stop_all(cls, fadeout_ms: int = 0) -> None:
        """Stop all audio (BGM, BGS, ME, SE)"""
        cls.stop_bgm(fadeout_ms)
        cls.stop_all_bgs(fadeout_ms)
        cls.stop_all_me(fadeout_ms)
        cls.stop_all_se(fadeout_ms)
        logger.info("[AudioManager] All audio stopped")

    # class method to initialize the audio manager
    @classmethod
    def init(cls,
             frequency: int = 44100,
             size: int = -16,
             channels: int = 2,
             buffer: int = 512) -> None:
        """
        Initialize the AudioManager and loading audio files from config
        """
        try:
            mixer_init(frequency, size, channels, buffer)
            set_num_channels(32)  # Set number of channels for concurrent sounds
            logger.debug("[AudioManager] Pygame mixer initialized")
            # Valid audio extensions
            valid_extensions = ('.mp3', '.ogg', '.wav', '.flac', '.mod', '.it', '.xm', '.s3m')

            # Loading all available BGM files
            try:
                for bgm in listdir(join(config.AUDIO_FOLDER, "bgm")):
                    if bgm.lower().endswith(valid_extensions):
                        filename = bgm.rsplit(".", 1)[0]
                        cls.load_bgm(filename, join(config.AUDIO_FOLDER, "bgm", bgm))
            except FileNotFoundError:
                logger.warning("[AudioManager] BGM folder not found, skipping BGM loading")

            # Loading all available BGS files
            try:
                for bgs in listdir(join(config.AUDIO_FOLDER, "bgs")):
                    if bgs.lower().endswith(valid_extensions):
                        filename = bgs.rsplit(".", 1)[0]
                        cls.load_bgs(filename, join(config.AUDIO_FOLDER, "bgs", bgs))
            except FileNotFoundError:
                logger.warning("[AudioManager] BGS folder not found, skipping BGS loading")

            # Loading all available ME files
            try:
                for me in listdir(join(config.AUDIO_FOLDER, "me")):
                    if me.lower().endswith(valid_extensions):
                        filename = me.rsplit(".", 1)[0]
                        cls.load_me(filename, join(config.AUDIO_FOLDER, "me", me))
            except FileNotFoundError:
                logger.warning("[AudioManager] ME folder not found, skipping ME loading")

            # Loading all available SE files
            try:
                for se in listdir(join(config.AUDIO_FOLDER, "se")):
                    if se.lower().endswith(valid_extensions):
                        filename = se.rsplit(".", 1)[0]
                        cls.load_se(filename, join(config.AUDIO_FOLDER, "se", se))
            except FileNotFoundError:
                logger.warning("[AudioManager] SE folder not found, skipping SE loading")

            logger.info("[AudioManager] AudioManager initialized")

        except Exception as e:
            logger.error(f"[AudioManager] Failed to initialize Pygame mixer: {e}")

    # class method to update the audio manager
    @classmethod
    def update(cls) -> None:
        """
        Update the AudioManager - Clean up finished sounds and manage audio state
        """
        # Clean up finished BGS channels
        for name, channels in list(cls._bgs_channels.items()):
            cls._bgs_channels[name] = [c for c in channels if c.get_busy()]
            if not cls._bgs_channels[name]:
                del cls._bgs_channels[name]
                logger.debug(f"[AudioManager] Cleaned up finished BGS <{name}>")

        # Clean up finished ME channels
        for name, channels in list(cls._me_channels.items()):
            cls._me_channels[name] = [c for c in channels if c.get_busy()]
            if not cls._me_channels[name]:
                del cls._me_channels[name]
                logger.debug(f"[AudioManager] Cleaned up finished ME <{name}>")

        # Clean up finished SE channels
        for name, channels in list(cls._se_channels.items()):
            cls._se_channels[name] = [c for c in channels if c.get_busy()]
            if not cls._se_channels[name]:
                del cls._se_channels[name]
                logger.debug(f"[AudioManager] Cleaned up finished SE <{name}>")
