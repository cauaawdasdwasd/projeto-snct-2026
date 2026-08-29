from __future__ import annotations

import pygame

from src.gameplay.cases import AuditCase
from src.gameplay.protocols import PROTOCOLS, Protocol


INK = (216, 221, 132)
INK_BRIGHT = (247, 239, 161)
INK_MUTED = (132, 142, 87)
SCREEN_BLACK = (5, 9, 8)
PANEL = (17, 23, 20)
PANEL_MID = (29, 36, 30)
BORDER = (127, 137, 80)
BORDER_DARK = (55, 64, 45)
PAPER = (180, 148, 83)

HINT_BUTTON_RECT = pygame.Rect(870, 72, 128, 34)
HINT_POPUP_RECT = pygame.Rect(385, 174, 786, 348)
HINT_CLOSE_RECT = pygame.Rect(1112, 191, 42, 42)
HINT_PROTOCOL_RECT = pygame.Rect(784, 450, 337, 48)


class CaseHint:
    """Contextual case hint that points to one protocol without giving the stamp away."""

    def __init__(self, case: AuditCase) -> None:
        self.case = case
        self.protocol = self._protocol_for_case(case)
        self.is_open = False
        self.hovered_control: str | None = None
        self.font_tiny = self._font(15)
        self.font_small = self._font(18)
        self.font_body = self._font(21)
        self.font_body_bold = self._font(21, bold=True)
        self.font_title = self._font(29, bold=True)

    def close(self) -> None:
        self.is_open = False
        self.hovered_control = None

    def handle_mouse_down(self, position: tuple[int, int]) -> str | None:
        if not self.is_open:
            if HINT_BUTTON_RECT.collidepoint(position):
                self.is_open = True
                return "open"
            return None

        if HINT_CLOSE_RECT.collidepoint(position):
            self.close()
            return "close"
        if HINT_PROTOCOL_RECT.collidepoint(position):
            self.close()
            return "open_protocol"
        return "consume"

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered_control = None
        if position is None:
            return
        if self.is_open:
            if HINT_CLOSE_RECT.collidepoint(position):
                self.hovered_control = "close"
            elif HINT_PROTOCOL_RECT.collidepoint(position):
                self.hovered_control = "protocol"
        elif HINT_BUTTON_RECT.collidepoint(position):
            self.hovered_control = "hint"

    def render_button(self, surface: pygame.Surface) -> None:
        hovered = self.hovered_control == "hint"
        pygame.draw.rect(surface, PANEL_MID if hovered else SCREEN_BLACK, HINT_BUTTON_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if hovered else BORDER_DARK, HINT_BUTTON_RECT, 2)

        icon_rect = pygame.Rect(HINT_BUTTON_RECT.x + 8, HINT_BUTTON_RECT.y + 5, 24, 24)
        pygame.draw.rect(surface, PAPER if hovered else PANEL_MID, icon_rect)
        pygame.draw.rect(surface, INK_BRIGHT if hovered else BORDER, icon_rect, 2)
        self._draw_text(
            surface,
            "?",
            self.font_body_bold,
            SCREEN_BLACK if hovered else INK_BRIGHT,
            icon_rect.center,
            anchor="center",
        )
        self._draw_text(
            surface,
            "DICA",
            self.font_small,
            INK_BRIGHT if hovered else INK,
            (HINT_BUTTON_RECT.x + 42, HINT_BUTTON_RECT.y + 7),
        )

    def render_popup(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 218))
        surface.blit(dim, (0, 0))

        self._draw_layered_rect(surface, HINT_POPUP_RECT, SCREEN_BLACK, BORDER)
        self._draw_text(surface, "DICA DE AUDITORIA", self.font_title, INK_BRIGHT, (421, 207))
        pygame.draw.line(surface, BORDER_DARK, (421, 251), (1136, 251), 2)

        self._draw_text(surface, "PROTOCOLO RECOMENDADO", self.font_tiny, INK_MUTED, (423, 278))
        protocol_label = f"{self.protocol.number:02d}  {self.protocol.scientist.upper()}"
        self._draw_text(surface, protocol_label, self.font_body_bold, PAPER, (423, 304))
        self._draw_text(surface, self.protocol.title.upper(), self.font_small, INK, (423, 337))

        hint_rect = pygame.Rect(421, 374, 714, 58)
        pygame.draw.rect(surface, PANEL, hint_rect)
        pygame.draw.rect(surface, BORDER_DARK, hint_rect, 2)
        self._draw_wrapped_text(
            surface,
            self.case.hint,
            self.font_small,
            INK,
            hint_rect.inflate(-18, -12),
            line_height=21,
            max_lines=2,
        )

        self._draw_button(
            surface,
            HINT_PROTOCOL_RECT,
            "ABRIR PROTOCOLO",
            self.hovered_control == "protocol",
        )
        self._draw_close(surface)

    def _draw_close(self, surface: pygame.Surface) -> None:
        hovered = self.hovered_control == "close"
        pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, HINT_CLOSE_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if hovered else BORDER, HINT_CLOSE_RECT, 2)
        center_x, center_y = HINT_CLOSE_RECT.center
        color = INK_BRIGHT if hovered else INK
        pygame.draw.line(surface, color, (center_x - 8, center_y - 8), (center_x + 8, center_y + 8), 3)
        pygame.draw.line(surface, color, (center_x + 8, center_y - 8), (center_x - 8, center_y + 8), 3)

    def _draw_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        hovered: bool,
    ) -> None:
        pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, rect)
        pygame.draw.rect(surface, INK_BRIGHT if hovered else BORDER, rect, 2)
        self._draw_text(surface, label, self.font_body_bold, INK_BRIGHT, rect.center, anchor="center")

    @staticmethod
    def _protocol_for_case(case: AuditCase) -> Protocol:
        for protocol in PROTOCOLS:
            if protocol.slug == case.protocol_focus:
                return protocol
        raise ValueError(f"Unknown protocol for case: {case.protocol_focus}")

    @staticmethod
    def _draw_layered_rect(
        surface: pygame.Surface,
        rect: pygame.Rect,
        fill: tuple[int, int, int],
        border: tuple[int, int, int],
    ) -> None:
        pygame.draw.rect(surface, BORDER_DARK, rect.move(4, 4))
        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, border, rect, 3)

    def _draw_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
        *,
        line_height: int,
        max_lines: int,
    ) -> None:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if not current or font.size(candidate)[0] <= rect.width:
                current = candidate
            else:
                lines.append(current)
                current = word
            if len(lines) >= max_lines:
                break
        if current and len(lines) < max_lines:
            lines.append(current)
        for index, line in enumerate(lines):
            self._draw_text(surface, line, font, color, (rect.x, rect.y + index * line_height))

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
