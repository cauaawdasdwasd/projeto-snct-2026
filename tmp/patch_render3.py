p = "src/gameplay/document_renderer.py"
s = open(p, encoding="utf-8").read()


def sub(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new)


sub("""                image_rect = pygame.Rect(38, 166, 544, 172)
                self._draw_picture(surface, document, image_rect, case_id, image_loader)
                start = image_rect.bottom + 28
            placed, info_top = self._flow_fields(document.fields, start)
            body_top = BODY_TOP
""", """                image_rect = pygame.Rect(38, 166, 544, IMAGE_HEIGHT)
                self._draw_picture(surface, document, image_rect, case_id, image_loader)
                start = image_rect.bottom + 26
            placed, info_top = self._flow_fields(document.fields, start)
            body_top = IMAGE_BODY_TOP if image_rect is not None else BODY_TOP
""")
sub("BODY_TOP = 528\n", "BODY_TOP = 528\nIMAGE_HEIGHT = 128\nIMAGE_BODY_TOP = 548\n")
sub("""        start = 166 + (194 if (document.image or document.image_art) else 0)
        _, top = self._flow_fields(document.fields, start)
        y, drawn, bottom = top + 26, 0, BODY_TOP - 10""", """        has_image = bool(document.image or document.image_art)
        start = 166 + IMAGE_HEIGHT + 26 if has_image else 166
        _, top = self._flow_fields(document.fields, start)
        y, drawn, bottom = top + 26, 0, (IMAGE_BODY_TOP if has_image else BODY_TOP) - 10""")
open(p, "w", encoding="utf-8").write(s)
