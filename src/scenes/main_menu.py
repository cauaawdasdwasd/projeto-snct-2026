from __future__ import annotations

import math
import random
from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame

from src.core.preferences import DISPLAY_MODES, RESOLUTIONS_BY_ASPECT, UserPreferences
from src.core.scene import Scene
from src.core.settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


INK = (222, 225, 180)
INK_BRIGHT = (246, 239, 164)
INK_MUTED = (118, 127, 91)
AMBER = (211, 166, 66)
RED = (167, 61, 47)
GREEN = (104, 158, 75)
PANEL = (15, 20, 17)
PANEL_LIGHT = (24, 30, 24)
LINE = (64, 72, 50)

MAIN_COMMANDS = ("INICIAR TURNO", "CONFIGURAÇÕES", "CRÉDITOS", "ENCERRAR")
SETTING_ROWS = (
    "PROPORÇÃO DA JANELA",
    "RESOLUÇÃO",
    "MODO DE EXIBIÇÃO",
    "VOLUME DA MÚSICA",
    "VOLUME DOS EFEITOS",
)
TEAM = (
    "CAUÃ DANIEL ABREU",
    "LETÍCIA FAUSTINO SORCHETI",
    "MARIAH LUIZA SOARES DE OLIVEIRA",
    "PEDRO GONÇALVES DA SILVA",
)


