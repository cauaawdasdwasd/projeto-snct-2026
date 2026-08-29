from __future__ import annotations

import math

import pygame


PAPER = (220, 208, 169)
PAPER_LIGHT = (238, 228, 193)
PAPER_DARK = (158, 143, 102)
INK = (24, 47, 68)
INK_MUTED = (86, 79, 59)
HEADER = (51, 63, 43)
AMBER = (181, 139, 63)
BLUE = (69, 105, 119)
SHADOW = (0, 0, 0, 130)

MODAL_RECT = pygame.Rect(205, 55, 1144, 586)
DRAW_RECT = pygame.Rect(274, 184, 1006, 270)
CLEAR_RECT = pygame.Rect(274, 518, 196, 56)
CANCEL_RECT = pygame.Rect(778, 518, 208, 56)
CONFIRM_RECT = pygame.Rect(1002, 518, 278, 56)


class SignaturePad:
    """Enlarged paper field that records a freehand mouse signature."""

    def __init__(self) -> None:
        self.is_open = False
        self.ink_surface = pygame.Surface(DRAW_RECT.size, pygame.SRCALPHA)
        self.drawing = False
        self.last_point: pygame.Vector2 | None = None
        self.stroke_width = 5.0
        self.pointer_position: tuple[int, int] | None = None
        self.hovered_control: str | None = None
        self.font_tiny = self._font(15)
        self.font_small = self._font(18)
        self.font_body_bold = self._font(21, bold=True)
        self.font_title = self._font(31, bold=True)

    @property
    def has_ink(self) -> bool:
        return self.ink_surface.get_bounding_rect(min_alpha=10).width > 0

    def open(self, existing_signature: pygame.Surface | None = None) -> None:
        self.ink_surface.fill((0, 0, 0, 0))
        if existing_signature is not None:
            if existing_signature.get_size() == self.ink_surface.get_size():
                self.ink_surface.blit(existing_signature, (0, 0))
            else:
                scaled = pygame.transform.smoothscale(
                    existing_signature,
                    self.ink_surface.get_size(),
                )
                self.ink_surface.blit(scaled, (0, 0))
        self.is_open = True
        self.drawing = False
        self.last_point = None
        self.stroke_width = 5.0
        self.pointer_position = None
        self.hovered_control = None

    def close(self) -> None:
        self.is_open = False
        self.drawing = False
        self.last_point = None
        self.pointer_position = None
        self.hovered_control = None

    def handle_event(
        self,
        event: pygame.event.Event,
        position: tuple[int, int] | None,
    ) -> tuple[str, pygame.Surface | None] | None:
        if not self.is_open:
            return None

        self.pointer_position = position
        self._update_hover(position)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if position is None:
                return ("consume", None)
            if CLEAR_RECT.collidepoint(position):
                self.ink_surface.fill((0, 0, 0, 0))
                return ("clear", None)
            if CANCEL_RECT.collidepoint(position):
                self.close()
                return ("cancel", None)
            if CONFIRM_RECT.collidepoint(position):
                if not self.has_ink:
                    return ("consume", None)
                signature = self.ink_surface.copy()
                self.close()
                return ("confirm", signature)
            if DRAW_RECT.collidepoint(position):
                self.drawing = True
                point = self._to_canvas(position)
                self.last_point = pygame.Vector2(point)
                self._draw_ink_dot(point, self.stroke_width)
                return ("draw", None)
            return ("consume", None)

        if event.type == pygame.MOUSEMOTION and self.drawing:
            if position is not None:
                self._continue_stroke(self._to_canvas_clamped(position))
            return ("draw", None)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False
            self.last_point = None
            return ("draw_end", None)

        return None

    def render(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return

        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 218))
        surface.blit(dim, (0, 0))

        pygame.draw.rect(surface, SHADOW, MODAL_RECT.move(8, 8))
        pygame.draw.rect(surface, PAPER, MODAL_RECT)
        pygame.draw.rect(surface, PAPER_DARK, MODAL_RECT, 4)
        pygame.draw.rect(surface, HEADER, (MODAL_RECT.x, MODAL_RECT.y, MODAL_RECT.width, 91))
        self._draw_text(
            surface,
            "ASSINATURA DO AUDITOR",
            self.font_title,
            PAPER_LIGHT,
            (MODAL_RECT.x + 42, MODAL_RECT.y + 24),
        )
        self._draw_text(
            surface,
            "Segure o botão esquerdo e assine no campo abaixo.",
            self.font_small,
            PAPER_DARK,
            (MODAL_RECT.x + 44, MODAL_RECT.y + 61),
        )

        pygame.draw.rect(surface, PAPER_LIGHT, DRAW_RECT)
        pygame.draw.rect(surface, BLUE, DRAW_RECT, 3)
        for y in range(DRAW_RECT.y + 54, DRAW_RECT.bottom - 20, 44):
            pygame.draw.line(
                surface,
                (205, 194, 158),
                (DRAW_RECT.x + 20, y),
                (DRAW_RECT.right - 20, y),
                1,
            )
        self._draw_text(
            surface,
            "ASSINE AQUI",
            self.font_tiny,
            INK_MUTED,
            (DRAW_RECT.x + 20, DRAW_RECT.y + 15),
        )
        pygame.draw.line(
            surface,
            INK_MUTED,
            (DRAW_RECT.x + 34, DRAW_RECT.bottom - 43),
            (DRAW_RECT.right - 34, DRAW_RECT.bottom - 43),
            2,
        )
        surface.blit(self.ink_surface, DRAW_RECT.topleft)

        self._draw_button(surface, CLEAR_RECT, "LIMPAR", "clear")
        self._draw_button(surface, CANCEL_RECT, "CANCELAR", "cancel")
        self._draw_button(
            surface,
            CONFIRM_RECT,
            "CONFIRMAR ASSINATURA",
            "confirm",
            enabled=self.has_ink,
        )
        self._draw_text(
            surface,
            "A assinatura será impressa na folha de auditoria.",
            self.font_tiny,
            INK_MUTED,
            (DRAW_RECT.x, MODAL_RECT.bottom - 39),
        )

        if self.pointer_position is not None and DRAW_RECT.collidepoint(self.pointer_position):
            self._draw_pen_cursor(surface, self.pointer_position)

    def _continue_stroke(self, point: tuple[int, int]) -> None:
        current = pygame.Vector2(point)
        if self.last_point is None:
            self.last_point = current
            self._draw_ink_dot(point, self.stroke_width)
            return

        distance = self.last_point.distance_to(current)
        target_width = max(2.8, min(7.2, 7.0 - distance * 0.13))
        new_width = self.stroke_width * 0.68 + target_width * 0.32
        steps = max(1, math.ceil(distance / 2.0))
        previous = self.last_point
        previous_width = self.stroke_width
        for index in range(1, steps + 1):
            amount = index / steps
            sample = self.last_point.lerp(current, amount)
            width = self.stroke_width + (new_width - self.stroke_width) * amount
            self._draw_ink_segment(previous, sample, previous_width, width)
            previous = sample
            previous_width = width
        self.last_point = current
        self.stroke_width = new_width

    def _draw_ink_segment(
        self,
        start: pygame.Vector2,
        end: pygame.Vector2,
        start_width: float,
        end_width: float,
    ) -> None:
        width = max(2, round((start_width + end_width) * 0.5))
        start_point = (round(start.x), round(start.y))
        end_point = (round(end.x), round(end.y))
        pygame.draw.line(
            self.ink_surface,
            (*INK, 246),
            start_point,
            end_point,
            width,
        )
        self._draw_ink_dot(end_point, end_width)

    def _draw_ink_dot(self, point: tuple[int, int], width: float) -> None:
        radius = max(1, round(width * 0.5))
        pygame.draw.circle(self.ink_surface, (*INK, 246), point, radius)

    def _update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered_control = None
        if position is None:
            return
        for control, rect in (
            ("clear", CLEAR_RECT),
            ("cancel", CANCEL_RECT),
            ("confirm", CONFIRM_RECT),
        ):
            if rect.collidepoint(position):
                self.hovered_control = control
                return

    def _draw_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        control: str,
        *,
        enabled: bool = True,
    ) -> None:
        hovered = enabled and self.hovered_control == control
        fill = (205, 194, 158) if hovered else (230, 219, 183)
        border = AMBER if hovered else PAPER_DARK
        text_color = INK if enabled else (150, 140, 111)
        pygame.draw.rect(surface, (111, 99, 71), rect.move(3, 3))
        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, border, rect, 3)
        self._draw_text(surface, label, self.font_body_bold, text_color, rect.center, anchor="center")

    @staticmethod
    def _draw_pen_cursor(surface: pygame.Surface, position: tuple[int, int]) -> None:
        x, y = position
        pygame.draw.line(surface, (238, 222, 153), (x + 5, y - 11), (x - 5, y + 8), 5)
        pygame.draw.line(surface, INK, (x + 3, y - 10), (x - 7, y + 9), 3)
        pygame.draw.circle(surface, INK, (x - 7, y + 9), 2)

    @staticmethod
    def _to_canvas(position: tuple[int, int]) -> tuple[int, int]:
        return position[0] - DRAW_RECT.x, position[1] - DRAW_RECT.y

    @staticmethod
    def _to_canvas_clamped(position: tuple[int, int]) -> tuple[int, int]:
        return (
            max(0, min(DRAW_RECT.width - 1, position[0] - DRAW_RECT.x)),
            max(0, min(DRAW_RECT.height - 1, position[1] - DRAW_RECT.y)),
        )

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)

    @staticmethod
    def _draw_text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
        *,
        anchor: str = "topleft",
    ) -> None:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
