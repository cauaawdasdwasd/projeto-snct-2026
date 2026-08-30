from __future__ import annotations

import pygame


class OSCursor:
    """Renders the workstation cursor in virtual-screen coordinates."""

    def __init__(self, image: pygame.Surface, screen_rect: pygame.Rect) -> None:
        self.image = image
        self.screen_rect = screen_rect.copy()

    def is_active(
        self,
        position: tuple[int, int] | None,
        *,
        blocked: bool = False,
    ) -> bool:
        return bool(
            not blocked
            and position is not None
            and self.screen_rect.collidepoint(position)
        )

    def render(
        self,
        surface: pygame.Surface,
        position: tuple[int, int] | None,
        *,
        blocked: bool = False,
    ) -> None:
        if self.is_active(position, blocked=blocked) and position is not None:
            surface.blit(self.image, position)
