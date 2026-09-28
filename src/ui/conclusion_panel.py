from __future__ import annotations

import random

import pygame

from src.gameplay.cases import AuditCase


INK = (216, 221, 132)
INK_BRIGHT = (247, 239, 161)
INK_MUTED = (132, 142, 87)
SCREEN_BLACK = (5, 9, 8)
PANEL = (17, 23, 20)
PANEL_MID = (29, 36, 30)
BORDER = (127, 137, 80)
BORDER_DARK = (55, 64, 45)
AMBER = (237, 193, 91)

PANEL_RECT = pygame.Rect(200, 30, 1154, 636)
ROW_HEIGHT = 84
ROW_TOP = 200
CONFIRM_RECT = pygame.Rect(900, 596, 424, 54)


class ConclusionPanel:
    """Before stamping, the player ticks the statements they believe are true."""

    def __init__(self) -> None:
        self.is_open = False
        self.statements: list[tuple[str, bool]] = []
        self.checked: set[int] = set()
        self.hovered: str | None = None
        self.font_tiny = self._font(16)
        self.font_body = self._font(22, bold=True)
        self.font_row = self._font(22)
        self.font_title = self._font(34, bold=True)
        self.font_button = self._font(22, bold=True)

    def open(self, case: AuditCase) -> None:
        order = list(case.conclusions)
        random.Random(case.case_id).shuffle(order)
        self.statements = order
        self.checked = set()
        self.is_open = True
        self.hovered = None

    def close(self) -> None:
        self.is_open = False

    def row_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(240, ROW_TOP + index * (ROW_HEIGHT + 8), 1074, ROW_HEIGHT)

    def score(self) -> tuple[int, int]:
        """(right answers, total): a ticked box is right for true statements, blank for false."""
        correct = sum(1 for index, (_, truth) in enumerate(self.statements) if (index in self.checked) == truth)
        return correct, len(self.statements)

    def tutorial_target(self) -> pygame.Rect:
        """The next true statement to tick, then the confirm button."""
        for index, (_, truth) in enumerate(self.statements):
            if truth and index not in self.checked:
                return self.row_rect(index)
        return CONFIRM_RECT

    def handle_mouse_down(self, position: tuple[int, int]) -> str | None:
        for index in range(len(self.statements)):
            if self.row_rect(index).collidepoint(position):
                self.checked.symmetric_difference_update({index})
                return "toggle"
        if CONFIRM_RECT.collidepoint(position):
            return "confirm"
        return "consume" if PANEL_RECT.collidepoint(position) else None

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered = None
        if position is None:
            return
        for index in range(len(self.statements)):
            if self.row_rect(index).collidepoint(position):
                self.hovered = f"row_{index}"
        if CONFIRM_RECT.collidepoint(position):
            self.hovered = "confirm"

    def render(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 165))  # translucent: the desk stays faintly visible behind the popup
        surface.blit(dim, (0, 0))
        pygame.draw.rect(surface, BORDER_DARK, PANEL_RECT.move(4, 4), border_radius=22)
        pygame.draw.rect(surface, SCREEN_BLACK, PANEL_RECT, border_radius=22)
        pygame.draw.rect(surface, BORDER, PANEL_RECT, 3, border_radius=22)
        self._text(surface, "ANTES DE CARIMBAR: O QUE VOCÊ DESCOBRIU?", self.font_title, INK_BRIGHT, (240, 58))
        self._text(surface, "Marque as frases que você acredita serem VERDADEIRAS. Use o que viu nos papéis.", self.font_row, INK, (240, 112))
        self._text(surface, "Não é prova: serve para você organizar o raciocínio. O jornal mostra quantas você acertou.", self.font_tiny, INK_MUTED, (240, 148))
        pygame.draw.line(surface, BORDER, (240, 180), (1314, 180), 2)

        for index, (text, _) in enumerate(self.statements):
            rect = self.row_rect(index)
            hovered = self.hovered == f"row_{index}"
            checked = index in self.checked
            pygame.draw.rect(surface, PANEL_MID if hovered or checked else PANEL, rect)
            pygame.draw.rect(surface, AMBER if checked else (INK_BRIGHT if hovered else BORDER_DARK), rect, 3 if checked else 2)
            box = pygame.Rect(rect.x + 24, rect.centery - 20, 40, 40)
            pygame.draw.rect(surface, SCREEN_BLACK, box)
            pygame.draw.rect(surface, INK_BRIGHT if checked else BORDER, box, 3)
            if checked:
                pygame.draw.line(surface, AMBER, (box.x + 8, box.centery + 1), (box.x + 17, box.bottom - 9), 6)
                pygame.draw.line(surface, AMBER, (box.x + 17, box.bottom - 9), (box.right - 7, box.y + 9), 6)
            self._wrap(surface, text, INK_BRIGHT if checked else INK, pygame.Rect(box.right + 28, rect.y + 20, rect.width - 130, rect.height - 30))

        hovered = self.hovered == "confirm"
        pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, CONFIRM_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if hovered else AMBER, CONFIRM_RECT, 3)
        self._text(surface, "CONFIRMAR CONCLUSÕES", self.font_button, INK_BRIGHT, CONFIRM_RECT.center, "center")
        self._text(surface, f"{len(self.checked)} de {len(self.statements)} marcadas", self.font_tiny, INK_MUTED, (240, 618))

    def _wrap(self, surface: pygame.Surface, text: str, color, rect: pygame.Rect) -> None:
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = f"{current} {word}".strip()
            if not current or self.font_row.size(candidate)[0] <= rect.width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        for index, line in enumerate(lines[:2]):
            self._text(surface, line, self.font_row, color, (rect.x, rect.y + index * 30))

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)

    @staticmethod
    def _text(surface, text, font, color, position, anchor="topleft") -> None:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
