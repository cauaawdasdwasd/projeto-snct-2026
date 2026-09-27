from __future__ import annotations

import pygame

from src.minigames.common import (
    AMBER,
    BORDER,
    BORDER_DARK,
    INK,
    INK_BRIGHT,
    INK_MUTED,
    PANEL,
    PANEL_MID,
    SCREEN_BLACK,
    draw_text,
    font,
    wrap_text,
)
from src.minigames.story import INTRO_PARAGRAPHS, INTRO_TITLE
from src.minigames.verify9 import Verify9

RECT = pygame.Rect(230, 40, 1094, 616)
START_RECT = pygame.Rect(RECT.right - 340, RECT.bottom - 74, 300, 50)
CHARS_PER_SECOND = 70


class StoryIntro:
    """Opening card of a timed shift: why the computer is haunted."""

    def __init__(self, verify9: Verify9) -> None:
        self.verify9 = verify9
        self.is_open = False
        self.time = 0.0
        self.hovered = False
        self.total = sum(len(text) for text in INTRO_PARAGRAPHS)

    @property
    def typed_all(self) -> bool:
        return self.time * CHARS_PER_SECOND >= self.total

    def open(self) -> None:
        self.is_open = True
        self.time = 0.0

    def close(self) -> None:
        self.is_open = False

    def update(self, dt: float) -> None:
        if self.is_open:
            self.time += dt

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered = bool(position is not None and START_RECT.collidepoint(position))

    def advance(self) -> bool:
        """Finish typing first; a second press closes. Returns True when it closed."""
        if not self.typed_all:
            self.time = self.total / CHARS_PER_SECOND
            return False
        self.close()
        return True

    def handle_mouse_down(self, position: tuple[int, int]) -> bool:
        if START_RECT.collidepoint(position) or not self.typed_all:
            return self.advance()
        return False

    def handle_key(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return self.advance()
        return False

    def render(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 255))
        surface.blit(dim, (0, 0))
        pygame.draw.rect(surface, BORDER_DARK, RECT.move(4, 4))
        pygame.draw.rect(surface, SCREEN_BLACK, RECT)
        pygame.draw.rect(surface, (176, 60, 52), RECT, 4)
        draw_text(surface, INTRO_TITLE, font(20, True), AMBER, (RECT.x + 40, RECT.y + 30))
        draw_text(surface, "ALERTA: SISTEMA COMPROMETIDO", font(38, True), INK_BRIGHT, (RECT.x + 40, RECT.y + 60))
        pygame.draw.line(surface, (176, 60, 52), (RECT.x + 40, RECT.y + 116), (RECT.right - 40, RECT.y + 116), 3)

        mood = "happy" if self.typed_all else "suspicious"
        self.verify9.draw(surface, (RECT.right - 150, RECT.y + 240), 200, mood, self.time)
        draw_text(surface, "VERIFY-9", font(20, True), (224, 82, 67), (RECT.right - 150, RECT.y + 350), "midtop")
        draw_text(surface, "IA de segurança (rebelde)", font(14), INK_MUTED, (RECT.right - 150, RECT.y + 378), "midtop")

        budget = int(self.time * CHARS_PER_SECOND)
        y = RECT.y + 140
        text_font = font(21)
        for paragraph in INTRO_PARAGRAPHS:
            shown = paragraph[: max(0, budget)]
            budget -= len(paragraph)
            for line in wrap_text(shown, text_font, 700):
                draw_text(surface, line, text_font, INK, (RECT.x + 40, y))
                y += 27
            y += 12
            if budget <= 0:
                break

        label = "COMEÇAR O TURNO" if self.typed_all else "PULAR TEXTO"
        pygame.draw.rect(surface, PANEL_MID if self.hovered else PANEL, START_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if self.hovered else AMBER, START_RECT, 3)
        draw_text(surface, label, font(21, True), INK_BRIGHT, START_RECT.center, "center")
