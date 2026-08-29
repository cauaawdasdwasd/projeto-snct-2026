from __future__ import annotations

import pygame

from src.gameplay.cases import AuditCase


INK = (216, 221, 132)
INK_BRIGHT = (247, 239, 161)
INK_MUTED = (132, 142, 87)
SCREEN_BLACK = (5, 9, 8)
PANEL = (17, 23, 20)
PANEL_MID = (29, 36, 30)
BORDER = (127, 137, 80)
BORDER_DARK = (55, 64, 45)
PAPER = (180, 148, 83)
GREEN = (99, 164, 72)
RED = (205, 76, 61)
BLUE = (93, 159, 177)
AMBER = (211, 149, 47)
PURPLE = (143, 74, 154)

BRIEFING_RECT = pygame.Rect(273, 118, 1008, 462)
BRIEFING_START_RECT = pygame.Rect(884, 499, 342, 57)

CONFIRM_RECT = pygame.Rect(354, 168, 846, 350)
CONFIRM_YES_RECT = pygame.Rect(756, 431, 393, 58)
CONFIRM_NO_RECT = pygame.Rect(405, 431, 319, 58)

STAMP_LABELS = {
    "approve": "APROVAR",
    "deny": "NEGAR",
    "review": "REVISÃO HUMANA",
    "violation": "VIOLAÇÃO",
}

STAMP_COLORS = {
    "approve": GREEN,
    "deny": RED,
    "review": AMBER,
    "violation": PURPLE,
}


class CaseDialog:
    """Briefing, decision confirmation and end-of-case feedback overlays."""

    def __init__(self, case: AuditCase) -> None:
        self.case = case
        self.mode: str | None = "briefing"
        self.pending_stamp_id: str | None = None
        self.hovered_control: str | None = None
        self.font_tiny = self._font(15)
        self.font_small = self._font(18)
        self.font_body = self._font(22)
        self.font_body_bold = self._font(22, bold=True)
        self.font_title = self._font(31, bold=True)
        self.font_header = self._font(38, bold=True)

    @property
    def is_open(self) -> bool:
        return self.mode is not None

    def request_confirmation(self, stamp_id: str) -> None:
        self.pending_stamp_id = stamp_id
        self.mode = "confirm"

    def reset(self) -> None:
        self.pending_stamp_id = None
        self.mode = "briefing"

    def handle_escape(self) -> bool:
        if self.mode == "confirm":
            self.pending_stamp_id = None
            self.mode = None
            return True
        if self.mode == "briefing":
            self.mode = None
            return True
        return False

    def handle_mouse_down(self, position: tuple[int, int]) -> str | None:
        if self.mode == "briefing":
            if BRIEFING_START_RECT.collidepoint(position):
                self.mode = None
                return "start"
            return "consume"

        if self.mode == "confirm":
            if CONFIRM_NO_RECT.collidepoint(position):
                self.pending_stamp_id = None
                self.mode = None
                return "cancel"
            if CONFIRM_YES_RECT.collidepoint(position) and self.pending_stamp_id is not None:
                return f"confirm:{self.pending_stamp_id}"
            return "consume"

        return None

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered_control = None
        if position is None:
            return
        controls: tuple[tuple[str, pygame.Rect], ...]
        if self.mode == "briefing":
            controls = (("start", BRIEFING_START_RECT),)
        elif self.mode == "confirm":
            controls = (("no", CONFIRM_NO_RECT), ("yes", CONFIRM_YES_RECT))
        else:
            controls = ()
        for control, rect in controls:
            if rect.collidepoint(position):
                self.hovered_control = control
                return

    def render(self, surface: pygame.Surface) -> None:
        if self.mode is None:
            return
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 220))
        surface.blit(dim, (0, 0))

        if self.mode == "briefing":
            self._render_briefing(surface)
        elif self.mode == "confirm":
            self._render_confirmation(surface)

    def _render_briefing(self, surface: pygame.Surface) -> None:
        self._draw_layered_rect(surface, BRIEFING_RECT, SCREEN_BLACK, BORDER)
        self._draw_text(surface, f"CASO {self.case.sequence:02d}", self.font_small, PAPER, (310, 151))
        self._draw_text(surface, self.case.title.upper(), self.font_header, INK_BRIGHT, (310, 184))
        pygame.draw.line(surface, BORDER, (310, 235), (1241, 235), 3)
        self._draw_wrapped_text(
            surface,
            self.case.briefing,
            self.font_body,
            INK,
            pygame.Rect(310, 267, 900, 126),
            line_height=31,
            max_lines=4,
        )

        steps = (
            "1. Abra e compare os documentos.",
            "2. Consulte os protocolos e a decisão da IA.",
            "3. Escolha um carimbo e aplique na folha de auditoria.",
        )
        for index, step in enumerate(steps):
            y = 405 + index * 33
            self._draw_text(surface, step, self.font_small, INK_MUTED, (312, y))

        self._draw_button(
            surface,
            BRIEFING_START_RECT,
            "ABRIR CASO",
            self.hovered_control == "start",
        )

    def _render_confirmation(self, surface: pygame.Surface) -> None:
        stamp_id = self.pending_stamp_id or "deny"
        stamp_label = STAMP_LABELS.get(stamp_id, stamp_id.upper())
        stamp_color = STAMP_COLORS.get(stamp_id, INK_BRIGHT)
        self._draw_layered_rect(surface, CONFIRM_RECT, SCREEN_BLACK, BORDER)
        self._draw_text(surface, "CONFIRMAR DECISÃO", self.font_title, INK_BRIGHT, (405, 207))
        pygame.draw.line(surface, BORDER_DARK, (405, 251), (1148, 251), 2)
        self._draw_text(
            surface,
            "Você tem certeza de sua decisão?",
            self.font_body,
            INK,
            (777, 296),
            anchor="center",
        )
        stamp_rect = pygame.Rect(536, 337, 483, 62)
        pygame.draw.rect(surface, PANEL_MID, stamp_rect)
        pygame.draw.rect(surface, stamp_color, stamp_rect, 3)
        self._draw_text(surface, stamp_label, self.font_title, stamp_color, stamp_rect.center, anchor="center")
        self._draw_button(surface, CONFIRM_NO_RECT, "CANCELAR", self.hovered_control == "no")
        self._draw_button(surface, CONFIRM_YES_RECT, "CONFIRMAR", self.hovered_control == "yes")

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
