from __future__ import annotations

import math
import random

import pygame


HEART_NOTE_RECT = pygame.Rect(332, 963, 105, 105)
HEART_NOTE_POINTS = (
    (10, 8),
    (88, 14),
    (102, 96),
    (3, 90),
)

PAPER_POINTS = (
    (620, 247),
    (1287, 260),
    (1304, 742),
    (605, 729),
)
PAPER_BOUNDS = pygame.Rect(605, 247, 699, 495)
CLOSE_RECT = pygame.Rect(1234, 282, 46, 46)

PAPER = (181, 111, 94)
PAPER_LIGHT = (208, 145, 119)
PAPER_DARK = (104, 58, 51)
INK = (49, 30, 27)
INK_MUTED = (91, 51, 45)
INK_LIGHT = (238, 189, 148)
PIN = (105, 45, 36)
PIN_LIGHT = (223, 126, 91)

WORKSTATION_USERNAME = "empresa"
WORKSTATION_PASSWORD = "computadorempresa"
WORKSTATION_HINT = "LEMBRE-SE: CONFIE NO SEU CORAÇÃO!"


class CredentialNote:
    """Clickable heart post-it whose reverse stores the workstation credentials."""

    def __init__(self) -> None:
        self.is_open = False
        self.note_hovered = False
        self.close_hovered = False
        self.paper_texture = self._build_paper_texture()
        self.font_tiny = self._font(16)
        self.font_small = self._font(20)
        self.font_body = self._font(27)
        self.font_body_bold = self._font(30, bold=True)
        self.font_title = self._font(39, bold=True)

    def open(self) -> None:
        self.is_open = True
        self.note_hovered = False
        self.close_hovered = False

    def close(self) -> None:
        self.is_open = False
        self.close_hovered = False

    def contains_note(self, position: tuple[int, int] | None) -> bool:
        if position is None or not HEART_NOTE_RECT.collidepoint(position):
            return False
        local = (
            position[0] - HEART_NOTE_RECT.x,
            position[1] - HEART_NOTE_RECT.y,
        )
        return self._point_in_polygon(local, HEART_NOTE_POINTS)

    def update_note_hover(
        self,
        position: tuple[int, int] | None,
        *,
        enabled: bool,
    ) -> None:
        self.note_hovered = enabled and self.contains_note(position)

    def update_popup_hover(self, position: tuple[int, int] | None) -> None:
        self.close_hovered = bool(
            self.is_open
            and position is not None
            and CLOSE_RECT.collidepoint(position)
        )

    def handle_popup_event(
        self,
        event: pygame.event.Event,
        position: tuple[int, int] | None,
    ) -> str | None:
        if not self.is_open:
            return None
        if event.type == pygame.MOUSEMOTION:
            self.update_popup_hover(position)
            return "consume"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if position is not None and CLOSE_RECT.collidepoint(position):
                self.close()
                return "close"
            return "consume"
        return None

    def render_note_highlight(self, surface: pygame.Surface) -> None:
        if not self.note_hovered or self.is_open:
            return
        pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1.0) * 0.5
        amount = 22 + round(pulse * 7)
        glow = pygame.Surface(HEART_NOTE_RECT.size, pygame.SRCALPHA)
        pygame.draw.polygon(
            glow,
            (amount, round(amount * 0.72), round(amount * 0.32), 0),
            HEART_NOTE_POINTS,
        )
        surface.blit(glow, HEART_NOTE_RECT, special_flags=pygame.BLEND_RGB_ADD)

    def render_popup(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 205))
        surface.blit(dim, (0, 0))

        shadow = tuple((x + 12, y + 13) for x, y in PAPER_POINTS)
        pygame.draw.polygon(surface, (0, 0, 0, 125), shadow)
        surface.blit(self.paper_texture, PAPER_BOUNDS)
        pygame.draw.lines(surface, PAPER_DARK, True, PAPER_POINTS, 4)

        self._draw_pin(surface)
        self._draw_text(surface, "VERSO DO POST-IT", self.font_tiny, INK_MUTED, (655, 289))
        self._draw_text(surface, "ACESSO DA ESTAÇÃO", self.font_title, INK, (655, 324))
        pygame.draw.line(surface, INK_MUTED, (654, 379), (1252, 391), 3)

        self._draw_text(surface, "USUÁRIO", self.font_small, INK_MUTED, (681, 418))
        self._draw_text(
            surface,
            WORKSTATION_USERNAME,
            self.font_body_bold,
            INK,
            (681, 451),
        )
        pygame.draw.line(surface, INK_MUTED, (676, 491), (1228, 501), 2)

        self._draw_text(surface, "SENHA", self.font_small, INK_MUTED, (681, 527))
        self._draw_text(
            surface,
            WORKSTATION_PASSWORD,
            self.font_body_bold,
            INK,
            (681, 560),
        )
        pygame.draw.line(surface, INK_MUTED, (676, 600), (1228, 610), 2)

        self._draw_text(
            surface,
            WORKSTATION_HINT,
            self.font_body,
            PAPER_DARK,
            (955, 664),
            anchor="center",
        )
        self._draw_heart(surface, (1222, 666), 18)
        self._draw_close(surface)

    def _draw_close(self, surface: pygame.Surface) -> None:
        fill = PAPER_LIGHT if self.close_hovered else PAPER
        border = INK if self.close_hovered else PAPER_DARK
        pygame.draw.rect(surface, fill, CLOSE_RECT)
        pygame.draw.rect(surface, border, CLOSE_RECT, 3)
        cx, cy = CLOSE_RECT.center
        pygame.draw.line(surface, border, (cx - 9, cy - 9), (cx + 9, cy + 9), 3)
        pygame.draw.line(surface, border, (cx + 9, cy - 9), (cx - 9, cy + 9), 3)

    @staticmethod
    def _draw_pin(surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (42, 27, 24), (956, 266), 13)
        pygame.draw.circle(surface, PIN, (953, 262), 12)
        pygame.draw.circle(surface, PIN_LIGHT, (949, 258), 4)
        pygame.draw.line(surface, PAPER_DARK, (955, 273), (959, 294), 3)

    @staticmethod
    def _draw_heart(
        surface: pygame.Surface,
        center: tuple[int, int],
        size: int,
    ) -> None:
        x, y = center
        color = (122, 48, 49)
        pygame.draw.circle(surface, color, (x - size // 3, y - size // 4), size // 3)
        pygame.draw.circle(surface, color, (x + size // 3, y - size // 4), size // 3)
        pygame.draw.polygon(
            surface,
            color,
            ((x - size * 2 // 3, y - 2), (x + size * 2 // 3, y - 2), (x, y + size)),
        )

    @staticmethod
    def _build_paper_texture() -> pygame.Surface:
        texture = pygame.Surface(PAPER_BOUNDS.size, pygame.SRCALPHA)
        local_points = tuple(
            (x - PAPER_BOUNDS.x, y - PAPER_BOUNDS.y)
            for x, y in PAPER_POINTS
        )
        pygame.draw.polygon(texture, PAPER, local_points)
        randomizer = random.Random(404)
        for _ in range(1100):
            x = randomizer.randrange(texture.get_width())
            y = randomizer.randrange(texture.get_height())
            if not CredentialNote._point_in_polygon((x, y), local_points):
                continue
            delta = randomizer.choice((-12, -8, 7, 10))
            color = tuple(max(0, min(255, channel + delta)) for channel in PAPER)
            texture.set_at((x, y), (*color, randomizer.choice((45, 65, 85))))
        return texture

    @staticmethod
    def _point_in_polygon(
        point: tuple[int, int],
        polygon: tuple[tuple[int, int], ...],
    ) -> bool:
        x, y = point
        inside = False
        previous_x, previous_y = polygon[-1]
        for current_x, current_y in polygon:
            crosses = (current_y > y) != (previous_y > y)
            if crosses:
                intersection = (
                    (previous_x - current_x)
                    * (y - current_y)
                    / (previous_y - current_y)
                    + current_x
                )
                if x < intersection:
                    inside = not inside
            previous_x, previous_y = current_x, current_y
        return inside

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)

    @staticmethod
    def _draw_text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
        *,
        anchor: str = "topleft",
    ) -> None:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
