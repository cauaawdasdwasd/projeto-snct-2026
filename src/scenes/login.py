from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.core.scene import Scene
from src.ui.credential_note import CredentialNote
from src.ui.desktop_window import RetroWindowTheme
from src.ui.item_inspector import ItemInspector
from src.ui.os_cursor import OSCursor

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


LOGIN_SCREEN_RECT = pygame.Rect(160, 55, 1600, 900)
USERNAME_RECT = pygame.Rect(1150, 410, 396, 72)
PASSWORD_RECT = pygame.Rect(1150, 526, 342, 72)
SUBMIT_RECT = pygame.Rect(1492, 522, 84, 80)

USERNAME = "sob_analise"
PASSWORD = "05112002LAB"
VALID_CREDENTIALS = (
    (USERNAME.casefold(), PASSWORD.casefold()),
    ("admin", "admin"),
)
MAX_FIELD_LENGTH = 24
SUCCESS_DELAY = 0.85

WELCOME_CENTER_X = 470
FORM_CENTER_X = USERNAME_RECT.centerx

INK_BRIGHT = (255, 255, 255)
INK_MUTED = (218, 230, 249)
GREEN = (133, 224, 99)
RED = (255, 224, 117)
XP_ORANGE = (240, 139, 35)


def credentials_are_valid(username: str, password: str) -> bool:
    candidate = (username.strip().casefold(), password.casefold())
    return candidate in VALID_CREDENTIALS


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
        self.background = self.assets.load_image("os/workstation_overlay.png")
        self.login_screen = self.assets.load_image("os/login_screen.png")
        self.theme = RetroWindowTheme(self.assets)
        self.os_cursor = OSCursor(
            self.assets.load_image("os/cursor.png"),
            LOGIN_SCREEN_RECT,
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
        self.submit_pressed = False

        self.font_tiny = self._font(16)
        self.font_small = self._font(20)
        self.font_body = self._font(23)
        self.font_title = self._font(34, bold=True)
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
        self.submit_pressed = False
        self.credential_note.clear_hover()
        self.item_inspector.close()
        if self.audio is not None:
            self.audio.stop_ambience()
            self.audio.play_music_sequence(("menu",), fade_ms=450)

    @property
    def screen_effect_rect(self) -> pygame.Rect:
        return LOGIN_SCREEN_RECT

    def on_exit(self) -> None:
        self.credential_note.clear_hover()
        self.item_inspector.close()

    def custom_cursor_active(self, position: tuple[int, int] | None) -> bool:
        return self.os_cursor.is_active(
            position,
            blocked=self.item_inspector.is_open,
        )

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
            if pointer is not None and SUBMIT_RECT.collidepoint(pointer):
                self.submit_pressed = True
                self._play_sound("click", 0.4)
            else:
                self._handle_click(pointer)
            return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            should_submit = bool(
                self.submit_pressed
                and pointer is not None
                and SUBMIT_RECT.collidepoint(pointer)
            )
            self.submit_pressed = False
            if should_submit:
                self._attempt_login()
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
                self.manager.switch_to("desktop")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        self._render_screen(surface)
        self.os_cursor.render(
            surface,
            self.input_manager.mouse_position,
            blocked=self.item_inspector.is_open,
        )
        surface.blit(self.background, (0, 0))
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
        if PASSWORD_RECT.collidepoint(pointer):
            self.active_field = "password"
            self.cursor_time = 0.0
            self._play_sound("click", 0.45)

    def _attempt_login(self) -> None:
        if credentials_are_valid(self.username, self.password):
            self.state = "success"
            self.message = "ACESSO AUTORIZADO"
            self.success_time = 0.0
            self.credential_note.clear_hover()
            self._play_sound("success", 0.75)
            return
        self.password = ""
        self.active_field = "password"
        self.cursor_time = 0.0
        self.message = "USUÁRIO OU SENHA INCORRETOS"
        self._play_sound("error", 0.7)

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
        surface.blit(self.login_screen, LOGIN_SCREEN_RECT.topleft)
        self._text(
            surface,
            "ORBE XP PROFESSIONAL",
            self.font_tiny,
            INK_BRIGHT,
            (LOGIN_SCREEN_RECT.x + 38, LOGIN_SCREEN_RECT.y + 35),
        )
        self._text(
            surface,
            "REDE DA EMPRESA",
            self.font_tiny,
            INK_BRIGHT,
            (LOGIN_SCREEN_RECT.right - 92, LOGIN_SCREEN_RECT.y + 35),
            "topright",
        )
        self._text(
            surface,
            "Bem-vinda",
            self._font(52, bold=True),
            INK_BRIGHT,
            (WELCOME_CENTER_X, 290),
            "midtop",
        )
        self._text(
            surface,
            "Para começar, entre com sua conta de trabalho.",
            self.font_body,
            INK_BRIGHT,
            (WELCOME_CENTER_X, 640),
            "midtop",
        )
        self._text(
            surface,
            "ESTAÇÃO 04",
            self.font_title,
            INK_BRIGHT,
            (FORM_CENTER_X, 318),
            "midtop",
        )
        self._text(
            surface,
            "Central de auditoria",
            self.font_small,
            INK_MUTED,
            (FORM_CENTER_X, 360),
            "midtop",
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
                (1320, 646),
                "center",
            )
        self._text(
            surface,
            "DICA DE SENHA: LEMBRE-SE, CONFIE NO SEU CORAÇÃO.",
            self.font_tiny,
            INK_BRIGHT,
            (350, LOGIN_SCREEN_RECT.bottom - 45),
        )
        self._text(
            surface,
            "Após entrar, abra o aplicativo Sob Análise na área de trabalho.",
            self.font_tiny,
            INK_MUTED,
            (LOGIN_SCREEN_RECT.right - 38, LOGIN_SCREEN_RECT.bottom - 45),
            "topright",
        )
        surface.blit(self.scanlines, LOGIN_SCREEN_RECT.topleft)

    def _draw_field(
        self,
        surface: pygame.Surface,
        label: str,
        rect: pygame.Rect,
        value: str,
        field_id: str,
    ) -> None:
        active = self.state == "entry" and self.active_field == field_id
        self.theme.draw_field(surface, rect, active=active)
        border = XP_ORANGE if active else (174, 194, 220)
        if active:
            pygame.draw.rect(surface, border, rect, 3)
        self._text(
            surface,
            label,
            self.font_tiny,
            INK_BRIGHT,
            (rect.x, rect.y - 25),
        )
        shown = value or ("Digite o usuário" if field_id == "username" else "Digite a senha")
        color = (25, 37, 59) if value else (115, 127, 143)
        self._text(surface, shown, self.font_body, color, (rect.x + 18, rect.y + 22))
        if active and self.cursor_time < 0.5:
            text_width = self.font_body.size(value)[0]
            cursor_x = min(rect.right - 72, rect.x + 19 + text_width)
            pygame.draw.line(
                surface,
                (25, 37, 59),
                (cursor_x, rect.y + 20),
                (cursor_x, rect.bottom - 18),
                2,
            )

    def _draw_submit(self, surface: pygame.Surface) -> None:
        active = self.state == "entry"
        hovered = active and self.submit_hovered
        state = "inactive" if not active else "pressed" if self.submit_pressed else "hover" if hovered else "normal"
        self.theme.draw_button(surface, SUBMIT_RECT, state)
        arrow_color = (25, 37, 59) if active else (125, 125, 125)
        center_x, center_y = SUBMIT_RECT.center
        pygame.draw.line(surface, arrow_color, (center_x - 13, center_y), (center_x + 12, center_y), 4)
        pygame.draw.line(surface, arrow_color, (center_x + 1, center_y - 11), (center_x + 13, center_y), 4)
        pygame.draw.line(surface, arrow_color, (center_x + 1, center_y + 11), (center_x + 13, center_y), 4)

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
            ("Tahoma", "Verdana", "Arial"),
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
        rendered = font.render(text, True, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
