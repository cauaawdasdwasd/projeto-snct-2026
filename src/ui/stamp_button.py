from __future__ import annotations

import pygame


OUTLINE_COLOR = (255, 232, 64, 255)
OUTLINE_WIDTH = 2
BLINK_INTERVAL_MS = 300


class StampButton:
    """Clickable stamp image used by the audit interface."""

    def __init__(
        self,
        stamp_id: str,
        image: pygame.Surface,
        center: tuple[int, int],
    ) -> None:
        self.stamp_id = stamp_id
        self.image = image
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)
        self.outline_surface = self._build_outline_surface()
        self.is_hovered = False
        self.is_selected = False

    def contains_point(self, position: tuple[int, int]) -> bool:
        if not self.rect.collidepoint(position):
            return False

        local_position = position[0] - self.rect.x, position[1] - self.rect.y
        return bool(self.mask.get_at(local_position))

    def update_hover(self, mouse_position: tuple[int, int] | None) -> None:
        self.is_hovered = mouse_position is not None and self.contains_point(mouse_position)

    def handle_click(self, mouse_position: tuple[int, int] | None) -> bool:
        return mouse_position is not None and self.contains_point(mouse_position)

    def set_selected(self, is_selected: bool) -> None:
        self.is_selected = is_selected

    def render(self, surface: pygame.Surface) -> None:
        if self._should_render_outline():
            outline_position = (
                self.rect.x - OUTLINE_WIDTH,
                self.rect.y - OUTLINE_WIDTH,
            )
            surface.blit(self.outline_surface, outline_position)

        surface.blit(self.image, self.rect)

    def _should_render_outline(self) -> bool:
        if self.is_selected:
            return (pygame.time.get_ticks() // BLINK_INTERVAL_MS) % 2 == 0

        return self.is_hovered

    def _build_outline_surface(self) -> pygame.Surface:
        width, height = self.rect.size
        outline_size = width + OUTLINE_WIDTH * 2, height + OUTLINE_WIDTH * 2
        outline_mask = pygame.mask.Mask(outline_size, fill=False)

        for dx in range(-OUTLINE_WIDTH, OUTLINE_WIDTH + 1):
            for dy in range(-OUTLINE_WIDTH, OUTLINE_WIDTH + 1):
                if dx == 0 and dy == 0:
                    continue
                outline_mask.draw(self.mask, (dx + OUTLINE_WIDTH, dy + OUTLINE_WIDTH))

        outline_mask.erase(self.mask, (OUTLINE_WIDTH, OUTLINE_WIDTH))
        return outline_mask.to_surface(
            setcolor=OUTLINE_COLOR,
            unsetcolor=(0, 0, 0, 0),
        ).convert_alpha()
