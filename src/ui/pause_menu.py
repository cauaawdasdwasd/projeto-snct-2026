from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame

from src.core.preferences import UserPreferences
from src.ui.settings_panel import SettingsPanel

if TYPE_CHECKING:
    from src.core.audio import AudioManager


INK = (218, 222, 174)
INK_BRIGHT = (247, 239, 164)
INK_MUTED = (103, 116, 82)
AMBER = (211, 166, 66)
LINE = (72, 82, 55)

PAUSE_COMMANDS = ("CONTINUAR", "CONFIGURAÇÕES", "VOLTAR AO MENU")


class PauseMenu:
    """Modal pause and settings flow rendered over the audit scene."""

    def __init__(
        self,
        audio: AudioManager | None,
        preferences_provider: Callable[[], UserPreferences],
        apply_preferences: Callable[[UserPreferences], bool] | None,
    ) -> None:
        self.audio = audio
        self.preferences_provider = preferences_provider
        self.is_open = False
        self.view = "menu"
        self.selection = 0
        self.panel_rect = pygame.Rect(620, 215, 680, 650)
        self.command_rects = tuple(
            pygame.Rect(720, 430 + index * 94, 480, 68)
            for index in range(len(PAUSE_COMMANDS))
        )
        self.settings = SettingsPanel(
            pygame.Rect(445, 125, 1030, 830),
            audio,
            apply_preferences,
            draw_frame=True,
        )
        self.font_tiny = self._font(17)
        self.font_body = self._font(27, bold=True)
        self.font_title = self._font(48, bold=True)

    def open(self) -> None:
        self.is_open = True
        self.view = "menu"
        self.selection = 0
        self._play_click(0.65)

    def close(self) -> None:
        self.is_open = False
        self.view = "menu"

    def handle_escape(self) -> bool:
        if self.view == "settings":
            self.view = "menu"
            self._play_sound("back", 0.65)
        else:
            self.close()
            self._play_sound("back", 0.65)
        return True

    def handle_event(
        self,
        event: pygame.event.Event,
        pointer: tuple[int, int] | None,
    ) -> str | None:
        if self.view == "settings":
            action = self.settings.handle_event(event, pointer)
            if action == "back":
                self.view = "menu"
            return None

        if event.type == pygame.MOUSEMOTION and pointer is not None:
            for index, rect in enumerate(self.command_rects):
                if rect.collidepoint(pointer):
                    self.selection = index
                    break
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pointer is not None:
            for index, rect in enumerate(self.command_rects):
                if rect.collidepoint(pointer):
                    return self._activate(index)
            return None
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selection = (self.selection - 1) % len(PAUSE_COMMANDS)
            self._play_click(0.5)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selection = (self.selection + 1) % len(PAUSE_COMMANDS)
            self._play_click(0.5)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return self._activate(self.selection)
        return None

    def update(self, dt: float) -> None:
        if self.view == "settings":
            self.settings.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        dimmer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dimmer.fill((0, 3, 2, 178))
        surface.blit(dimmer, (0, 0))
        if self.view == "settings":
            self.settings.render(surface)
            return

        shadow = pygame.Surface((self.panel_rect.width + 32, self.panel_rect.height + 32), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 145))
        surface.blit(shadow, (self.panel_rect.x - 16, self.panel_rect.y - 8))
        pygame.draw.rect(surface, (9, 15, 12), self.panel_rect)
        pygame.draw.rect(surface, (79, 87, 58), self.panel_rect, 3)
        pygame.draw.rect(surface, (25, 31, 23), self.panel_rect.inflate(-18, -18), 2)

        self._text(surface, "TURNO PAUSADO", self.font_title, INK_BRIGHT, (960, 285), "midtop")
        self._text(surface, "ESTAÇÃO EM ESPERA", self.font_tiny, AMBER, (960, 346), "midtop")
        pygame.draw.line(surface, LINE, (690, 390), (1230, 390), 2)

        for index, (label, rect) in enumerate(zip(PAUSE_COMMANDS, self.command_rects)):
            active = index == self.selection
            if active:
                pygame.draw.rect(surface, (28, 35, 26), rect)
                pygame.draw.rect(surface, AMBER, (rect.x, rect.y, 6, rect.height))
                pygame.draw.polygon(
                    surface,
                    INK_BRIGHT,
                    ((rect.right - 28, rect.centery - 9), (rect.right - 13, rect.centery), (rect.right - 28, rect.centery + 9)),
                )
            pygame.draw.line(surface, LINE, rect.bottomleft, rect.bottomright, 2)
            self._text(
                surface,
                label,
                self.font_body,
                INK_BRIGHT if active else INK,
                (rect.x + 34, rect.y + 19),
            )

    def _activate(self, index: int) -> str | None:
        self._play_sound("back" if index in (0, 2) else "forward")
        if index == 0:
            self.close()
        elif index == 1:
            self.settings.open(self.preferences_provider())
            self.view = "settings"
        else:
            self.close()
            return "main_menu"
        return None

    def _play_click(self, volume: float = 0.8) -> None:
        self._play_sound("click", volume)

    def _play_sound(self, name: str, volume: float = 0.8) -> None:
        if self.audio is not None:
            self.audio.play(name, volume)

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
