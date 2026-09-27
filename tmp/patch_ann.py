def patch(path, pairs):
    s = open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert old in s, (path, old[:70])
        s = s.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(s)


patch("src/scenes/audit.py", [
    ("rendered_documents = self.document_renderer.render_case(self.case, portrait)",
     "rendered_documents = self.document_renderer.render_case(self.case, portrait, self.assets.load_image)"),
    ("""            evidence = document.evidence_at_monitor(monitor_position)
            if evidence is not None and click_count < 2:
                self._handle_evidence_comparison(document, evidence)
                return
""", """            evidence = document.evidence_at_monitor(monitor_position)
            if evidence is not None and click_count < 2:
                self._handle_evidence_comparison(document, evidence)
                return

            if click_count < 2 and document.toggle_annotation(document.source_position(monitor_position)):
                self._play_sound("paper", 0.5)
                return
"""),
])

patch("src/ui/case_document.py", [
    ("        self.signature_target = rendered.signature_target\n",
     "        self.signature_target = rendered.signature_target\n        self.image_rect = rendered.image_rect\n        self.annotations: list[tuple[int, int]] = []\n"),
    ("    def evidence_at_monitor(self,", '''    def toggle_annotation(self, source_position: tuple[int, int]) -> bool:
        """Click inside the picture of a paper: draw a red circle there, or erase one already there."""
        if self.image_rect is None or not self.image_rect.collidepoint(source_position):
            return False
        for point in self.annotations:
            if abs(point[0] - source_position[0]) < 37 and abs(point[1] - source_position[1]) < 26:
                self.annotations.remove(point)
                break
        else:
            self.annotations.append(source_position)
        self._decorated_cache = None
        return True

    def evidence_at_monitor(self,'''),
    ("            composed.blit(overlay, (0, 0))\n", "            composed.blit(overlay, (0, 0))\n            document_art.draw_annotations(composed, self.annotations)\n"),
    ("from src.gameplay.document_renderer import EvidenceRegion, RenderedDocument\n", "from src.gameplay import document_art\nfrom src.gameplay.document_renderer import EvidenceRegion, RenderedDocument\n"),
])

patch("src/ui/document_inspector.py", [
    ("""        self.panning = True
        self.pan_drag_offset.update(position[0] - self.pan.x, position[1] - self.pan.y)
        return True
""", """        display = self._document_display_rect()
        if display.width > 0 and display.collidepoint(position):
            source = (
                round((position[0] - display.x) * document.source_image.get_width() / display.width),
                round((position[1] - display.y) * document.source_image.get_height() / display.height),
            )
            if document.toggle_annotation(source):
                return True

        self.panning = True
        self.pan_drag_offset.update(position[0] - self.pan.x, position[1] - self.pan.y)
        return True
"""),
])
