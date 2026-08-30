from __future__ import annotations

import pygame

from src.core.assets import AssetManager


class AudioManager:
    """Small audio facade that keeps the game playable without an audio device."""

    MUSIC_END_EVENT = pygame.USEREVENT + 17
    TYPING_MAXTIME_MS = 120
    MUSIC_PATHS = {
        "menu": "music/menu.mp3",
        "audit_1": "music/audit_1.mp3",
        "audit_2": "music/audit_2.mp3",
    }
    SOUND_PATHS = {
        "click": "sfx/retro_click.mp3",
        "toggle": "sfx/retro_click_alt.mp3",
        "document": "sfx/ui_click.wav",
        "typing": "sfx/retro_typing.mp3",
        "forward": "sfx/transition_forward.mp3",
        "back": "sfx/transition_back.mp3",
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
        self.music_sequence: tuple[str, ...] = ()
        self.music_index = 0
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
        self.play_music_sequence(("menu",), fade_ms=700)

    def play_music_sequence(self, names: tuple[str, ...], *, fade_ms: int = 500) -> None:
        if not self.enabled or not names:
            return
        if names == self.music_sequence and pygame.mixer.music.get_busy():
            return
        self.music_sequence = names
        self.music_index = 0
        self._start_current_music(fade_ms)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type != self.MUSIC_END_EVENT:
            return False
        if self.enabled and self.music_sequence:
            self.music_index = (self.music_index + 1) % len(self.music_sequence)
            self._start_current_music(180)
        return True

    def _start_current_music(self, fade_ms: int) -> None:
        music_name = self.music_sequence[self.music_index]
        relative_path = self.MUSIC_PATHS.get(music_name)
        if relative_path is None:
            return
        music_path = self.assets.assets_root / relative_path
        if not music_path.is_file():
            return
        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)
            pygame.mixer.music.play(0, fade_ms=fade_ms)
        except pygame.error:
            self.music_sequence = ()

    def play(
        self,
        name: str,
        volume: float = 1.0,
        *,
        maxtime_ms: int = 0,
    ) -> None:
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        try:
            if name in {"click", "toggle", "typing"}:
                sound.stop()
            effective_maxtime = maxtime_ms
            if name == "typing" and effective_maxtime <= 0:
                effective_maxtime = self.TYPING_MAXTIME_MS
            channel = sound.play(maxtime=max(0, effective_maxtime))
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
            pygame.mixer.music.set_endevent()
            pygame.mixer.music.fadeout(350)
