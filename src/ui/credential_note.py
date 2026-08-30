from __future__ import annotations

import pygame


class CredentialNote:
    """Pixel-perfect hotspot and hover treatment for the heart post-it."""

    def __init__(self, note_asset: pygame.Surface) -> None:
        self.note_rect = note_asset.get_bounding_rect(min_alpha=16)
        if self.note_rect.width == 0 or self.note_rect.height == 0:
            raise ValueError("Heart note asset cannot be empty")
        note_crop = note_asset.subsurface(self.note_rect).copy()
        self.note_mask = pygame.mask.from_surface(note_crop, threshold=16)
        self.note_highlight = note_crop.copy()
        self.note_highlight.fill(
            (82, 82, 82, 0),
            special_flags=pygame.BLEND_RGBA_ADD,
        )
        self.note_hovered = False

    def clear_hover(self) -> None:
        self.note_hovered = False

    def contains_note(self, position: tuple[int, int] | None) -> bool:
        if position is None or not self.note_rect.collidepoint(position):
            return False
        local = (
            position[0] - self.note_rect.x,
            position[1] - self.note_rect.y,
        )
        return bool(self.note_mask.get_at(local))

    def update_note_hover(
        self,
        position: tuple[int, int] | None,
        *,
        enabled: bool,
    ) -> None:
        self.note_hovered = enabled and self.contains_note(position)

    def render_note_highlight(self, surface: pygame.Surface) -> None:
        if self.note_hovered:
            surface.blit(self.note_highlight, self.note_rect)
