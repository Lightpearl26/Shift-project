#-*- coding: utf-8 -*-
#pylint: disable=broad-except

"""
SHIFT PROJECT game_libs
____________________________________________________________________________________________________
game_libs.managers.audio
version : 2.0
____________________________________________________________________________________________________
This Package contains the audio manager lib with channel management
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# Importing the pygame mixer module
from __future__ import annotations
from os import listdir
from os.path import join, splitext, isfile
from typing import TYPE_CHECKING
from pygame.mixer import init as mixer_init, set_num_channels
from pygame.mixer_music import (
    load as music_load,
    play as music_play,
    stop as music_stop,
    pause as music_pause,
    unpause as music_unpause,
    fadeout as music_fadeout,
    set_volume as music_set_volume,
    get_busy as music_get_busy
)

# Importing the AssetsCache for audio file management
from ..assets_cache import AssetsCache

# Importing config file
from .. import config

# Importing the logger
from .. import logger

if TYPE_CHECKING:
    from pygame.mixer import Sound, Channel

# ----- Audio Manager Class ----- #
class AudioManager:
    """
    Audio Manager Class
    """
    # protected class variables for volume levels
    _master_volume: float = 1.0
    _bgm_volume: float = 1.0
    _bgs_volume: float = 1.0
    _me_volume: float = 1.0
    _se_volume: float = 1.0

    # protected class variable for sounds cache
    _bgm: dict[str, str] = {}
    _bgs: dict[str, str] = {}
    _me: dict[str, str] = {}
    _se: dict[str, str] = {}

    # protected class variable for channels
    _bgs_channel: dict[str, list[Channel]] = {}
    _me_channel: dict[str, list[Channel]] = {}
    _se_channel: dict[str, list[Channel]] = {}

    # Current BGM state
    _current_bgm: str | None = None
    _bgm_paused: bool = False

    # ===== Volume Getters ===== #
    @classmethod
    def get_master_volume(cls) -> float:
        """Get the master volume level"""
        return cls._master_volume

    @classmethod
    def get_bgm_volume(cls) -> float:
        """Get the background music volume level"""
        return cls._bgm_volume

    @classmethod
    def get_bgs_volume(cls) -> float:
        """Get the background sounds volume level"""
        return cls._bgs_volume

    @classmethod
    def get_me_volume(cls) -> float:
        """Get the music effects volume level"""
        return cls._me_volume

    @classmethod
    def get_se_volume(cls) -> float:
        """Get the sound effects volume level"""
        return cls._se_volume

    # ===== Volume Setters ===== #
    @classmethod
    def set_master_volume(cls, volume: float) -> None:
        """
        Set the master volume level
        """
        cls._master_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.info(f"[AudioManager] Master volume set to {cls._master_volume}")

    @classmethod
    def set_bgm_volume(cls, volume: float) -> None:
        """
        Set the background music volume level
        """
        cls._bgm_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.info(f"[AudioManager] BGM volume set to {cls._bgm_volume}")

    @classmethod
    def set_bgs_volume(cls, volume: float) -> None:
        """
        Set the background sounds volume level
        """
        cls._bgs_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.info(f"[AudioManager] BGS volume set to {cls._bgs_volume}")

    @classmethod
    def set_me_volume(cls, volume: float) -> None:
        """
        Set the music effects volume level
        """
        cls._me_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.info(f"[AudioManager] ME volume set to {cls._me_volume}")

    @classmethod
    def set_se_volume(cls, volume: float) -> None:
        """
        Set the sound effects volume level
        """
        cls._se_volume = max(0.0, min(1.0, volume))
        cls._update_volumes()
        logger.info(f"[AudioManager] SE volume set to {cls._se_volume}")

    @classmethod
    def _update_volumes(cls) -> None:
        """
        Update all volumes based on the master volume and individual volumes
        """
        # Update BGM volume
        music_set_volume(cls._master_volume * cls._bgm_volume)

        # Update BGS channels volume
        for channels in cls._bgs_channel.values():
            for channel in channels:
                channel.set_volume(cls._master_volume * cls._bgs_volume)

        # Update ME channels volume
        for channels in cls._me_channel.values():
            for channel in channels:
                channel.set_volume(cls._master_volume * cls._me_volume)

        # Update SE channels volume
        for channels in cls._se_channel.values():
            for channel in channels:
                channel.set_volume(cls._master_volume * cls._se_volume)


    # ===== Initialization Methods ===== #
    @classmethod
    def init(cls,
             frequency: int = 44100,
             size: int = -16,
             channels: int = 2,
             buffer: int = 512) -> None:
        """
        Initialize the audio manager
        
        Args:
            frequency: Sample rate (Hz) - typically 22050 or 44100
            size: Bit size - 8, -16 (negative for signed)
            channels: Number of channels - 1 (mono) or 2 (stereo)
            buffer: Buffer size - smaller = less lag, larger = less CPU
        """
        try:
            mixer_init(frequency, size, channels, buffer)
            set_num_channels(32)  # Allow up to 32 simultaneous sounds
            logger.info(f"[AudioManager] Initialized: {frequency}Hz, {channels}ch, buffer={buffer}")

            # Auto-load audio files from assets folders
            cls._auto_load_audio_files()

        except Exception as e:
            logger.error(f"[AudioManager] Failed to initialize: {e}")

    @classmethod
    def _auto_load_audio_files(cls) -> None:
        """
        Automatically load all audio files from assets folders
        """
        # Load BGM files (musics)
        try:
            bgm_files = [f
                         for f in listdir(config.BGM_FOLDER)
                         if isfile(join(config.BGM_FOLDER, f))]
            for file in bgm_files:
                name, _ = splitext(file)
                filepath = join(config.BGM_FOLDER, file)
                cls._bgm[name] = filepath
            logger.info(f"[AudioManager] Loaded {len(bgm_files)} BGM files")
        except Exception as e:
            logger.error(f"[AudioManager] Failed to load BGM files: {e}")

        # Load BGS files (background sounds)
        try:
            bgs_files = [f
                         for f in listdir(config.BGS_FOLDER)
                         if isfile(join(config.BGS_FOLDER, f))]
            for file in bgs_files:
                name, _ = splitext(file)
                filepath = join(config.BGS_FOLDER, file)
                cls._bgs[name] = filepath
            logger.info(f"[AudioManager] Loaded {len(bgs_files)} BGS files")
        except Exception as e:
            logger.error(f"[AudioManager] Failed to load BGS files: {e}")

        # Load ME files (music effects)
        try:
            me_files = [f
                        for f in listdir(config.ME_FOLDER)
                        if isfile(join(config.ME_FOLDER, f))]
            for file in me_files:
                name, _ = splitext(file)
                filepath = join(config.ME_FOLDER, file)
                cls._me[name] = filepath
            logger.info(f"[AudioManager] Loaded {len(me_files)} ME files")
        except Exception as e:
            logger.error(f"[AudioManager] Failed to load ME files: {e}")

        # Load SE files (sound effects)
        try:
            se_files = [f
                        for f in listdir(config.SE_FOLDER)
                        if isfile(join(config.SE_FOLDER, f))]
            for file in se_files:
                name, _ = splitext(file)
                filepath = join(config.SE_FOLDER, file)
                cls._se[name] = filepath
            logger.info(f"[AudioManager] Loaded {len(se_files)} SE files")
        except Exception as e:
            logger.error(f"[AudioManager] Failed to load SE files: {e}")

    # ===== BGM Playback Methods ===== #
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
            music_load(cls._bgm[name])
            music_set_volume(cls._master_volume * cls._bgm_volume)
            if fadein_ms > 0:
                music_play(loops=loops, start=start, fade_ms=fadein_ms)
            else:
                music_play(loops=loops, start=start)
            cls._current_bgm = name
            cls._bgm_paused = False
            logger.debug(f"[AudioManager] Playing BGM: {name}")
        except Exception as e:
            logger.error(f"[AudioManager] Failed to play BGM '{name}': {e}")

    @classmethod
    def pause_bgm(cls) -> None:
        """Pause the currently playing BGM"""
        if music_get_busy() and not cls._bgm_paused:
            music_pause()
            cls._bgm_paused = True
            logger.debug("[AudioManager] BGM paused")

    @classmethod
    def resume_bgm(cls) -> None:
        """Resume the paused BGM"""
        if cls._bgm_paused:
            music_unpause()
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
            music_fadeout(fadeout_ms)
        else:
            music_stop()
        cls._current_bgm = None
        cls._bgm_paused = False
        logger.debug("[AudioManager] BGM stopped")

    @classmethod
    def is_bgm_playing(cls) -> bool:
        """Check if BGM is currently playing"""
        return music_get_busy() and not cls._bgm_paused

    # ===== BGS Playback Methods ===== #
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
            if name in cls._bgs_channel:
                cls.stop_bgs(name)
            
            sound: Sound = AssetsCache.load_sound(cls._bgs[name])
            channel = sound.play(loops=loops, fade_ms=fadein_ms)
            
            if channel:
                channel.set_volume(cls._master_volume * cls._bgs_volume)
                if name not in cls._bgs_channel:
                    cls._bgs_channel[name] = []
                cls._bgs_channel[name].append(channel)
                logger.debug(f"[AudioManager] Playing BGS: {name}")
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
        if name in cls._bgs_channel:
            for channel in cls._bgs_channel[name]:
                if channel and channel.get_busy():
                    if fadeout_ms > 0:
                        channel.fadeout(fadeout_ms)
                    else:
                        channel.stop()
            del cls._bgs_channel[name]
            logger.debug(f"[AudioManager] BGS stopped: {name}")

    @classmethod
    def stop_all_bgs(cls, fadeout_ms: int = 0) -> None:
        """Stop all background sounds"""
        for name in list(cls._bgs_channel.keys()):
            cls.stop_bgs(name, fadeout_ms)
        logger.debug("[AudioManager] All BGS stopped")

    # ===== ME Playback Methods ===== #
    @classmethod
    def play_me(cls, name: str, pause_bgm: bool = True) -> Channel | None:
        """
        Play a music effect
        
        Args:
            name: Name of the ME to play
            pause_bgm: Whether to temporarily pause BGM while ME plays
            
        Returns:
            The channel playing the sound, or None if failed
        """
        if name not in cls._me:
            logger.warning(f"[AudioManager] ME '{name}' not found")
            return None

        try:
            if pause_bgm and music_get_busy():
                cls.pause_bgm()

            sound: Sound = AssetsCache.load_sound(cls._me[name])
            channel = sound.play()

            if channel:
                channel.set_volume(cls._master_volume * cls._me_volume)
                if name not in cls._me_channel:
                    cls._me_channel[name] = []
                cls._me_channel[name].append(channel)
                logger.debug(f"[AudioManager] Playing ME: {name}")
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
        if name in cls._me_channel:
            for channel in cls._me_channel[name]:
                if channel and channel.get_busy():
                    if fadeout_ms > 0:
                        channel.fadeout(fadeout_ms)
                    else:
                        channel.stop()
            del cls._me_channel[name]
            logger.debug(f"[AudioManager] ME stopped: {name}")

    @classmethod
    def stop_all_me(cls, fadeout_ms: int = 0) -> None:
        """Stop all music effects"""
        for name in list(cls._me_channel.keys()):
            cls.stop_me(name, fadeout_ms)
        logger.debug("[AudioManager] All ME stopped")

    # ===== SE Playback Methods ===== #
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
                if name not in cls._se_channel:
                    cls._se_channel[name] = []
                cls._se_channel[name].append(channel)
                logger.debug(f"[AudioManager] Playing SE: {name}")
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
        if name in cls._se_channel:
            for channel in cls._se_channel[name]:
                if channel and channel.get_busy():
                    if fadeout_ms > 0:
                        channel.fadeout(fadeout_ms)
                    else:
                        channel.stop()
            del cls._se_channel[name]
            logger.debug(f"[AudioManager] SE stopped: {name}")

    @classmethod
    def stop_all_se(cls, fadeout_ms: int = 0) -> None:
        """Stop all sound effects"""
        for name in list(cls._se_channel.keys()):
            cls.stop_se(name, fadeout_ms)
        logger.debug("[AudioManager] All SE stopped")

    # ===== Utility Methods ===== #
    @classmethod
    def stop_all(cls, fadeout_ms: int = 0) -> None:
        """Stop all audio (BGM, BGS, ME, SE)"""
        cls.stop_bgm(fadeout_ms)
        cls.stop_all_bgs(fadeout_ms)
        cls.stop_all_me(fadeout_ms)
        cls.stop_all_se(fadeout_ms)
        logger.info("[AudioManager] All audio stopped")

    @classmethod
    def cleanup(cls) -> None:
        """Clean up finished channels"""
        # Clean BGS channels
        for name in list(cls._bgs_channel.keys()):
            cls._bgs_channel[name] = [ch for ch in cls._bgs_channel[name] if ch.get_busy()]
            if not cls._bgs_channel[name]:
                del cls._bgs_channel[name]

        # Clean ME channels
        for name in list(cls._me_channel.keys()):
            cls._me_channel[name] = [ch for ch in cls._me_channel[name] if ch.get_busy()]
            if not cls._me_channel[name]:
                del cls._me_channel[name]

        # Clean SE channels
        for name in list(cls._se_channel.keys()):
            cls._se_channel[name] = [ch for ch in cls._se_channel[name] if ch.get_busy()]
            if not cls._se_channel[name]:
                del cls._se_channel[name]
        
        logger.debug("[AudioManager] Cleaned up finished channels")