class MainMenuScene(Scene):
    """Industrial terminal menu with functional display and audio settings."""

    def __init__(
        self,
        manager: SceneManager,
        assets: AssetManager,
        input_manager: InputManager,
        audio: AudioManager | None = None,
        preferences: UserPreferences | None = None,
        apply_preferences: Callable[[UserPreferences], bool] | None = None,
        quit_game: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(manager, assets, input_manager)
        self.audio = audio
        self.preferences = (preferences or UserPreferences()).copy()
        self.pending_preferences = self.preferences.copy()
        self.apply_preferences_callback = apply_preferences
        self.quit_game = quit_game

        self.view = "main"
        self.main_selection = 0
        self.settings_selection = 0
        self.elapsed = 0.0
        self.status_message = ""
        self.status_time = 0.0

        self.font_tiny = self._font(17)
        self.font_small = self._font(22)
        self.font_body = self._font(28)
        self.font_body_bold = self._font(29, bold=True)
        self.font_title = self._font(104, bold=True)
        self.font_section = self._font(43, bold=True)

        self.main_rects = tuple(
            pygame.Rect(1190, 340 + index * 106, 560, 82)
            for index in range(len(MAIN_COMMANDS))
        )
        self.settings_row_rects = tuple(
            pygame.Rect(655, 280 + index * 103, 990, 78)
            for index in range(len(SETTING_ROWS))
        )
        self.settings_arrow_rects = tuple(
            (
                pygame.Rect(rect.right - 330, rect.y + 12, 50, 54),
                pygame.Rect(rect.right - 50, rect.y + 12, 50, 54),
            )
            for rect in self.settings_row_rects
        )
        self.apply_rect = pygame.Rect(1115, 846, 248, 70)
        self.back_rect = pygame.Rect(1390, 846, 255, 70)
        self.credits_back_rect = pygame.Rect(1390, 864, 255, 70)

        self.noise_overlay = self._build_noise_overlay()
        self.scanline_overlay = self._build_scanline_overlay()

    def on_enter(self) -> None:
        self.elapsed = 0.0
        self.view = "main"
        self.main_selection = 0

    def handle_escape(self) -> bool:
        if self.view == "main":
            return False
        self._play_click()
        self.view = "main"
        self.status_message = ""
        return True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(self.input_manager.mouse_position)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(self.input_manager.mouse_position)
            return

        if event.type != pygame.KEYDOWN:
            return

        if self.view == "main":
            self._handle_main_key(event.key)
        elif self.view == "settings":
            self._handle_settings_key(event.key)
        elif self.view == "credits" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._play_click()
            self.view = "main"

    def update(self, dt: float) -> None:
        self.elapsed += dt
        if self.status_time > 0:
            self.status_time = max(0.0, self.status_time - dt)
            if self.status_time == 0:
                self.status_message = ""

    def render(self, surface: pygame.Surface) -> None:
        self._render_machine_background(surface)
        if self.view == "main":
            self._render_main(surface)
        elif self.view == "settings":
            self._render_settings(surface)
        else:
            self._render_credits(surface)
        self._render_screen_finish(surface)

    def _handle_main_key(self, key: int) -> None:
        if key in (pygame.K_UP, pygame.K_w):
            self.main_selection = (self.main_selection - 1) % len(MAIN_COMMANDS)
            self._play_click(0.5)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.main_selection = (self.main_selection + 1) % len(MAIN_COMMANDS)
            self._play_click(0.5)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate_main_command(self.main_selection)

    def _handle_settings_key(self, key: int) -> None:
        item_count = len(SETTING_ROWS) + 2
        if key in (pygame.K_UP, pygame.K_w):
            self.settings_selection = (self.settings_selection - 1) % item_count
            self._play_click(0.5)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.settings_selection = (self.settings_selection + 1) % item_count
            self._play_click(0.5)
        elif key in (pygame.K_LEFT, pygame.K_a) and self.settings_selection < len(SETTING_ROWS):
            self._change_setting(self.settings_selection, -1)
        elif key in (pygame.K_RIGHT, pygame.K_d) and self.settings_selection < len(SETTING_ROWS):
            self._change_setting(self.settings_selection, 1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.settings_selection == len(SETTING_ROWS):
                self._apply_settings()
            elif self.settings_selection == len(SETTING_ROWS) + 1:
                self._play_click()
                self.view = "main"

    def _handle_mouse_motion(self, position: tuple[int, int] | None) -> None:
        if position is None:
            return
        if self.view == "main":
            for index, rect in enumerate(self.main_rects):
                if rect.collidepoint(position):
                    self.main_selection = index
                    return
        elif self.view == "settings":
            for index, rect in enumerate(self.settings_row_rects):
                if rect.collidepoint(position):
                    self.settings_selection = index
                    return
            if self.apply_rect.collidepoint(position):
                self.settings_selection = len(SETTING_ROWS)
            elif self.back_rect.collidepoint(position):
                self.settings_selection = len(SETTING_ROWS) + 1

    def _handle_click(self, position: tuple[int, int] | None) -> None:
        if position is None:
            return
        if self.view == "main":
            for index, rect in enumerate(self.main_rects):
                if rect.collidepoint(position):
                    self._activate_main_command(index)
                    return
        elif self.view == "settings":
            for index, (left_rect, right_rect) in enumerate(self.settings_arrow_rects):
                if left_rect.collidepoint(position):
                    self.settings_selection = index
                    self._change_setting(index, -1)
                    return
                if right_rect.collidepoint(position):
                    self.settings_selection = index
                    self._change_setting(index, 1)
                    return
            if self.apply_rect.collidepoint(position):
                self.settings_selection = len(SETTING_ROWS)
                self._apply_settings()
            elif self.back_rect.collidepoint(position):
                self._play_click()
                self.view = "main"
        elif self.credits_back_rect.collidepoint(position):
            self._play_click()
            self.view = "main"

    def _activate_main_command(self, index: int) -> None:
        self._play_click()
        if index == 0:
            self.manager.switch_to("audit")
        elif index == 1:
            self.pending_preferences = self.preferences.copy()
            self.settings_selection = 0
            self.status_message = ""
            self.view = "settings"
        elif index == 2:
            self.view = "credits"
        elif self.quit_game is not None:
            self.quit_game()

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

    def _apply_settings(self) -> None:
        self._play_click()
        was_applied = True
        if self.apply_preferences_callback is not None:
            was_applied = self.apply_preferences_callback(self.pending_preferences)
        if was_applied:
            self.preferences = self.pending_preferences.copy()
            self.status_message = "CONFIGURAÇÕES APLICADAS"
        else:
            self.status_message = "NÃO FOI POSSÍVEL APLICAR"
        self.status_time = 2.5

    def _render_machine_background(self, surface: pygame.Surface) -> None:
        surface.fill((6, 9, 7))
        pygame.draw.rect(surface, (9, 13, 10), (54, 42, 1812, 996))
        pygame.draw.rect(surface, (45, 45, 34), (54, 42, 1812, 996), 5)
        pygame.draw.rect(surface, (19, 24, 18), (75, 63, 1770, 954), 3)

        pygame.draw.rect(surface, (20, 24, 19), (75, 63, 1770, 92))
        pygame.draw.line(surface, LINE, (75, 155), (1845, 155), 2)
        self._text(surface, "SISTEMA DE AUDITORIA ALGORÍTMICA", self.font_small, INK, (115, 98))
        self._text(surface, "TERMINAL 04", self.font_tiny, INK_MUTED, (1502, 101))
        led_color = GREEN if int(self.elapsed * 2.2) % 2 == 0 else (66, 104, 51)
        pygame.draw.circle(surface, (30, 42, 26), (1768, 108), 13)
        pygame.draw.circle(surface, led_color, (1768, 108), 7)

        pygame.draw.line(surface, (38, 45, 34), (1110, 195), (1110, 957), 2)
        pygame.draw.rect(surface, PANEL, (1138, 200, 650, 760))
        pygame.draw.rect(surface, LINE, (1138, 200, 650, 760), 2)

        if self.view == "main":
            for x in range(110, 1050, 78):
                pygame.draw.line(surface, (17, 24, 18), (x, 500), (x, 930), 1)
            for y in range(500, 931, 54):
                pygame.draw.line(surface, (17, 24, 18), (110, y), (1050, y), 1)

            signal_y = 722 + int(math.sin(self.elapsed * 1.3) * 22)
            points = [(115, 722), (270, 722), (322, signal_y), (390, 722), (548, 722)]
            points.extend(
                (x, 722 + int(math.sin(x * 0.025 + self.elapsed * 2.0) * 18))
                for x in range(570, 1030, 24)
            )
            pygame.draw.lines(surface, (71, 105, 61), False, points, 3)
        surface.blit(self.noise_overlay, (0, 0))

    def _render_main(self, surface: pygame.Surface) -> None:
        reveal = max(0.0, min(1.0, self.elapsed / 0.65))
        self._text(surface, "CENTRAL DE REVISÃO", self.font_small, AMBER, (120, 250))
        title_surface = self.font_title.render("SOB ANÁLISE", False, INK_BRIGHT)
        title_surface.set_alpha(round(255 * reveal))
        surface.blit(title_surface, (112, 292))
        pygame.draw.rect(surface, RED, (118, 425, round(760 * reveal), 8))

        self._text(surface, "TURNO DISPONÍVEL", self.font_tiny, INK_MUTED, (120, 470))
        self._text(surface, "06 DECISÕES PENDENTES", self.font_body_bold, INK, (120, 500))

        self._text(surface, "SELECIONE UMA OPERAÇÃO", self.font_tiny, INK_MUTED, (1190, 275))
        for index, (label, rect) in enumerate(zip(MAIN_COMMANDS, self.main_rects)):
            selected = index == self.main_selection
            if selected:
                pygame.draw.rect(surface, (31, 37, 27), rect)
                pygame.draw.rect(surface, AMBER, (rect.x, rect.y, 7, rect.height))
                pygame.draw.polygon(
                    surface,
                    INK_BRIGHT,
                    (
                        (rect.right - 34, rect.centery - 10),
                        (rect.right - 16, rect.centery),
                        (rect.right - 34, rect.centery + 10),
                    ),
                )
            pygame.draw.line(surface, LINE, rect.bottomleft, rect.bottomright, 2)
            number_color = AMBER if selected else INK_MUTED
            label_color = INK_BRIGHT if selected else INK
            self._text(surface, f"0{index + 1}", self.font_tiny, number_color, (rect.x + 28, rect.y + 29))
            self._text(surface, label, self.font_body_bold, label_color, (rect.x + 90, rect.y + 23))

        self._text(surface, "VERSÃO 0.1 // SNCT 2026", self.font_tiny, INK_MUTED, (118, 966))

    def _render_settings(self, surface: pygame.Surface) -> None:
        self._render_section_heading(surface, "CONFIGURAÇÕES", "PARÂMETROS DO TERMINAL")
        values = (
            self.pending_preferences.aspect_ratio,
            f"{self.pending_preferences.resolution[0]} x {self.pending_preferences.resolution[1]}",
            "TELA CHEIA" if self.pending_preferences.display_mode == "fullscreen" else "JANELA",
            self._volume_label(self.pending_preferences.music_volume),
            self._volume_label(self.pending_preferences.sfx_volume),
        )

        for index, (label, value, rect) in enumerate(
            zip(SETTING_ROWS, values, self.settings_row_rects)
        ):
            selected = index == self.settings_selection
            if selected:
                pygame.draw.rect(surface, PANEL_LIGHT, rect)
                pygame.draw.rect(surface, AMBER, (rect.x, rect.y, 6, rect.height))
            pygame.draw.line(surface, LINE, rect.bottomleft, rect.bottomright, 2)
            self._text(
                surface,
                label,
                self.font_small,
                INK if selected else INK_MUTED,
                (rect.x + 26, rect.y + 26),
            )
            left_rect, right_rect = self.settings_arrow_rects[index]
            self._draw_arrow_button(surface, left_rect, -1, selected)
            self._draw_arrow_button(surface, right_rect, 1, selected)
            value_font = self.font_small if index >= 3 else self.font_body_bold
            self._text(
                surface,
                value,
                value_font,
                INK_BRIGHT,
                (rect.right - 165, rect.y + 22),
                "midtop",
            )

        apply_selected = self.settings_selection == len(SETTING_ROWS)
        back_selected = self.settings_selection == len(SETTING_ROWS) + 1
        self._draw_command_button(surface, self.apply_rect, "APLICAR", apply_selected)
        self._draw_command_button(surface, self.back_rect, "VOLTAR", back_selected)
        if self.status_message:
            color = GREEN if self.status_message == "CONFIGURAÇÕES APLICADAS" else RED
            self._text(surface, self.status_message, self.font_small, color, (655, 873))

    def _render_credits(self, surface: pygame.Surface) -> None:
        self._render_section_heading(surface, "CRÉDITOS", "EQUIPE DE DESENVOLVIMENTO")
        y = 318
        for index, name in enumerate(TEAM, start=1):
            self._text(surface, f"0{index}", self.font_small, AMBER, (675, y + 5))
            self._text(surface, name, self.font_body_bold, INK_BRIGHT, (748, y))
            pygame.draw.line(surface, LINE, (655, y + 62), (1645, y + 62), 2)
            y += 112
        self._draw_command_button(surface, self.credits_back_rect, "VOLTAR", True)

    def _render_section_heading(self, surface: pygame.Surface, title: str, subtitle: str) -> None:
        self._text(surface, title, self.font_section, INK_BRIGHT, (655, 190))
        self._text(surface, subtitle, self.font_tiny, AMBER, (655, 244))

    def _render_screen_finish(self, surface: pygame.Surface) -> None:
        surface.blit(self.scanline_overlay, (0, 0))
        flicker = 4 + int((math.sin(self.elapsed * 7.0) + 1) * 2)
        glow = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        glow.fill((220, 235, 170, flicker))
        surface.blit(glow, (0, 0))

        for inset, alpha in ((0, 95), (14, 58), (28, 28)):
            border = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(
                border,
                (0, 0, 0, alpha),
                (inset, inset, VIRTUAL_WIDTH - inset * 2, VIRTUAL_HEIGHT - inset * 2),
                18,
            )
            surface.blit(border, (0, 0))

    def _draw_arrow_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        direction: int,
        active: bool,
    ) -> None:
        pygame.draw.rect(surface, (10, 15, 11), rect)
        pygame.draw.rect(surface, AMBER if active else LINE, rect, 2)
        center_x, center_y = rect.center
        if direction < 0:
            points = (
                (center_x + 7, center_y - 11),
                (center_x - 8, center_y),
                (center_x + 7, center_y + 11),
            )
        else:
            points = (
                (center_x - 7, center_y - 11),
                (center_x + 8, center_y),
                (center_x - 7, center_y + 11),
            )
        pygame.draw.polygon(surface, INK_BRIGHT if active else INK_MUTED, points)

    def _draw_command_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        selected: bool,
    ) -> None:
        pygame.draw.rect(surface, PANEL_LIGHT if selected else PANEL, rect)
        pygame.draw.rect(surface, AMBER if selected else LINE, rect, 3 if selected else 2)
        self._text(
            surface,
            label,
            self.font_body_bold,
            INK_BRIGHT if selected else INK,
            rect.center,
            "center",
        )

    @staticmethod
    def _build_noise_overlay() -> pygame.Surface:
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        rng = random.Random(2608)
        for _ in range(4200):
            shade = rng.choice((16, 22, 31, 38))
            overlay.set_at(
                (rng.randrange(VIRTUAL_WIDTH), rng.randrange(VIRTUAL_HEIGHT)),
                (175, 181, 130, shade),
            )
        return overlay

    @staticmethod
    def _build_scanline_overlay() -> pygame.Surface:
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        for y in range(0, VIRTUAL_HEIGHT, 4):
            pygame.draw.line(overlay, (0, 0, 0, 24), (0, y), (VIRTUAL_WIDTH, y))
        return overlay

    @staticmethod
    def _step_volume(value: float, direction: int) -> float:
        return max(0.0, min(1.0, round(value * 10 + direction) / 10))

    @staticmethod
    def _volume_label(value: float) -> str:
        if value <= 0:
            return "MUDO"
        bars = round(value * 10)
        return f"{'|' * bars}{'.' * (10 - bars)}  {round(value * 100):02d}%"

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
