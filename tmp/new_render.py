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
                image_rect = pygame.Rect(38, 166, 544, 172)
                self._draw_picture(surface, document, image_rect, case_id, image_loader)
                start = image_rect.bottom + 28
            placed, info_top = self._flow_fields(document.fields, start)
            body_top = BODY_TOP
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

        if document.info and not document.show_portrait:
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
        self._draw_scribble(surface, document.issuer or document.organization or document.title, (352, 672), 228, theme.signature)
        return RenderedDocument(document.document_id, document.title, surface, tuple(evidence), image_rect=image_rect)

    def _draw_picture(self, surface, document: CaseDocumentData, rect: pygame.Rect, case_id: str, image_loader) -> None:
        picture = None
        if document.image and image_loader is not None:
            try:
                picture = image_loader(f"cases/{case_id}/{document.image}")
            except Exception:
                picture = None
        if picture is not None:
            picture = self._cover(picture, rect.size)
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
        caption = document.image_caption or "Clique na imagem para circular algo suspeito."
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
        start = 166 + (194 if (document.image or document.image_art) else 0)
        _, top = self._flow_fields(document.fields, start)
        y, drawn, bottom = top + 26, 0, BODY_TOP - 10
        for _label, value in document.info:
            lines = self._wrap_small(value, 340)
            height = INFO_ROW if len(lines) == 1 else INFO_ROW + 18 * (len(lines) - 1)
            if y + height > bottom:
                break
            y += height
            drawn += 1
        return drawn

