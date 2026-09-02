from __future__ import annotations

from pathlib import Path

import pygame
from PIL import Image, ImageEnhance, ImageOps

from src.core.assets import AssetManager


class ScreenEffect:
    """Subtle static monitor texture that never resamples the rendered UI."""

    TEXTURES = {
        "crt": "vendor_local/screen_effects/crt.png",
        "vhs": "vendor_local/screen_effects/vhs.png",
    }
    MAX_ALPHA = {"crt": 12, "vhs": 15}

    def __init__(self, assets: AssetManager) -> None:
        self.assets = assets
        self._cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}

    def apply(self, surface: pygame.Surface, mode: str, rect: pygame.Rect) -> None:
        if mode == "off" or rect.width <= 0 or rect.height <= 0:
            return
        surface.blit(self._overlay(mode, rect.size), rect.topleft)

    def _overlay(self, mode: str, size: tuple[int, int]) -> pygame.Surface:
        key = (mode, size)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        relative_path = self.TEXTURES.get(mode)
        texture_path = self.assets.assets_root / relative_path if relative_path else Path()
        if relative_path and texture_path.is_file():
            overlay = self._texture_overlay(texture_path, size, self.MAX_ALPHA[mode])
        else:
            overlay = self._procedural_overlay(size, mode)
        self._cache[key] = overlay
        return overlay

    @staticmethod
    def _texture_overlay(path: Path, size: tuple[int, int], max_alpha: int) -> pygame.Surface:
        with Image.open(path) as source:
            grayscale = ImageOps.grayscale(source)
            grayscale = ImageEnhance.Contrast(grayscale).enhance(1.35)
            grayscale = grayscale.resize(size, Image.Resampling.BILINEAR)
            alpha = grayscale.point(
                lambda value: round((255 - value) * max_alpha / 255)
            )
            rgba = Image.new("RGBA", size, (0, 0, 0, 0))
            rgba.putalpha(alpha)
            return pygame.image.frombytes(rgba.tobytes(), size, "RGBA").convert_alpha()

    @staticmethod
    def _procedural_overlay(size: tuple[int, int], mode: str) -> pygame.Surface:
        overlay = pygame.Surface(size, pygame.SRCALPHA)
        spacing = 4 if mode == "crt" else 7
        alpha = 10 if mode == "crt" else 7
        for y in range(0, size[1], spacing):
            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (size[0], y))
        return overlay
