from __future__ import annotations

import pygame

from src.core.assets import AssetManager


class AudioManager:
    """Small audio facade that keeps the game playable without an audio device."""

    SOUND_PATHS = {
        "click": "sfx/ui_click.wav",
        "paper": "sfx/paper_flip.wav",
        "stamp": "sfx/stamp.wav",
        "hint": "sfx/hint.wav",
        "confirm": "sfx/confirm.wav",
        "scroll": "sfx/scroll.wav",
    }

    def __init__(self, assets: AssetManager) -> None:
        self.assets = assets
        self.enabled = False
        self.music_volume = 0.2
        self.sfx_volume = 0.75
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self._start_mixer()
        if self.enabled:
            self._load_sounds()

    def _start_mixer(self) -> None:
        if pygame.mixer.get_init() is not None:
            self.enabled = True
            return
        try:
            pygame.mixer.init(frequency=44_100, size=-16, channels=1, buffer=512)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def _load_sounds(self) -> None:
        for name, asset_path in self.SOUND_PATHS.items():
            try:
                self.sounds[name] = self.assets.load_sound(asset_path)
            except (FileNotFoundError, pygame.error):
                continue

    def start_music(self) -> None:
        if not self.enabled:
            return
        music_path = self.assets.assets_root / "music" / "audit_ambient.wav"
        if not music_path.is_file():
            return
        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1, fade_ms=800)
        except pygame.error:
            self.enabled = False

    def play(self, name: str, volume: float = 1.0) -> None:
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        try:
            channel = sound.play()
            if channel is not None:
                channel.set_volume(max(0.0, min(1.0, volume * self.sfx_volume)))
        except pygame.error:
            pass

    def set_music_volume(self, volume: float) -> None:
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, volume))

    def stop(self) -> None:
        if self.enabled:
            pygame.mixer.music.fadeout(350)
