from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from src.gameplay.cases import AuditCase, CaseDocumentData, DocumentField


DOCUMENT_SIZE = (620, 800)

PAPER = (220, 208, 169)
PAPER_LIGHT = (235, 225, 190)
PAPER_DARK = (159, 143, 101)
INK = (45, 40, 30)
INK_MUTED = (91, 81, 58)
OLIVE = (99, 113, 71)
OLIVE_DARK = (51, 63, 43)
BLUE = (69, 105, 119)
AMBER = (158, 113, 39)
RED = (155, 61, 52)

ACCENT_COLORS = {
    "olive": OLIVE_DARK,
    "blue": BLUE,
    "amber": AMBER,
    "red": RED,
}


@dataclass(frozen=True)
class EvidenceRegion:
    key: str
    rect: pygame.Rect
    note: str


@dataclass(frozen=True)
class RenderedDocument:
    document_id: str
    title: str
    surface: pygame.Surface
    evidence_regions: tuple[EvidenceRegion, ...] = ()
    stamp_target: pygame.Rect | None = None
    signature_target: pygame.Rect | None = None


class DocumentRenderer:
    """Builds readable paper documents from case data."""

    def __init__(self) -> None:
        self.font_tiny = self._font(14)
        self.font_small = self._font(17)
        self.font_body = self._font(20)
        self.font_body_bold = self._font(20, bold=True)
        self.font_field = self._font(22, bold=True)
        self.font_title = self._font(29, bold=True)
        self.font_header = self._font(20, bold=True)

    def render_case(
        self,
        case: AuditCase,
        employee_portrait: pygame.Surface | None = None,
    ) -> tuple[RenderedDocument, ...]:
        if len(case.documents) != 4:
            raise ValueError(f"Case {case.case_id} must contain four source documents")
        if any(document.show_portrait for document in case.documents) and employee_portrait is None:
            raise ValueError(f"Case {case.case_id} requires a portrait")

        documents = tuple(
            self._render_document(document, employee_portrait)
            for document in case.documents
        )
        return (*documents, self._render_final_decision(case))

    def _render_document(
        self,
        document: CaseDocumentData,
        portrait: pygame.Surface | None,
    ) -> RenderedDocument:
        accent = ACCENT_COLORS.get(document.accent)
        if accent is None:
            raise ValueError(f"Unknown document accent: {document.accent}")
        surface = self._new_paper(document.document_id, accent, document.organization)
        self._draw_fitted_text(
            surface,
            document.title.upper(),
            INK,
            pygame.Rect(34, 102, 550, 42),
            maximum_size=29,
        )
        pygame.draw.line(surface, accent, (32, 151), (588, 151), 3)

        evidence: list[EvidenceRegion] = []
        if document.show_portrait:
            if portrait is None:
                raise ValueError(f"Document {document.document_id} requires a portrait")
            portrait_rect = pygame.Rect(38, 178, 190, 220)
            surface.blit(self._cover(portrait, portrait_rect.size), portrait_rect)
            pygame.draw.rect(surface, INK_MUTED, portrait_rect, 4)
            positions = tuple((250, 178 + index * 77, 332) for index in range(4))
            body_rect = pygame.Rect(38, 510, 544, 145)
        else:
            positions = tuple(
                (
                    38 if index % 2 == 0 else 314,
                    178 + (index // 2) * 98,
                    250 if index % 2 == 0 else 268,
                )
                for index in range(6)
            )
            body_rect = pygame.Rect(38, 500, 544, 155)

        if len(document.fields) > len(positions):
            raise ValueError(f"Document {document.document_id} has too many fields")
        for field, (x, y, width) in zip(document.fields, positions, strict=False):
            field_rect = self._draw_field(
                surface,
                field,
                (x, y),
                width,
                accent if field.highlight else None,
            )
            if field.evidence_key is not None:
                if field.evidence_note is None:
                    raise ValueError(f"Evidence {field.evidence_key} needs a note")
                evidence.append(EvidenceRegion(field.evidence_key, field_rect, field.evidence_note))

        pygame.draw.rect(surface, PAPER_LIGHT, body_rect)
        pygame.draw.rect(surface, accent, body_rect, 3)
        self._draw_text(surface, document.body_title, self.font_body_bold, accent, (body_rect.x + 16, body_rect.y + 15))
        self._draw_wrapped_text(
            surface,
            document.body,
            self.font_body,
            INK,
            pygame.Rect(body_rect.x + 16, body_rect.y + 51, body_rect.width - 32, body_rect.height - 62),
            line_height=24,
            max_lines=4,
        )
        self._draw_signature_line(surface, "Responsável pelo documento", (350, 710), 232)
        return RenderedDocument(document.document_id, document.title, surface, tuple(evidence))

    def _render_final_decision(self, case: AuditCase) -> RenderedDocument:
        surface = self._new_paper("final", AMBER, "UNIDADE DE AUDITORIA ALGORÍTMICA")
        self._draw_text(surface, "FOLHA DE AUDITORIA", self.font_title, INK, (34, 106))
        pygame.draw.line(surface, AMBER, (32, 151), (588, 151), 3)

        self._draw_plain_field(surface, "CASO", f"{case.sequence:03d}/2026", (38, 180), 250)
        self._draw_plain_field(surface, case.subject_label, case.subject_name, (314, 180), 268)
        self._draw_plain_field(surface, "OBJETO", case.decision_object, (38, 255), 544)

        self._draw_text(surface, "VERIFICAÇÕES DO AUDITOR", self.font_body_bold, INK, (40, 353))
        checklist = (
            "Identidade e correspondência dos dados",
            "Critérios, datas e cálculos utilizados",
            "Permissão, viés e limite da automação",
        )
        for index, label in enumerate(checklist):
            y = 392 + index * 39
            pygame.draw.rect(surface, INK_MUTED, (42, y, 20, 20), 2)
            self._draw_text(surface, label, self.font_small, INK, (76, y - 1))

        stamp_target = pygame.Rect(72, 535, 476, 158)
        pygame.draw.rect(surface, (228, 217, 182), stamp_target)
        pygame.draw.rect(surface, AMBER, stamp_target, 4)
        self._draw_text(surface, "DECISÃO FINAL", self.font_body_bold, INK_MUTED, (92, 550))
        self._draw_text(surface, "APLIQUE O CARIMBO AQUI", self.font_field, PAPER_DARK, stamp_target.center, anchor="center")
        self._draw_text(surface, "O registro encerra o caso.", self.font_tiny, INK_MUTED, (190, 663))

        signature_target = pygame.Rect(310, 696, 290, 88)
        pygame.draw.rect(surface, PAPER_LIGHT, signature_target)
        pygame.draw.rect(surface, BLUE, signature_target, 3)
        self._draw_text(
            surface,
            "ASSINATURA DO AUDITOR",
            self.font_tiny,
            INK_MUTED,
            (signature_target.x + 12, signature_target.y + 8),
        )
        pygame.draw.line(
            surface,
            INK_MUTED,
            (signature_target.x + 12, signature_target.bottom - 20),
            (signature_target.right - 12, signature_target.bottom - 20),
            2,
        )
        self._draw_text(
            surface,
            "CLIQUE PARA ASSINAR",
            self.font_tiny,
            BLUE,
            (signature_target.centerx, signature_target.bottom - 17),
            anchor="midtop",
        )
        return RenderedDocument(
            "final",
            "Folha de auditoria",
            surface,
            stamp_target=stamp_target,
            signature_target=signature_target,
        )

    def _new_paper(
        self,
        seed_text: str,
        header_color: tuple[int, int, int],
        organization: str,
    ) -> pygame.Surface:
        surface = pygame.Surface(DOCUMENT_SIZE, pygame.SRCALPHA)
        surface.fill(PAPER)
        randomizer = random.Random(seed_text)
        for _ in range(850):
            x = randomizer.randrange(8, DOCUMENT_SIZE[0] - 8)
            y = randomizer.randrange(8, DOCUMENT_SIZE[1] - 8)
            value = randomizer.choice((-8, -5, 5, 7))
            color = tuple(max(0, min(255, channel + value)) for channel in PAPER)
            pygame.draw.rect(surface, color, (x, y, 2, 2))

        pygame.draw.rect(surface, header_color, (0, 0, DOCUMENT_SIZE[0], 88))
        pygame.draw.rect(surface, INK, surface.get_rect(), 6)
        pygame.draw.rect(surface, PAPER_DARK, surface.get_rect().inflate(-18, -18), 2)
        self._draw_fitted_text(surface, organization, PAPER_LIGHT, pygame.Rect(28, 17, 560, 50), maximum_size=20)
        self._draw_text(surface, "DOCUMENTO INTERNO", self.font_tiny, PAPER_DARK, (448, 744))
        return surface

    def _draw_field(
        self,
        surface: pygame.Surface,
        field: DocumentField,
        position: tuple[int, int],
        width: int,
        accent: tuple[int, int, int] | None,
    ) -> pygame.Rect:
        x, y = position
        self._draw_text(surface, field.label, self.font_tiny, INK_MUTED, (x, y))
        value_rect = pygame.Rect(x, y + 23, width, 39)
        pygame.draw.rect(surface, PAPER_LIGHT, value_rect)
        pygame.draw.line(surface, accent or PAPER_DARK, value_rect.bottomleft, value_rect.bottomright, 3)
        self._draw_fitted_text(surface, field.value, accent or INK, pygame.Rect(x + 7, y + 24, width - 14, 36), maximum_size=20)
        return value_rect

    def _draw_plain_field(
        self,
        surface: pygame.Surface,
        label: str,
        value: str,
        position: tuple[int, int],
        width: int,
    ) -> pygame.Rect:
        return self._draw_field(surface, DocumentField(label, value), position, width, None)

    def _draw_fitted_text(
        self,
        surface: pygame.Surface,
        text: str,
        color: tuple[int, int, int],
        rect: pygame.Rect,
        *,
        maximum_size: int,
    ) -> None:
        size = maximum_size
        font = self._font(size, bold=True)
        while font.size(text)[0] > rect.width and size > 12:
            size -= 1
            font = self._font(size, bold=True)
        rendered = font.render(text, False, color)
        surface.blit(rendered, rendered.get_rect(midleft=(rect.left, rect.centery)))

    def _draw_signature_line(self, surface: pygame.Surface, label: str, position: tuple[int, int], width: int) -> None:
        x, y = position
        pygame.draw.line(surface, INK_MUTED, (x, y), (x + width, y), 2)
        self._draw_text(surface, label, self.font_tiny, INK_MUTED, (x, y + 6))

    @staticmethod
    def _cover(image: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
        target_width, target_height = size
        scale = max(target_width / image.get_width(), target_height / image.get_height())
        scaled_size = (max(1, round(image.get_width() * scale)), max(1, round(image.get_height() * scale)))
        scaled = pygame.transform.scale(image, scaled_size)
        crop_rect = pygame.Rect(0, 0, target_width, target_height)
        crop_rect.center = scaled.get_rect().center
        return scaled.subsurface(crop_rect).copy()

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
