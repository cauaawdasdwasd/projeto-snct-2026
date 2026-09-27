"""VERIFY-9: the rogue security AI. Drawn in code, replaced by art when available."""

from __future__ import annotations

import math
from pathlib import Path

import pygame

from src.minigames.common import load_optional_image

MOODS = ("neutral", "suspicious", "angry", "happy")
MOOD_COLORS = {
    "neutral": (110, 230, 120),
    "suspicious": (237, 193, 91),
    "angry": (224, 82, 67),
    "happy": (110, 220, 230),
}


class Verify9:
    """Draws the avatar at any size; uses assets/captcha/verify9/verify9_<mood>.png if present."""

    def __init__(self, assets_root: Path) -> None:
        self.images: dict[str, pygame.Surface | None] = {
            mood: load_optional_image(assets_root, f"captcha/verify9/verify9_{mood}.png") for mood in MOODS
        }

    def draw(self, surface: pygame.Surface, center: tuple[int, int], size: int, mood: str = "neutral", time: float = 0.0) -> None:
        image = self.images.get(mood) or self.images.get("neutral")
        if image is not None:
            scaled = pygame.transform.smoothscale(image, (size, size))
            surface.blit(scaled, scaled.get_rect(center=center))
            return
        color = MOOD_COLORS.get(mood, MOOD_COLORS["neutral"])
        cx, cy = center
        radius = size // 2
        hexagon = [
            (cx + math.cos(math.radians(60 * i + 30)) * radius, cy + math.sin(math.radians(60 * i + 30)) * radius)
            for i in range(6)
        ]
        pygame.draw.polygon(surface, (10, 20, 16), hexagon)
        pygame.draw.polygon(surface, color, hexagon, max(2, size // 22))
        eye = pygame.Rect(0, 0, round(size * 0.66), round(size * 0.4))
        eye.center = center
        pygame.draw.ellipse(surface, (230, 240, 220), eye)
        drift = math.sin(time * 1.7) * size * 0.05
        iris_radius = round(size * 0.14)
        pygame.draw.circle(surface, color, (round(cx + drift), cy), iris_radius)
        pygame.draw.circle(surface, (4, 10, 8), (round(cx + drift), cy), max(2, iris_radius // 2))
        pygame.draw.ellipse(surface, color, eye, max(2, size // 30))
        lid = {"suspicious": 0.5, "angry": 0.35}.get(mood)
        if lid is not None:
            cover = pygame.Rect(eye.x - 2, eye.y - 2, eye.width + 4, round(eye.height * lid))
            pygame.draw.rect(surface, (10, 20, 16), cover)
            slope = 1 if mood == "angry" else 0
            pygame.draw.line(surface, color, (cover.left, cover.bottom - slope * size // 10), (cover.right, cover.bottom + slope * size // 10), max(2, size // 22))
        if mood == "happy":
            pygame.draw.arc(surface, color, pygame.Rect(cx - size // 6, cy + size // 8, size // 3, size // 5), math.pi, math.tau, max(2, size // 26))
        pygame.draw.rect(surface, color, pygame.Rect(cx - size // 8, cy + radius - size // 5, size // 4, size // 8), max(1, size // 40))
