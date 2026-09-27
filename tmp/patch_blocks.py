def patch(path, pairs):
    s = open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert old in s, (path, old[:80])
        s = s.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(s)


patch("src/gameplay/cases.py", [
    ("    info: tuple[tuple[str, str], ...] = ()\n", "    info: tuple[tuple[str, str], ...] = ()\n    blocks: tuple[dict, ...] = ()\n"),
    ('            inset=extras.get(doc["id"], {}).get("inset", ""),\n', '            inset=extras.get(doc["id"], {}).get("inset", ""),\n            blocks=tuple(extras.get(doc["id"], {}).get("blocks", ())),\n'),
])

patch("src/gameplay/document_renderer.py", [
    ("from src.gameplay import document_art\n", "from src.gameplay import document_art\nfrom src.gameplay.document_blocks import BlockPainter, Ink\n"),
    ("def theme_for(document: CaseDocumentData) -> Theme:\n", "def theme_for(document: CaseDocumentData) -> Theme:\n    return THEMES[\"paper\"]  # every paper keeps the game's warm beige; layouts differ, not colours\n\n\ndef _unused_theme_for(document: CaseDocumentData) -> Theme:\n"),
    ("""            placed, info_top = self._flow_fields(document.fields, start)
            body_top = IMAGE_BODY_TOP if image_rect is not None else BODY_TOP
            flow_bottom = body_top - 8
""", """            embedded = self._referenced_labels(document.blocks)
            loose = tuple(field for field in document.fields if field.label.strip().upper() not in embedded)
            placed, info_top = self._flow_fields(loose, start)
            if not loose:
                info_top = start
            body_top = IMAGE_BODY_TOP if image_rect is not None else BODY_TOP
            flow_bottom = body_top - 8
"""),
    ("""        if document.info and not document.show_portrait:
            self._draw_info_table(surface, document, accent, info_top, body_top - 10)
""", """        if document.blocks and not document.show_portrait:
            painter = BlockPainter(
                {"small": self.font_small, "small_bold": self.font_small_bold, "tiny": self.font_tiny, "tiny_bold": self._font(14, True)},
                Ink(theme.paper, theme.light, theme.dark, theme.ink, theme.muted, accent),
                document.fields,
            )
            y = info_top + (4 if loose else 0)
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
"""),
    ("    def _draw_picture(self,", '''    @staticmethod
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

    def _draw_picture(self,'''),
])
