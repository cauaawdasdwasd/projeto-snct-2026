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

BRIEFING_RECT = pygame.Rect(120, 20, 1314, 656)
BRIEFING_START_RECT = pygame.Rect(1030, 602, 368, 46)

CONFIRM_RECT = pygame.Rect(354, 168, 846, 350)
CONFIRM_YES_RECT = pygame.Rect(756, 431, 393, 58)
CONFIRM_NO_RECT = pygame.Rect(405, 431, 319, 58)

STAMP_LABELS = {
    "approve": "APROVAR",
    "deny": "NEGAR",
    "review": "REVISÃO HUMANA",
    "violation": "VIOLAÇÃO",
    "timeout": "TEMPO ESGOTADO",
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
        self.reopened = False
        self.pending_stamp_id: str | None = None
        self.hovered_control: str | None = None
        self.font_tiny = self._font(15)
        self.font_small = self._font(18)
        self.font_body = self._font(22)
        self.font_story = self._font(20)
        self.font_body_bold = self._font(22, bold=True)
        self.font_title = self._font(31, bold=True)
        self.font_header = self._font(38, bold=True)

    @property
    def is_open(self) -> bool:
        return self.mode is not None

    def request_confirmation(self, stamp_id: str) -> None:
        self.pending_stamp_id = stamp_id
        self.mode = "confirm"

    def reopen(self) -> None:
        """Show the case dossier again without touching the case progress."""
        self.mode = "briefing"
        self.reopened = True
        self.hovered_control = None

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
        dim.fill((0, 0, 0, 255))
        surface.blit(dim, (0, 0))

        if self.mode == "briefing":
            self._render_briefing(surface)
        elif self.mode == "confirm":
            self._render_confirmation(surface)

    def _render_briefing(self, surface: pygame.Surface) -> None:
        case = self.case
        self._draw_layered_rect(surface, BRIEFING_RECT, SCREEN_BLACK, BORDER)
        left = BRIEFING_RECT.x + 36
        eyebrow = "TREINAMENTO GUIADO" if case.is_tutorial else f"CASO {case.sequence:02d}  ·  {case.newspaper_section}"
        self._draw_text(surface, eyebrow, self.font_small, PAPER, (left, BRIEFING_RECT.y + 22))
        self._draw_text(surface, case.title.upper(), self.font_header, INK_BRIGHT, (left, BRIEFING_RECT.y + 46))
        self._draw_text(
            surface,
            "DOSSIÊ DO CASO — leia com calma, você pode reabrir quando quiser",
            self.font_tiny,
            INK_MUTED,
            (BRIEFING_RECT.right - 36, BRIEFING_RECT.y + 30),
            anchor="topright",
        )
        pygame.draw.line(surface, BORDER, (left, BRIEFING_RECT.y + 96), (BRIEFING_RECT.right - 36, BRIEFING_RECT.y + 96), 3)

        # left column: the story, the papers on the desk and what to look at
        text_width = 700
        y = BRIEFING_RECT.y + 112
        self._draw_text(surface, "A HISTÓRIA", self.font_tiny, PAPER, (left, y))
        self._draw_wrapped_text(
            surface,
            case.story or case.briefing,
            self.font_story,
            INK,
            pygame.Rect(left, y + 24, text_width, 240),
            line_height=25,
            max_lines=9,
        )
        y = BRIEFING_RECT.y + 372
        papers_label = "DOCUMENTOS-CHAVE (JÁ ESTÃO NA MESA)" if case.is_tutorial else "OS PAPÉIS JÁ ESTÃO NA MESA — LEIA NESTA ORDEM"
        self._draw_text(surface, papers_label, self.font_tiny, PAPER, (left, y))
        for index, document in enumerate(case.documents[:4]):
            self._draw_text(surface, f"{index + 1}   {document.title}", self.font_small, INK_BRIGHT, (left + 8, y + 20 + index * 22))
            if document.issuer:
                self._draw_text(surface, f"emitido por {document.issuer}", self.font_tiny, INK_MUTED, (left + 420, y + 24 + index * 22))
        y = BRIEFING_RECT.y + 506
        pygame.draw.line(surface, BORDER_DARK, (left, y - 8), (left + text_width, y - 8), 2)
        self._draw_text(surface, "O QUE CHAMA ATENÇÃO", self.font_tiny, AMBER, (left, y))
        self._draw_wrapped_text(
            surface,
            case.attention,
            self.font_small,
            INK_BRIGHT,
            pygame.Rect(left, y + 22, text_width, 96),
            line_height=24,
            max_lines=4,
        )

        # right column: what the AI decided and the question to answer
        right = left + text_width + 44
        width = BRIEFING_RECT.right - 36 - right
        ai = case.ai_decision
        decision_rect = pygame.Rect(right, BRIEFING_RECT.y + 112, width, 218)
        pygame.draw.rect(surface, PANEL, decision_rect)
        pygame.draw.rect(surface, BORDER_DARK, decision_rect, 2)
        self._draw_text(surface, "O QUE A IA DECIDIU", self.font_tiny, PAPER, (decision_rect.x + 16, decision_rect.y + 14))
        self._draw_wrapped_text(
            surface,
            ai.verdict,
            self.font_title,
            INK_BRIGHT,
            pygame.Rect(decision_rect.x + 16, decision_rect.y + 40, width - 32, 70),
            line_height=32,
            max_lines=2,
        )
        self._draw_text(
            surface,
            f"{ai.model_name}  ·  confiança {ai.confidence}",
            self.font_tiny,
            INK_MUTED,
            (decision_rect.x + 16, decision_rect.y + 104),
        )
        self._draw_text(surface, "MOTIVO DADO PELA IA", self.font_tiny, PAPER, (decision_rect.x + 16, decision_rect.y + 130))
        self._draw_wrapped_text(
            surface,
            f"“{ai.reason}”",
            self.font_small,
            INK,
            pygame.Rect(decision_rect.x + 16, decision_rect.y + 152, width - 32, 64),
            line_height=23,
            max_lines=3,
        )
        mission_rect = pygame.Rect(right, decision_rect.bottom + 14, width, 132)
        pygame.draw.rect(surface, PANEL_MID, mission_rect)
        pygame.draw.rect(surface, BORDER, mission_rect, 2)
        self._draw_text(surface, "SUA MISSÃO: RESPONDER", self.font_tiny, AMBER, (mission_rect.x + 16, mission_rect.y + 14))
        self._draw_wrapped_text(
            surface,
            case.review_question,
            self.font_body_bold,
            INK_BRIGHT,
            pygame.Rect(mission_rect.x + 16, mission_rect.y + 42, width - 32, 86),
            line_height=27,
            max_lines=3,
        )

        # how to play: explicit steps in the training, general ones afterwards
        if case.is_tutorial:
            steps = (
                "1. Abra a decisão da IA.",
                "2. Os papéis já estão na mesa: compare os dados destacados.",
                "3. Abra a FOLHA DE AUDITORIA (painel da direita) e carimbe.",
                "4. Assine a folha e envie.",
            )
        else:
            steps = (
                "1. Abra a decisão da IA.",
                "2. Leia os papéis 1, 2, 3... e compare os dados amarelos.",
                "3. Ao comparar, o jogo diz qual protocolo consultar.",
                "4. Abra a FOLHA DE AUDITORIA, carimbe, assine e envie.",
            )
        steps_top = mission_rect.bottom + 12
        for index, step in enumerate(steps):
            self._draw_text(surface, step, self.font_tiny, INK_MUTED, (right, steps_top + index * 20))

        self._draw_button(
            surface,
            BRIEFING_START_RECT,
            "CONTINUAR AUDITORIA" if self.reopened else "COMEÇAR AUDITORIA",
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
