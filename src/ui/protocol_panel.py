from __future__ import annotations

import math
from collections.abc import Callable, Iterable

import pygame

from src.gameplay.protocols import PROTOCOLS, Protocol
from src.rendering.protocol_films import DURATION as FILM_DURATION, Film, create_film


PAGE_SIZE = 3
AMBER_BAR = (237, 193, 91)

INK = (214, 219, 128)
INK_BRIGHT = (244, 236, 157)
INK_MUTED = (134, 143, 89)
SCREEN_BLACK = (5, 9, 8)
PANEL_DARK = (13, 18, 16)
PANEL_MID = (26, 32, 27)
BORDER_DARK = (54, 62, 44)
BORDER_LIGHT = (135, 142, 83)
PAPER = (177, 147, 86)
PAPER_DARK = (82, 62, 39)
DENY_RED = (202, 77, 63)
REVIEW_BLUE = (105, 164, 177)
VIOLATION_AMBER = (224, 161, 62)

BUTTON_RECTS = (
    pygame.Rect(15, 96, 243, 137),
    pygame.Rect(15, 246, 243, 137),
    pygame.Rect(15, 396, 243, 137),
)
PREVIOUS_PAGE_RECT = pygame.Rect(18, 574, 49, 46)
NEXT_PAGE_RECT = pygame.Rect(206, 574, 49, 46)
PAGE_LABEL_RECT = pygame.Rect(73, 574, 127, 46)

POPUP_RECT = pygame.Rect(38, 31, 1478, 634)
POPUP_CLOSE_RECT = pygame.Rect(1444, 48, 43, 43)
VIDEO_RECT = pygame.Rect(906, 174, 548, 293)


