from __future__ import annotations

import pygame

from src.minigames.captchas import CANVAS, Captcha
from src.minigames.common import (
    AMBER,
    BORDER,
    BORDER_DARK,
    GREEN,
    INK,
    INK_BRIGHT,
    INK_MUTED,
    PANEL,
    PANEL_MID,
    RED,
    SCREEN_BLACK,
    draw_text,
    draw_wrapped,
    font,
)
from src.minigames.verify9 import Verify9

RECT = pygame.Rect(377, 30, 800, 636)
CANVAS_ORIGIN = (RECT.x + 40, RECT.y + 166)
SKIP_RECT = pygame.Rect(RECT.right - 250, RECT.bottom - 50, 226, 36)
SKIP_AFTER_SECONDS = 25.0
CELEBRATION_SECONDS = 1.0


class CaptchaOverlay:
    """Window that hosts one captcha. It reports what happened through `pop_events()`."""

    def __init__(self, verify9: Verify9) -> None:
        self.verify9 = verify9
        self.is_open = False
        self.captcha: Captcha | None = None
        self.elapsed = 0.0
        self.celebration = 0.0
        self.failures = 0
        self.number = 1
        self._events: list[tuple[str, float | str | None]] = []
        self.clock = 0.0

    # -- lifecycle -------------------------------------------------------
    def open(self, captcha: Captcha, number: int = 1) -> None:
        self.captcha = captcha
        self.is_open = True
        self.elapsed = 0.0
        self.celebration = 0.0
        self.failures = 0
        self.number = number

    def close(self) -> None:
        self.is_open = False
        self.captcha = None

    def pop_events(self) -> list[tuple[str, float | str | None]]:
        events, self._events = self._events, []
        return events

    @property
    def can_skip(self) -> bool:
        return self.is_open and self.celebration <= 0 and self.elapsed >= SKIP_AFTER_SECONDS

    # -- update ----------------------------------------------------------
    def update(self, dt: float) -> None:
        if not self.is_open or self.captcha is None:
            return
        self.clock += dt
        if self.celebration > 0:
            self.celebration -= dt
            if self.celebration <= 0:
                self._events.append(("solved", self.elapsed))
                self.close()
            return
        self.elapsed += dt
        self.captcha.update(dt)
        for name in self.captcha.take_events():
            self._events.append(("sound", name))
            if name == "error":
                self.failures += 1
                self._events.append(("penalty", None))
        if self.captcha.solved:
            self.celebration = CELEBRATION_SECONDS

    # -- input -----------------------------------------------------------
    def _local(self, position: tuple[int, int]) -> tuple[int, int]:
        return position[0] - CANVAS_ORIGIN[0], position[1] - CANVAS_ORIGIN[1]

    def handle_mouse_down(self, position: tuple[int, int]) -> None:
        if not self.is_open or self.captcha is None or self.celebration > 0:
            return
        if self.can_skip and SKIP_RECT.collidepoint(position):
            self._events.append(("skipped", None))
            self.close()
            return
        self.captcha.on_mouse_down(self._local(position))

    def handle_mouse_up(self, position: tuple[int, int]) -> None:
        if self.is_open and self.captcha is not None:
            self.captcha.on_mouse_up(self._local(position))

    def handle_mouse_move(self, position: tuple[int, int] | None) -> None:
        if self.is_open and self.captcha is not None and position is not None:
            self.captcha.on_mouse_move(self._local(position))

    def handle_key(self, event: pygame.event.Event) -> None:
        if self.is_open and self.captcha is not None and self.celebration <= 0:
            self.captcha.on_key(event)

    # -- drawing ---------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        if not self.is_open or self.captcha is None:
            return
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 165))  # translucent: the desk stays faintly visible behind the popup
        surface.blit(dim, (0, 0))
        radius = 22
        pygame.draw.rect(surface, (0, 0, 0), RECT.move(6, 6), border_radius=radius)
        pygame.draw.rect(surface, SCREEN_BLACK, RECT, border_radius=radius)
        pygame.draw.rect(surface, RED if self.failures else BORDER, RECT, 4, border_radius=radius)
        pygame.draw.rect(
            surface, (120, 34, 30), pygame.Rect(RECT.x, RECT.y, RECT.width, 44),
            border_top_left_radius=radius, border_top_right_radius=radius,
        )
        draw_text(surface, "VERIFICAÇÃO DE HUMANIDADE", font(20, True), INK_BRIGHT, (RECT.x + 18, RECT.y + 11))
        draw_text(surface, f"VERIFY-9  ·  teste {self.number}", font(15), (240, 190, 180), (RECT.right - 18, RECT.y + 14), "topright")

        mood = "happy" if self.celebration > 0 else ("angry" if self.failures else "suspicious")
        self.verify9.draw(surface, (RECT.x + 84, RECT.y + 108), 88, mood, self.clock)
        draw_text(surface, "PROVE QUE VOCÊ NÃO É UM ROBÔ", font(24, True), INK_BRIGHT, (RECT.x + 150, RECT.y + 66))
        draw_wrapped(surface, self.captcha.instruction, font(18), INK, pygame.Rect(RECT.x + 150, RECT.y + 100, RECT.width - 190, 60), 24)

        canvas = pygame.Surface(CANVAS)
        canvas.fill((13, 20, 16))
        self.captcha.render(canvas)
        surface.blit(canvas, CANVAS_ORIGIN)
        pygame.draw.rect(surface, BORDER_DARK, pygame.Rect(CANVAS_ORIGIN, CANVAS), 2)

        footer_y = RECT.bottom - 44
        draw_text(surface, f"Erros: {self.failures}   (cada erro custa 3 segundos)", font(15), RED if self.failures else INK_MUTED, (RECT.x + 40, footer_y))
        minutes, seconds = divmod(int(self.elapsed), 60)
        draw_text(surface, f"Tempo aqui: {minutes:02d}:{seconds:02d}", font(15), INK_MUTED, (RECT.x + 40, footer_y + 20))
        if self.can_skip:
            pygame.draw.rect(surface, PANEL_MID, SKIP_RECT)
            pygame.draw.rect(surface, AMBER, SKIP_RECT, 2)
            draw_text(surface, "PULAR  (-15 segundos)", font(16, True), INK_BRIGHT, SKIP_RECT.center, "center")
        elif self.celebration <= 0:
            remaining = max(0, int(SKIP_AFTER_SECONDS - self.elapsed))
            draw_text(surface, f"Não consegue? Pular libera em {remaining}s", font(14), INK_MUTED, (SKIP_RECT.right, footer_y + 10), "topright")
        if self.celebration > 0:
            banner = pygame.Rect(0, 0, 520, 90)
            banner.center = (RECT.centerx, RECT.centery + 40)
            pygame.draw.rect(surface, (10, 34, 18), banner)
            pygame.draw.rect(surface, GREEN, banner, 4)
            draw_text(surface, "HUMANO VERIFICADO", font(36, True), GREEN, banner.center, "center")
