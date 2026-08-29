from __future__ import annotations

import pygame

from src.gameplay.cases import EvidenceSummary
from src.gameplay.document_renderer import EvidenceRegion
from src.ui.case_document import CaseDocument


INK = (218, 221, 134)
INK_BRIGHT = (246, 238, 159)
INK_MUTED = (132, 142, 88)
SCREEN_BLACK = (5, 9, 8)
PANEL = (17, 23, 20)
PANEL_MID = (28, 35, 29)
BORDER = (127, 136, 80)
BORDER_DARK = (55, 64, 45)
PAPER = (177, 147, 86)

PANEL_RECT = pygame.Rect(20, 18, 1514, 660)
DOCUMENT_VIEW_RECT = pygame.Rect(44, 94, 1028, 558)
NOTEBOOK_RECT = pygame.Rect(1092, 94, 418, 558)
CLOSE_RECT = pygame.Rect(1470, 35, 42, 42)
ZOOM_OUT_RECT = pygame.Rect(852, 37, 46, 40)
ZOOM_LABEL_RECT = pygame.Rect(904, 37, 105, 40)
ZOOM_IN_RECT = pygame.Rect(1015, 37, 46, 40)


class DocumentInspector:
    """Fullscreen document viewer with zoom, pan and evidence collection."""

    MIN_ZOOM = 0.65
    MAX_ZOOM = 3.5
    ZOOM_STEP = 0.2

    def __init__(self, evidence_summary: EvidenceSummary) -> None:
        self.evidence_summary = evidence_summary
        self.document: CaseDocument | None = None
        self.zoom = 1.0
        self.pan = pygame.Vector2(0, 0)
        self.panning = False
        self.pan_drag_offset = pygame.Vector2(0, 0)
        self.hovered_evidence_key: str | None = None
        self.font_tiny = self._font(15)
        self.font_small = self._font(18)
        self.font_body = self._font(21)
        self.font_body_bold = self._font(21, bold=True)
        self.font_title = self._font(28, bold=True)

    @property
    def is_open(self) -> bool:
        return self.document is not None

    def open(self, document: CaseDocument) -> None:
        self.document = document
        self.zoom = 1.0
        self.pan.update(0, 0)
        self.panning = False
        self.hovered_evidence_key = None

    def close(self) -> None:
        self.document = None
        self.panning = False
        self.hovered_evidence_key = None

    def handle_mouse_down(
        self,
        position: tuple[int, int],
        notes: dict[str, str],
    ) -> bool:
        document = self.document
        if document is None:
            return False

        if CLOSE_RECT.collidepoint(position):
            self.close()
            return True

        if ZOOM_OUT_RECT.collidepoint(position):
            self._change_zoom(-self.ZOOM_STEP, DOCUMENT_VIEW_RECT.center)
            return True

        if ZOOM_IN_RECT.collidepoint(position):
            self._change_zoom(self.ZOOM_STEP, DOCUMENT_VIEW_RECT.center)
            return True

        if ZOOM_LABEL_RECT.collidepoint(position):
            self._set_zoom(1.0, DOCUMENT_VIEW_RECT.center)
            return True

        if not DOCUMENT_VIEW_RECT.collidepoint(position):
            return PANEL_RECT.collidepoint(position)

        evidence = self._evidence_at_display_position(position)
        if evidence is not None:
            if evidence.key in notes:
                del notes[evidence.key]
                document.set_evidence_marked(evidence.key, False)
            else:
                notes[evidence.key] = evidence.note
                document.set_evidence_marked(evidence.key, True)
            return True

        self.panning = True
        self.pan_drag_offset.update(position[0] - self.pan.x, position[1] - self.pan.y)
        return True

    def handle_mouse_up(self) -> None:
        self.panning = False

    def handle_mouse_motion(self, position: tuple[int, int] | None) -> None:
        if self.document is None or position is None:
            self.hovered_evidence_key = None
            return

        if self.panning:
            self.pan.update(
                position[0] - self.pan_drag_offset.x,
                position[1] - self.pan_drag_offset.y,
            )
            self._clamp_pan()

        evidence = self._evidence_at_display_position(position)
        self.hovered_evidence_key = evidence.key if evidence is not None else None

    def handle_wheel(
        self,
        wheel_y: int,
        focus_position: tuple[int, int] | None = None,
    ) -> None:
        if self.document is None or wheel_y == 0:
            return
        focus = (
            focus_position
            if focus_position is not None and DOCUMENT_VIEW_RECT.collidepoint(focus_position)
            else DOCUMENT_VIEW_RECT.center
        )
        self._change_zoom(self.ZOOM_STEP * wheel_y, focus)

    def render(self, surface: pygame.Surface, notes: dict[str, str]) -> None:
        document = self.document
        if document is None:
            return

        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 218))
        surface.blit(dim, (0, 0))
        self._draw_layered_rect(surface, PANEL_RECT, SCREEN_BLACK, BORDER)

        self._draw_text(surface, document.title.upper(), self.font_title, INK_BRIGHT, (45, 38))
        self._draw_text(
            surface,
            "RODA: ZOOM  |  ARRASTE: MOVER  |  CLIQUE EM CAMPOS: ANOTAR",
            self.font_tiny,
            INK_MUTED,
            (45, 70),
        )
        self._draw_zoom_controls(surface)
        self._draw_close(surface)

        pygame.draw.rect(surface, (2, 5, 4), DOCUMENT_VIEW_RECT)
        pygame.draw.rect(surface, BORDER_DARK, DOCUMENT_VIEW_RECT, 3)
        self._draw_document(surface, document)
        self._draw_notebook(surface, notes)

    def _draw_document(self, surface: pygame.Surface, document: CaseDocument) -> None:
        previous_clip = surface.get_clip()
        surface.set_clip(DOCUMENT_VIEW_RECT)
        display_rect = self._document_display_rect()
        rendered = pygame.transform.smoothscale(document.composed_surface(), display_rect.size)
        shadow = pygame.Surface(display_rect.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        surface.blit(shadow, display_rect.move(9, 9))
        surface.blit(rendered, display_rect)

        if self.hovered_evidence_key is not None:
            for evidence in document.evidence_regions:
                if evidence.key != self.hovered_evidence_key:
                    continue
                evidence_rect = self._source_rect_to_display(evidence.rect)
                glow = pygame.Surface(evidence_rect.size, pygame.SRCALPHA)
                glow.fill((244, 220, 70, 72))
                surface.blit(glow, evidence_rect)
                pygame.draw.rect(surface, (246, 225, 95), evidence_rect, 4)
                break

        surface.set_clip(previous_clip)

    def _draw_notebook(self, surface: pygame.Surface, notes: dict[str, str]) -> None:
        self._draw_layered_rect(surface, NOTEBOOK_RECT, PANEL, BORDER_DARK)
        self._draw_text(surface, "CADERNO DE EVIDÊNCIAS", self.font_body_bold, PAPER, (1112, 113))
        pygame.draw.line(surface, BORDER_DARK, (1111, 147), (1490, 147), 2)

        if not notes:
            self._draw_wrapped_text(
                surface,
                "Clique nos campos destacados dos documentos para guardar informações importantes.",
                self.font_body,
                INK_MUTED,
                pygame.Rect(1114, 170, 372, 110),
                line_height=26,
                max_lines=4,
            )
        else:
            y = 169
            comparison_visible = all(
                key in notes for key in self.evidence_summary.required_keys
            )
            visible_limit = 3 if comparison_visible else 4
            visible_notes = list(notes.values())[:visible_limit]
            for note in visible_notes:
                note_rect = pygame.Rect(1112, y, 377, 78)
                pygame.draw.rect(surface, PANEL_MID, note_rect)
                pygame.draw.rect(surface, BORDER_DARK, note_rect, 2)
                pygame.draw.rect(surface, INK_MUTED, (1123, y + 13, 10, 10))
                self._draw_wrapped_text(
                    surface,
                    note,
                    self.font_small,
                    INK,
                    pygame.Rect(1144, y + 10, 332, 61),
                    line_height=20,
                    max_lines=3,
                )
                y += 88

            hidden_count = len(notes) - len(visible_notes)
            if hidden_count > 0:
                self._draw_text(
                    surface,
                    f"+ {hidden_count} evidência adicional",
                    self.font_tiny,
                    INK_MUTED,
                    (1120, 438),
                )

        if all(key in notes for key in self.evidence_summary.required_keys):
            comparison_rect = pygame.Rect(1112, 478, 377, 148)
            pygame.draw.rect(surface, (35, 30, 20), comparison_rect)
            pygame.draw.rect(surface, (201, 156, 44), comparison_rect, 3)
            self._draw_text(
                surface,
                "CONCLUSÃO OBJETIVA",
                self.font_body_bold,
                (225, 184, 74),
                (1128, 491),
            )
            for index, line in enumerate(self.evidence_summary.lines[:3]):
                self._draw_text(
                    surface,
                    line,
                    self.font_tiny,
                    INK_BRIGHT,
                    (1128, 524 + index * 22),
                )
            self._draw_wrapped_text(
                surface,
                self.evidence_summary.conclusion,
                self.font_tiny,
                (225, 184, 74),
                pygame.Rect(1128, 593, 342, 30),
                line_height=17,
                max_lines=2,
            )

    def _draw_zoom_controls(self, surface: pygame.Surface) -> None:
        self._draw_button(surface, ZOOM_OUT_RECT, "−")
        self._draw_button(surface, ZOOM_IN_RECT, "+")
        pygame.draw.rect(surface, PANEL, ZOOM_LABEL_RECT)
        pygame.draw.rect(surface, BORDER_DARK, ZOOM_LABEL_RECT, 2)
        self._draw_text(
            surface,
            f"{round(self.zoom * 100)}%",
            self.font_body,
            INK,
            ZOOM_LABEL_RECT.center,
            anchor="center",
        )

    def _draw_close(self, surface: pygame.Surface) -> None:
        self._draw_button(surface, CLOSE_RECT, "×")

    def _draw_button(self, surface: pygame.Surface, rect: pygame.Rect, label: str) -> None:
        pygame.draw.rect(surface, PANEL_MID, rect)
        pygame.draw.rect(surface, BORDER, rect, 2)
        self._draw_text(surface, label, self.font_title, INK_BRIGHT, rect.center, anchor="center")

    def _change_zoom(
        self,
        delta: float,
        focus_position: tuple[int, int],
    ) -> None:
        self._set_zoom(self.zoom + delta, focus_position)

    def _set_zoom(
        self,
        zoom: float,
        focus_position: tuple[int, int],
    ) -> None:
        old_zoom = self.zoom
        new_zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, zoom))
        if new_zoom == old_zoom:
            return

        old_center = pygame.Vector2(DOCUMENT_VIEW_RECT.center) + self.pan
        focus = pygame.Vector2(focus_position)
        ratio = new_zoom / old_zoom
        new_center = focus - (focus - old_center) * ratio
        self.zoom = new_zoom
        self.pan.update(new_center - pygame.Vector2(DOCUMENT_VIEW_RECT.center))
        self._clamp_pan()

    def _document_display_rect(self) -> pygame.Rect:
        document = self.document
        if document is None:
            return pygame.Rect(0, 0, 1, 1)
        source_size = document.source_image.get_size()
        base_scale = min(
            (DOCUMENT_VIEW_RECT.width - 36) / source_size[0],
            (DOCUMENT_VIEW_RECT.height - 28) / source_size[1],
        )
        scale = base_scale * self.zoom
        size = (max(1, round(source_size[0] * scale)), max(1, round(source_size[1] * scale)))
        rect = pygame.Rect((0, 0), size)
        rect.center = (
            round(DOCUMENT_VIEW_RECT.centerx + self.pan.x),
            round(DOCUMENT_VIEW_RECT.centery + self.pan.y),
        )
        return rect

    def _source_rect_to_display(self, source_rect: pygame.Rect) -> pygame.Rect:
        document = self.document
        display_rect = self._document_display_rect()
        if document is None:
            return pygame.Rect(0, 0, 0, 0)
        scale_x = display_rect.width / document.source_image.get_width()
        scale_y = display_rect.height / document.source_image.get_height()
        return pygame.Rect(
            round(display_rect.x + source_rect.x * scale_x),
            round(display_rect.y + source_rect.y * scale_y),
            max(1, round(source_rect.width * scale_x)),
            max(1, round(source_rect.height * scale_y)),
        )

    def _evidence_at_display_position(
        self,
        position: tuple[int, int],
    ) -> EvidenceRegion | None:
        document = self.document
        if document is None or not DOCUMENT_VIEW_RECT.collidepoint(position):
            return None
        for evidence in document.evidence_regions:
            if self._source_rect_to_display(evidence.rect).collidepoint(position):
                return evidence
        return None

    def _clamp_pan(self) -> None:
        display_rect = self._document_display_rect()
        max_pan_x = max(0, (display_rect.width - DOCUMENT_VIEW_RECT.width) // 2 + 90)
        max_pan_y = max(0, (display_rect.height - DOCUMENT_VIEW_RECT.height) // 2 + 90)
        self.pan.x = max(-max_pan_x, min(max_pan_x, self.pan.x))
        self.pan.y = max(-max_pan_y, min(max_pan_y, self.pan.y))

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
