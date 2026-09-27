from __future__ import annotations

from difflib import SequenceMatcher

import pygame


INK = (216, 221, 132)
INK_BRIGHT = (247, 239, 161)
INK_MUTED = (132, 142, 87)
SCREEN_BLACK = (5, 9, 8)
PANEL = (17, 23, 20)
EQUAL = (101, 191, 91)
DIFFERENT = (224, 82, 67)
RELATED = (222, 186, 82)
BRIGHT_AMBER = (250, 220, 120)
UNRELATED = (150, 156, 140)

VERDICTS = {
    "equal": ("= IGUAIS", EQUAL),
    "different": ("≠ DIFERENTES", DIFFERENT),
    "related": ("RELACIONADOS", RELATED),
    "none": ("SEM RELAÇÃO", UNRELATED),
}

CARD_RECT = pygame.Rect(302, 572, 851, 114)
CLOSE_RECT = pygame.Rect(CARD_RECT.right - 34, CARD_RECT.y + 6, 26, 26)
PROTOCOL_BUTTON_RECT = pygame.Rect(CARD_RECT.right - 262, CARD_RECT.y + 68, 250, 38)
VALUE_WIDTH = 300


def diff_segments(left: str, right: str) -> tuple[list[tuple[str, bool]], list[tuple[str, bool]]]:
    """Split both strings into (text, differs) pieces so changes can be coloured."""
    matcher = SequenceMatcher(a=left, b=right, autojunk=False)
    left_parts: list[tuple[str, bool]] = []
    right_parts: list[tuple[str, bool]] = []
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        differs = tag != "equal"
        if a1 > a0:
            left_parts.append((left[a0:a1], differs))
        if b1 > b0:
            right_parts.append((right[b0:b1], differs))
    return left_parts, right_parts


