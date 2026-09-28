from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from src.gameplay.cases import AuditCase, CaseDocumentData, DocumentField
from src.gameplay import document_art
from src.gameplay.document_blocks import BlockPainter, Ink


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
class Theme:
    """Each kind of paper (form, log printout, e-mail, receipt, rulebook) has its own look."""

    name: str
    paper: tuple[int, int, int]
    light: tuple[int, int, int]
    dark: tuple[int, int, int]
    ink: tuple[int, int, int]
    muted: tuple[int, int, int]
    signature: tuple[int, int, int] = (28, 42, 104)
    accent_override: tuple[int, int, int] | None = None
    stamp_label: str = "DOCUMENTO INTERNO"


THEMES = {
    "paper": Theme("paper", PAPER, PAPER_LIGHT, PAPER_DARK, INK, INK_MUTED),
    "log": Theme("log", (16, 23, 19), (26, 36, 30), (70, 100, 62), (196, 232, 150), (120, 156, 96),
                 (150, 200, 255), (112, 210, 122), "IMPRESSÃO DE SISTEMA"),
    "email": Theme("email", (236, 240, 244), (255, 255, 255), (170, 180, 196), (30, 38, 52), (92, 102, 124),
                   (40, 60, 130), None, "MENSAGEM ARQUIVADA"),
    "receipt": Theme("receipt", (248, 244, 232), (255, 253, 244), (196, 188, 164), (52, 48, 42), (108, 100, 84),
                     (40, 52, 110), None, "VIA DO CLIENTE"),
    "official": Theme("official", (224, 228, 222), (240, 243, 238), (150, 160, 150), (38, 46, 42), (92, 104, 96),
                      (28, 42, 104), None, "DOCUMENTO OFICIAL"),
}

THEME_KEYWORDS = (
    ("email", ("e-mail", "reclamação", "notificação", "fóruns", "mensagem")),
    ("receipt", ("nota fiscal", "holerite", "extrato", "fatura", "fechamento", "pedido de compra", "balanço")),
    ("official", ("regra", "manual", "política", "lei ", "termo", "contrato", "edital", "cláusula", "tabela",
                  "metas", "guia", "certidão", "licença", "mapa", "lista do", "lista de", "regulad", "agência",
                  "formulário", "cadastro", "avaliação", "registro")),
    ("log", ("histórico", "rastro", "painel", "relatório", "cálculo", "alerta", "sensor", "gps", "scanner",
             "log", "leitura", "controle de versão")),
)


def theme_for(document: CaseDocumentData) -> Theme:
    return THEMES["paper"]  # every paper keeps the game's warm beige; layouts differ, not colours


def _unused_theme_for(document: CaseDocumentData) -> Theme:
    if document.theme in THEMES:
        return THEMES[document.theme]
    title = f" {document.title.lower()} "
    for name, words in THEME_KEYWORDS:
        if any(word in title for word in words):
            return THEMES[name]
    return THEMES["paper"]


@dataclass(frozen=True)
class EvidenceRegion:
    key: str
    rect: pygame.Rect
    note: str
    value: str


@dataclass(frozen=True)
class RenderedDocument:
    document_id: str
    title: str
    surface: pygame.Surface
    evidence_regions: tuple[EvidenceRegion, ...] = ()
    stamp_target: pygame.Rect | None = None
    signature_target: pygame.Rect | None = None
    image_rect: pygame.Rect | None = None


