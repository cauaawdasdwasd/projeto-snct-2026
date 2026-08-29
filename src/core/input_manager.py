from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class Viewport:
    """Visible area where the virtual surface is drawn inside the window."""

    rect: pygame.Rect
    scale: float


class InputManager:
    """Converts physical window input into virtual game coordinates."""

    def __init__(self, virtual_size: tuple[int, int]) -> None:
        self._virtual_width, self._virtual_height = virtual_size
        self._viewport = Viewport(
            rect=pygame.Rect(0, 0, self._virtual_width, self._virtual_height),
            scale=1.0,
        )
        self._camera_rect = pygame.Rect(0, 0, self._virtual_width, self._virtual_height)
        self.mouse_position: tuple[int, int] | None = None

    @property
    def viewport(self) -> Viewport:
        return self._viewport

    @property
    def mouse_is_valid(self) -> bool:
        return self.mouse_position is not None

    def set_viewport(self, rect: pygame.Rect, scale: float) -> None:
        self._viewport = Viewport(rect=rect.copy(), scale=scale)
        self.update_mouse_position()

    def set_camera_rect(self, rect: pygame.Rect) -> None:
        virtual_bounds = pygame.Rect(0, 0, self._virtual_width, self._virtual_height)
        camera_rect = rect.copy()
        camera_rect.width = max(1, min(camera_rect.width, self._virtual_width))
        camera_rect.height = max(1, min(camera_rect.height, self._virtual_height))
        camera_rect.clamp_ip(virtual_bounds)
        self._camera_rect = camera_rect
        self.update_mouse_position()

    def handle_event(self, event: pygame.event.Event) -> None:
        if hasattr(event, "pos"):
            self.mouse_position = self.window_to_virtual(event.pos)

    def update_mouse_position(self) -> None:
        self.mouse_position = self.window_to_virtual(pygame.mouse.get_pos())

    def window_to_virtual(self, window_position: tuple[int, int]) -> tuple[int, int] | None:
        viewport_rect = self._viewport.rect

        if self._viewport.scale <= 0 or not viewport_rect.collidepoint(window_position):
            return None

        window_x, window_y = window_position
        display_x = (window_x - viewport_rect.x) / self._viewport.scale
        display_y = (window_y - viewport_rect.y) / self._viewport.scale
        virtual_x = int(
            self._camera_rect.x
            + display_x * self._camera_rect.width / self._virtual_width
        )
        virtual_y = int(
            self._camera_rect.y
            + display_y * self._camera_rect.height / self._virtual_height
        )

        if not (0 <= virtual_x < self._virtual_width and 0 <= virtual_y < self._virtual_height):
            return None

        return virtual_x, virtual_y