class ComparisonCard:
    """Side-by-side result of comparing two pieces of evidence."""

    def __init__(self) -> None:
        self.hovered_close = False
        self.hovered_protocol = False
        self.font_tiny = self._font(14)
        self.font_small = self._font(17, bold=True)
        self.font_value = self._font(25, bold=True)
        self.font_value_small = self._font(19, bold=True)
        self.font_verdict = self._font(22, bold=True)

    def contains(self, position: tuple[int, int] | None) -> bool:
        return position is not None and CARD_RECT.collidepoint(position)

    def is_close_hit(self, position: tuple[int, int] | None) -> bool:
        return position is not None and CLOSE_RECT.collidepoint(position)

    def is_protocol_hit(self, position: tuple[int, int] | None) -> bool:
        return position is not None and PROTOCOL_BUTTON_RECT.collidepoint(position)

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered_close = self.is_close_hit(position)
        self.hovered_protocol = self.is_protocol_hit(position)

    def render(
        self,
        surface: pygame.Surface,
        first: tuple[str, str],
        second: tuple[str, str],
        kind: str,
        text: str,
        protocol: tuple[int, str, str] | None = None,
    ) -> None:
        verdict, color = VERDICTS.get(kind, VERDICTS["none"])
        pygame.draw.rect(surface, (0, 0, 0), CARD_RECT.move(4, 4))
        pygame.draw.rect(surface, SCREEN_BLACK, CARD_RECT)
        pygame.draw.rect(surface, color, CARD_RECT, 3)

        left_rect = pygame.Rect(CARD_RECT.x + 14, CARD_RECT.y + 8, VALUE_WIDTH, 54)
        right_rect = pygame.Rect(CARD_RECT.right - 50 - VALUE_WIDTH, left_rect.y, VALUE_WIDTH, left_rect.height)
        # Character highlights only make sense for codes of the same length
        # (LAB-4827O vs LAB-48270); other values are shown plainly.
        if kind == "different" and len(first[1]) == len(second[1]):
            left_parts, right_parts = diff_segments(first[1], second[1])
        else:
            left_parts, right_parts = [(first[1], False)], [(second[1], False)]
        self._draw_value(surface, left_rect, first[0], left_parts, color)
        self._draw_value(surface, right_rect, second[0], right_parts, color)

        middle_x = (left_rect.right + right_rect.x) // 2
        self._text(surface, verdict, self.font_verdict, color, (middle_x, left_rect.y + 38), "center")

        pygame.draw.line(surface, (55, 64, 45), (CARD_RECT.x + 14, CARD_RECT.y + 66), (CARD_RECT.right - 14, CARD_RECT.y + 66), 1)
        text_width = CARD_RECT.width - 28 - (PROTOCOL_BUTTON_RECT.width + 14 if protocol else 0)
        self._wrap(surface, text, color, pygame.Rect(CARD_RECT.x + 14, CARD_RECT.y + 74, text_width, 36))
        if protocol is not None:
            self._draw_protocol_button(surface, protocol)

        pygame.draw.rect(surface, (44, 50, 38) if self.hovered_close else PANEL, CLOSE_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if self.hovered_close else INK_MUTED, CLOSE_RECT, 2)
        cx, cy = CLOSE_RECT.center
        pygame.draw.line(surface, INK_BRIGHT, (cx - 5, cy - 5), (cx + 5, cy + 5), 3)
        pygame.draw.line(surface, INK_BRIGHT, (cx + 5, cy - 5), (cx - 5, cy + 5), 3)

    def _draw_value(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        parts: list[tuple[str, bool]],
        color: tuple[int, int, int],
    ) -> None:
        caption = label.upper()
        while len(caption) > 4 and self.font_tiny.size(caption)[0] > rect.width - 6:
            caption = caption[:-2].rstrip() + "…"
        self._text(surface, caption, self.font_tiny, INK_MUTED, (rect.x, rect.y))
        font = self.font_value
        if font.size("".join(text for text, _ in parts))[0] > rect.width:
            font = self.font_value_small
        x = rect.x
        for text, differs in parts:
            rendered = font.render(text, False, INK_BRIGHT if not differs else (255, 255, 255))
            width = rendered.get_width()
            if x + width > rect.right:
                break
            if differs:
                pygame.draw.rect(surface, color, pygame.Rect(x - 1, rect.y + 20, width + 2, 30))
            surface.blit(rendered, (x, rect.y + 20))
            x += width

    def _draw_protocol_button(self, surface: pygame.Surface, protocol: tuple[int, str, str]) -> None:
        number, scientist, topic = protocol
        rect = PROTOCOL_BUTTON_RECT
        pygame.draw.rect(surface, (44, 36, 14) if self.hovered_protocol else PANEL, rect)
        pygame.draw.rect(surface, BRIGHT_AMBER if self.hovered_protocol else (176, 148, 74), rect, 2)
        title_font = self._font(14, bold=True)
        title = self._fit(f"CONFIRA O PROTOCOLO {number:02d}", title_font, rect.width - 24)
        self._text(surface, title, title_font, BRIGHT_AMBER, (rect.x + 12, rect.y + 5))
        arrow_x, arrow_y = rect.right - 26, rect.centery
        pygame.draw.polygon(surface, BRIGHT_AMBER, [(arrow_x, arrow_y - 9), (arrow_x, arrow_y + 9), (arrow_x + 13, arrow_y)])
        subtitle_font = self._font(12)
        subtitle = self._fit(f"{scientist} · {topic}", subtitle_font, rect.width - 24)
        self._text(surface, subtitle, subtitle_font, INK, (rect.x + 12, rect.y + 22))

    @staticmethod
    def _fit(text: str, font: pygame.font.Font, width: int) -> str:
        """Truncate with an ellipsis instead of letting the text run past its box."""
        if font.size(text)[0] <= width:
            return text
        while text and font.size(text + "…")[0] > width:
            text = text[:-1]
        return text.rstrip() + "…"

    def _wrap(self, surface: pygame.Surface, text: str, color: tuple[int, int, int], rect: pygame.Rect) -> None:
        font = self._font(15, bold=True)
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = f"{current} {word}".strip()
            if not current or font.size(candidate)[0] <= rect.width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        if len(lines) > 2:  # never let text run off the card: fold it back into two lines with an ellipsis
            lines = [lines[0], self._fit(" ".join(lines[1:]), font, rect.width)]
        for index, line in enumerate(lines[:2]):
            self._text(surface, line, font, color, (rect.x, rect.y + index * 19))

    def _text_fitted(
        self,
        surface: pygame.Surface,
        text: str,
        color: tuple[int, int, int],
        position: tuple[int, int],
        width: int,
    ) -> None:
        for size in (17, 16, 15, 14, 13):
            font = self._font(size, bold=size >= 16)
            if font.size(text)[0] <= width:
                break
        while font.size(text)[0] > width and len(text) > 4:
            text = text[:-2].rstrip() + "…"
        self._text(surface, text, font, color, position, "midbottom")

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
