p = "src/gameplay/document_renderer.py"
s = open(p, encoding="utf-8").read()


def sub(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new)


# final decision keeps the classic paper
sub('        surface = self._new_paper("final", AMBER, "UNIDADE DE AUDITORIA ALGORÍTMICA")',
    '        self.theme = THEMES["paper"]\n        surface = self._new_paper("final", AMBER, "UNIDADE DE AUDITORIA ALGORÍTMICA")')

# paper background per theme
i = s.index("        surface = pygame.Surface(DOCUMENT_SIZE, pygame.SRCALPHA)\n        surface.fill(PAPER)")
j = s.index("        return surface", i)
new_paper = '''        theme = self.theme
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
'''
s = s[:i] + new_paper + s[j:]

# field drawing with theme
sub("        self._draw_text(surface, field.label, self.font_tiny, INK_MUTED, (x, y))", "        theme = self.theme\n        self._draw_text(surface, field.label, self.font_tiny, theme.muted, (x, y))")
sub("        pygame.draw.rect(surface, PAPER_LIGHT, value_rect)\n        pygame.draw.line(surface, accent or PAPER_DARK, value_rect.bottomleft, value_rect.bottomright, 3)",
    "        pygame.draw.rect(surface, theme.light, value_rect)\n        pygame.draw.line(surface, accent or theme.dark, value_rect.bottomleft, value_rect.bottomright, 3)")
sub("field.value, accent or INK, pygame.Rect(x + 7, y + 24", "field.value, accent or theme.ink, pygame.Rect(x + 7, y + 24")
sub("rendered = font.render(line, False, accent or INK)", "rendered = font.render(line, False, accent or theme.ink)")
sub("        pygame.draw.line(surface, INK_MUTED, (x, y), (x + width, y), 2)\n        self._draw_text(surface, label, self.font_tiny, INK_MUTED, (x, y + 6))",
    "        pygame.draw.line(surface, self.theme.muted, (x, y), (x + width, y), 2)\n        self._draw_text(surface, label, self.font_tiny, self.theme.muted, (x, y + 6))")
open(p, "w", encoding="utf-8").write(s)
