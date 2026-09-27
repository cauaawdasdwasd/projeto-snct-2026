"""Building blocks that give every paper its own layout: tables, chats, timelines, charts, receipts...

A paper is described in `data/case_docs_extra.json` as a list of blocks. A cell, line or value written as
"@LABEL" is replaced by the case field with that label, and becomes a clickable piece of evidence right
inside the layout (so the data that matters sits in the table, the chat or the receipt where it belongs).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from src.gameplay.cases import DocumentField

WIDTH = 544
LEFT = 38
GAP = 12


@dataclass
class Ink:
    paper: tuple[int, int, int]
    light: tuple[int, int, int]
    dark: tuple[int, int, int]
    ink: tuple[int, int, int]
    muted: tuple[int, int, int]
    accent: tuple[int, int, int]


class BlockPainter:
    def __init__(self, fonts: dict[str, pygame.font.Font], ink: Ink, fields: tuple[DocumentField, ...]) -> None:
        self.f = fonts
        self.c = ink
        self.fields = {field.label.strip().upper(): field for field in fields}
        self.used: set[str] = set()
        self.regions: list[tuple[DocumentField, pygame.Rect]] = []
        self.pad = 0  # extra air per row, grown by the renderer when a paper has spare room

    # --- helpers ------------------------------------------------------------------------------

    def resolve(self, text: str) -> tuple[str, DocumentField | None]:
        if isinstance(text, str) and text.startswith("@"):
            field = self.fields.get(text[1:].strip().upper())
            if field is None:
                raise ValueError(f"Unknown field reference {text}")
            return field.value, field
        return str(text), None

    def wrap(self, text: str, font: pygame.font.Font, width: int) -> list[str]:
        lines: list[str] = []
        for paragraph in text.split("\n"):
            current = ""
            for word in paragraph.split():
                candidate = f"{current} {word}".strip()
                if not current or font.size(candidate)[0] <= width:
                    current = candidate
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
        return lines or [""]

    def clip(self, lines: list[str], limit: int) -> list[str]:
        if len(lines) > limit:
            raise ValueError(f"Text does not fit in {limit} lines: {' '.join(lines)[:70]}")
        return lines

    def text(self, surface, text, font, color, pos, anchor="topleft") -> pygame.Rect:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, pos)
        surface.blit(rendered, rect)
        return rect

    def mark(self, surface: pygame.Surface, field: DocumentField, rect: pygame.Rect) -> None:
        """Underline a piece of evidence and register its clickable area."""
        pygame.draw.line(surface, self.c.accent, rect.bottomleft, rect.bottomright, 3)
        self.used.add(field.label.strip().upper())
        self.regions.append((field, rect))

    def title(self, surface, title: str, x: int, y: int) -> int:
        if not title:
            return y
        self.text(surface, title.upper(), self.f["tiny"], self.c.muted, (x, y))
        pygame.draw.line(surface, self.c.dark, (x, y + 18), (x + WIDTH, y + 18), 1)
        return y + 24

    def title_height(self, block: dict) -> int:
        return 24 if block.get("title") else 0

    # --- measure + draw dispatch --------------------------------------------------------------

    def height(self, block: dict) -> int:
        return getattr(self, f"_h_{block['type']}")(block)

    def draw(self, surface: pygame.Surface, block: dict, y: int) -> int:
        """Draw the block with its top at y; returns the height used."""
        getattr(self, f"_d_{block['type']}")(surface, block, y)
        return self.height(block)

    # --- table --------------------------------------------------------------------------------

    def _col_widths(self, block: dict) -> list[int]:
        cols = block["cols"]
        shares = block.get("widths") or [1 / len(cols)] * len(cols)
        widths = [int(WIDTH * share) for share in shares]
        widths[-1] += WIDTH - sum(widths)
        return widths

    def _row_height(self, row: list, widths: list[int]) -> int:
        lines = 1
        for cell, width in zip(row, widths):
            value, _ = self.resolve(cell)
            lines = max(lines, len(self.clip(self.wrap(value, self.f["small"], width - 14), 4)))
        return 12 + 18 * lines + self.pad

    def _h_table(self, block: dict) -> int:
        widths = self._col_widths(block)
        return self.title_height(block) + 26 + sum(self._row_height(row, widths) for row in block["rows"])

    def _d_table(self, surface, block: dict, y: int) -> None:
        widths = self._col_widths(block)
        y = self.title(surface, block.get("title", ""), LEFT, y)
        x = LEFT
        pygame.draw.rect(surface, self.c.accent, (LEFT, y, WIDTH, 26))
        for name, width in zip(block["cols"], widths):
            self.text(surface, name.upper(), self.f["tiny_bold"], self.c.paper, (x + 7, y + 6))
            x += width
        y += 26
        body_top = y
        for index, row in enumerate(block["rows"]):
            height = self._row_height(row, widths)
            pygame.draw.rect(surface, self.c.light if index % 2 == 0 else self.c.paper, (LEFT, y, WIDTH, height))
            x = LEFT
            for cell, width in zip(row, widths):
                value, field = self.resolve(cell)
                cell_rect = pygame.Rect(x + 2, y + 2, width - 4, height - 4)
                color = self.c.accent if field else self.c.ink
                font = self.f["small_bold"] if field else self.f["small"]
                for line_index, line in enumerate(self.clip(self.wrap(value, font, width - 14), 4)):
                    self.text(surface, line, font, color, (x + 7, y + 6 + self.pad // 2 + line_index * 18))
                if field is not None:
                    self.mark(surface, field, cell_rect)
                x += width
            y += height
            pygame.draw.line(surface, self.c.dark, (LEFT, y), (LEFT + WIDTH, y), 1)
        x = LEFT
        for width in widths[:-1]:
            x += width
            pygame.draw.line(surface, self.c.dark, (x, body_top), (x, y), 1)
        pygame.draw.rect(surface, self.c.dark, (LEFT, body_top - 26, WIDTH, y - body_top + 26), 2)

    # --- chat ---------------------------------------------------------------------------------

    def _bubble_lines(self, message: list) -> list[str]:
        value, _ = self.resolve(message[2])
        return self.clip(self.wrap(value, self.f["small"], 380), 4)

    def _h_chat(self, block: dict) -> int:
        return self.title_height(block) + sum(24 + 18 * len(self._bubble_lines(m)) + 8 + self.pad for m in block["messages"])

    def _d_chat(self, surface, block: dict, y: int) -> None:
        y = self.title(surface, block.get("title", ""), LEFT, y)
        for side, who, body in block["messages"]:
            lines = self._bubble_lines([side, who, body])
            height = 24 + 18 * len(lines) + self.pad // 2
            width = 410
            x = LEFT + (WIDTH - width if side == "R" else 0)
            fill = self.c.light if side == "L" else tuple(int(a * 0.82 + b * 0.18) for a, b in zip(self.c.light, self.c.accent))
            pygame.draw.rect(surface, fill, (x, y, width, height), border_radius=8)
            pygame.draw.rect(surface, self.c.dark, (x, y, width, height), 2, border_radius=8)
            self.text(surface, who, self.f["tiny_bold"], self.c.accent, (x + 10, y + 5 + self.pad // 4))
            value, field = self.resolve(body)
            for index, line in enumerate(lines):
                rect = self.text(surface, line, self.f["small_bold"] if field else self.f["small"], self.c.ink, (x + 10, y + 22 + self.pad // 4 + index * 18))
            if field is not None:
                self.mark(surface, field, pygame.Rect(x + 6, y + 20 + self.pad // 4, width - 12, 4 + 18 * len(lines)))
            y += height + 8 + self.pad // 2

    # --- timeline -----------------------------------------------------------------------------

    def _tl_lines(self, entry: list) -> list[str]:
        value, _ = self.resolve(entry[1])
        return self.clip(self.wrap(value, self.f["small"], 390), 3)

    def _h_timeline(self, block: dict) -> int:
        return self.title_height(block) + sum(14 + 18 * len(self._tl_lines(e)) + self.pad for e in block["entries"]) + 4

    def _d_timeline(self, surface, block: dict, y: int) -> None:
        y = self.title(surface, block.get("title", ""), LEFT, y)
        top = y
        total = sum(14 + 18 * len(self._tl_lines(e)) + self.pad for e in block["entries"])
        pygame.draw.line(surface, self.c.dark, (LEFT + 96, top), (LEFT + 96, top + total), 3)
        for time, body in block["entries"]:
            lines = self._tl_lines([time, body])
            value, field = self.resolve(body)
            self.text(surface, time, self.f["small_bold"], self.c.accent, (LEFT + 4, y + 2))
            pygame.draw.circle(surface, self.c.accent if field else self.c.ink, (LEFT + 96, y + 11), 7)
            pygame.draw.circle(surface, self.c.paper, (LEFT + 96, y + 11), 3)
            for index, line in enumerate(lines):
                self.text(surface, line, self.f["small_bold"] if field else self.f["small"], self.c.ink, (LEFT + 116, y + 2 + index * 18))
            if field is not None:
                self.mark(surface, field, pygame.Rect(LEFT + 110, y, WIDTH - 110, 6 + 18 * len(lines)))
            y += 14 + 18 * len(lines) + self.pad

    # --- checklist ----------------------------------------------------------------------------

    def _h_checklist(self, block: dict) -> int:
        return self.title_height(block) + (30 + self.pad) * len(block["items"]) + 4

    def _d_checklist(self, surface, block: dict, y: int) -> None:
        y = self.title(surface, block.get("title", ""), LEFT, y)
        for label, mark in block["items"]:
            value, field = self.resolve(label)
            box = pygame.Rect(LEFT + 4, y + 3, 20, 20)
            pygame.draw.rect(surface, self.c.light, box)
            pygame.draw.rect(surface, self.c.ink, box, 2)
            if mark == "x":
                pygame.draw.line(surface, self.c.accent, (box.x + 4, box.centery), (box.x + 8, box.bottom - 4), 4)
                pygame.draw.line(surface, self.c.accent, (box.x + 8, box.bottom - 4), (box.right - 3, box.y + 3), 4)
            elif mark == "-":
                pygame.draw.line(surface, self.c.muted, (box.x + 4, box.centery), (box.right - 4, box.centery), 3)
            self.text(surface, value, self.f["small_bold"] if field else self.f["small"], self.c.ink, (LEFT + 36, y + 4))
            if field is not None:
                self.mark(surface, field, pygame.Rect(LEFT + 32, y, WIDTH - 36, 26))
            y += 30 + self.pad

    # --- bars ---------------------------------------------------------------------------------

    def _h_bars(self, block: dict) -> int:
        return self.title_height(block) + (32 + self.pad) * len(block["bars"]) + 4

    def _d_bars(self, surface, block: dict, y: int) -> None:
        y = self.title(surface, block.get("title", ""), LEFT, y)
        for label, share, shown in block["bars"]:
            value, field = self.resolve(shown)
            self.text(surface, label, self.f["small"], self.c.ink, (LEFT + 2, y + 5))
            track = pygame.Rect(LEFT + 170, y + 4, 240, 22)
            pygame.draw.rect(surface, self.c.light, track)
            pygame.draw.rect(surface, self.c.accent if field else self.c.muted, (track.x, track.y, int(track.width * share), track.height))
            pygame.draw.rect(surface, self.c.ink, track, 2)
            rect = self.text(surface, value, self.f["small_bold"], self.c.ink, (track.right + 10, y + 5))
            if field is not None:
                self.mark(surface, field, pygame.Rect(track.right + 4, y, WIDTH - 170 - 240 - 4, 28))
            y += 32 + self.pad

    # --- terminal -----------------------------------------------------------------------------

    def _terminal_rows(self, block: dict) -> list[tuple[str, DocumentField | None]]:
        rows: list[tuple[str, DocumentField | None]] = []
        for line in block["lines"]:
            value, field = self.resolve(line)
            for piece in self.clip(self.wrap(value, self.f["small"], 480), 3):
                rows.append((piece, field))
        return rows

    def _h_terminal(self, block: dict) -> int:
        return self.title_height(block) + 34 + 21 * len(self._terminal_rows(block))

    def _d_terminal(self, surface, block: dict, y: int) -> None:
        y = self.title(surface, block.get("title", ""), LEFT, y)
        rows = self._terminal_rows(block)
        box = pygame.Rect(LEFT, y, WIDTH, 34 + 21 * len(rows))
        pygame.draw.rect(surface, (14, 20, 17), box)
        pygame.draw.rect(surface, (90, 110, 60), box, 3)
        for index, color in enumerate(((224, 82, 67), (237, 193, 91), (101, 191, 91))):
            pygame.draw.circle(surface, color, (box.x + 16 + index * 16, box.y + 12), 5)
        spans: dict[str, list[int]] = {}
        for index, (line, field) in enumerate(rows):
            rect = self.text(surface, "> " + line, self.f["small_bold"] if field else self.f["small"], (244, 236, 157) if field else (150, 210, 130), (box.x + 12, box.y + 26 + index * 21))
            if field is not None:
                spans.setdefault(field.label.strip().upper(), [index, index, field])
                spans[field.label.strip().upper()][1] = index
        for _label, (first, last, field) in spans.items():
            area = pygame.Rect(box.x + 8, box.y + 24 + first * 21, WIDTH - 16, 22 + (last - first) * 21)
            pygame.draw.line(surface, (244, 236, 157), area.bottomleft, area.bottomright, 2)
            self.used.add(field.label.strip().upper())
            self.regions.append((field, area))

    # --- note (sticky) ------------------------------------------------------------------------

    def _note_lines(self, block: dict) -> list[str]:
        value, _ = self.resolve(block["text"])
        return self.clip(self.wrap(value, self.f["small"], 300), 5)

    def _h_note(self, block: dict) -> int:
        return 34 + 19 * len(self._note_lines(block)) + 10

    def _d_note(self, surface, block: dict, y: int) -> None:
        lines = self._note_lines(block)
        height = 24 + 19 * len(lines)
        note = pygame.Surface((330, height + 6), pygame.SRCALPHA)
        pygame.draw.rect(note, (0, 0, 0, 50), (5, 6, 322, height))
        pygame.draw.rect(note, (244, 226, 128), (0, 0, 322, height))
        pygame.draw.rect(note, (214, 190, 90), (0, 0, 322, 14))
        for index, line in enumerate(lines):
            self.text(note, line, self.f["small"], (70, 54, 20), (12, 20 + index * 19))
        note = pygame.transform.rotate(note, block.get("tilt", 1.5))
        x = LEFT + (WIDTH - note.get_width() - 4 if block.get("side", "R") == "R" else 4)
        surface.blit(note, (x, y + 4))

    # --- letter / paragraph -------------------------------------------------------------------

    def _h_letter(self, block: dict) -> int:
        height = self.title_height(block) + 26 * len(block.get("headers", []))
        if block.get("text"):
            height += 12 + 20 * len(self.clip(self.wrap(block["text"], self.f["small"], WIDTH - 24), 6))
        return height + 8

    def _d_letter(self, surface, block: dict, y: int) -> None:
        y = self.title(surface, block.get("title", ""), LEFT, y)
        for label, value in block.get("headers", []):
            text, field = self.resolve(value)
            self.text(surface, label, self.f["tiny_bold"], self.c.muted, (LEFT + 4, y + 6))
            self.text(surface, text, self.f["small_bold"] if field else self.f["small"], self.c.ink, (LEFT + 90, y + 4))
            pygame.draw.line(surface, self.c.dark, (LEFT, y + 24), (LEFT + WIDTH, y + 24), 1)
            if field is not None:
                self.mark(surface, field, pygame.Rect(LEFT + 86, y, WIDTH - 86, 24))
            y += 26
        if block.get("text"):
            y += 8
            for line in self.clip(self.wrap(block["text"], self.f["small"], WIDTH - 24), 6):
                self.text(surface, line, self.f["small"], self.c.ink, (LEFT + 8, y))
                y += 20

    def _para_items(self, block: dict) -> list[tuple[list[str], DocumentField | None]]:
        items = []
        for item in block["items"]:
            value, field = self.resolve(item)
            items.append((self.clip(self.wrap(value, self.f["small_bold"] if field else self.f["small"], WIDTH - 48), 4), field))
        return items

    def _h_para(self, block: dict) -> int:
        return self.title_height(block) + sum(10 + 19 * len(lines) + self.pad for lines, _ in self._para_items(block)) + 2

    def _d_para(self, surface, block: dict, y: int) -> None:
        y = self.title(surface, block.get("title", ""), LEFT, y)
        for number, (lines, field) in enumerate(self._para_items(block), 1):
            height = 10 + 19 * len(lines) + self.pad
            if block.get("numbered", True):
                self.text(surface, f"{number}.", self.f["small_bold"], self.c.accent, (LEFT + 4, y + 4))
            for index, line in enumerate(lines):
                self.text(surface, line, self.f["small_bold"] if field else self.f["small"], self.c.ink, (LEFT + 36, y + 4 + index * 19))
            if field is not None:
                self.mark(surface, field, pygame.Rect(LEFT + 32, y, WIDTH - 36, height))
            y += height

    # --- receipt ------------------------------------------------------------------------------

    def _h_receipt(self, block: dict) -> int:
        return self.title_height(block) + (26 + self.pad // 2) * len(block["items"]) + (30 + self.pad // 2) * len(block.get("totals", [])) + 12

    def _d_receipt(self, surface, block: dict, y: int) -> None:
        y = self.title(surface, block.get("title", ""), LEFT, y)
        for name, qty, price in block["items"]:
            self._receipt_row(surface, y, name, qty, price, False)
            y += 26 + self.pad // 2
        pygame.draw.line(surface, self.c.ink, (LEFT, y + 2), (LEFT + WIDTH, y + 2), 2)
        y += 8
        for name, qty, price in [t if len(t) == 3 else [t[0], "", t[1]] for t in block.get("totals", [])]:
            self._receipt_row(surface, y, name, qty, price, True)
            y += 30 + self.pad // 2

    def _receipt_row(self, surface, y: int, name: str, qty: str, price: str, total: bool) -> None:
        font = self.f["small_bold"] if total else self.f["small"]
        name_text, name_field = self.resolve(name)
        qty_text, qty_field = self.resolve(qty)
        price_text, price_field = self.resolve(price)
        self.text(surface, name_text, font, self.c.ink, (LEFT + 4, y + 4))
        if qty_text:
            rect = self.text(surface, qty_text, font, self.c.accent if qty_field else self.c.ink, (LEFT + 340, y + 4), "topright")
            if qty_field is not None:
                self.mark(surface, qty_field, pygame.Rect(LEFT + 250, y, 94, 26))
        rect = self.text(surface, price_text, self.f["small_bold"] if price_field else font, self.c.accent if price_field else self.c.ink, (LEFT + WIDTH - 4, y + 4), "topright")
        if price_field is not None:
            self.mark(surface, price_field, pygame.Rect(LEFT + WIDTH - 190, y, 190, 26))
        if name_field is not None:
            self.mark(surface, name_field, pygame.Rect(LEFT, y, 240, 26))
        for x in range(LEFT + 4 + self.f["small"].size(name_text)[0] + 8, LEFT + 246, 8):  # dotted leader
            pygame.draw.rect(surface, self.c.dark, (x, y + 19, 2, 2))

    # --- seal ---------------------------------------------------------------------------------

    def _h_seal(self, block: dict) -> int:
        return 44

    def _d_seal(self, surface, block: dict, y: int) -> None:
        text = block["text"].upper()
        font = self.f["small_bold"]
        width = font.size(text)[0] + 28
        stamp = pygame.Surface((width, 36), pygame.SRCALPHA)
        color = self.c.accent
        pygame.draw.rect(stamp, color, (0, 0, width, 36), 3, border_radius=4)
        self.text(stamp, text, font, color, (width // 2, 18), "center")
        stamp = pygame.transform.rotate(stamp, block.get("tilt", -4))
        x = LEFT + (WIDTH - stamp.get_width() - 6 if block.get("side", "R") == "R" else 6)
        surface.blit(stamp, (x, y + 2))