class ProtocolPanel:
    """Paged protocol menu and its educational popup."""

    def __init__(
        self,
        portraits: dict[str, pygame.Surface],
        play_sound: Callable[[str, float], None] | None = None,
    ) -> None:
        self.play_sound = play_sound
        self.protocols = PROTOCOLS
        self.portraits = {
            slug: self._fit_portrait(image)
            for slug, image in portraits.items()
        }
        self.page = 0
        self.selected_protocol: Protocol | None = None
        self.hovered_protocol_slug: str | None = None
        self.hovered_control: str | None = None
        self.films: dict[str, Film] = {}
        self.film_time = 0.0
        self.film_playing = False
        self._film_event_index = 0

        self.font_tiny = self._make_font(15)
        self.font_small = self._make_font(18)
        self.font_body = self._make_font(21)
        self.font_body_bold = self._make_font(21, bold=True)
        self.font_title = self._make_font(27, bold=True)
        self.font_header = self._make_font(34, bold=True)

    @property
    def is_popup_open(self) -> bool:
        return self.selected_protocol is not None

    def handle_mouse_down(self, position: tuple[int, int]) -> bool:
        if self.selected_protocol is not None:
            if POPUP_CLOSE_RECT.collidepoint(position):
                self.close_popup()
                return True

            if VIDEO_RECT.collidepoint(position):
                self._video_click(position)
                return True

            return POPUP_RECT.collidepoint(position)

        for protocol, rect in zip(self._page_protocols(), BUTTON_RECTS, strict=True):
            if rect.collidepoint(position):
                self.selected_protocol = protocol
                self.start_film()
                return True

        if PREVIOUS_PAGE_RECT.collidepoint(position):
            self.page = max(0, self.page - 1)
            return True

        if NEXT_PAGE_RECT.collidepoint(position):
            self.page = min(self.page_count - 1, self.page + 1)
            return True

        return False

    def handle_key_down(self, key: int) -> bool:
        if key == pygame.K_ESCAPE and self.selected_protocol is not None:
            self.close_popup()
            return True

        if self.selected_protocol is not None:
            return False

        if key in (pygame.K_LEFT, pygame.K_a):
            self.page = max(0, self.page - 1)
            return True

        if key in (pygame.K_RIGHT, pygame.K_d):
            self.page = min(self.page_count - 1, self.page + 1)
            return True

        return False

    def close_popup(self) -> None:
        self.selected_protocol = None
        self.film_playing = False

    # -- tutorial film --------------------------------------------------
    def _film(self) -> Film | None:
        protocol = self.selected_protocol
        if protocol is None:
            return None
        if protocol.slug not in self.films:
            self.films[protocol.slug] = create_film(protocol.slug, self.portraits.get(protocol.slug))
        return self.films[protocol.slug]

    def start_film(self) -> None:
        self.film_time = 0.0
        self.film_playing = True
        self._film_event_index = 0

    def update(self, dt: float) -> None:
        film = self._film() if self.selected_protocol is not None else None
        if film is None or not self.film_playing:
            return
        previous = self.film_time
        self.film_time = min(FILM_DURATION, previous + dt)
        events = film.events
        while self._film_event_index < len(events) and events[self._film_event_index][0] <= self.film_time:
            time, sound = events[self._film_event_index]
            if time >= previous - 0.001 and self.play_sound is not None:
                self.play_sound(sound, 0.45)
            self._film_event_index += 1
        if self.film_time >= FILM_DURATION:
            self.film_playing = False

    def _video_click(self, position: tuple[int, int]) -> None:
        film = self._film()
        if film is None:
            return
        bar = pygame.Rect(VIDEO_RECT.x + 4, VIDEO_RECT.bottom - 18, VIDEO_RECT.width - 8, 16)
        if bar.collidepoint(position):
            self.film_time = FILM_DURATION * (position[0] - bar.x) / bar.width
            self._film_event_index = sum(1 for time, _ in film.events if time < self.film_time)
            self.film_playing = True
        elif self.film_time >= FILM_DURATION and not self.film_playing:
            self.start_film()
        else:
            self.film_playing = not self.film_playing

    def open_protocol(self, slug: str) -> None:
        for index, protocol in enumerate(self.protocols):
            if protocol.slug != slug:
                continue
            self.page = index // PAGE_SIZE
            self.selected_protocol = protocol
            self.start_film()
            return
        raise ValueError(f"Unknown protocol: {slug}")

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered_protocol_slug = None
        self.hovered_control = None

        if position is None:
            return

        if self.selected_protocol is not None:
            if POPUP_CLOSE_RECT.collidepoint(position):
                self.hovered_control = "close"
            elif VIDEO_RECT.collidepoint(position):
                self.hovered_control = "video"
            return

        for protocol, rect in zip(self._page_protocols(), BUTTON_RECTS, strict=True):
            if rect.collidepoint(position):
                self.hovered_protocol_slug = protocol.slug
                return

        if PREVIOUS_PAGE_RECT.collidepoint(position):
            self.hovered_control = "previous"
        elif NEXT_PAGE_RECT.collidepoint(position):
            self.hovered_control = "next"

    @property
    def page_count(self) -> int:
        return math.ceil(len(self.protocols) / PAGE_SIZE)

    def render_menu(self, surface: pygame.Surface) -> None:
        self._draw_menu_backdrop(surface)

        for protocol, rect in zip(self._page_protocols(), BUTTON_RECTS, strict=True):
            self._draw_protocol_button(surface, protocol, rect)

        self._draw_pagination(surface)

    def render_popup(self, surface: pygame.Surface) -> None:
        protocol = self.selected_protocol
        if protocol is None:
            return

        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 255))
        surface.blit(dim, (0, 0))

        self._draw_layered_rect(surface, POPUP_RECT, PANEL_DARK, BORDER_LIGHT)
        inner = POPUP_RECT.inflate(-12, -12)
        pygame.draw.rect(surface, SCREEN_BLACK, inner)

        self._draw_popup_header(surface, protocol)
        self._draw_popup_text(surface, protocol)
        self._draw_video_area(surface, protocol)
        self._draw_close_button(surface)

    def _page_protocols(self) -> tuple[Protocol, ...]:
        start = self.page * PAGE_SIZE
        return self.protocols[start : start + PAGE_SIZE]

    def _draw_menu_backdrop(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, SCREEN_BLACK, (10, 86, 253, 550))
        scanline = pygame.Surface((253, 2), pygame.SRCALPHA)
        scanline.fill((115, 128, 72, 8))
        for y in range(88, 635, 4):
            surface.blit(scanline, (10, y))

    def _draw_protocol_button(
        self,
        surface: pygame.Surface,
        protocol: Protocol,
        rect: pygame.Rect,
    ) -> None:
        hovered = protocol.slug == self.hovered_protocol_slug
        fill = PANEL_MID if hovered else PANEL_DARK
        border = INK_BRIGHT if hovered else BORDER_LIGHT
        self._draw_layered_rect(surface, rect, fill, border)

        number_rect = pygame.Rect(rect.x + 7, rect.y + 7, 34, 27)
        pygame.draw.rect(surface, INK_MUTED, number_rect)
        self._draw_text(
            surface,
            f"{protocol.number:02d}",
            self.font_small,
            SCREEN_BLACK,
            number_rect.center,
            anchor="center",
        )

        portrait_rect = pygame.Rect(rect.x + 7, rect.y + 40, 64, 64)
        pygame.draw.rect(surface, SCREEN_BLACK, portrait_rect)
        pygame.draw.rect(surface, BORDER_DARK, portrait_rect, 2)
        portrait = self.portraits.get(protocol.slug)
        if portrait is not None:
            surface.blit(portrait, portrait_rect)
        else:
            initials = "".join(part[0] for part in protocol.scientist.split()[:2])
            self._draw_text(
                surface,
                initials,
                self.font_title,
                INK_MUTED,
                portrait_rect.center,
                anchor="center",
            )

        text_x = rect.x + 80
        self._draw_wrapped_text(
            surface,
            protocol.scientist.upper(),
            self.font_small,
            INK_BRIGHT,
            pygame.Rect(text_x, rect.y + 9, rect.right - text_x - 6, 43),
            line_height=18,
            max_lines=2,
        )
        self._draw_wrapped_text(
            surface,
            protocol.title.upper(),
            self.font_tiny,
            INK_MUTED,
            pygame.Rect(text_x, rect.y + 53, rect.right - text_x - 6, 35),
            line_height=16,
            max_lines=2,
        )
        self._draw_wrapped_text(
            surface,
            protocol.menu_hint,
            self.font_tiny,
            INK,
            pygame.Rect(text_x, rect.y + 87, rect.right - text_x - 7, 46),
            line_height=15,
            max_lines=3,
        )

        if hovered:
            pygame.draw.rect(surface, INK_BRIGHT, (rect.right - 7, rect.y + 4, 3, rect.height - 8))

    def _draw_pagination(self, surface: pygame.Surface) -> None:
        previous_enabled = self.page > 0
        next_enabled = self.page < self.page_count - 1

        self._draw_arrow_button(
            surface,
            PREVIOUS_PAGE_RECT,
            direction=-1,
            enabled=previous_enabled,
            hovered=self.hovered_control == "previous",
        )
        self._draw_arrow_button(
            surface,
            NEXT_PAGE_RECT,
            direction=1,
            enabled=next_enabled,
            hovered=self.hovered_control == "next",
        )
        self._draw_layered_rect(surface, PAGE_LABEL_RECT, PANEL_DARK, BORDER_DARK)
        self._draw_text(
            surface,
            f"PÁGINA {self.page + 1}/{self.page_count}",
            self.font_tiny,
            INK,
            PAGE_LABEL_RECT.center,
            anchor="center",
        )

    def _draw_arrow_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        direction: int,
        enabled: bool,
        hovered: bool,
    ) -> None:
        active_hover = enabled and hovered
        fill = PANEL_MID if active_hover else PANEL_DARK
        border = INK_BRIGHT if active_hover else BORDER_DARK
        self._draw_layered_rect(surface, rect, fill, border)
        color = INK_BRIGHT if enabled else BORDER_DARK
        center_x, center_y = rect.center
        points = (
            [(center_x + 6, center_y - 11), (center_x - 7, center_y), (center_x + 6, center_y + 11)]
            if direction < 0
            else [(center_x - 6, center_y - 11), (center_x + 7, center_y), (center_x - 6, center_y + 11)]
        )
        pygame.draw.polygon(surface, color, points)

    def _draw_popup_header(self, surface: pygame.Surface, protocol: Protocol) -> None:
        header_rect = pygame.Rect(55, 48, 1414, 88)
        pygame.draw.rect(surface, PANEL_MID, header_rect)
        pygame.draw.line(surface, BORDER_LIGHT, header_rect.bottomleft, header_rect.bottomright, 3)

        portrait_rect = pygame.Rect(68, 59, 64, 64)
        pygame.draw.rect(surface, SCREEN_BLACK, portrait_rect)
        portrait = self.portraits.get(protocol.slug)
        if portrait is not None:
            surface.blit(portrait, portrait_rect)
        pygame.draw.rect(surface, INK_MUTED, portrait_rect, 2)

        self._draw_text(
            surface,
            f"PROTOCOLO {protocol.scientist.upper()}",
            self.font_header,
            INK_BRIGHT,
            (151, 59),
        )
        self._draw_text(surface, protocol.title.upper(), self.font_body, INK_MUTED, (153, 101))

    def _draw_popup_text(self, surface: pygame.Surface, protocol: Protocol) -> None:
        left_x = 72
        content_width = 770
        y = 158

        y = self._draw_section(
            surface,
            "REGRA",
            (protocol.introduction,),
            pygame.Rect(left_x, y, content_width, 87),
        )
        y = self._draw_section(
            surface,
            "COMO CONFERIR",
            protocol.checks,
            pygame.Rect(left_x, y + 10, content_width, 194),
            bullets=True,
        )
        y = self._draw_section(
            surface,
            "EXEMPLO",
            protocol.example_lines,
            pygame.Rect(left_x, y + 8, content_width, 124),
        )

        verdict_color = {
            "deny": DENY_RED,
            "review": REVIEW_BLUE,
            "violation": VIOLATION_AMBER,
        }.get(protocol.expected_stamp, INK_BRIGHT)
        verdict_rect = pygame.Rect(left_x, y + 8, content_width, 67)
        pygame.draw.rect(surface, PANEL_MID, verdict_rect)
        pygame.draw.rect(surface, verdict_color, verdict_rect, 3)
        self._draw_text(
            surface,
            f"RESULTADO: {protocol.verdict}",
            self.font_title,
            verdict_color,
            (verdict_rect.x + 15, verdict_rect.y + 9),
        )
        self._draw_wrapped_text(
            surface,
            protocol.reason,
            self.font_small,
            INK,
            pygame.Rect(verdict_rect.x + 16, verdict_rect.y + 39, verdict_rect.width - 30, 24),
            line_height=19,
            max_lines=1,
        )

    def _draw_section(
        self,
        surface: pygame.Surface,
        heading: str,
        lines: Iterable[str],
        rect: pygame.Rect,
        bullets: bool = False,
    ) -> int:
        self._draw_text(surface, heading, self.font_body_bold, INK_BRIGHT, rect.topleft)
        pygame.draw.line(
            surface,
            BORDER_DARK,
            (rect.x, rect.y + 29),
            (rect.right, rect.y + 29),
            2,
        )

        y = rect.y + 38
        for line in lines:
            prefix = "> " if bullets else ""
            used_lines = self._draw_wrapped_text(
                surface,
                prefix + line,
                self.font_small,
                INK,
                pygame.Rect(rect.x + 4, y, rect.width - 8, rect.bottom - y),
                line_height=21,
                max_lines=2,
            )
            y += used_lines * 21 + 4

        return rect.bottom

    def _draw_video_area(self, surface: pygame.Surface, protocol: Protocol) -> None:
        self._draw_text(surface, "TUTORIAL EM VÍDEO", self.font_body_bold, INK_BRIGHT, (906, 144))
        hovered = self.hovered_control == "video"
        border = INK_BRIGHT if hovered else BORDER_LIGHT
        self._draw_layered_rect(surface, VIDEO_RECT, (7, 11, 10), border)

        film = self._film()
        if film is not None:
            frame = film.render(self.film_time)
            surface.blit(frame, (VIDEO_RECT.x + 4, VIDEO_RECT.y + 4))
            self._draw_film_controls(surface, hovered)

        note_rect = pygame.Rect(906, 489, 548, 132)
        self._draw_layered_rect(surface, note_rect, PANEL_MID, BORDER_DARK)
        self._draw_text(surface, "FICHA DE CONSULTA", self.font_body_bold, PAPER, (924, 505))
        self._draw_wrapped_text(
            surface,
            "Os protocolos ficam disponíveis durante toda a auditoria. Consulte-os antes de carimbar.",
            self.font_body,
            INK,
            pygame.Rect(924, 542, 510, 62),
            line_height=25,
            max_lines=3,
        )

    def _draw_film_controls(self, surface: pygame.Surface, hovered: bool) -> None:
        bar = pygame.Rect(VIDEO_RECT.x + 4, VIDEO_RECT.bottom - 10, VIDEO_RECT.width - 8, 6)
        pygame.draw.rect(surface, (20, 28, 22), bar)
        fill = round(bar.width * self.film_time / FILM_DURATION)
        pygame.draw.rect(surface, AMBER_BAR, (bar.x, bar.y, fill, bar.height))
        finished = self.film_time >= FILM_DURATION and not self.film_playing
        if self.film_playing:
            if hovered:
                self._draw_text(surface, "CLIQUE PARA PAUSAR", self.font_tiny, INK_BRIGHT, (VIDEO_RECT.right - 12, VIDEO_RECT.y + 10), anchor="topright")
            return
        if finished:
            replay = pygame.Rect(VIDEO_RECT.right - 150, VIDEO_RECT.y + 10, 138, 30)
            pygame.draw.rect(surface, PANEL_MID, replay)
            pygame.draw.rect(surface, INK_BRIGHT if hovered else INK_MUTED, replay, 2)
            self._draw_text(surface, "REPETIR", self.font_small, INK_BRIGHT, replay.center, anchor="center")
            return
        center = (VIDEO_RECT.centerx, VIDEO_RECT.y + 128)
        veil = pygame.Surface((VIDEO_RECT.width - 8, VIDEO_RECT.height - 8 - 44), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 110))
        surface.blit(veil, (VIDEO_RECT.x + 4, VIDEO_RECT.y + 4))
        play_rect = pygame.Rect(0, 0, 90, 70)
        play_rect.center = center
        pygame.draw.rect(surface, PANEL_MID, play_rect)
        pygame.draw.rect(surface, INK_BRIGHT, play_rect, 3)
        pygame.draw.polygon(
            surface,
            INK_BRIGHT,
            [(center[0] - 12, center[1] - 21), (center[0] + 22, center[1]), (center[0] - 12, center[1] + 21)],
        )
        self._draw_text(
            surface,
            "CONTINUAR",
            self.font_small,
            INK_BRIGHT,
            (center[0], center[1] + 58),
            anchor="center",
        )

    def _draw_close_button(self, surface: pygame.Surface) -> None:
        hovered = self.hovered_control == "close"
        fill = PANEL_MID if hovered else PANEL_DARK
        border = INK_BRIGHT if hovered else BORDER_LIGHT
        self._draw_layered_rect(surface, POPUP_CLOSE_RECT, fill, border)
        center_x, center_y = POPUP_CLOSE_RECT.center
        color = INK_BRIGHT if hovered else INK
        pygame.draw.line(surface, color, (center_x - 9, center_y - 9), (center_x + 9, center_y + 9), 3)
        pygame.draw.line(surface, color, (center_x + 9, center_y - 9), (center_x - 9, center_y + 9), 3)

    def _draw_layered_rect(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        fill: tuple[int, int, int],
        border: tuple[int, int, int],
    ) -> None:
        pygame.draw.rect(surface, BORDER_DARK, rect.move(3, 3))
        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, border, rect, 2)
        pygame.draw.line(surface, (*border,), rect.topleft, (rect.right - 1, rect.top), 1)

    def _draw_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
        line_height: int,
        max_lines: int,
    ) -> int:
        words = text.split()
        lines: list[str] = []
        current = ""

        for word in words:
            candidate = f"{current} {word}".strip()
            if not current or font.size(candidate)[0] <= rect.width:
                current = candidate
                continue

            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break

        if current and len(lines) < max_lines:
            lines.append(current)

        for index, line in enumerate(lines):
            self._draw_text(surface, line, font, color, (rect.x, rect.y + index * line_height))

        return max(1, len(lines))

    @staticmethod
    def _make_font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)

    @staticmethod
    def _fit_portrait(image: pygame.Surface) -> pygame.Surface:
        canvas = pygame.Surface((64, 64), pygame.SRCALPHA)
        scale = min(64 / image.get_width(), 64 / image.get_height())
        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )
        scaled = pygame.transform.scale(image, size)
        canvas.blit(scaled, scaled.get_rect(center=canvas.get_rect().center))
        return canvas

    @staticmethod
    def _draw_text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
        anchor: str = "topleft",
    ) -> None:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
