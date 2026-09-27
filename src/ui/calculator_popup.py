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
AMBER = (211, 149, 47)

TITLE_HEIGHT = 34
SIZE = (292, 396)
START_POSITION = (846, 196)
BOUNDS = pygame.Rect(0, 0, 1554, 696)
BUTTON_LAYOUT = (
    ("←", "C", "÷", "×"),
    ("7", "8", "9", "-"),
    ("4", "5", "6", "+"),
    ("1", "2", "3", "%"),
    ("0", ".", "", "="),
)
OPERATORS = {"+", "-", "×", "÷"}
KEY_LABELS = {
    pygame.K_KP_PLUS: "+",
    pygame.K_KP_MINUS: "-",
    pygame.K_KP_MULTIPLY: "×",
    pygame.K_KP_DIVIDE: "÷",
    pygame.K_RETURN: "=",
    pygame.K_KP_ENTER: "=",
    pygame.K_BACKSPACE: "←",
    pygame.K_DELETE: "C",
}


class CalculatorPopup:
    """Small floating calculator that stays usable over the document desk."""

    def __init__(self) -> None:
        self.is_open = False
        self.rect = pygame.Rect(START_POSITION, SIZE)
        self.display = "0"
        self.accumulator: float | None = None
        self.operator: str | None = None
        self.new_entry = True
        self.hovered_label: str | None = None
        self.hovered_close = False
        self._drag_offset: tuple[int, int] | None = None
        self.font_title = self._font(17, bold=True)
        self.font_display = self._font(34, bold=True)
        self.font_button = self._font(24, bold=True)
        self.font_tiny = self._font(14)

    # -- lifecycle -------------------------------------------------------
    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False
        self._drag_offset = None
        self.hovered_label = None
        self.hovered_close = False

    def toggle(self) -> None:
        if self.is_open:
            self.close()
        else:
            self.open()

    # -- geometry ----------------------------------------------------------
    @property
    def title_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.x, self.rect.y, self.rect.width, TITLE_HEIGHT)

    @property
    def close_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.right - 32, self.rect.y + 4, 26, 26)

    @property
    def display_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.x + 14, self.rect.y + TITLE_HEIGHT + 12, self.rect.width - 28, 62)

    def button_rects(self) -> tuple[tuple[str, pygame.Rect], ...]:
        left = self.rect.x + 14
        top = self.display_rect.bottom + 14
        gap = 8
        width = (self.rect.width - 28 - gap * 3) // 4
        height = (self.rect.bottom - 14 - top - gap * 4) // 5
        buttons: list[tuple[str, pygame.Rect]] = []
        for row, labels in enumerate(BUTTON_LAYOUT):
            for column, label in enumerate(labels):
                if not label:
                    continue
                rect = pygame.Rect(
                    left + column * (width + gap),
                    top + row * (height + gap),
                    width,
                    height,
                )
                if label == "0":
                    rect.width = width * 2 + gap
                elif label == "." and row == 4:
                    rect.x = left + 2 * (width + gap)
                buttons.append((label, rect))
        return tuple(buttons)

    def contains(self, position: tuple[int, int] | None) -> bool:
        return bool(self.is_open and position is not None and self.rect.collidepoint(position))

    # -- input -------------------------------------------------------------
    def handle_mouse_down(self, position: tuple[int, int]) -> str | None:
        """Return a sound hint when the click belongs to the calculator."""
        if not self.contains(position):
            return None
        if self.close_rect.collidepoint(position):
            self.close()
            return "back"
        if self.title_rect.collidepoint(position):
            self._drag_offset = (position[0] - self.rect.x, position[1] - self.rect.y)
            return "consume"
        for label, rect in self.button_rects():
            if rect.collidepoint(position):
                self.press(label)
                return "click"
        return "consume"

    def handle_mouse_motion(self, position: tuple[int, int] | None) -> None:
        if position is None:
            return
        if self._drag_offset is not None:
            self.rect.topleft = (position[0] - self._drag_offset[0], position[1] - self._drag_offset[1])
            self.rect.clamp_ip(BOUNDS)

    def handle_mouse_up(self) -> None:
        self._drag_offset = None

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered_label = None
        self.hovered_close = False
        if not self.contains(position):
            return
        self.hovered_close = self.close_rect.collidepoint(position)
        for label, rect in self.button_rects():
            if rect.collidepoint(position):
                self.hovered_label = label
                return

    def handle_key(self, event: pygame.event.Event) -> bool:
        if not self.is_open:
            return False
        label = KEY_LABELS.get(event.key)
        typed = getattr(event, "unicode", "")
        if typed and typed in "0123456789.,+-*/%=":
            label = {"*": "×", "/": "÷", ",": "."}.get(typed, typed)
        if label is None:
            return False
        self.press(label)
        return True

    # -- arithmetic --------------------------------------------------------
    def press(self, label: str) -> None:
        if self.display == "Erro" and label != "C":
            return
        if label.isdigit() or label == ".":
            self._press_digit(label)
        elif label == "C":
            self.display, self.accumulator, self.operator, self.new_entry = "0", None, None, True
        elif label == "←":
            self.display = self.display[:-1] or "0"
            if self.display == "-":
                self.display = "0"
        elif label == "%":
            self.display = f"{float(self.display) / 100:.10g}"
            self.new_entry = True
        elif label in OPERATORS:
            if self.operator is not None and not self.new_entry:
                self._calculate()
            if self.display != "Erro":
                self.accumulator = float(self.display)
            self.operator = label
            self.new_entry = True
        elif label == "=":
            self._calculate()

    def _press_digit(self, label: str) -> None:
        if self.new_entry:
            self.display = "0." if label == "." else label
            self.new_entry = False
            return
        if len(self.display) >= 15 or (label == "." and "." in self.display):
            return
        self.display = label if self.display == "0" and label != "." else self.display + label

    def _calculate(self) -> None:
        if self.accumulator is None or self.operator is None:
            return
        right = float(self.display)
        try:
            result = {
                "+": self.accumulator + right,
                "-": self.accumulator - right,
                "×": self.accumulator * right,
                "÷": self.accumulator / right,
            }[self.operator]
            self.display = f"{result:.10g}"
        except ZeroDivisionError:
            self.display = "Erro"
        self.accumulator = None
        self.operator = None
        self.new_entry = True

    # -- drawing -----------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return
        pygame.draw.rect(surface, (0, 0, 0), self.rect.move(6, 6))
        pygame.draw.rect(surface, SCREEN_BLACK, self.rect)
        pygame.draw.rect(surface, BORDER, self.rect, 3)

        pygame.draw.rect(surface, (47, 54, 37), self.title_rect.inflate(-6, -6).move(0, 3))
        self._text(surface, "CALCULADORA", self.font_title, INK_BRIGHT, (self.rect.x + 16, self.rect.y + 9))
        close_fill = (120, 46, 38) if self.hovered_close else PANEL
        pygame.draw.rect(surface, close_fill, self.close_rect)
        pygame.draw.rect(surface, INK_BRIGHT if self.hovered_close else BORDER, self.close_rect, 2)
        cx, cy = self.close_rect.center
        pygame.draw.line(surface, INK_BRIGHT, (cx - 6, cy - 6), (cx + 6, cy + 6), 3)
        pygame.draw.line(surface, INK_BRIGHT, (cx + 6, cy - 6), (cx - 6, cy + 6), 3)

        pygame.draw.rect(surface, (9, 20, 15), self.display_rect)
        pygame.draw.rect(surface, BORDER_DARK, self.display_rect, 2)
        if self.operator is not None and self.accumulator is not None:
            self._text(
                surface,
                f"{self.accumulator:.10g} {self.operator}",
                self.font_tiny,
                INK_MUTED,
                (self.display_rect.x + 10, self.display_rect.y + 6),
            )
        shown = self.display if len(self.display) <= 12 else self.display[:12]
        self._text(surface, shown, self.font_display, INK_BRIGHT, (self.display_rect.right - 12, self.display_rect.bottom - 10), "bottomright")

        for label, rect in self.button_rects():
            hovered = label == self.hovered_label
            is_operator = label in OPERATORS or label == "="
            fill = PANEL_MID if hovered else PANEL
            if is_operator:
                fill = (66, 52, 24) if hovered else (44, 36, 19)
            pygame.draw.rect(surface, fill, rect)
            pygame.draw.rect(surface, INK_BRIGHT if hovered else (AMBER if is_operator else BORDER_DARK), rect, 2)
            self._text(surface, label, self.font_button, INK_BRIGHT if hovered else INK, rect.center, "center")

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)

    @staticmethod
    def _text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
        anchor: str = "topleft",
    ) -> None:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
