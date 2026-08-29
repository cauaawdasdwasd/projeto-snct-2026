from __future__ import annotations

import pygame

from src.gameplay.cases import AuditCase


INK = (214, 219, 128)
INK_BRIGHT = (245, 237, 156)
INK_MUTED = (128, 139, 84)
SCREEN_BLACK = (5, 9, 8)
PANEL = (16, 22, 19)
PANEL_MID = (27, 34, 28)
BORDER = (126, 136, 78)
BORDER_DARK = (53, 62, 43)
RED = (211, 82, 67)
GREEN = (104, 169, 74)
PAPER = (177, 147, 86)

DECISION_CONTENT_RECT = pygame.Rect(1212, 79, 302, 201)
OPEN_BUTTON_RECT = pygame.Rect(1220, 230, 286, 43)
DATA_VIEW_RECT = pygame.Rect(1206, 395, 322, 237)
DATA_ROWS_RECT = pygame.Rect(1212, 405, 286, 212)
DATA_SCROLL_UP_RECT = pygame.Rect(1506, 395, 22, 25)
DATA_SCROLL_TRACK_RECT = pygame.Rect(1506, 424, 22, 179)
DATA_SCROLL_DOWN_RECT = pygame.Rect(1506, 607, 22, 25)
DATA_ROW_HEIGHT = 68
DATA_ROW_GAP = 4
VISIBLE_DATA_ROWS = 3

POPUP_RECT = pygame.Rect(90, 42, 1374, 612)
CLOSE_RECT = pygame.Rect(1397, 59, 43, 43)
AI_ID_RECT = pygame.Rect(807, 331, 556, 126)


