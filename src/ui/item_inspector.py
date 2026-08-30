from __future__ import annotations

from pathlib import Path

import pygame

from src.rendering.glb_renderer import GlbRenderer


CLOSE_RECT = pygame.Rect(1812, 42, 58, 58)
MIN_ZOOM = 0.62
MAX_ZOOM = 1.75
ZOOM_STEP = 0.1
ROTATION_SPEED = 0.0042


class ItemInspector:
    """Full-screen physical inspection for a single GLB item."""

    def __init__(self, model_path: Path, title: str) -> None:
        self.model_path = model_path
        self.title = title
        self.renderer: GlbRenderer | None = None
        self.render_error: str | None = None
        self.is_open = False
        self.dragging = False
        self.last_drag_position: tuple[int, int] | None = None
        self.rotation_x = -0.08
        self.rotation_y = -0.10
        self.zoom = 1.0
        self.close_hovered = False
        self.title_font = pygame.font.SysFont(
            ("Consolas", "Courier New", "monospace"),
            25,
            bold=True,
        )
        self.error_font = pygame.font.SysFont(
            ("Consolas", "Courier New", "monospace"),
            19,
        )

    def open(self) -> bool:
        if self.renderer is None and self.render_error is None:
            try:
                self.renderer = GlbRenderer(self.model_path)
            except Exception as exc:
                self.render_error = str(exc)
        self.is_open = True
        self.dragging = False
        self.last_drag_position = None
        self.rotation_x = -0.08
        self.rotation_y = -0.10
        self.zoom = 1.0
        return self.renderer is not None

    def close(self) -> None:
        self.is_open = False
        self.dragging = False
        self.last_drag_position = None
        self.close_hovered = False

    def release(self) -> None:
        if self.renderer is not None:
            self.renderer.release()
            self.renderer = None

    def handle_event(
        self,
        event: pygame.event.Event,
        position: tuple[int, int] | None,
    ) -> str | None:
        if not self.is_open:
            return None
        if event.type == pygame.MOUSEWHEEL:
            self.zoom = max(
                MIN_ZOOM,
                min(MAX_ZOOM, self.zoom + event.y * ZOOM_STEP),
            )
            return "zoom"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if position is not None and CLOSE_RECT.collidepoint(position):
                self.close()
                return "close"
            self.dragging = position is not None
            self.last_drag_position = position
            return "grab"
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            self.last_drag_position = None
            return "release"
        if event.type == pygame.MOUSEMOTION:
            self.close_hovered = bool(
                position is not None and CLOSE_RECT.collidepoint(position)
            )
            if (
                self.dragging
                and position is not None
                and self.last_drag_position is not None
            ):
                delta_x = position[0] - self.last_drag_position[0]
                delta_y = position[1] - self.last_drag_position[1]
                self.rotation_y += delta_x * ROTATION_SPEED
                self.rotation_x += delta_y * ROTATION_SPEED
                self.last_drag_position = position
                return "rotate"
        return "consume"

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.close_hovered = bool(
            self.is_open
            and position is not None
            and CLOSE_RECT.collidepoint(position)
        )

    def render(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 222))
        surface.blit(dim, (0, 0))

        if self.renderer is not None:
            rendered = self.renderer.render(
                self.rotation_x,
                self.rotation_y,
                self.zoom,
            )
            if rendered.get_size() != surface.get_size():
                rendered = pygame.transform.smoothscale(rendered, surface.get_size())
            surface.blit(
                rendered,
                (0, 0),
                special_flags=pygame.BLEND_ALPHA_SDL2,
            )
        else:
            self._render_error(surface)

        title = self.title_font.render(self.title.upper(), False, (218, 220, 181))
        surface.blit(title, (54, 50))
        self._draw_close(surface)

    def _draw_close(self, surface: pygame.Surface) -> None:
        fill = (43, 49, 42) if self.close_hovered else (14, 18, 16)
        border = (238, 232, 166) if self.close_hovered else (102, 111, 74)
        pygame.draw.rect(surface, fill, CLOSE_RECT)
        pygame.draw.rect(surface, border, CLOSE_RECT, 2)
        center_x, center_y = CLOSE_RECT.center
        pygame.draw.line(
            surface,
            border,
            (center_x - 11, center_y - 11),
            (center_x + 11, center_y + 11),
            3,
        )
        pygame.draw.line(
            surface,
            border,
            (center_x + 11, center_y - 11),
            (center_x - 11, center_y + 11),
            3,
        )

    def _render_error(self, surface: pygame.Surface) -> None:
        heading = self.title_font.render(
            "OBJETO 3D INDISPONÍVEL",
            False,
            (222, 117, 96),
        )
        surface.blit(heading, heading.get_rect(center=(960, 495)))
        detail = self.error_font.render(
            self.render_error or "Falha ao carregar o modelo.",
            False,
            (181, 185, 148),
        )
        surface.blit(detail, detail.get_rect(center=(960, 540)))
