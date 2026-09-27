from __future__ import annotations

import pygame


INK = (216, 221, 132)
INK_BRIGHT = (247, 239, 161)
INK_MUTED = (132, 142, 87)
SCREEN_BLACK = (5, 9, 8)
PANEL = (17, 23, 20)
PANEL_MID = (29, 36, 30)
BORDER = (127, 137, 80)
BORDER_DARK = (55, 64, 45)
AMBER = (237, 193, 91)

SETUP_RECT = pygame.Rect(230, 40, 1094, 616)
OPTIONS = (
    (1, "CASO", "RÁPIDO", "Um caso sorteado do banco. Ótimo para experimentar."),
    (5, "CASOS", "TURNO NORMAL", "Um caso de cada nível, do mais fácil ao mais difícil."),
    (10, "CASOS", "TURNO LONGO", "Dois casos de cada nível, do mais fácil ao mais difícil."),
)
CARD_RECTS = tuple(pygame.Rect(270 + index * 347, 176, 320, 250) for index in range(len(OPTIONS)))
TUTORIAL_RECT = pygame.Rect(270, 452, 900, 40)
CLOCK_RECT = pygame.Rect(270, 498, 900, 40)
START_RECT = pygame.Rect(870, 566, 414, 56)


class GameSetup:
    """Pick how many cases to audit before the shift starts."""

    def __init__(self) -> None:
        self.is_open = False
        self.count = 5
        self.with_tutorial = True
        self.with_clock = True
        self.hovered: str | None = None
        self.font_tiny = self._font(16)
        self.font_small = self._font(19)
        self.font_body = self._font(22, bold=True)
        self.font_title = self._font(40, bold=True)
        self.font_number = self._font(84, bold=True)

    def open(self) -> None:
        self.is_open = True
        self.hovered = None

    def close(self) -> None:
        self.is_open = False

    def handle_mouse_down(self, position: tuple[int, int]) -> str | None:
        for (count, *_), rect in zip(OPTIONS, CARD_RECTS):
            if rect.collidepoint(position):
                self.count = count
                return "select"
        if TUTORIAL_RECT.collidepoint(position):
            self.with_tutorial = not self.with_tutorial
            return "select"
        if CLOCK_RECT.collidepoint(position):
            self.with_clock = not self.with_clock
            return "select"
        if START_RECT.collidepoint(position):
            return "start"
        return None

    def handle_key(self, event: pygame.event.Event) -> str | None:
        if event.type != pygame.KEYDOWN:
            return None
        counts = [option[0] for option in OPTIONS]
        index = counts.index(self.count)
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.count = counts[max(0, index - 1)]
            return "select"
        if event.key in (pygame.K_RIGHT, pygame.K_d):
            self.count = counts[min(len(counts) - 1, index + 1)]
            return "select"
        if event.key == pygame.K_1:
            self.count = 1
            return "select"
        if event.key == pygame.K_5:
            self.count = 5
            return "select"
        if event.key == pygame.K_0:
            self.count = 10
            return "select"
        if event.key == pygame.K_t:
            self.with_tutorial = not self.with_tutorial
            return "select"
        if event.key == pygame.K_c:
            self.with_clock = not self.with_clock
            return "select"
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return "start"
        return None

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered = None
        if position is None:
            return
        for (count, *_), rect in zip(OPTIONS, CARD_RECTS):
            if rect.collidepoint(position):
                self.hovered = f"card_{count}"
        if TUTORIAL_RECT.collidepoint(position):
            self.hovered = "tutorial"
        elif CLOCK_RECT.collidepoint(position):
            self.hovered = "clock"
        elif START_RECT.collidepoint(position):
            self.hovered = "start"

    def render(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 255))
        surface.blit(dim, (0, 0))
        pygame.draw.rect(surface, BORDER_DARK, SETUP_RECT.move(4, 4))
        pygame.draw.rect(surface, SCREEN_BLACK, SETUP_RECT)
        pygame.draw.rect(surface, BORDER, SETUP_RECT, 3)
        self._text(surface, "MONTE O SEU TURNO", self.font_title, INK_BRIGHT, (270, 70))
        self._text(surface, "Quantos casos você quer auditar? Eles são sorteados de um banco de 50.", self.font_small, INK, (270, 126))
        pygame.draw.line(surface, BORDER, (270, 160), (1284, 160), 2)

        for (count, unit, name, description), rect in zip(OPTIONS, CARD_RECTS):
            selected = count == self.count
            hovered = self.hovered == f"card_{count}"
            pygame.draw.rect(surface, PANEL_MID if selected or hovered else PANEL, rect)
            pygame.draw.rect(surface, AMBER if selected else (INK_BRIGHT if hovered else BORDER_DARK), rect, 4 if selected else 2)
            self._text(surface, str(count), self.font_number, INK_BRIGHT if selected else INK, (rect.centerx, rect.y + 28), "midtop")
            self._text(surface, unit, self.font_body, AMBER if selected else INK_MUTED, (rect.centerx, rect.y + 122), "midtop")
            self._text(surface, name, self.font_body, INK_BRIGHT, (rect.centerx, rect.y + 158), "midtop")
            self._wrap(surface, description, self.font_tiny, INK_MUTED, pygame.Rect(rect.x + 20, rect.y + 192, rect.width - 40, 52))
            if selected:
                self._text(surface, "ESCOLHIDO", self.font_tiny, AMBER, (rect.right - 14, rect.y + 12), "topright")

        self._checkbox(surface, TUTORIAL_RECT, self.with_tutorial, self.hovered == "tutorial",
                       "Começar pelo treinamento guiado (recomendado para quem nunca jogou)")
        self._checkbox(surface, CLOCK_RECT, self.with_clock, self.hovered == "clock",
                       "Modo relógio: cota de tempo e as verificações do VERIFY-9 (mais emoção!)")
        self._text(surface, "Dica: setas escolhem, T liga o treinamento, C liga o relógio e Enter começa.", self.font_tiny, INK_MUTED, (270, 566))

        hovered = self.hovered == "start"
        pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, START_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if hovered else AMBER, START_RECT, 3)
        self._text(surface, "COMEÇAR TURNO", self.font_body, INK_BRIGHT, START_RECT.center, "center")

    def _checkbox(self, surface: pygame.Surface, area: pygame.Rect, checked: bool, hovered: bool, label: str) -> None:
        box = pygame.Rect(area.x, area.y + 3, 34, 34)
        pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, box)
        pygame.draw.rect(surface, INK_BRIGHT if hovered else BORDER, box, 3)
        if checked:
            pygame.draw.line(surface, INK_BRIGHT, (box.x + 7, box.centery), (box.x + 14, box.bottom - 8), 5)
            pygame.draw.line(surface, INK_BRIGHT, (box.x + 14, box.bottom - 8), (box.right - 6, box.y + 8), 5)
        self._text(surface, label, self.font_small, INK, (box.right + 16, box.y + 6))

    def _wrap(self, surface: pygame.Surface, text: str, font: pygame.font.Font, color, rect: pygame.Rect) -> None:
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
        lines.append(current)
        for index, line in enumerate(lines[:3]):
            self._text(surface, line, font, color, (rect.centerx, rect.y + index * 20), "midtop")

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)

    @staticmethod
    def _text(surface, text, font, color, position, anchor="topleft") -> None:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