class AIDecisionPanel:
    """Compact decision summary, data shortcuts and detailed AI report."""

    def __init__(self, case: AuditCase) -> None:
        self.case = case
        self.popup_open = False
        self.data_scroll_offset = 0
        self.dragging_scroll_thumb = False
        self.scroll_drag_offset = 0
        self.hovered_control: str | None = None
        self.font_tiny = self._font(14)
        self.font_small = self._font(17)
        self.font_body = self._font(20)
        self.font_body_bold = self._font(20, bold=True)
        self.font_title = self._font(27, bold=True)
        self.font_header = self._font(33, bold=True)

    def close(self) -> None:
        self.popup_open = False
        self.dragging_scroll_thumb = False

    def handle_panel_mouse_down(self, position: tuple[int, int]) -> tuple[str, str | None] | None:
        if OPEN_BUTTON_RECT.collidepoint(position):
            self.popup_open = True
            return "open", None

        if DATA_SCROLL_UP_RECT.collidepoint(position):
            self._scroll_data(-1)
            return "scroll", None
        if DATA_SCROLL_DOWN_RECT.collidepoint(position):
            self._scroll_data(1)
            return "scroll", None

        thumb_rect = self._scroll_thumb_rect()
        if thumb_rect.collidepoint(position) and self._maximum_scroll > 0:
            self.dragging_scroll_thumb = True
            self.scroll_drag_offset = position[1] - thumb_rect.y
            return "scroll", None
        if DATA_SCROLL_TRACK_RECT.collidepoint(position):
            direction = -VISIBLE_DATA_ROWS if position[1] < thumb_rect.y else VISIBLE_DATA_ROWS
            self._scroll_data(direction)
            return "scroll", None

        for visible_index, rect in enumerate(self._visible_row_rects()):
            if rect.collidepoint(position):
                source_index = self.data_scroll_offset + visible_index
                if source_index >= len(self.case.data_sources):
                    return "scroll", None
                source = self.case.data_sources[source_index]
                return "toggle", source.document_id
        return None

    def handle_wheel(self, wheel_y: int, position: tuple[int, int] | None) -> bool:
        if self.popup_open or position is None or not DATA_VIEW_RECT.collidepoint(position):
            return False
        self._scroll_data(-wheel_y)
        return True

    def handle_mouse_motion(self, position: tuple[int, int] | None) -> None:
        if not self.dragging_scroll_thumb or position is None or self._maximum_scroll <= 0:
            return
        thumb = self._scroll_thumb_rect()
        travel = DATA_SCROLL_TRACK_RECT.height - thumb.height
        if travel <= 0:
            return
        top = position[1] - self.scroll_drag_offset
        ratio = (top - DATA_SCROLL_TRACK_RECT.y) / travel
        self._set_scroll_offset(round(max(0.0, min(1.0, ratio)) * self._maximum_scroll))

    def handle_mouse_up(self) -> None:
        self.dragging_scroll_thumb = False

    def handle_popup_mouse_down(
        self,
        position: tuple[int, int],
        notes: dict[str, str],
    ) -> bool:
        if not self.popup_open:
            return False

        if CLOSE_RECT.collidepoint(position):
            self.close()
            return True

        if AI_ID_RECT.collidepoint(position):
            key = self.case.ai_decision.evidence_key
            if key in notes:
                del notes[key]
            else:
                notes[key] = self.case.ai_decision.evidence_note
            return True

        return POPUP_RECT.collidepoint(position)

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered_control = None
        if position is None:
            return

        if self.popup_open:
            if CLOSE_RECT.collidepoint(position):
                self.hovered_control = "close"
            elif AI_ID_RECT.collidepoint(position):
                self.hovered_control = "ai_id"
            return

        if OPEN_BUTTON_RECT.collidepoint(position):
            self.hovered_control = "open"
            return
        if DATA_SCROLL_UP_RECT.collidepoint(position):
            self.hovered_control = "scroll_up"
            return
        if DATA_SCROLL_DOWN_RECT.collidepoint(position):
            self.hovered_control = "scroll_down"
            return
        if self._scroll_thumb_rect().collidepoint(position):
            self.hovered_control = "scroll_thumb"
            return
        if DATA_SCROLL_TRACK_RECT.collidepoint(position):
            self.hovered_control = "scroll_track"
            return
        for index, rect in enumerate(self._visible_row_rects()):
            if rect.collidepoint(position):
                self.hovered_control = f"row_{index}"
                return

    def render_panel(
        self,
        surface: pygame.Surface,
        visible_document_ids: set[str] | None = None,
    ) -> None:
        visible_document_ids = visible_document_ids or set()
        verdict_color = self._verdict_color
        pygame.draw.rect(surface, SCREEN_BLACK, DECISION_CONTENT_RECT)
        pygame.draw.rect(surface, BORDER_DARK, DECISION_CONTENT_RECT, 2)
        self._draw_text(surface, "RESULTADO", self.font_tiny, INK_MUTED, (1220, 86))
        self._draw_wrapped_text(
            surface,
            self.case.ai_decision.verdict,
            self.font_title,
            verdict_color,
            pygame.Rect(1220, 111, 286, 51),
            line_height=28,
            max_lines=2,
        )
        self._draw_text(
            surface,
            f"CONFIANÇA: {self.case.ai_decision.confidence}",
            self.font_small,
            INK,
            (1220, 175),
        )
        self._draw_wrapped_text(
            surface,
            self.case.ai_decision.reason,
            self.font_tiny,
            INK_MUTED,
            pygame.Rect(1220, 199, 286, 31),
            line_height=16,
            max_lines=2,
        )
        self._draw_button(
            surface,
            OPEN_BUTTON_RECT,
            "ABRIR DECISÃO",
            self.hovered_control == "open",
        )

        for visible_index, rect in enumerate(self._visible_row_rects()):
            source_index = self.data_scroll_offset + visible_index
            if source_index >= len(self.case.data_sources):
                break
            source = self.case.data_sources[source_index]
            on_desk = source.document_id in visible_document_ids
            hovered = self.hovered_control == f"row_{visible_index}"
            pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, rect)
            pygame.draw.rect(surface, INK_BRIGHT if hovered else BORDER_DARK, rect, 2)
            state_rect = pygame.Rect(rect.x + 9, rect.y + 9, 18, 18)
            pygame.draw.rect(surface, GREEN if on_desk else BORDER_DARK, state_rect, 2)
            if on_desk:
                pygame.draw.rect(surface, GREEN, state_rect.inflate(-6, -6))
            self._draw_text(surface, source.label.upper(), self.font_tiny, INK, (rect.x + 37, rect.y + 4))
            action = "NA MESA — CLIQUE PARA RETIRAR" if on_desk else "CLIQUE PARA COLOCAR NA MESA"
            self._draw_text(surface, action, self.font_tiny, GREEN if on_desk else INK_MUTED, (rect.x + 37, rect.y + 24))
        self._draw_data_scrollbar(surface)

    def render_popup(self, surface: pygame.Surface, notes: dict[str, str]) -> None:
        if not self.popup_open:
            return

        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 215))
        surface.blit(dim, (0, 0))
        self._draw_layered_rect(surface, POPUP_RECT, SCREEN_BLACK, BORDER)

        header_rect = pygame.Rect(108, 59, 1334, 86)
        pygame.draw.rect(surface, PANEL_MID, header_rect)
        pygame.draw.line(surface, BORDER, header_rect.bottomleft, header_rect.bottomright, 3)
        self._draw_text(surface, "RELATÓRIO DE DECISÃO DA IA", self.font_header, INK_BRIGHT, (129, 76))
        self._draw_text(
            surface,
            f"{self.case.ai_decision.model_name}  |  CASO {self.case.sequence:03d}/2026",
            self.font_small,
            INK_MUTED,
            (132, 116),
        )
        self._draw_close(surface)

        left = pygame.Rect(130, 176, 610, 430)
        right = pygame.Rect(785, 176, 600, 430)
        self._draw_layered_rect(surface, left, PANEL, BORDER_DARK)
        self._draw_layered_rect(surface, right, PANEL, BORDER_DARK)

        verdict_color = self._verdict_color
        self._draw_text(surface, "DECISÃO AUTOMÁTICA", self.font_body_bold, PAPER, (152, 196))
        verdict_rect = pygame.Rect(151, 238, 568, 88)
        verdict_fill = (23, 42, 23) if verdict_color == GREEN else (43, 22, 20)
        pygame.draw.rect(surface, verdict_fill, verdict_rect)
        pygame.draw.rect(surface, verdict_color, verdict_rect, 3)
        self._draw_text(
            surface,
            self.case.ai_decision.verdict,
            self.font_header,
            verdict_color,
            verdict_rect.center,
            anchor="center",
        )
        self._draw_text(surface, "JUSTIFICATIVA", self.font_tiny, INK_MUTED, (152, 357))
        self._draw_wrapped_text(
            surface,
            self.case.ai_decision.reason,
            self.font_body,
            INK,
            pygame.Rect(152, 384, 560, 70),
            line_height=25,
            max_lines=3,
        )
        self._draw_text(surface, "CONFIANÇA DO MODELO", self.font_tiny, INK_MUTED, (152, 482))
        pygame.draw.rect(surface, BORDER_DARK, (152, 514, 430, 27))
        confidence = max(0, min(100, int(self.case.ai_decision.confidence.rstrip("%"))))
        pygame.draw.rect(surface, verdict_color, (152, 514, round(430 * confidence / 100), 27))
        self._draw_text(surface, self.case.ai_decision.confidence, self.font_body_bold, INK_BRIGHT, (600, 514))
        self._draw_text(
            surface,
            "Confiança alta não substitui verificação.",
            self.font_small,
            INK_MUTED,
            (152, 561),
        )

        self._draw_text(surface, "COMO A IA CHEGOU NISSO", self.font_body_bold, PAPER, (807, 196))
        self._draw_text(surface, "1. DADOS CONSULTADOS", self.font_tiny, INK_MUTED, (807, 235))
        self._draw_wrapped_text(
            surface,
            self.case.ai_decision.source_document,
            self.font_body,
            INK,
            pygame.Rect(807, 258, 534, 48),
            line_height=24,
            max_lines=2,
        )
        hovered = self.hovered_control == "ai_id"
        marked = self.case.ai_decision.evidence_key in notes
        pygame.draw.rect(surface, PANEL_MID, AI_ID_RECT)
        pygame.draw.rect(
            surface,
            INK_BRIGHT if hovered or marked else BORDER,
            AI_ID_RECT,
            4 if hovered or marked else 2,
        )
        self._draw_text(surface, "2. O QUE A IA FEZ", self.font_tiny, INK_MUTED, (825, 342))
        self._draw_text(
            surface,
            self.case.ai_decision.evidence_value,
            self.font_title,
            INK_BRIGHT,
            (825, 367),
        )
        self._draw_wrapped_text(
            surface,
            self.case.ai_decision.evidence_note,
            self.font_small,
            INK,
            pygame.Rect(825, 405, 510, 39),
            line_height=19,
            max_lines=2,
        )
        annotation = "EVIDÊNCIA ANOTADA" if marked else "CLIQUE PARA ANOTAR"
        self._draw_text(surface, annotation, self.font_tiny, GREEN if marked else INK_MUTED, (1344, 342), anchor="topright")

        self._draw_text(surface, "3. SUA TAREFA", self.font_tiny, INK_MUTED, (807, 481))
        task_rect = pygame.Rect(807, 505, 556, 72)
        pygame.draw.rect(surface, SCREEN_BLACK, task_rect)
        pygame.draw.rect(surface, BORDER_DARK, task_rect, 2)
        task = (
            f"Confira nos documentos se {self.case.ai_decision.evidence_value} "
            f"realmente sustenta a decisão: {self.case.ai_decision.verdict}."
        )
        self._draw_wrapped_text(
            surface,
            task,
            self.font_small,
            INK,
            task_rect.inflate(-16, -12),
            line_height=21,
            max_lines=3,
        )

    def _draw_close(self, surface: pygame.Surface) -> None:
        hovered = self.hovered_control == "close"
        self._draw_button(surface, CLOSE_RECT, "×", hovered)

    @property
    def _maximum_scroll(self) -> int:
        return max(0, len(self.case.data_sources) - VISIBLE_DATA_ROWS)

    @property
    def _verdict_color(self) -> tuple[int, int, int]:
        verdict = self.case.ai_decision.verdict.upper()
        return GREEN if verdict.startswith(("APROVAR", "LIBERAR")) else RED

    def _visible_row_rects(self) -> tuple[pygame.Rect, ...]:
        return tuple(
            pygame.Rect(
                DATA_ROWS_RECT.x,
                DATA_ROWS_RECT.y + index * (DATA_ROW_HEIGHT + DATA_ROW_GAP),
                DATA_ROWS_RECT.width,
                DATA_ROW_HEIGHT,
            )
            for index in range(VISIBLE_DATA_ROWS)
        )

    def _set_scroll_offset(self, offset: int) -> None:
        self.data_scroll_offset = max(0, min(self._maximum_scroll, offset))

    def _scroll_data(self, direction: int) -> None:
        self._set_scroll_offset(self.data_scroll_offset + direction)

    def _scroll_thumb_rect(self) -> pygame.Rect:
        if not self.case.data_sources:
            return DATA_SCROLL_TRACK_RECT.copy()
        visible_ratio = min(1.0, VISIBLE_DATA_ROWS / len(self.case.data_sources))
        height = max(24, round(DATA_SCROLL_TRACK_RECT.height * visible_ratio))
        travel = DATA_SCROLL_TRACK_RECT.height - height
        progress = self.data_scroll_offset / self._maximum_scroll if self._maximum_scroll else 0.0
        return pygame.Rect(
            DATA_SCROLL_TRACK_RECT.x + 3,
            DATA_SCROLL_TRACK_RECT.y + round(travel * progress),
            DATA_SCROLL_TRACK_RECT.width - 6,
            height,
        )

    def _draw_data_scrollbar(self, surface: pygame.Surface) -> None:
        thumb = self._scroll_thumb_rect()
        thumb_active = self.hovered_control == "scroll_thumb" or self.dragging_scroll_thumb
        # The base PNG already contains the rail and its arrow buttons; draw only
        # the moving thumb so the interface does not acquire a second scrollbar.
        pygame.draw.rect(surface, (70, 79, 48) if thumb_active else (43, 51, 35), thumb)
        pygame.draw.rect(surface, INK_BRIGHT if thumb_active else INK_MUTED, thumb, 1)

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
        pygame.draw.rect(surface, BORDER_DARK, rect.move(3, 3))
        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, border, rect, 2)

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
