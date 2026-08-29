from __future__ import annotations

from pathlib import Path

import pygame


class AssetManager:
    """Centralized asset loader with simple per-type caches."""

    def __init__(self, assets_root: Path) -> None:
        self.assets_root = assets_root.resolve()
        self._image_cache: dict[Path, pygame.Surface] = {}
        self._sound_cache: dict[Path, pygame.mixer.Sound] = {}
        self._font_cache: dict[tuple[Path, int], pygame.font.Font] = {}

    def load_image(self, relative_path: str | Path, *, alpha: bool = True) -> pygame.Surface:
        path = self._resolve_asset_path(relative_path)

        if path in self._image_cache:
            return self._image_cache[path]

        image = pygame.image.load(path)
        image = image.convert_alpha() if alpha else image.convert()
        self._image_cache[path] = image
        return image

    def load_sound(self, relative_path: str | Path) -> pygame.mixer.Sound:
        path = self._resolve_asset_path(relative_path)

        if path not in self._sound_cache:
            self._sound_cache[path] = pygame.mixer.Sound(path)

        return self._sound_cache[path]

    def load_font(self, relative_path: str | Path, size: int) -> pygame.font.Font:
        path = self._resolve_asset_path(relative_path)
        cache_key = (path, size)

        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = pygame.font.Font(path, size)

        return self._font_cache[cache_key]

    def _resolve_asset_path(self, relative_path: str | Path) -> Path:
        path = (self.assets_root / relative_path).resolve()

        try:
            path.relative_to(self.assets_root)
        except ValueError as exc:
            raise ValueError(f"Asset path escapes assets directory: {relative_path}") from exc

        if not path.is_file():
            raise FileNotFoundError(
                f"Asset not found: {relative_path!s} "
                f"(resolved to {path})"
            )

        return path