INFO_ROW = 27
BODY_TOP = 528
IMAGE_HEIGHT = 128
IMAGE_BODY_TOP = 548


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
        self.font_small_bold = self._font(17, bold=True)
        self.theme = THEMES["paper"]

    def render_case(
        self,
        case: AuditCase,
        employee_portrait: pygame.Surface | None = None,
        image_loader=None,
    ) -> tuple[RenderedDocument, ...]:
        if not 2 <= len(case.documents) <= 4:
            raise ValueError(f"Case {case.case_id} must contain between two and four source documents")
        if any(document.show_portrait for document in case.documents) and employee_portrait is None:
            raise ValueError(f"Case {case.case_id} requires a portrait")

        documents = tuple(
            self._render_document(document, employee_portrait, case.case_id, image_loader)
            for document in case.documents
        )
        return (*documents, self._render_final_decision(case))

    def _render_document(
        self,
        document: CaseDocumentData,
        portrait: pygame.Surface | None,
        case_id: str = "",
        image_loader=None,
    ) -> RenderedDocument:
        accent = ACCENT_COLORS.get(document.accent)
        if accent is None:
            raise ValueError(f"Unknown document accent: {document.accent}")
        theme = theme_for(document)
        self.theme = theme
        if theme.accent_override is not None:
            accent = theme.accent_override
        surface = self._new_paper(document.document_id, accent, document.organization)
        self._draw_fitted_text(
            surface,
            document.title.upper(),
            theme.ink,
            pygame.Rect(34, 102, 550, 42),
            maximum_size=29,
        )
        pygame.draw.line(surface, accent, (32, 151), (588, 151), 3)

        evidence: list[EvidenceRegion] = []
        image_rect: pygame.Rect | None = None
        info_top = 0
        loose: tuple = ()
        if document.show_portrait:
            if portrait is None:
                raise ValueError(f"Document {document.document_id} requires a portrait")
            portrait_rect = pygame.Rect(38, 178, 190, 220)
            surface.blit(self._cover(portrait, portrait_rect.size), portrait_rect)
            pygame.draw.rect(surface, theme.muted, portrait_rect, 4)
            slots = tuple((250, 178 + index * 77, 332) for index in range(4))
            if len(document.fields) > len(slots):
                raise ValueError(f"Document {document.document_id} has too many fields")
            placed = [
                (field, (x, y), width, 1)
                for field, (x, y, width) in zip(document.fields, slots)
            ]
            body_top = 510
            flow_bottom = 500
        else:
            start = 166
            if document.image or document.image_art:
                image_rect = pygame.Rect(38, 166, 544, IMAGE_HEIGHT)
                self._draw_picture(surface, document, image_rect, case_id, image_loader)
                start = image_rect.bottom + 26
            embedded = self._referenced_labels(document.blocks)
            loose = tuple(field for field in document.fields if field.label.strip().upper() not in embedded)
            placed, info_top = self._flow_fields(loose, start)
            if not loose:
                info_top = start
            body_top = IMAGE_BODY_TOP if image_rect is not None else BODY_TOP
            flow_bottom = body_top - 8

        for field, position, width, lines in placed:
            field_rect = self._draw_field(
                surface,
                field,
                position,
                width,
                accent if field.highlight else None,
                lines,
            )
            if field_rect.bottom > flow_bottom:
                raise ValueError(f"Document {document.document_id} has too much text")
            if field.evidence_key is not None:
                if field.evidence_note is None:
                    raise ValueError(f"Evidence {field.evidence_key} needs a note")
                evidence.append(EvidenceRegion(field.evidence_key, field_rect, field.evidence_note, field.value))

        if document.blocks and not document.show_portrait:
            painter = BlockPainter(
                {"small": self.font_small, "small_bold": self.font_small_bold, "tiny": self.font_tiny, "tiny_bold": self._font(14, True)},
                Ink(theme.paper, theme.light, theme.dark, theme.ink, theme.muted, accent),
                document.fields,
            )
            y = info_top + (4 if loose else 0)
            room = body_top - 8 - y
            painter.pad = 0
            for candidate in range(16, -1, -2):  # spread out (more air per row) when the paper is sparse
                painter.pad = candidate
                used = sum(painter.height(block) + 10 for block in document.blocks) - 10
                if used <= room - 26 or candidate == 0:
                    break
            for block in document.blocks:
                height = painter.height(block)
                if y + height > body_top - 8:
                    raise ValueError(f"Document {document.document_id} has too much content ({block['type']})")
                painter.draw(surface, block, y)
                y += height + 10
            for field, rect in painter.regions:
                if field.evidence_key is not None:
                    evidence.append(EvidenceRegion(field.evidence_key, rect, field.evidence_note or "", field.value))
        elif document.info and not document.show_portrait:
            self._draw_info_table(surface, document, accent, info_top, body_top - 10)

        if document.body or document.body_title:
            body_rect = pygame.Rect(38, body_top, 544, 655 - body_top)
            pygame.draw.rect(surface, theme.light, body_rect)
            pygame.draw.rect(surface, accent, body_rect, 3)
            self._draw_text(surface, document.body_title, self.font_small_bold, accent, (body_rect.x + 14, body_rect.y + 9))
            self._draw_wrapped_text(
                surface,
                document.body,
                self.font_small,
                theme.ink,
                pygame.Rect(body_rect.x + 14, body_rect.y + 34, body_rect.width - 28, body_rect.height - 40),
                line_height=21,
                max_lines=5,
            )
        self._draw_signature_line(surface, "Responsável pelo documento", (350, 710), 232)
        # Seeded by the specific document, not just its organization: "RH" alone signs 16 different
        # papers across 16 different cases, and they must not all get the exact same scribble.
        signer_seed = f"{case_id}:{document.document_id}:{document.issuer or document.organization or document.title}"
        self._draw_scribble(surface, signer_seed, (352, 672), 228, theme.signature)
        return RenderedDocument(document.document_id, document.title, surface, tuple(evidence), image_rect=image_rect)

    @staticmethod
    def _referenced_labels(blocks) -> set[str]:
        found: set[str] = set()

        def walk(value) -> None:
            if isinstance(value, str):
                if value.startswith("@"):
                    found.add(value[1:].strip().upper())
            elif isinstance(value, dict):
                for item in value.values():
                    walk(item)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    walk(item)

        walk(blocks)
        return found

    def _draw_picture(self, surface, document: CaseDocumentData, rect: pygame.Rect, case_id: str, image_loader) -> None:
        picture = None
        if document.image and image_loader is not None:
            try:
                picture = image_loader(f"cases/{case_id}/{document.image}")
            except Exception:
                picture = None
        if picture is not None:
            if document.image_art.startswith("face"):  # ID photos: come closer to the face
                width, height = picture.get_size()
                crop = pygame.Rect(0, 0, width // 2, height // 2)
                crop.center = (width // 2, round(height * 0.36))
                picture = picture.subsurface(crop.clip(picture.get_rect())).copy()
            picture = document_art.pixelate_picture(self._cover(picture, rect.size), rect.size)
        else:
            art = document.image_art or document.image.rsplit(".", 1)[0]
            picture = document_art.draw_art(art, rect.size, f"{case_id}{document.document_id}")
        surface.blit(picture, rect)
        if document.inset.startswith("plate:"):
            _, text, mode = (document.inset.split(":") + ["clean"])[:3]
            document_art.draw_plate_inset(
                surface, pygame.Rect(rect.right - 168, rect.y + 10, 154, 52), text, mode == "mud", f"{case_id}plate"
            )
        pygame.draw.rect(surface, self.theme.ink, rect, 3)
        caption = document.image_caption or "Imagem reconstituída pela perícia."
        self._draw_text(surface, caption, self.font_tiny, self.theme.muted, (rect.x, rect.bottom + 6))

    def _draw_info_table(self, surface, document: CaseDocumentData, accent, top: int, bottom: int) -> None:
        theme = self.theme
        if top + 24 + INFO_ROW > bottom:
            return
        self._draw_text(surface, "OUTRAS INFORMAÇÕES DO PAPEL", self.font_tiny, theme.muted, (38, top))
        pygame.draw.line(surface, theme.dark, (38, top + 19), (582, top + 19), 1)
        y = top + 26
        for label, value in document.info:
            lines = self._wrap_small(value, 340)
            height = INFO_ROW if len(lines) == 1 else INFO_ROW + 18 * (len(lines) - 1)
            if y + height > bottom:
                break
            self._draw_text(surface, label, self.font_tiny, theme.muted, (44, y + 6))
            for index, line in enumerate(lines[:2]):
                self._draw_text(surface, line, self.font_small, theme.ink, (232, y + 3 + index * 18))
            y += height
            pygame.draw.line(surface, theme.dark, (38, y - 3), (582, y - 3), 1)

    def _wrap_small(self, text: str, width: int) -> list[str]:
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = f"{current} {word}".strip()
            if not current or self.font_small.size(candidate)[0] <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [""]

    def info_rows_that_fit(self, document: CaseDocumentData) -> int:
        """How many info rows of this paper are really drawn (used by the content tests)."""
        self.theme = theme_for(document)
        has_image = bool(document.image or document.image_art)
        start = 166 + IMAGE_HEIGHT + 26 if has_image else 166
        _, top = self._flow_fields(document.fields, start)
        y, drawn, bottom = top + 26, 0, (IMAGE_BODY_TOP if has_image else BODY_TOP) - 10
        for _label, value in document.info:
            lines = self._wrap_small(value, 340)
            height = INFO_ROW if len(lines) == 1 else INFO_ROW + 18 * (len(lines) - 1)
            if y + height > bottom:
                break
            y += height
            drawn += 1
        return drawn


    @staticmethod
    def _draw_scribble(surface: pygame.Surface, seed_text: str, origin: tuple[int, int], width: int, ink: tuple[int, int, int] = (28, 42, 104)) -> None:
        """A believable hand-written signature, unique per document (seeded by case + document + issuer).

        Three different handwriting "styles" (looping cursive, sharp zigzag, tall spaced print) plus
        per-letter jitter, so two signatures never read as the same doodle just because two unrelated
        cases both happen to have a document issued by "RH" or "TI".
        """
        rng = random.Random(seed_text)
        x0, y0 = origin
        style = rng.choice(("loop", "zigzag", "print"))
        baseline = y0 + rng.uniform(-3, 3)
        points: list[tuple[float, float]] = []
        letters = rng.randint(5, 9)
        x = 0.0
        for _ in range(letters):
            height = rng.uniform(12, 36)
            span = width / (letters + 1) * rng.uniform(0.65, 1.2)
            jitter = rng.uniform(-4, 4)
            steps = 5 if style == "zigzag" else 7
            for step in range(steps + 1):
                phase = step / steps
                if style == "zigzag":
                    lift = height * (1 - abs(2 * phase - 1))
                elif style == "print":
                    lift = height * (0.15 + 0.85 * (1 - abs(2 * phase - 1) ** 3))
                else:
                    loop = math.sin(phase * math.pi * 2) * height * 0.5
                    lift = abs(math.sin(phase * math.pi)) * height - loop * 0.25
                points.append((x0 + x + phase * span, baseline + jitter * phase + 20 - lift))
            x += span * (0.78 if style == "print" else 0.85)
        if len(points) > 2:
            thickness = 4 if style == "print" else 3
            pygame.draw.lines(surface, ink, False, points, thickness)
            pygame.draw.lines(surface, tuple(min(255, c + 30) for c in ink), False, [(px, py + 1) for px, py in points], 1)
        underline_y = y0 + 34
        pygame.draw.line(surface, ink, (x0 + 6, underline_y), (x0 + width * rng.uniform(0.7, 0.95), underline_y - rng.randint(2, 7)), 2)

    def _flow_fields(
        self,
        fields: tuple[DocumentField, ...],
        start: int = 178,
    ) -> tuple[list[tuple[DocumentField, tuple[int, int], int, int]], int]:
        """Short values sit two per row; long values take a full row and wrap. Also returns the y below them."""
        placed: list[tuple[DocumentField, tuple[int, int], int, int]] = []
        y = start
        pitch = 86
        half_open = False
        for field in fields:
            lines = self._wrapped_lines(field.value, 520)
            if len(field.value) <= 22 and len(lines) == 1:
                if half_open:
                    placed.append((field, (314, y), 268, 1))
                    half_open = False
                    y += pitch
                else:
                    placed.append((field, (38, y), 250, 1))
                    half_open = True
                continue
            if half_open:
                half_open = False
                y += pitch
            shown = min(len(lines), 4)
            placed.append((field, (38, y), 544, shown))
            y += 23 + 39 + 25 * (shown - 1) + 22
        if half_open:
            y += pitch
        return placed, y

    def _wrapped_lines(self, text: str, width: int) -> list[str]:
        font = self._font(20, bold=True)
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = f"{current} {word}".strip()
            if not current or font.size(candidate)[0] <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [""]

    def _render_final_decision(self, case: AuditCase) -> RenderedDocument:
        self.theme = THEMES["paper"]
        surface = self._new_paper("final", AMBER, "UNIDADE DE AUDITORIA ALGORÍTMICA")
        self._draw_text(surface, "FOLHA DE AUDITORIA", self.font_title, INK, (34, 106))
        pygame.draw.line(surface, AMBER, (32, 151), (588, 151), 3)

        case_label = "TREINAMENTO" if case.is_tutorial else f"{case.sequence:03d}/2026"
        self._draw_plain_field(surface, "CASO", case_label, (38, 180), 250)
        self._draw_plain_field(surface, case.subject_label, case.subject_name, (314, 180), 268)
        self._draw_plain_field(surface, "OBJETO", case.decision_object, (38, 255), 544)

        self._draw_text(surface, "VERIFICAÇÕES DO AUDITOR", self.font_body_bold, INK, (40, 353))
        checklist = (
            "Relatório da IA lido",
            "Documentos-chave comparados",
            "Dados decisivos conferidos",
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
        theme = self.theme
        surface = pygame.Surface(DOCUMENT_SIZE, pygame.SRCALPHA)
        surface.fill(theme.paper)
        randomizer = random.Random(seed_text)
        grain = (-8, -5, 5, 7) if theme.name != "log" else (-3, 3, 6, -2)
        for _ in range(850):
            x = randomizer.randrange(8, DOCUMENT_SIZE[0] - 8)
            y = randomizer.randrange(8, DOCUMENT_SIZE[1] - 8)
            value = randomizer.choice(grain)
            color = tuple(max(0, min(255, channel + value)) for channel in theme.paper)
            pygame.draw.rect(surface, color, (x, y, 2, 2))

        width, height = DOCUMENT_SIZE
        if theme.name == "log":
            for y in range(0, height, 4):  # scan lines
                pygame.draw.line(surface, (12, 18, 15), (8, y), (width - 8, y))
            pygame.draw.rect(surface, header_color, (0, 0, width, 88))
            for index, dot in enumerate(((224, 82, 67), (237, 193, 91), (101, 191, 91))):
                pygame.draw.circle(surface, dot, (width - 30 - index * 22, 68), 6)
            pygame.draw.rect(surface, theme.dark, surface.get_rect(), 6)
            self._draw_fitted_text(surface, "> " + organization, (10, 20, 14), pygame.Rect(28, 17, 500, 50), maximum_size=20)
        elif theme.name == "email":
            pygame.draw.rect(surface, header_color, (0, 0, width, 88))
            pygame.draw.rect(surface, (255, 255, 255), (28, 22, 44, 34))
            pygame.draw.lines(surface, header_color, False, [(28, 22), (50, 42), (72, 22)], 3)
            pygame.draw.rect(surface, theme.dark, surface.get_rect(), 6)
            self._draw_fitted_text(surface, organization, (245, 248, 255), pygame.Rect(90, 17, 490, 50), maximum_size=20)
        elif theme.name == "receipt":
            pygame.draw.rect(surface, header_color, (0, 0, width, 88))
            for x in range(14, width - 10, 24):  # perforated edge
                pygame.draw.circle(surface, (0, 0, 0, 0), (x, 4), 7)
                pygame.draw.circle(surface, (0, 0, 0, 0), (x, height - 4), 7)
            pygame.draw.rect(surface, theme.dark, surface.get_rect(), 3)
            self._draw_fitted_text(surface, organization, (250, 248, 240), pygame.Rect(28, 17, 560, 50), maximum_size=20)
            for index in range(36):  # barcode
                pygame.draw.rect(surface, theme.ink, (44 + index * 6, 716, randomizer.choice((2, 3, 4)), 26))
        elif theme.name == "official":
            pygame.draw.rect(surface, header_color, (0, 0, width, 88))
            pygame.draw.rect(surface, theme.ink, surface.get_rect(), 6)
            pygame.draw.rect(surface, theme.dark, surface.get_rect().inflate(-18, -18), 2)
            seal = pygame.Surface((160, 160), pygame.SRCALPHA)
            pygame.draw.circle(seal, (*theme.dark, 46), (80, 80), 76, 6)
            pygame.draw.circle(seal, (*theme.dark, 46), (80, 80), 58, 2)
            for index in range(8):
                angle = index * math.pi / 4
                pygame.draw.line(seal, (*theme.dark, 46), (80, 80), (80 + 56 * math.cos(angle), 80 + 56 * math.sin(angle)), 3)
            surface.blit(seal, (width - 200, 560))
            self._draw_fitted_text(surface, organization, (240, 244, 240), pygame.Rect(28, 17, 560, 50), maximum_size=20)
        else:
            pygame.draw.rect(surface, header_color, (0, 0, width, 88))
            pygame.draw.rect(surface, theme.ink, surface.get_rect(), 6)
            pygame.draw.rect(surface, theme.dark, surface.get_rect().inflate(-18, -18), 2)
            if randomizer.random() < 0.4:  # a coffee ring
                ring = pygame.Surface((110, 110), pygame.SRCALPHA)
                pygame.draw.circle(ring, (120, 84, 44, 70), (55, 55), 50, 5)
                surface.blit(ring, (randomizer.randrange(380, 470), randomizer.randrange(130, 200)))
            self._draw_fitted_text(surface, organization, theme.light, pygame.Rect(28, 17, 560, 50), maximum_size=20)
        if theme.name != "receipt":
            self._draw_text(surface, theme.stamp_label, self.font_tiny, theme.dark, (width - 30, 744), anchor="topright")
        return surface

    def _draw_field(
        self,
        surface: pygame.Surface,
        field: DocumentField,
        position: tuple[int, int],
        width: int,
        accent: tuple[int, int, int] | None,
        lines: int = 1,
    ) -> pygame.Rect:
        x, y = position
        theme = self.theme
        self._draw_text(surface, field.label, self.font_tiny, theme.muted, (x, y))
        height = 39 + 25 * (lines - 1)
        value_rect = pygame.Rect(x, y + 23, width, height)
        pygame.draw.rect(surface, theme.light, value_rect)
        pygame.draw.line(surface, accent or theme.dark, value_rect.bottomleft, value_rect.bottomright, 3)
        if lines <= 1:
            self._draw_fitted_text(surface, field.value, accent or theme.ink, pygame.Rect(x + 7, y + 24, width - 14, 36), maximum_size=20)
        else:
            wrapped = self._wrapped_lines(field.value, width - 14)[:lines]
            font = self._font(20, bold=True)
            for index, line in enumerate(wrapped):
                rendered = font.render(line, False, accent or theme.ink)
                surface.blit(rendered, (x + 7, y + 29 + index * 25))
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
        pygame.draw.line(surface, self.theme.muted, (x, y), (x + width, y), 2)
        self._draw_text(surface, label, self.font_tiny, self.theme.muted, (x, y + 6))

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
