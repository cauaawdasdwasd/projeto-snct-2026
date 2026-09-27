"""Side-by-side view: two papers of the case next to each other, so data can be compared with the eyes.

Everything is in monitor coordinates (the same space as the other modals). Clicking a piece of
evidence in either paper works exactly like on the desk (it starts or finishes a comparison), and
clicking a picture draws a red circle.
"""

from __future__ import annotations

import pygame

from src.minigames.common import (
    AMBER,
    BORDER,
    BORDER_DARK,
    INK,
    INK_BRIGHT,
    INK_MUTED,
    PANEL,
    PANEL_MID,
    SCREEN_BLACK,
    draw_text,
    font,
)

PANE_SIZE = (480, 620)
PANE_TOP = 58
LEFT_X = 281
RIGHT_X = 793
CLOSE_RECT = pygame.Rect(1440, 12, 104, 34)
SOURCE_SIZE = (620, 800)


class SideBySide:
    def __init__(self) -> None:
        self.is_open = False
        self.documents: list = []
        self.picks = [0, 1]
        self.hovered: str | None = None

    def open(self, documents: list, first: int = 0) -> None:
        self.documents = [d for d in documents if d.document_id != "final"]
        if len(self.documents) < 2:
            return
        self.is_open = True
        self.picks = [min(first, len(self.documents) - 1), 0]
        self.picks[1] = (self.picks[0] + 1) % len(self.documents)

    def close(self) -> None:
        self.is_open = False
        self.hovered = None

    # --- geometry -----------------------------------------------------------------------------

    @staticmethod
    def pane_rect(side: int) -> pygame.Rect:
        return pygame.Rect(LEFT_X if side == 0 else RIGHT_X, PANE_TOP, *PANE_SIZE)

    def chip_rects(self, side: int) -> list[pygame.Rect]:
        count = len(self.documents)
        pane = self.pane_rect(side)
        width = (pane.width - 6 * (count - 1)) // count
        return [pygame.Rect(pane.x + index * (width + 6), 14, width, 34) for index in range(count)]

    def document_at(self, position: tuple[int, int]):
        for side in (0, 1):
            pane = self.pane_rect(side)
            if pane.collidepoint(position):
                document = self.documents[self.picks[side]]
                source = (
                    round((position[0] - pane.x) * SOURCE_SIZE[0] / pane.width),
                    round((position[1] - pane.y) * SOURCE_SIZE[1] / pane.height),
                )
                return document, source
        return None

    # --- input --------------------------------------------------------------------------------

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered = None
        if position is None or not self.is_open:
            return
        if CLOSE_RECT.collidepoint(position):
            self.hovered = "close"
            return
        for side in (0, 1):
            for index, rect in enumerate(self.chip_rects(side)):
                if rect.collidepoint(position):
                    self.hovered = f"chip_{side}_{index}"

    def handle_mouse_down(self, position: tuple[int, int]):
        """Returns "close", "chip", ("paper", document, source_position) or None."""
        if CLOSE_RECT.collidepoint(position):
            return "close"
        for side in (0, 1):
            for index, rect in enumerate(self.chip_rects(side)):
                if rect.collidepoint(position):
                    other = 1 - side
                    if index == self.picks[other]:  # never show the same paper twice: swap instead
                        self.picks[other] = self.picks[side]
                    self.picks[side] = index
                    return "chip"
        hit = self.document_at(position)
        if hit is not None:
            return ("paper", *hit)
        return None

    # --- drawing ------------------------------------------------------------------------------

    def render(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 255))
        surface.blit(dim, (0, 0))
        draw_text(surface, "LADO A LADO", font(20, True), INK_BRIGHT, (LEFT_X - 250, 22))
        hovered = self.hovered == "close"
        pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, CLOSE_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if hovered else AMBER, CLOSE_RECT, 3)
        draw_text(surface, "FECHAR", font(16, True), INK_BRIGHT, CLOSE_RECT.center, "center")

        for side in (0, 1):
            pane = self.pane_rect(side)
            for index, rect in enumerate(self.chip_rects(side)):
                document = self.documents[index]
                selected = self.picks[side] == index
                hot = self.hovered == f"chip_{side}_{index}"
                pygame.draw.rect(surface, PANEL_MID if selected or hot else PANEL, rect)
                pygame.draw.rect(surface, AMBER if selected else (INK_BRIGHT if hot else BORDER_DARK), rect, 3 if selected else 2)
                label = f"{document.order_number or index + 1} {document.title}"
                while font(13, True).size(label)[0] > rect.width - 10 and len(label) > 4:
                    label = label[:-2]
                draw_text(surface, label, font(13, True), INK_BRIGHT if selected else INK, rect.center, "center")

            document = self.documents[self.picks[side]]
            pygame.draw.rect(surface, (0, 0, 0), pane.move(6, 6))
            picture = pygame.transform.smoothscale(document.composed_surface(), pane.size)
            surface.blit(picture, pane)
            scale_x = pane.width / SOURCE_SIZE[0]
            scale_y = pane.height / SOURCE_SIZE[1]
            for region in document.evidence_regions:  # a small marker on every clickable piece of evidence
                if region.key in document.marked_evidence:
                    continue
                rect = pygame.Rect(
                    pane.x + region.rect.x * scale_x,
                    pane.y + region.rect.y * scale_y,
                    max(1, region.rect.width * scale_x),
                    max(1, region.rect.height * scale_y),
                )
                center = (rect.right - 8, rect.centery)
                pygame.draw.polygon(surface, (244, 216, 65), [(center[0], center[1] - 6), (center[0] + 6, center[1]), (center[0], center[1] + 6), (center[0] - 6, center[1])])
            pygame.draw.rect(surface, BORDER, pane, 3)

        draw_text(
            surface,
            "Clique nos dados com losango para comparar",
            font(14),
            INK_MUTED,
            (777, 682),
            "midtop",
        )
