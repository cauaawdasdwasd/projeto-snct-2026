from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame

from src.core.preferences import DISPLAY_MODES, RESOLUTIONS_BY_ASPECT, UserPreferences

if TYPE_CHECKING:
    from src.core.audio import AudioManager


INK = (216, 221, 171)
INK_BRIGHT = (246, 239, 164)
INK_MUTED = (105, 119, 83)
AMBER = (211, 166, 66)
GREEN = (103, 166, 81)
RED = (190, 72, 54)
PANEL = (8, 14, 11)
PANEL_SELECTED = (26, 34, 25)
LINE = (63, 76, 52)

ROW_LABELS = (
    "PROPORÇÃO DA JANELA",
    "RESOLUÇÃO",
    "MODO DE EXIBIÇÃO",
    "VOLUME DA MÚSICA",
    "VOLUME DOS EFEITOS",
)


class SettingsPanel:
    """Reusable settings surface shared by the title and pause menus."""

    def __init__(
        self,
        bounds: pygame.Rect,
        audio: AudioManager | None,
        apply_preferences: Callable[[UserPreferences], bool] | None,
        *,
        draw_frame: bool,
    ) -> None:
        self.bounds = bounds.copy()
        self.audio = audio
        self.apply_preferences_callback = apply_preferences
        self.draw_frame = draw_frame
        self.applied_preferences = UserPreferences()
        self.pending_preferences = UserPreferences()
        self.selection = 0
        self.status_message = ""
        self.status_time = 0.0

        self.font_tiny = self._font(16)
        self.font_small = self._font(20)
        self.font_body = self._font(24, bold=True)
        self.font_title = self._font(38, bold=True)

        rows_top = self.bounds.y + 112
        self.row_rects = tuple(
            pygame.Rect(self.bounds.x + 36, rows_top + index * 78, self.bounds.width - 72, 64)
            for index in range(len(ROW_LABELS))
        )
        self.arrow_rects = tuple(
            (
                pygame.Rect(rect.right - 300, rect.y + 8, 46, 48),
                pygame.Rect(rect.right - 46, rect.y + 8, 46, 48),
            )
            for rect in self.row_rects
        )
        self.apply_rect = pygame.Rect(
            self.bounds.right - 490,
            self.bounds.bottom - 82,
            210,
            58,
        )
        self.back_rect = pygame.Rect(
            self.bounds.right - 250,
            self.bounds.bottom - 82,
            210,
            58,
        )

    def open(self, preferences: UserPreferences) -> None:
        self.applied_preferences = preferences.copy()
        self.pending_preferences = preferences.copy()
        self.selection = 0
        self.status_message = ""
        self.status_time = 0.0

    def update(self, dt: float) -> None:
        if self.status_time <= 0:
            return
        self.status_time = max(0.0, self.status_time - dt)
        if self.status_time == 0:
            self.status_message = ""

    def handle_event(
        self,
        event: pygame.event.Event,
        pointer: tuple[int, int] | None,
    ) -> str | None:
        if event.type == pygame.MOUSEMOTION:
            self._update_hover(pointer)
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(pointer)
        if event.type != pygame.KEYDOWN:
            return None

        item_count = len(ROW_LABELS) + 2
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selection = (self.selection - 1) % item_count
            self._play_click(0.5)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selection = (self.selection + 1) % item_count
            self._play_click(0.5)
        elif event.key in (pygame.K_LEFT, pygame.K_a) and self.selection < len(ROW_LABELS):
            self._change_setting(self.selection, -1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.selection < len(ROW_LABELS):
            self._change_setting(self.selection, 1)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.selection == len(ROW_LABELS):
                self._apply()
                return "applied"
            if self.selection == len(ROW_LABELS) + 1:
                self._play_click()
                return "back"
        return None

    def render(self, surface: pygame.Surface) -> None:
        if self.draw_frame:
            shadow = pygame.Surface((self.bounds.width + 28, self.bounds.height + 28), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 135))
            surface.blit(shadow, (self.bounds.x - 14, self.bounds.y - 8))
            pygame.draw.rect(surface, (10, 16, 13), self.bounds)
            pygame.draw.rect(surface, (79, 86, 58), self.bounds, 3)
            pygame.draw.rect(surface, (24, 31, 23), self.bounds.inflate(-18, -18), 2)

        self._text(surface, "CONFIGURAÇÕES", self.font_title, INK_BRIGHT, (self.bounds.x + 38, self.bounds.y + 30))
        self._text(surface, "PARÂMETROS DO TERMINAL", self.font_tiny, AMBER, (self.bounds.x + 40, self.bounds.y + 78))

        values = (
            self.pending_preferences.aspect_ratio,
            f"{self.pending_preferences.resolution[0]} x {self.pending_preferences.resolution[1]}",
            "TELA CHEIA" if self.pending_preferences.display_mode == "fullscreen" else "JANELA",
            self._volume_label(self.pending_preferences.music_volume),
            self._volume_label(self.pending_preferences.sfx_volume),
        )
        for index, (label, value, rect) in enumerate(zip(ROW_LABELS, values, self.row_rects)):
            selected = self.selection == index
            if selected:
                pygame.draw.rect(surface, PANEL_SELECTED, rect)
                pygame.draw.rect(surface, AMBER, (rect.x, rect.y, 5, rect.height))
            pygame.draw.line(surface, LINE, rect.bottomleft, rect.bottomright, 2)
            self._text(
                surface,
                label,
                self.font_small,
                INK if selected else INK_MUTED,
                (rect.x + 22, rect.y + 21),
            )
            left_rect, right_rect = self.arrow_rects[index]
            self._draw_arrow(surface, left_rect, -1, selected)
            self._draw_arrow(surface, right_rect, 1, selected)
            value_font = self.font_small if index >= 3 else self.font_body
            self._text(
                surface,
                value,
                value_font,
                INK_BRIGHT,
                (rect.right - 150, rect.y + 19),
                "midtop",
            )

        self._draw_button(surface, self.apply_rect, "APLICAR", self.selection == len(ROW_LABELS))
        self._draw_button(surface, self.back_rect, "VOLTAR", self.selection == len(ROW_LABELS) + 1)
        if self.status_message:
            color = GREEN if self.status_message == "CONFIGURAÇÕES APLICADAS" else RED
            self._text(
                surface,
                self.status_message,
                self.font_small,
                color,
                (self.bounds.x + 40, self.bounds.bottom - 60),
            )

    def _update_hover(self, pointer: tuple[int, int] | None) -> None:
        if pointer is None:
            return
        for index, rect in enumerate(self.row_rects):
            if rect.collidepoint(pointer):
                self.selection = index
                return
        if self.apply_rect.collidepoint(pointer):
            self.selection = len(ROW_LABELS)
        elif self.back_rect.collidepoint(pointer):
            self.selection = len(ROW_LABELS) + 1

    def _handle_click(self, pointer: tuple[int, int] | None) -> str | None:
        if pointer is None:
            return None
        for index, (left_rect, right_rect) in enumerate(self.arrow_rects):
            if left_rect.collidepoint(pointer):
                self.selection = index
                self._change_setting(index, -1)
                return None
            if right_rect.collidepoint(pointer):
                self.selection = index
                self._change_setting(index, 1)
                return None
        if self.apply_rect.collidepoint(pointer):
            self.selection = len(ROW_LABELS)
            self._apply()
            return "applied"
        if self.back_rect.collidepoint(pointer):
            self.selection = len(ROW_LABELS) + 1
            self._play_click()
            return "back"
        return None

    def _change_setting(self, index: int, direction: int) -> None:
        if index == 0:
            aspects = tuple(RESOLUTIONS_BY_ASPECT)
            current = aspects.index(self.pending_preferences.aspect_ratio)
            self.pending_preferences.aspect_ratio = aspects[(current + direction) % len(aspects)]
            self.pending_preferences.resolution = RESOLUTIONS_BY_ASPECT[
                self.pending_preferences.aspect_ratio
            ][0]
        elif index == 1:
            resolutions = RESOLUTIONS_BY_ASPECT[self.pending_preferences.aspect_ratio]
            current = resolutions.index(self.pending_preferences.resolution)
            self.pending_preferences.resolution = resolutions[(current + direction) % len(resolutions)]
        elif index == 2:
            current = DISPLAY_MODES.index(self.pending_preferences.display_mode)
            self.pending_preferences.display_mode = DISPLAY_MODES[
                (current + direction) % len(DISPLAY_MODES)
            ]
        elif index == 3:
            self.pending_preferences.music_volume = self._step_volume(
                self.pending_preferences.music_volume,
                direction,
            )
        elif index == 4:
            self.pending_preferences.sfx_volume = self._step_volume(
                self.pending_preferences.sfx_volume,
                direction,
            )
        self._play_click(0.55)

    def _apply(self) -> None:
        self._play_click()
        applied = True
        if self.apply_preferences_callback is not None:
            applied = self.apply_preferences_callback(self.pending_preferences)
        if applied:
            self.applied_preferences = self.pending_preferences.copy()
            self.status_message = "CONFIGURAÇÕES APLICADAS"
        else:
            self.status_message = "NÃO FOI POSSÍVEL APLICAR"
        self.status_time = 2.5

    @staticmethod
    def _step_volume(value: float, direction: int) -> float:
        return max(0.0, min(1.0, round(value * 10 + direction) / 10))

    @staticmethod
    def _volume_label(value: float) -> str:
        if value <= 0:
            return "MUDO"
        bars = round(value * 10)
        return f"{'|' * bars}{'.' * (10 - bars)} {round(value * 100):02d}%"

    def _draw_arrow(self, surface: pygame.Surface, rect: pygame.Rect, direction: int, active: bool) -> None:
        pygame.draw.rect(surface, PANEL, rect)
        pygame.draw.rect(surface, AMBER if active else LINE, rect, 2)
        cx, cy = rect.center
        points = (
            ((cx + 7, cy - 10), (cx - 7, cy), (cx + 7, cy + 10))
            if direction < 0
            else ((cx - 7, cy - 10), (cx + 7, cy), (cx - 7, cy + 10))
        )
        pygame.draw.polygon(surface, INK_BRIGHT if active else INK_MUTED, points)

    def _draw_button(self, surface: pygame.Surface, rect: pygame.Rect, label: str, active: bool) -> None:
        pygame.draw.rect(surface, PANEL_SELECTED if active else PANEL, rect)
        pygame.draw.rect(surface, AMBER if active else LINE, rect, 3 if active else 2)
        self._text(surface, label, self.font_body, INK_BRIGHT if active else INK, rect.center, "center")

    def _play_click(self, volume: float = 0.8) -> None:
        if self.audio is not None:
            self.audio.play("click", volume)

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
