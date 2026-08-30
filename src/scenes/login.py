from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from src.core.scene import Scene
from src.ui.credential_note import CredentialNote
from src.ui.item_inspector import ItemInspector

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


LOGIN_SCREEN_RECT = pygame.Rect(186, 87, 1554, 696)
USERNAME_RECT = pygame.Rect(716, 438, 488, 58)
PASSWORD_RECT = pygame.Rect(716, 532, 488, 58)
SUBMIT_RECT = pygame.Rect(PASSWORD_RECT.right - 58, PASSWORD_RECT.y, 58, 58)

USERNAME = "sob_analise"
PASSWORD = "05112002LAB"
MAX_FIELD_LENGTH = 24
SUCCESS_DELAY = 0.85

SCREEN_TOP = (18, 34, 38)
SCREEN_BOTTOM = (8, 18, 20)
PANEL = (8, 15, 17)
PANEL_ACTIVE = (15, 24, 24)
INK = (211, 218, 190)
INK_BRIGHT = (245, 239, 172)
INK_MUTED = (121, 139, 119)
AMBER = (218, 165, 62)
GREEN = (107, 177, 89)
RED = (210, 91, 75)
BORDER = (75, 94, 75)


class LoginScene(Scene):
    """Workstation sign-in placed between the title screen and audit app."""

    def __init__(
        self,
        manager: SceneManager,
        assets: AssetManager,
        input_manager: InputManager,
        audio: AudioManager | None = None,
    ) -> None:
        super().__init__(manager, assets, input_manager)
        self.audio = audio
        self.background = self.assets.load_image(
            "backgrounds/novo_sprite_teste.png"
        )
        self.credential_note = CredentialNote(
            self.assets.load_image("ui/heart_note.png")
        )
        self.item_inspector = ItemInspector(
            self.assets.assets_root / "models" / "heart_note.glb",
            "Post-it de acesso",
        )
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.state = "entry"
        self.message = ""
        self.elapsed = 0.0
        self.success_time = 0.0
        self.cursor_time = 0.0
        self.submit_hovered = False

        self.font_tiny = self._font(16)
        self.font_small = self._font(20)
        self.font_body = self._font(25)
        self.font_body_bold = self._font(27, bold=True)
        self.font_title = self._font(42, bold=True)
        self.scanlines = self._build_scanlines()

    def on_enter(self) -> None:
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.state = "entry"
        self.message = ""
        self.elapsed = 0.0
        self.success_time = 0.0
        self.cursor_time = 0.0
        self.submit_hovered = False
        self.credential_note.clear_hover()
        self.item_inspector.close()
        if self.audio is not None:
            self.audio.play_music_sequence(("menu",), fade_ms=450)

    def on_exit(self) -> None:
        self.credential_note.clear_hover()
        self.item_inspector.close()

    def handle_escape(self) -> bool:
        if self.item_inspector.is_open:
            self.item_inspector.close()
            self._play_sound("back", 0.65)
            return True
        self.manager.switch_to("main_menu")
        self._play_sound("back", 0.65)
        return True

    def handle_event(self, event: pygame.event.Event) -> None:
        pointer = self.input_manager.mouse_position
        if self.item_inspector.is_open:
            action = self.item_inspector.handle_event(event, pointer)
            if action == "close":
                self._play_sound("back", 0.65)
            elif action == "zoom":
                self._play_sound("scroll", 0.45)
            return
        if self.state != "entry":
            return

        if event.type == pygame.MOUSEMOTION:
            self.submit_hovered = bool(
                pointer is not None and SUBMIT_RECT.collidepoint(pointer)
            )
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(pointer)
            return
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_TAB:
            self.active_field = (
                "password" if self.active_field == "username" else "username"
            )
            self.cursor_time = 0.0
            self._play_sound("click", 0.45)
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.active_field == "username":
                self.active_field = "password"
                self.cursor_time = 0.0
                self._play_sound("click", 0.45)
            else:
                self._attempt_login()
            return
        if event.key == pygame.K_BACKSPACE:
            self._erase_character()
            return
        typed = getattr(event, "unicode", "")
        if typed and typed.isprintable():
            self._append_text(typed)

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.cursor_time = (self.cursor_time + dt) % 1.0
        pointer = self.input_manager.mouse_position
        if self.item_inspector.is_open:
            self.item_inspector.update_hover(pointer)
            return
        self.credential_note.update_note_hover(
            pointer,
            enabled=self.state == "entry",
        )
        self.submit_hovered = bool(
            self.state == "entry"
            and pointer is not None
            and SUBMIT_RECT.collidepoint(pointer)
        )

        if self.state == "success":
            self.success_time += dt
            if self.success_time >= SUCCESS_DELAY:
                self.item_inspector.release()
                self.manager.switch_to("audit")

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))
        self._render_screen(surface)
        self.credential_note.render_note_highlight(surface)
        self.item_inspector.render(surface)

    def _handle_click(self, pointer: tuple[int, int] | None) -> None:
        if pointer is None:
            return
        if self.credential_note.contains_note(pointer):
            self.credential_note.clear_hover()
            self.item_inspector.open()
            self._play_sound("paper", 0.55)
            return
        if USERNAME_RECT.collidepoint(pointer):
            self.active_field = "username"
            self.cursor_time = 0.0
            self._play_sound("click", 0.45)
            return
        if SUBMIT_RECT.collidepoint(pointer):
            self._attempt_login()
            return
        if PASSWORD_RECT.collidepoint(pointer):
            self.active_field = "password"
            self.cursor_time = 0.0
            self._play_sound("click", 0.45)

    def _attempt_login(self) -> None:
        if (
            self.username.casefold() == USERNAME.casefold()
            and self.password.casefold() == PASSWORD.casefold()
        ):
            self.state = "success"
            self.message = "ACESSO AUTORIZADO"
            self.success_time = 0.0
            self.credential_note.clear_hover()
            self._play_sound("confirm", 0.75)
            return
        self.password = ""
        self.active_field = "password"
        self.cursor_time = 0.0
        self.message = "USUÁRIO OU SENHA INCORRETOS"
        self._play_sound("back", 0.7)

    def _append_text(self, text: str) -> None:
        value = self.username if self.active_field == "username" else self.password
        if len(value) >= MAX_FIELD_LENGTH:
            return
        value += text
        if self.active_field == "username":
            self.username = value
        else:
            self.password = value
        self.message = ""
        self.cursor_time = 0.0
        self._play_sound("typing", 0.28)

    def _erase_character(self) -> None:
        if self.active_field == "username":
            self.username = self.username[:-1]
        else:
            self.password = self.password[:-1]
        self.message = ""
        self.cursor_time = 0.0
        self._play_sound("typing", 0.22)

    def _render_screen(self, surface: pygame.Surface) -> None:
        for offset in range(LOGIN_SCREEN_RECT.height):
            amount = offset / max(1, LOGIN_SCREEN_RECT.height - 1)
            color = tuple(
                round(top + (bottom - top) * amount)
                for top, bottom in zip(SCREEN_TOP, SCREEN_BOTTOM)
            )
            pygame.draw.line(
                surface,
                color,
                (LOGIN_SCREEN_RECT.left, LOGIN_SCREEN_RECT.top + offset),
                (LOGIN_SCREEN_RECT.right - 1, LOGIN_SCREEN_RECT.top + offset),
            )

        pygame.draw.rect(surface, BORDER, LOGIN_SCREEN_RECT, 2)
        self._text(
            surface,
            "REDE INTERNA // ACESSO RESTRITO",
            self.font_tiny,
            INK_MUTED,
            (LOGIN_SCREEN_RECT.x + 34, LOGIN_SCREEN_RECT.y + 29),
        )
        pulse = (math.sin(self.elapsed * 2.4) + 1.0) * 0.5
        led = (78 + round(pulse * 35), 145 + round(pulse * 36), 65)
        pygame.draw.circle(surface, led, (LOGIN_SCREEN_RECT.right - 148, 124), 5)
        self._text(
            surface,
            "ESTAÇÃO 04",
            self.font_tiny,
            GREEN,
            (LOGIN_SCREEN_RECT.right - 132, 114),
        )
        pygame.draw.line(
            surface,
            BORDER,
            (LOGIN_SCREEN_RECT.x + 32, 151),
            (LOGIN_SCREEN_RECT.right - 32, 151),
            2,
        )

        self._draw_profile(surface)
        self._text(surface, "BEM-VINDA", self.font_title, INK_BRIGHT, (960, 324), "center")
        self._text(
            surface,
            "Entre com sua conta de trabalho",
            self.font_small,
            INK_MUTED,
            (960, 370),
            "center",
        )
        self._draw_field(surface, "USUÁRIO", USERNAME_RECT, self.username, "username")
        masked_password = "*" * len(self.password)
        self._draw_field(surface, "SENHA", PASSWORD_RECT, masked_password, "password")
        self._draw_submit(surface)

        message_color = GREEN if self.state == "success" else RED
        if self.message:
            self._text(
                surface,
                self.message,
                self.font_small,
                message_color,
                (960, 625),
                "center",
            )
        self._text(
            surface,
            "DICA DE SENHA: LEMBRE-SE, CONFIE NO SEU CORAÇÃO.",
            self.font_tiny,
            AMBER,
            (960, 684),
            "center",
        )
        surface.blit(self.scanlines, LOGIN_SCREEN_RECT.topleft)

    def _draw_profile(self, surface: pygame.Surface) -> None:
        center = (960, 225)
        pygame.draw.circle(surface, (7, 14, 15), center, 58)
        pygame.draw.circle(surface, BORDER, center, 58, 3)
        pygame.draw.circle(surface, (150, 163, 140), (960, 209), 19)
        pygame.draw.ellipse(surface, (150, 163, 140), (921, 234, 78, 39))

    def _draw_field(
        self,
        surface: pygame.Surface,
        label: str,
        rect: pygame.Rect,
        value: str,
        field_id: str,
    ) -> None:
        active = self.state == "entry" and self.active_field == field_id
        border = AMBER if active else BORDER
        pygame.draw.rect(surface, PANEL_ACTIVE if active else PANEL, rect)
        pygame.draw.rect(surface, border, rect, 3 if active else 2)
        self._text(
            surface,
            label,
            self.font_tiny,
            AMBER if active else INK_MUTED,
            (rect.x, rect.y - 25),
        )
        shown = value or ("Digite o usuário" if field_id == "username" else "Digite a senha")
        color = INK_BRIGHT if value else INK_MUTED
        self._text(surface, shown, self.font_body, color, (rect.x + 18, rect.y + 15))
        if active and self.cursor_time < 0.5:
            text_width = self.font_body.size(value)[0]
            cursor_x = min(rect.right - 72, rect.x + 19 + text_width)
            pygame.draw.line(
                surface,
                INK_BRIGHT,
                (cursor_x, rect.y + 15),
                (cursor_x, rect.bottom - 14),
                2,
            )

    def _draw_submit(self, surface: pygame.Surface) -> None:
        active = self.state == "entry"
        hovered = active and self.submit_hovered
        fill = (56, 52, 30) if hovered else (28, 31, 23)
        border = INK_BRIGHT if hovered else AMBER if active else BORDER
        pygame.draw.rect(surface, fill, SUBMIT_RECT)
        pygame.draw.rect(surface, border, SUBMIT_RECT, 3)
        center_x, center_y = SUBMIT_RECT.center
        pygame.draw.line(
            surface,
            border,
            (center_x - 12, center_y),
            (center_x + 10, center_y),
            3,
        )
        pygame.draw.line(
            surface,
            border,
            (center_x + 2, center_y - 8),
            (center_x + 10, center_y),
            3,
        )
        pygame.draw.line(
            surface,
            border,
            (center_x + 2, center_y + 8),
            (center_x + 10, center_y),
            3,
        )

    @staticmethod
    def _build_scanlines() -> pygame.Surface:
        overlay = pygame.Surface(LOGIN_SCREEN_RECT.size, pygame.SRCALPHA)
        for y in range(0, LOGIN_SCREEN_RECT.height, 4):
            pygame.draw.line(
                overlay,
                (0, 0, 0, 27),
                (0, y),
                (LOGIN_SCREEN_RECT.width, y),
            )
        return overlay

    def _play_sound(self, name: str, volume: float = 0.8) -> None:
        if self.audio is not None:
            self.audio.play(name, volume)

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(
            ("Consolas", "Courier New", "monospace"),
            size,
            bold=bold,
        )

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
