from __future__ import annotations

import pygame

from src.minigames.common import BORDER_DARK, INK_BRIGHT, INK_MUTED, SCREEN_BLACK, draw_text, font
from src.minigames.verify9 import MOOD_COLORS, Verify9

TOAST_RECT = pygame.Rect(302, 186, 851, 66)
DURATION_SECONDS = 4.2
CHARS_PER_SECOND = 48


class Toast:
    """A short message from VERIFY-9 that slides over the desk and disappears by itself."""

    def __init__(self, verify9: Verify9) -> None:
        self.verify9 = verify9
        self.text = ""
        self.mood = "neutral"
        self.time = 0.0
        self.left = 0.0
        self.sender = "VERIFY-9"

    @property
    def visible(self) -> bool:
        return self.left > 0

    def show(self, text: str, mood: str = "neutral", sender: str = "VERIFY-9") -> None:
        self.text, self.mood, self.sender = text, mood, sender
        self.time = 0.0
        self.left = DURATION_SECONDS

    def clear(self) -> None:
        self.left = 0.0

    def update(self, dt: float) -> None:
        if self.left > 0:
            self.left -= dt
            self.time += dt

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        slide = min(1.0, self.time / 0.2)
        fade = min(1.0, self.left / 0.4)
        rect = TOAST_RECT.copy()
        rect.y -= round((1 - slide) * 40)
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((*SCREEN_BLACK, round(232 * fade)))
        color = MOOD_COLORS.get(self.mood, MOOD_COLORS["neutral"])
        pygame.draw.rect(panel, (*color, round(255 * fade)), panel.get_rect(), 3)
        surface.blit(panel, rect)
        self.verify9.draw(surface, (rect.x + 40, rect.centery), 50, self.mood, self.time)
        draw_text(surface, self.sender, font(13, True), color, (rect.x + 78, rect.y + 8))
        shown = self.text[: int(self.time * CHARS_PER_SECOND)]
        draw_text(surface, shown, font(20, True), INK_BRIGHT, (rect.x + 78, rect.y + 28))
