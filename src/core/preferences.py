from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from src.core.settings import USER_SETTINGS_PATH


RESOLUTIONS_BY_ASPECT: dict[str, tuple[tuple[int, int], ...]] = {
    "16:9": ((1280, 720), (1600, 900), (1920, 1080)),
    "16:10": ((1280, 800), (1440, 900), (1680, 1050)),
    "4:3": ((1024, 768), (1280, 960), (1600, 1200)),
}
DISPLAY_MODES = ("windowed", "fullscreen")
SCREEN_FILTERS = ("off", "crt", "vhs")


@dataclass
class UserPreferences:
    """Player-owned display and audio settings persisted between sessions."""

    aspect_ratio: str = "16:9"
    resolution: tuple[int, int] = (1280, 720)
    display_mode: str = "windowed"
    screen_filter: str = "crt"
    music_volume: float = 0.2
    sfx_volume: float = 0.75

    def copy(self) -> UserPreferences:
        return replace(self)

    def normalize(self) -> None:
        if self.aspect_ratio not in RESOLUTIONS_BY_ASPECT:
            self.aspect_ratio = "16:9"

        options = RESOLUTIONS_BY_ASPECT[self.aspect_ratio]
        self.resolution = tuple(self.resolution)
        if self.resolution not in options:
            self.resolution = options[0]

        if self.display_mode not in DISPLAY_MODES:
            self.display_mode = "windowed"

        if self.screen_filter not in SCREEN_FILTERS:
            self.screen_filter = "crt"

        self.music_volume = max(0.0, min(1.0, float(self.music_volume)))
        self.sfx_volume = max(0.0, min(1.0, float(self.sfx_volume)))

    def save(self, path: Path = USER_SETTINGS_PATH) -> None:
        self.normalize()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["resolution"] = list(self.resolution)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path = USER_SETTINGS_PATH) -> UserPreferences:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            preferences = cls(
                aspect_ratio=payload.get("aspect_ratio", "16:9"),
                resolution=tuple(payload.get("resolution", (1280, 720))),
                display_mode=payload.get("display_mode", "windowed"),
                screen_filter=payload.get("screen_filter", "crt"),
                music_volume=payload.get("music_volume", 0.2),
                sfx_volume=payload.get("sfx_volume", 0.75),
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            preferences = cls()

        try:
            preferences.normalize()
        except (TypeError, ValueError):
            preferences = cls()
        return preferences
