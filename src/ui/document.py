from __future__ import annotations

import pygame


class Document:
    """Interactive visual document that can be dragged around a virtual surface."""

    def __init__(
        self,
        image: pygame.Surface,
        position: tuple[int, int],
        *,
        name: str = "document",
    ) -> None:
        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.position = self.rect.topleft
        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)
        self.name = name

    def contains_point(self, position: tuple[int, int]) -> bool:
        return self.rect.collidepoint(position)

    def start_drag(self, mouse_position: tuple[int, int]) -> None:
        self.dragging = True
        self.drag_offset.update(
            mouse_position[0] - self.rect.x,
            mouse_position[1] - self.rect.y,
        )

    def drag(self, mouse_position: tuple[int, int], bounds: pygame.Rect | None = None) -> None:
        if not self.dragging:
            return

        target_x = int(mouse_position[0] - self.drag_offset.x)
        target_y = int(mouse_position[1] - self.drag_offset.y)
        self.rect.topleft = (target_x, target_y)

        if bounds is not None:
            self._clamp_to_bounds(bounds)

        self.position = self.rect.topleft

    def stop_drag(self) -> None:
        self.dragging = False

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.rect)

    def _clamp_to_bounds(self, bounds: pygame.Rect) -> None:
        if self.rect.width <= bounds.width:
            self.rect.left = max(bounds.left, min(self.rect.left, bounds.right - self.rect.width))
        else:
            self.rect.centerx = bounds.centerx

        if self.rect.height <= bounds.height:
            self.rect.top = max(bounds.top, min(self.rect.top, bounds.bottom - self.rect.height))
        else:
            self.rect.centery = bounds.centery
