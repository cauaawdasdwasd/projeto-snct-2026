p = "src/gameplay/document_renderer.py"
s = open(p, encoding="utf-8").read()
i = s.index("    def _render_document(")
j = s.index("    @staticmethod\n    def _draw_scribble")
s = s[:i] + open("tmp/new_render.py", encoding="utf-8").read() + "\n" + s[j:]


def sub(old, new):
    global s
    assert old in s, old[:60]
    s = s.replace(old, new)


sub("""        employee_portrait: pygame.Surface | None = None,
    ) -> tuple[RenderedDocument, ...]:""", """        employee_portrait: pygame.Surface | None = None,
        image_loader=None,
    ) -> tuple[RenderedDocument, ...]:""")
sub("self._render_document(document, employee_portrait)", "self._render_document(document, employee_portrait, case.case_id, image_loader)")
sub("        self.font_header = self._font(20, bold=True)\n", "        self.font_header = self._font(20, bold=True)\n        self.font_small_bold = self._font(17, bold=True)\n        self.theme = THEMES[\"paper\"]\n")
sub("def _draw_scribble(surface: pygame.Surface, seed_text: str, origin: tuple[int, int], width: int) -> None:", "def _draw_scribble(surface: pygame.Surface, seed_text: str, origin: tuple[int, int], width: int, ink: tuple[int, int, int] = (28, 42, 104)) -> None:")
sub("        ink = (28, 42, 104)\n", "")
sub("pygame.draw.lines(surface, (60, 78, 150), False, [(px, py + 1) for px, py in points], 1)", "pygame.draw.lines(surface, tuple(min(255, c + 30) for c in ink), False, [(px, py + 1) for px, py in points], 1)")
sub("""        fields: tuple[DocumentField, ...],
    ) -> list[tuple[DocumentField, tuple[int, int], int, int]]:
        \"\"\"Short values sit two per row; long values take a full row and wrap.\"\"\"
        placed: list[tuple[DocumentField, tuple[int, int], int, int]] = []
        y = 178
        half_open = False""", """        fields: tuple[DocumentField, ...],
        start: int = 178,
    ) -> tuple[list[tuple[DocumentField, tuple[int, int], int, int]], int]:
        \"\"\"Short values sit two per row; long values take a full row and wrap. Also returns the y below them.\"\"\"
        placed: list[tuple[DocumentField, tuple[int, int], int, int]] = []
        y = start
        pitch = 86
        half_open = False""")
sub("""                    placed.append((field, (314, y), 268, 1))
                    half_open = False
                    y += 98""", """                    placed.append((field, (314, y), 268, 1))
                    half_open = False
                    y += pitch""")
sub("""            if half_open:
                half_open = False
                y += 98
            shown = min(len(lines), 4)
            placed.append((field, (38, y), 544, shown))
            y += 23 + 39 + 25 * (shown - 1) + 36
        return placed""", """            if half_open:
                half_open = False
                y += pitch
            shown = min(len(lines), 4)
            placed.append((field, (38, y), 544, shown))
            y += 23 + 39 + 25 * (shown - 1) + 22
        if half_open:
            y += pitch
        return placed, y""")
open(p, "w", encoding="utf-8").write(s)
