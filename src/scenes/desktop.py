from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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


SCREEN_RECT = pygame.Rect(186, 87, 1554, 696)
TASKBAR_RECT = pygame.Rect(SCREEN_RECT.x, SCREEN_RECT.bottom - 52, SCREEN_RECT.width, 52)
START_RECT = pygame.Rect(SCREEN_RECT.x, TASKBAR_RECT.y, 158, TASKBAR_RECT.height)
START_MENU_RECT = pygame.Rect(SCREEN_RECT.x, TASKBAR_RECT.y - 394, 438, 394)

XP_BLUE = (38, 96, 191)
XP_BLUE_DARK = (20, 57, 145)
XP_BLUE_LIGHT = (69, 132, 229)
XP_GREEN = (58, 159, 47)
XP_GREEN_DARK = (34, 111, 31)
XP_ORANGE = (244, 151, 38)
WINDOW_BG = (236, 233, 216)
WINDOW_INK = (25, 25, 25)
WHITE = (255, 255, 255)


@dataclass(frozen=True)
class DesktopIcon:
    app_id: str
    label: str
    rect: pygame.Rect
    kind: str


class DesktopScene(Scene):
    """Small, functional XP-era desktop that hosts the audit application."""

    def __init__(
        self,
        manager: SceneManager,
        assets: AssetManager,
        input_manager: InputManager,
        audio: AudioManager | None = None,
    ) -> None:
        super().__init__(manager, assets, input_manager)
        self.audio = audio
        self.station = self.assets.load_image("backgrounds/novo_sprite_teste.png")
        wallpaper = self.assets.load_image("backgrounds/desktop_xp_original.png")
        self.wallpaper = pygame.transform.scale(wallpaper, SCREEN_RECT.size)
        self.credential_note = CredentialNote(self.assets.load_image("ui/heart_note.png"))
        self.item_inspector = ItemInspector(
            self.assets.assets_root / "models" / "heart_note.glb",
            "Post-it de acesso",
        )

        self.font_small = self._font(18)
        self.font_body = self._font(22)
        self.font_body_bold = self._font(22, bold=True)
        self.font_title = self._font(25, bold=True)
        self.font_clock = self._font(17)
        self.icons = self._build_icons()
        self.scanlines = self._build_scanlines()

        self.start_open = False
        self.selected_icon: str | None = None
        self.last_icon_click: str | None = None
        self.last_icon_click_time = 0
        self.active_app: str | None = None
        self.hovered_target: str | None = None

        self.calc_display = "0"
        self.calc_accumulator: float | None = None
        self.calc_operator: str | None = None
        self.calc_new_entry = True

        self.entries: list[dict[str, str]] = [
            {"kind": "folder", "name": "Casos arquivados", "content": ""},
            {"kind": "text", "name": "leia-me.txt", "content": "A calculadora ajuda nos protocolos de cálculo."},
        ]
        self.naming_kind: str | None = None
        self.name_buffer = ""
        self.editing_index: int | None = None
        self.notepad_text = ""
        self.status_message = ""

    def on_enter(self) -> None:
        self.start_open = False
        self.active_app = None
        self.selected_icon = None
        self.hovered_target = None
        self.naming_kind = None
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
            self._sound("back", 0.55)
        elif self.naming_kind is not None:
            self.naming_kind = None
            self.name_buffer = ""
            self._sound("back", 0.55)
        elif self.active_app is not None:
            self._close_app()
        elif self.start_open:
            self.start_open = False
            self._sound("back", 0.45)
        return True

    def handle_event(self, event: pygame.event.Event) -> None:
        pointer = self.input_manager.mouse_position
        if self.item_inspector.is_open:
            action = self.item_inspector.handle_event(event, pointer)
            if action == "close":
                self._sound("back", 0.55)
            elif action == "zoom":
                self._sound("scroll", 0.4)
            return

        if self.naming_kind is not None:
            self._handle_name_input(event)
            return
        if self.active_app == "notepad" and event.type == pygame.KEYDOWN:
            self._handle_notepad_key(event)
            return
        if self.active_app == "calculator" and event.type == pygame.KEYDOWN:
            if self._handle_calculator_key(event):
                return

        if event.type == pygame.MOUSEMOTION:
            self.hovered_target = self._target_at(pointer)
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1 or pointer is None:
            return

        if self.credential_note.contains_note(pointer):
            self.credential_note.clear_hover()
            self.item_inspector.open()
            self._sound("paper", 0.5)
            return

        if self.active_app is not None:
            if self._handle_app_click(pointer):
                return

        if START_RECT.collidepoint(pointer):
            self.start_open = not self.start_open
            self._sound("click", 0.45)
            return

        if self.start_open and self._handle_start_click(pointer):
            return

        if not SCREEN_RECT.collidepoint(pointer) or TASKBAR_RECT.collidepoint(pointer):
            self.start_open = False
            return

        self.start_open = False
        for icon in self.icons:
            if not icon.rect.collidepoint(pointer):
                continue
            now = pygame.time.get_ticks()
            is_double = self.last_icon_click == icon.app_id and now - self.last_icon_click_time <= 470
            self.selected_icon = icon.app_id
            self.last_icon_click = icon.app_id
            self.last_icon_click_time = now
            self._sound("click", 0.38)
            if is_double:
                self._open_app(icon.app_id)
            return
        self.selected_icon = None

    def update(self, dt: float) -> None:
        pointer = self.input_manager.mouse_position
        if self.item_inspector.is_open:
            self.item_inspector.update_hover(pointer)
            return
        self.credential_note.update_note_hover(pointer, enabled=True)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.station, (0, 0))
        surface.blit(self.wallpaper, SCREEN_RECT.topleft)
        self._draw_desktop_icons(surface)
        if self.active_app is not None:
            self._draw_active_app(surface)
        self._draw_taskbar(surface)
        if self.start_open:
            self._draw_start_menu(surface)
        if self.naming_kind is not None:
            self._draw_name_dialog(surface)
        surface.blit(self.scanlines, SCREEN_RECT.topleft)
        self.credential_note.render_note_highlight(surface)
        self.item_inspector.render(surface)

    def _build_icons(self) -> tuple[DesktopIcon, ...]:
        return (
            DesktopIcon("audit", "Sob Análise", pygame.Rect(214, 122, 132, 102), "audit"),
            DesktopIcon("browser", "Google", pygame.Rect(214, 240, 132, 102), "browser"),
            DesktopIcon("calculator", "Calculadora", pygame.Rect(214, 358, 132, 102), "calculator"),
            DesktopIcon("explorer", "Meus documentos", pygame.Rect(214, 476, 154, 102), "folder"),
        )

    def _open_app(self, app_id: str) -> None:
        self.start_open = False
        self.selected_icon = app_id
        self._sound("forward", 0.55)
        if app_id == "audit":
            self.item_inspector.release()
            self.manager.switch_to("audit")
            return
        self.active_app = app_id
        self.status_message = ""

    def _close_app(self) -> None:
        if self.active_app == "notepad":
            self._save_notepad()
        self.active_app = None
        self.editing_index = None
        self._sound("back", 0.5)

    def _handle_start_click(self, pointer: tuple[int, int]) -> bool:
        if not START_MENU_RECT.collidepoint(pointer):
            self.start_open = False
            return False
        for app_id, rect in self._start_item_rects():
            if rect.collidepoint(pointer):
                self._open_app(app_id)
                return True
        logout_rect = pygame.Rect(START_MENU_RECT.x + 218, START_MENU_RECT.bottom - 48, 210, 40)
        if logout_rect.collidepoint(pointer):
            self._sound("back", 0.6)
            self.manager.switch_to("login")
            return True
        return True

    def _handle_app_click(self, pointer: tuple[int, int]) -> bool:
        window = self._window_rect()
        close_rect = pygame.Rect(window.right - 35, window.y + 5, 29, 27)
        if close_rect.collidepoint(pointer):
            self._close_app()
            return True
        if not window.collidepoint(pointer):
            return False
        if self.active_app == "calculator":
            for label, rect in self._calculator_buttons():
                if rect.collidepoint(pointer):
                    self._calculator_press(label)
                    return True
        elif self.active_app == "explorer":
            new_folder = pygame.Rect(window.x + 20, window.y + 45, 152, 38)
            new_text = pygame.Rect(window.x + 182, window.y + 45, 152, 38)
            if new_folder.collidepoint(pointer):
                self._begin_naming("folder")
                return True
            if new_text.collidepoint(pointer):
                self._begin_naming("text")
                return True
            for index, rect in self._entry_rects(window):
                if rect.collidepoint(pointer) and self.entries[index]["kind"] == "text":
                    self.editing_index = index
                    self.notepad_text = self.entries[index]["content"]
                    self.active_app = "notepad"
                    self._sound("document", 0.45)
                    return True
        return True

    def _handle_name_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.naming_kind = None
            self.name_buffer = ""
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            name = self.name_buffer.strip()
            if name:
                if self.naming_kind == "text" and not name.lower().endswith(".txt"):
                    name += ".txt"
                self.entries.append({"kind": self.naming_kind, "name": name[:28], "content": ""})
                self._sound("confirm", 0.55)
            self.naming_kind = None
            self.name_buffer = ""
            return
        if event.key == pygame.K_BACKSPACE:
            self.name_buffer = self.name_buffer[:-1]
            return
        typed = getattr(event, "unicode", "")
        if typed.isprintable() and len(self.name_buffer) < 28:
            self.name_buffer += typed
            self._sound("typing", 0.2)

    def _handle_notepad_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self._close_app()
            return
        if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
            self._save_notepad()
            self.status_message = "Arquivo salvo"
            self._sound("confirm", 0.45)
            return
        if event.key == pygame.K_BACKSPACE:
            self.notepad_text = self.notepad_text[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.notepad_text += "\n"
        else:
            typed = getattr(event, "unicode", "")
            if typed.isprintable() and len(self.notepad_text) < 1500:
                self.notepad_text += typed
        self._sound("typing", 0.18)

    def _save_notepad(self) -> None:
        if self.editing_index is not None:
            self.entries[self.editing_index]["content"] = self.notepad_text

    def _handle_calculator_key(self, event: pygame.event.Event) -> bool:
        key_map = {
            pygame.K_KP_PLUS: "+",
            pygame.K_KP_MINUS: "-",
            pygame.K_KP_MULTIPLY: "×",
            pygame.K_KP_DIVIDE: "÷",
            pygame.K_RETURN: "=",
            pygame.K_KP_ENTER: "=",
            pygame.K_BACKSPACE: "←",
            pygame.K_ESCAPE: "C",
        }
        label = key_map.get(event.key)
        typed = getattr(event, "unicode", "")
        if typed in "0123456789.,+-*/":
            label = {"*": "×", "/": "÷", ",": "."}.get(typed, typed)
        if label is None:
            return False
        self._calculator_press(label)
        return True

    def _calculator_press(self, label: str) -> None:
        self._sound("click", 0.32)
        if label.isdigit() or label == ".":
            if self.calc_new_entry:
                self.calc_display = "0" if label == "." else label
                self.calc_new_entry = False
            elif len(self.calc_display) < 15 and not (label == "." and "." in self.calc_display):
                self.calc_display += label
            if label == "." and "." not in self.calc_display:
                self.calc_display += "."
            return
        if label == "C":
            self.calc_display = "0"
            self.calc_accumulator = None
            self.calc_operator = None
            self.calc_new_entry = True
            return
        if label == "←":
            self.calc_display = self.calc_display[:-1] or "0"
            return
        if label in {"+", "-", "×", "÷"}:
            if self.calc_operator is not None and not self.calc_new_entry:
                self._calculate()
            else:
                self.calc_accumulator = float(self.calc_display)
            self.calc_operator = label
            self.calc_new_entry = True
            return
        if label == "=":
            self._calculate()

    def _calculate(self) -> None:
        if self.calc_accumulator is None or self.calc_operator is None:
            return
        right = float(self.calc_display)
        try:
            result = {
                "+": self.calc_accumulator + right,
                "-": self.calc_accumulator - right,
                "×": self.calc_accumulator * right,
                "÷": self.calc_accumulator / right,
            }[self.calc_operator]
            self.calc_display = f"{result:.10g}"
        except ZeroDivisionError:
            self.calc_display = "Erro"
        self.calc_accumulator = None
        self.calc_operator = None
        self.calc_new_entry = True

    def _draw_desktop_icons(self, surface: pygame.Surface) -> None:
        for icon in self.icons:
            selected = self.selected_icon == icon.app_id
            if selected:
                highlight = pygame.Surface(icon.rect.size, pygame.SRCALPHA)
                highlight.fill((45, 91, 190, 125))
                surface.blit(highlight, icon.rect.topleft)
                pygame.draw.rect(surface, (190, 215, 255), icon.rect, 1)
            self._draw_icon_art(surface, icon.kind, (icon.rect.centerx, icon.rect.y + 36), 44)
            label = self.font_small.render(icon.label, True, WHITE)
            label_rect = label.get_rect(midtop=(icon.rect.centerx, icon.rect.y + 70))
            shadow = self.font_small.render(icon.label, True, (0, 0, 0))
            surface.blit(shadow, label_rect.move(2, 2))
            surface.blit(label, label_rect)

    def _draw_taskbar(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, XP_BLUE_DARK, TASKBAR_RECT)
        pygame.draw.rect(surface, XP_BLUE_LIGHT, (TASKBAR_RECT.x, TASKBAR_RECT.y, TASKBAR_RECT.width, 3))
        start_color = (71, 181, 58) if self.hovered_target == "start" or self.start_open else XP_GREEN
        pygame.draw.rect(surface, start_color, START_RECT, border_radius=0)
        pygame.draw.rect(surface, XP_GREEN_DARK, START_RECT, 2)
        self._draw_flag(surface, (START_RECT.x + 26, START_RECT.centery), 22)
        self._text(surface, "iniciar", self.font_body_bold, WHITE, (START_RECT.x + 48, START_RECT.y + 14))

        if self.active_app is not None:
            app_rect = pygame.Rect(START_RECT.right + 12, TASKBAR_RECT.y + 7, 278, 38)
            pygame.draw.rect(surface, (25, 70, 156), app_rect)
            pygame.draw.rect(surface, (105, 154, 236), app_rect, 2)
            label = {
                "browser": "Google",
                "calculator": "Calculadora",
                "explorer": "Meus documentos",
                "notepad": "Bloco de notas",
            }.get(self.active_app, self.active_app)
            self._text(surface, label, self.font_small, WHITE, (app_rect.x + 14, app_rect.y + 9))

        tray = pygame.Rect(TASKBAR_RECT.right - 170, TASKBAR_RECT.y, 170, TASKBAR_RECT.height)
        pygame.draw.rect(surface, (32, 130, 207), tray)
        pygame.draw.line(surface, (116, 190, 244), tray.topleft, tray.bottomleft, 2)
        pygame.draw.circle(surface, (94, 218, 75), (tray.x + 24, tray.centery), 6)
        clock = datetime.now().strftime("%H:%M")
        self._text(surface, clock, self.font_clock, WHITE, (tray.right - 58, tray.y + 17), "midtop")

    def _draw_start_menu(self, surface: pygame.Surface) -> None:
        shadow = pygame.Surface((START_MENU_RECT.width + 8, START_MENU_RECT.height + 8), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 95))
        surface.blit(shadow, START_MENU_RECT.move(5, 5))
        pygame.draw.rect(surface, WHITE, START_MENU_RECT)
        pygame.draw.rect(surface, XP_BLUE, (START_MENU_RECT.x, START_MENU_RECT.y, START_MENU_RECT.width, 72))
        pygame.draw.rect(surface, XP_BLUE_DARK, START_MENU_RECT, 3)
        self._draw_user_tile(surface, (START_MENU_RECT.x + 18, START_MENU_RECT.y + 12), 48)
        self._text(surface, "sob_analise", self.font_title, WHITE, (START_MENU_RECT.x + 82, START_MENU_RECT.y + 22))

        for app_id, rect in self._start_item_rects():
            active = self.hovered_target == f"start:{app_id}"
            if active:
                pygame.draw.rect(surface, (49, 106, 197), rect)
            kind = "folder" if app_id == "explorer" else app_id
            self._draw_icon_art(surface, kind, (rect.x + 29, rect.centery), 30)
            label = {
                "audit": "Sob Análise",
                "browser": "Google",
                "calculator": "Calculadora",
                "explorer": "Meus documentos",
            }[app_id]
            self._text(surface, label, self.font_body_bold, WHITE if active else WINDOW_INK, (rect.x + 58, rect.y + 13))

        footer = pygame.Rect(START_MENU_RECT.x, START_MENU_RECT.bottom - 55, START_MENU_RECT.width, 55)
        pygame.draw.rect(surface, (214, 229, 252), footer)
        pygame.draw.line(surface, (150, 174, 214), footer.topleft, footer.topright, 2)
        self._draw_power_icon(surface, (footer.right - 190, footer.centery), 22)
        self._text(surface, "Encerrar sessão", self.font_small, WINDOW_INK, (footer.right - 162, footer.y + 18))

    def _draw_active_app(self, surface: pygame.Surface) -> None:
        window = self._window_rect()
        self._draw_window_frame(surface, window, self._window_title())
        if self.active_app == "browser":
            self._draw_browser(surface, window)
        elif self.active_app == "calculator":
            self._draw_calculator(surface, window)
        elif self.active_app == "explorer":
            self._draw_explorer(surface, window)
        elif self.active_app == "notepad":
            self._draw_notepad(surface, window)

    def _draw_browser(self, surface: pygame.Surface, window: pygame.Rect) -> None:
        toolbar = pygame.Rect(window.x + 4, window.y + 35, window.width - 8, 80)
        pygame.draw.rect(surface, WINDOW_BG, toolbar)
        for x, symbol in ((toolbar.x + 28, "←"), (toolbar.x + 70, "→"), (toolbar.x + 112, "⌂")):
            self._text(surface, symbol, self.font_title, (39, 91, 176), (x, toolbar.y + 8), "midtop")
        address = pygame.Rect(toolbar.x + 18, toolbar.y + 43, toolbar.width - 36, 29)
        pygame.draw.rect(surface, WHITE, address)
        pygame.draw.rect(surface, (127, 157, 185), address, 2)
        self._text(surface, "http://rede.local/noticias", self.font_small, WINDOW_INK, (address.x + 9, address.y + 5))

        page = pygame.Rect(window.x + 8, window.y + 118, window.width - 16, window.height - 126)
        pygame.draw.rect(surface, WHITE, page)
        self._text(surface, "REDE LOCAL", self.font_title, (34, 79, 152), (page.x + 48, page.y + 42))
        pygame.draw.line(surface, XP_ORANGE, (page.x + 48, page.y + 82), (page.right - 48, page.y + 82), 4)
        self._text(surface, "Notícias da estação", self._font(34, bold=True), WINDOW_INK, (page.x + 48, page.y + 118))
        self._text(surface, "Nenhuma notícia recebida hoje.", self.font_body, (76, 76, 76), (page.x + 48, page.y + 182))
        self._text(surface, "A rede externa será atualizada em breve.", self.font_small, (105, 105, 105), (page.x + 48, page.y + 222))

    def _draw_calculator(self, surface: pygame.Surface, window: pygame.Rect) -> None:
        body = window.inflate(-18, -52)
        body.y += 18
        pygame.draw.rect(surface, WINDOW_BG, body)
        display = pygame.Rect(body.x + 18, body.y + 16, body.width - 36, 62)
        pygame.draw.rect(surface, (231, 240, 222), display)
        pygame.draw.rect(surface, (108, 119, 99), display, 2)
        shown = self.font_title.render(self.calc_display, True, WINDOW_INK)
        surface.blit(shown, shown.get_rect(midright=(display.right - 12, display.centery)))
        for label, rect in self._calculator_buttons():
            hovered = self.hovered_target == f"calc:{label}:{rect.x}:{rect.y}"
            pygame.draw.rect(surface, (249, 248, 242) if hovered else (222, 219, 203), rect)
            pygame.draw.rect(surface, (121, 119, 109), rect, 2)
            color = (171, 34, 34) if label in {"C", "←"} else (27, 48, 119) if label in {"+", "-", "×", "÷", "="} else WINDOW_INK
            self._text(surface, label, self.font_body_bold, color, rect.center, "center")

    def _draw_explorer(self, surface: pygame.Surface, window: pygame.Rect) -> None:
        toolbar = pygame.Rect(window.x + 4, window.y + 35, window.width - 8, 58)
        pygame.draw.rect(surface, WINDOW_BG, toolbar)
        for label, rect in (("Nova pasta", pygame.Rect(window.x + 20, window.y + 45, 152, 38)), ("Novo texto", pygame.Rect(window.x + 182, window.y + 45, 152, 38))):
            pygame.draw.rect(surface, (246, 244, 235), rect)
            pygame.draw.rect(surface, (123, 128, 121), rect, 2)
            self._text(surface, label, self.font_small, WINDOW_INK, rect.center, "center")
        sidebar = pygame.Rect(window.x + 7, window.y + 95, 205, window.height - 103)
        pygame.draw.rect(surface, (214, 229, 252), sidebar)
        self._text(surface, "Tarefas", self.font_body_bold, (34, 79, 152), (sidebar.x + 18, sidebar.y + 20))
        self._text(surface, "Crie pastas e notas", self.font_small, (57, 78, 111), (sidebar.x + 18, sidebar.y + 62))
        content = pygame.Rect(sidebar.right + 4, sidebar.y, window.right - sidebar.right - 11, sidebar.height)
        pygame.draw.rect(surface, WHITE, content)
        for index, rect in self._entry_rects(window):
            entry = self.entries[index]
            self._draw_icon_art(surface, entry["kind"], (rect.x + 29, rect.centery), 28)
            self._text(surface, entry["name"], self.font_small, WINDOW_INK, (rect.x + 54, rect.y + 15))

    def _draw_notepad(self, surface: pygame.Surface, window: pygame.Rect) -> None:
        menu = pygame.Rect(window.x + 4, window.y + 35, window.width - 8, 30)
        pygame.draw.rect(surface, WINDOW_BG, menu)
        self._text(surface, "Arquivo   Editar   Formatar   Ajuda", self.font_small, WINDOW_INK, (menu.x + 8, menu.y + 5))
        page = pygame.Rect(window.x + 7, menu.bottom, window.width - 14, window.bottom - menu.bottom - 7)
        pygame.draw.rect(surface, WHITE, page)
        lines = self._wrap_notepad(self.notepad_text, 72)
        for index, line in enumerate(lines[:17]):
            self._text(surface, line, self.font_body, WINDOW_INK, (page.x + 14, page.y + 12 + index * 27))
        cursor_line = min(16, len(lines) - 1)
        if int(pygame.time.get_ticks() / 480) % 2 == 0:
            cursor_x = page.x + 14 + self.font_body.size(lines[cursor_line])[0]
            cursor_y = page.y + 12 + cursor_line * 27
            pygame.draw.line(surface, WINDOW_INK, (cursor_x, cursor_y), (cursor_x, cursor_y + 23), 2)
        if self.status_message:
            self._text(surface, self.status_message, self.font_small, (50, 110, 45), (page.right - 18, page.bottom - 25), "bottomright")

    def _draw_name_dialog(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface(SCREEN_RECT.size, pygame.SRCALPHA)
        dim.fill((0, 0, 0, 80))
        surface.blit(dim, SCREEN_RECT.topleft)
        rect = pygame.Rect(684, 354, 548, 192)
        self._draw_window_frame(surface, rect, "Criar novo item")
        kind = "pasta" if self.naming_kind == "folder" else "documento de texto"
        self._text(surface, f"Nome da {kind}:", self.font_body, WINDOW_INK, (rect.x + 28, rect.y + 62))
        field = pygame.Rect(rect.x + 28, rect.y + 98, rect.width - 56, 44)
        pygame.draw.rect(surface, WHITE, field)
        pygame.draw.rect(surface, (45, 92, 172), field, 2)
        self._text(surface, self.name_buffer, self.font_body, WINDOW_INK, (field.x + 10, field.y + 9))
        self._text(surface, "ENTER confirma • ESC cancela", self.font_small, (90, 90, 90), (rect.centerx, rect.bottom - 30), "center")

    def _draw_window_frame(self, surface: pygame.Surface, rect: pygame.Rect, title: str) -> None:
        pygame.draw.rect(surface, WINDOW_BG, rect)
        pygame.draw.rect(surface, XP_BLUE_DARK, rect, 3)
        titlebar = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, 31)
        pygame.draw.rect(surface, XP_BLUE, titlebar)
        pygame.draw.line(surface, XP_BLUE_LIGHT, titlebar.topleft, titlebar.topright, 2)
        self._text(surface, title, self.font_body_bold, WHITE, (titlebar.x + 10, titlebar.y + 5))
        close_rect = pygame.Rect(rect.right - 35, rect.y + 5, 29, 27)
        pygame.draw.rect(surface, (210, 62, 41), close_rect)
        pygame.draw.rect(surface, WHITE, close_rect, 1)
        self._text(surface, "×", self.font_title, WHITE, close_rect.center, "center")

    def _window_rect(self) -> pygame.Rect:
        if self.active_app == "calculator":
            return pygame.Rect(692, 146, 520, 566)
        if self.active_app == "notepad":
            return pygame.Rect(432, 137, 1080, 578)
        return pygame.Rect(406, 131, 1120, 586)

    def _window_title(self) -> str:
        return {
            "browser": "Google - Internet Explorer",
            "calculator": "Calculadora",
            "explorer": "Meus documentos",
            "notepad": self.entries[self.editing_index]["name"] if self.editing_index is not None else "Bloco de notas",
        }.get(self.active_app or "", "")

    def _calculator_buttons(self) -> tuple[tuple[str, pygame.Rect], ...]:
        window = pygame.Rect(692, 146, 520, 566)
        labels = (
            ("←", "C", "÷", "×"),
            ("7", "8", "9", "-"),
            ("4", "5", "6", "+"),
            ("1", "2", "3", "="),
            ("0", ".", "=", "="),
        )
        buttons: list[tuple[str, pygame.Rect]] = []
        start_x = window.x + 27
        start_y = window.y + 146
        width, height, gap = 104, 58, 10
        for row, row_labels in enumerate(labels):
            for column, label in enumerate(row_labels):
                if label == "=" and (row, column) in {(4, 2), (4, 3)}:
                    continue
                rect = pygame.Rect(start_x + column * (width + gap), start_y + row * (height + gap), width, height)
                if label == "=" and row == 3:
                    rect.height = height * 2 + gap
                if label == "0":
                    rect.width = width * 2 + gap
                if label == "." and row == 4:
                    rect.x += width + gap
                buttons.append((label, rect))
        return tuple(buttons)

    def _entry_rects(self, window: pygame.Rect) -> tuple[tuple[int, pygame.Rect], ...]:
        rects = []
        start_x = window.x + 236
        start_y = window.y + 118
        for index in range(len(self.entries)):
            column = index % 2
            row = index // 2
            rects.append((index, pygame.Rect(start_x + column * 380, start_y + row * 66, 355, 56)))
        return tuple(rects)

    def _start_item_rects(self) -> tuple[tuple[str, pygame.Rect], ...]:
        return tuple(
            (app_id, pygame.Rect(START_MENU_RECT.x + 8, START_MENU_RECT.y + 82 + index * 57, START_MENU_RECT.width - 16, 52))
            for index, app_id in enumerate(("audit", "browser", "calculator", "explorer"))
        )

    def _target_at(self, pointer: tuple[int, int] | None) -> str | None:
        if pointer is None:
            return None
        if START_RECT.collidepoint(pointer):
            return "start"
        if self.start_open:
            for app_id, rect in self._start_item_rects():
                if rect.collidepoint(pointer):
                    return f"start:{app_id}"
        if self.active_app == "calculator":
            for label, rect in self._calculator_buttons():
                if rect.collidepoint(pointer):
                    return f"calc:{label}:{rect.x}:{rect.y}"
        return None

    def _draw_icon_art(self, surface: pygame.Surface, kind: str, center: tuple[int, int], size: int) -> None:
        x, y = center
        if kind in {"folder", "text"}:
            if kind == "folder":
                pygame.draw.rect(surface, (239, 184, 47), (x - size // 2, y - size // 4, size, size // 2 + 10))
                pygame.draw.rect(surface, (253, 210, 80), (x - size // 2 + 4, y - size // 2, size // 2, size // 3))
            else:
                pygame.draw.rect(surface, WHITE, (x - size // 3, y - size // 2, size * 2 // 3, size))
                pygame.draw.rect(surface, (73, 123, 197), (x - size // 4, y - size // 4, size // 2, 3))
                pygame.draw.rect(surface, (73, 123, 197), (x - size // 4, y - 5, size // 2, 3))
            return
        if kind == "browser":
            pygame.draw.circle(surface, (50, 116, 218), center, size // 2)
            pygame.draw.circle(surface, (107, 204, 245), center, size // 2 - 5, 3)
            pygame.draw.arc(surface, (238, 210, 52), (x - size // 2 - 5, y - size // 4, size + 10, size // 2), 3.2, 6.0, 5)
            return
        if kind == "calculator":
            rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
            pygame.draw.rect(surface, (198, 205, 208), rect)
            pygame.draw.rect(surface, (63, 83, 90), rect, 3)
            pygame.draw.rect(surface, (198, 225, 184), (rect.x + 6, rect.y + 6, rect.width - 12, 10))
            for row in range(2):
                for column in range(3):
                    pygame.draw.rect(surface, (52, 83, 151), (rect.x + 7 + column * 12, rect.y + 23 + row * 11, 8, 8))
            return
        shield = pygame.Rect(x - size // 2, y - size // 2, size, size)
        pygame.draw.rect(surface, (27, 54, 67), shield)
        pygame.draw.rect(surface, (225, 201, 65), shield, 3)
        self._text(surface, "S", self._font(max(20, size - 13), bold=True), (244, 237, 154), center, "center")

    def _draw_flag(self, surface: pygame.Surface, center: tuple[int, int], size: int) -> None:
        x, y = center
        half = size // 2
        colors = ((238, 65, 52), (74, 168, 64), (64, 116, 219), (244, 191, 38))
        rects = (
            pygame.Rect(x - half, y - half, half - 1, half - 1),
            pygame.Rect(x + 1, y - half, half - 1, half - 1),
            pygame.Rect(x - half, y + 1, half - 1, half - 1),
            pygame.Rect(x + 1, y + 1, half - 1, half - 1),
        )
        for color, rect in zip(colors, rects):
            pygame.draw.rect(surface, color, rect)

    def _draw_user_tile(self, surface: pygame.Surface, position: tuple[int, int], size: int) -> None:
        rect = pygame.Rect(position, (size, size))
        pygame.draw.rect(surface, WHITE, rect)
        pygame.draw.rect(surface, (115, 157, 70), rect.inflate(-4, -4))
        pygame.draw.circle(surface, (242, 223, 169), (rect.centerx, rect.y + 17), 9)
        pygame.draw.ellipse(surface, (247, 239, 193), (rect.x + 10, rect.y + 27, rect.width - 20, 17))

    def _draw_power_icon(self, surface: pygame.Surface, center: tuple[int, int], size: int) -> None:
        pygame.draw.circle(surface, (230, 98, 42), center, size // 2)
        pygame.draw.arc(surface, WHITE, (center[0] - 7, center[1] - 7, 14, 14), -0.5, 3.65, 2)
        pygame.draw.line(surface, WHITE, (center[0], center[1] - 9), (center[0], center[1]), 2)

    @staticmethod
    def _wrap_notepad(text: str, width: int) -> list[str]:
        lines: list[str] = []
        for paragraph in text.split("\n"):
            if not paragraph:
                lines.append("")
                continue
            remaining = paragraph
            while len(remaining) > width:
                split = remaining.rfind(" ", 0, width + 1)
                if split <= 0:
                    split = width
                lines.append(remaining[:split])
                remaining = remaining[split:].lstrip()
            lines.append(remaining)
        return lines or [""]

    @staticmethod
    def _build_scanlines() -> pygame.Surface:
        overlay = pygame.Surface(SCREEN_RECT.size, pygame.SRCALPHA)
        for y in range(0, SCREEN_RECT.height, 4):
            pygame.draw.line(overlay, (0, 0, 0, 14), (0, y), (SCREEN_RECT.width, y))
        return overlay

    def _sound(self, name: str, volume: float = 0.8) -> None:
        if self.audio is not None:
            self.audio.play(name, volume)

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Tahoma", "Verdana", "Arial"), size, bold=bold)

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
