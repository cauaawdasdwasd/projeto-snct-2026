from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pygame

from src.core.scene import Scene
from src.ui.credential_note import CredentialNote
from src.ui.desktop_window import DesktopWindow, DesktopWindowManager, RetroWindowTheme, WindowHit
from src.ui.item_inspector import ItemInspector
from src.ui.os_cursor import OSCursor

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager
    from src.scenes.audit import AuditScene


SCREEN_RECT = pygame.Rect(160, 55, 1600, 900)
TASKBAR_RECT = pygame.Rect(SCREEN_RECT.x, SCREEN_RECT.bottom - 82, SCREEN_RECT.width, 82)
WORK_AREA_RECT = pygame.Rect(SCREEN_RECT.x, SCREEN_RECT.y, SCREEN_RECT.width, SCREEN_RECT.height - TASKBAR_RECT.height)
START_RECT = pygame.Rect(315, TASKBAR_RECT.y, 140, TASKBAR_RECT.height)
START_MENU_RECT = pygame.Rect(315, TASKBAR_RECT.y - 676, 350, 676)
AUDIT_SOURCE_RECT = pygame.Rect(186, 87, 1554, 883)

XP_ORANGE = (244, 151, 38)
WINDOW_BG = (236, 233, 216)
WINDOW_INK = (25, 25, 25)
WHITE = (255, 255, 255)


class DesktopIcon:
    def __init__(self, app_id: str, label: str, rect: pygame.Rect, kind: str) -> None:
        self.app_id = app_id
        self.label = label
        self.rect = rect
        self.kind = kind


class DesktopScene(Scene):
    """Interactive XP-era desktop that hosts every tool in real windows."""

    def __init__(
        self,
        manager: SceneManager,
        assets: AssetManager,
        input_manager: InputManager,
        audio: AudioManager | None = None,
        audit_scene: AuditScene | None = None,
    ) -> None:
        super().__init__(manager, assets, input_manager)
        self.audio = audio
        self.audit_scene = audit_scene
        self.station = self.assets.load_image("os/workstation_overlay.png")
        self.desktop_screen = self.assets.load_image("os/desktop_screen.png")
        start_source = pygame.Rect(0, TASKBAR_RECT.y - SCREEN_RECT.y, START_RECT.width, START_RECT.height)
        self.start_button_skin = self.desktop_screen.subsurface(start_source).copy()
        self.start_menu_skin = self.assets.load_image("os/start_menu.png")
        self.user_avatar = self.assets.load_image("os/user_avatar.png")
        self.app_icon_images = {
            "audit": self.assets.load_image("os/icon_audit.png"),
            "browser": self.assets.load_image("os/icon_browser.png"),
            "calculator": self.assets.load_image("os/icon_calculator.png"),
            "documents": self.assets.load_image("os/icon_documents.png"),
            "folder": self.assets.load_image("os/icon_folder.png"),
        }
        self.theme = RetroWindowTheme(self.assets)
        self.window_manager = DesktopWindowManager(WORK_AREA_RECT)
        self.audit_surface = pygame.Surface((1920, 1080)).convert()
        self.audit_composite = pygame.Surface(AUDIT_SOURCE_RECT.size).convert()
        self.audit_view_rect: pygame.Rect | None = None
        self.audit_pointer_capture = False

        self.os_cursor = OSCursor(self.assets.load_image("os/cursor.png"), SCREEN_RECT)
        self.credential_note = CredentialNote(self.assets.load_image("ui/heart_note.png"))
        self.item_inspector = ItemInspector(
            self.assets.assets_root / "models" / "heart_note.glb",
            "Post-it de acesso",
        )

        self.font_tiny = self._font(15)
        self.font_small = self._font(18)
        self.font_body = self._font(22)
        self.font_body_bold = self._font(22, bold=True)
        self.font_title = self._font(25, bold=True)
        self.icons = self._build_icons()
        self.scanlines = self._build_scanlines()

        self.start_open = False
        self.selected_icon: str | None = None
        self.last_icon_click: str | None = None
        self.last_icon_click_time = 0
        self.hovered_target: str | None = None
        self.pressed_target: str | None = None

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
        self.selected_icon = None
        self.hovered_target = None
        self.pressed_target = None
        self.naming_kind = None
        self.audit_pointer_capture = False
        self.window_manager.windows.clear()
        self.window_manager.z_order.clear()
        self.window_manager.task_order.clear()
        self.window_manager.cancel_interaction()
        self.credential_note.clear_hover()
        self.item_inspector.close()
        if self.audit_scene is not None:
            self.audit_scene.set_embedded_mode(True)
        if self.audio is not None:
            self.audio.play_music_sequence(("menu",), fade_ms=450)

    def on_exit(self) -> None:
        self.credential_note.clear_hover()
        self.item_inspector.close()
        if self.audit_scene is not None and "audit" in self.window_manager.windows:
            self.audit_scene.on_exit()

    def custom_cursor_active(self, position: tuple[int, int] | None) -> bool:
        return self.os_cursor.is_active(position, blocked=self.item_inspector.is_open)

    def handle_escape(self) -> bool:
        if self.item_inspector.is_open:
            self.item_inspector.close()
            self._sound("back", 0.55)
            return True
        if self.naming_kind is not None:
            self.naming_kind = None
            self.name_buffer = ""
            self._sound("back", 0.55)
            return True
        if self.start_open:
            self.start_open = False
            self._sound("back", 0.45)
            return True
        if self.window_manager.focused_id == "audit" and self.audit_scene is not None:
            self._with_audit_pointer(self.input_manager.mouse_position, self.audit_scene.handle_escape)
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

        focused = self.window_manager.focused_id
        if event.type == pygame.KEYDOWN:
            if focused == "notepad":
                self._handle_notepad_key(event)
                return
            if focused == "calculator" and self._handle_calculator_key(event):
                return
            if focused == "audit" and self.audit_scene is not None:
                self._forward_audit_event(event, pointer)
                return

        if event.type == pygame.MOUSEMOTION:
            self.window_manager.update_pointer(pointer)
            self.hovered_target = self._target_at(pointer)
            if self.window_manager.interaction_app is not None:
                return
            if (self.audit_pointer_capture or focused == "audit") and self.audit_scene is not None:
                self._forward_audit_event(event, pointer)
            return

        if event.type == pygame.MOUSEWHEEL:
            if focused == "audit" and self.audit_scene is not None and self._map_to_audit(pointer) is not None:
                self._forward_audit_event(event, pointer)
            return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.audit_pointer_capture and self.audit_scene is not None:
                self._forward_audit_event(event, pointer)
                self.audit_pointer_capture = False
            activated = self.window_manager.end_interaction(pointer)
            self.pressed_target = None
            if activated is not None:
                self._activate_window_control(*activated)
            return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            if self.audit_pointer_capture and self.audit_scene is not None:
                self._forward_audit_event(event, pointer)
                self.audit_pointer_capture = False
            return

        if event.type != pygame.MOUSEBUTTONDOWN or pointer is None:
            return
        if self.credential_note.contains_note(pointer):
            self.credential_note.clear_hover()
            self.item_inspector.open()
            self._sound("paper", 0.5)
            return

        if event.button == 1:
            if START_RECT.collidepoint(pointer):
                self.start_open = not self.start_open
                self._sound("click", 0.45)
                return
            for app_id, rect in self._taskbar_button_rects():
                if rect.collidepoint(pointer):
                    self.window_manager.toggle_taskbar(app_id)
                    self.start_open = False
                    self._sound("click", 0.42)
                    return
            if self.start_open and self._handle_start_click(pointer):
                return

        hit = self.window_manager.hit_test(pointer)
        if hit is not None:
            self.start_open = False
            self._handle_window_pointer_down(hit, event, pointer)
            return
        if event.button != 1:
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
        self.window_manager.update_pointer(pointer)
        self.hovered_target = self._target_at(pointer)
        audit_window = self.window_manager.windows.get("audit")
        if self.audit_scene is not None and audit_window is not None and not audit_window.minimized:
            self._with_audit_pointer(pointer, lambda: self.audit_scene.update(dt))
            if self.audit_scene.consume_desktop_request():
                self.window_manager.minimize("audit")
                self._sound("back", 0.5)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        surface.blit(self.desktop_screen, SCREEN_RECT.topleft)
        self._draw_desktop_icons(surface)
        for window in self.window_manager.visible_windows():
            self._draw_window(surface, window)
        self._draw_taskbar(surface)
        if self.start_open:
            self._draw_start_menu(surface)
        if self.naming_kind is not None:
            self._draw_name_dialog(surface)
        surface.blit(self.scanlines, SCREEN_RECT.topleft)
        self.os_cursor.render(surface, self.input_manager.mouse_position, blocked=self.item_inspector.is_open)
        surface.blit(self.station, (0, 0))
        self.credential_note.render_note_highlight(surface)
        self.item_inspector.render(surface)

    def _handle_window_pointer_down(self, hit: WindowHit, event: pygame.event.Event, pointer: tuple[int, int]) -> None:
        self.window_manager.focus(hit.app_id)
        if event.button == 1 and hit.area == "titlebar" and getattr(event, "clicks", 1) >= 2:
            self.window_manager.toggle_maximize(hit.app_id)
            self._sound("click", 0.45)
            return
        if event.button == 1 and hit.area in {"control", "titlebar", "resize"}:
            self.window_manager.begin_interaction(hit, pointer)
            if hit.area == "control" and hit.control is not None:
                self.pressed_target = f"window:{hit.app_id}:{hit.control}"
            return
        if hit.area != "client":
            return
        if hit.app_id == "audit" and self.audit_scene is not None:
            if self._map_to_audit(pointer) is not None:
                self.audit_pointer_capture = event.button in (1, 3)
                self._forward_audit_event(event, pointer)
            return
        if event.button == 1:
            self._handle_app_click(hit.app_id, pointer)

    def _activate_window_control(self, app_id: str, control: str) -> None:
        if control == "minimize":
            self.window_manager.minimize(app_id)
            self._sound("click", 0.4)
        elif control == "maximize":
            self.window_manager.toggle_maximize(app_id)
            self._sound("click", 0.45)
        else:
            self._close_app(app_id)

    def _open_app(self, app_id: str) -> None:
        self.start_open = False
        self.selected_icon = app_id
        self.status_message = ""
        was_open = app_id in self.window_manager.windows
        title, rect, min_size = self._window_spec(app_id)
        self.window_manager.open(app_id, title, rect, min_size)
        self._sound("forward", 0.55)
        if app_id == "audit" and self.audit_scene is not None and not was_open:
            self.audit_scene.set_embedded_mode(True)
            self.audit_scene.on_enter()

    def _close_app(self, app_id: str) -> None:
        if app_id == "notepad":
            self._save_notepad()
            self.editing_index = None
        elif app_id == "audit" and self.audit_scene is not None:
            self.audit_scene.on_exit()
            self.audit_pointer_capture = False
        self.window_manager.close(app_id)
        self._sound("back", 0.5)

    def _window_spec(self, app_id: str) -> tuple[str, pygame.Rect, tuple[int, int]]:
        if app_id == "audit":
            return "Sob Análise - Central de Auditoria", pygame.Rect(280, 65, 1360, 805), (920, 570)
        if app_id == "calculator":
            return "Calculadora", pygame.Rect(710, 105, 520, 680), (410, 620)
        if app_id == "explorer":
            return "Meus documentos", pygame.Rect(350, 115, 1210, 670), (720, 450)
        if app_id == "notepad":
            title = self.entries[self.editing_index]["name"] if self.editing_index is not None else "Bloco de notas"
            return title, pygame.Rect(470, 145, 1040, 610), (620, 400)
        return "Google - Internet Explorer", pygame.Rect(420, 125, 1180, 650), (700, 440)

    def _handle_start_click(self, pointer: tuple[int, int]) -> bool:
        if not START_MENU_RECT.collidepoint(pointer):
            self.start_open = False
            return False
        for app_id, rect in self._start_item_rects():
            if rect.collidepoint(pointer):
                self._open_app(app_id)
                return True
        logout_rect = pygame.Rect(START_MENU_RECT.x + 188, START_MENU_RECT.bottom - 72, 150, 62)
        if logout_rect.collidepoint(pointer):
            self._sound("back", 0.6)
            self.manager.switch_to("login")
            return True
        return True

    def _handle_app_click(self, app_id: str, pointer: tuple[int, int]) -> None:
        window = self.window_manager.windows[app_id]
        if app_id == "calculator":
            for label, rect in self._calculator_buttons(window):
                if rect.collidepoint(pointer):
                    self._calculator_press(label)
                    return
        elif app_id == "explorer":
            new_folder, new_text = self._explorer_toolbar_buttons(window)
            if new_folder.collidepoint(pointer):
                self._begin_naming("folder")
                return
            if new_text.collidepoint(pointer):
                self._begin_naming("text")
                return
            for index, rect in self._entry_rects(window):
                if rect.collidepoint(pointer) and self.entries[index]["kind"] == "text":
                    self.editing_index = index
                    self.notepad_text = self.entries[index]["content"]
                    title, target, min_size = self._window_spec("notepad")
                    self.window_manager.open("notepad", title, target, min_size)
                    self._sound("document", 0.45)
                    return

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
                self.entries.append({"kind": self.naming_kind or "text", "name": name[:28], "content": ""})
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
            pygame.K_KP_PLUS: "+", pygame.K_KP_MINUS: "-", pygame.K_KP_MULTIPLY: "×",
            pygame.K_KP_DIVIDE: "÷", pygame.K_RETURN: "=", pygame.K_KP_ENTER: "=",
            pygame.K_BACKSPACE: "←", pygame.K_ESCAPE: "C",
        }
        label = key_map.get(event.key)
        typed = getattr(event, "unicode", "")
        if typed in "0123456789.,+-*/%":
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
        if label == "%":
            self.calc_display = f"{float(self.calc_display) / 100:.10g}"
            self.calc_new_entry = True
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
            result = {"+": self.calc_accumulator + right, "-": self.calc_accumulator - right, "×": self.calc_accumulator * right, "÷": self.calc_accumulator / right}[self.calc_operator]
            self.calc_display = f"{result:.10g}"
        except ZeroDivisionError:
            self.calc_display = "Erro"
        self.calc_accumulator = None
        self.calc_operator = None
        self.calc_new_entry = True

    def _draw_desktop_icons(self, surface: pygame.Surface) -> None:
        for icon in self.icons:
            if self.selected_icon == icon.app_id:
                highlight = pygame.Surface(icon.rect.size, pygame.SRCALPHA)
                highlight.fill((45, 91, 190, 105))
                surface.blit(highlight, icon.rect.topleft)
                pygame.draw.rect(surface, (190, 215, 255), icon.rect, 1)
            image = self.app_icon_images[icon.kind]
            surface.blit(image, image.get_rect(midtop=(icon.rect.centerx, icon.rect.y + 5)))
            label = self.font_small.render(icon.label, True, WHITE)
            label_rect = label.get_rect(midtop=(icon.rect.centerx, icon.rect.y + 106))
            surface.blit(self.font_small.render(icon.label, True, (0, 0, 0)), label_rect.move(2, 2))
            surface.blit(label, label_rect)

    def _draw_window(self, surface: pygame.Surface, window: DesktopWindow) -> None:
        focused = self.window_manager.focused_id == window.app_id
        icon_kind = "documents" if window.app_id in {"explorer", "notepad"} else window.app_id
        self.theme.draw_window(surface, window, focused, self.window_manager.hovered_control, self.window_manager.pressed_control, self.font_small, self.app_icon_images.get(icon_kind))
        old_clip = surface.get_clip()
        surface.set_clip(window.client_rect)
        if window.app_id == "audit":
            self._draw_audit(surface, window)
        elif window.app_id == "browser":
            self._draw_browser(surface, window)
        elif window.app_id == "calculator":
            self._draw_calculator(surface, window)
        elif window.app_id == "explorer":
            self._draw_explorer(surface, window)
        elif window.app_id == "notepad":
            self._draw_notepad(surface, window)
        surface.set_clip(old_clip)

    def _draw_audit(self, surface: pygame.Surface, window: DesktopWindow) -> None:
        client = window.client_rect
        pygame.draw.rect(surface, (2, 5, 4), client)
        if self.audit_scene is None:
            self._text(surface, "Aplicativo indisponível", self.font_body, WHITE, client.center, "center")
            return
        self._with_audit_pointer(self.input_manager.mouse_position, lambda: self.audit_scene.render_embedded(self.audit_surface))
        view = self._fit_rect(AUDIT_SOURCE_RECT.size, client)
        self.audit_composite.blit(self.audit_surface, (0, 0), AUDIT_SOURCE_RECT)
        footer_y = 696
        self.audit_composite.fill((2, 5, 4), pygame.Rect(0, footer_y, self.audit_composite.width, self.audit_composite.height - footer_y))
        stamp_source = pygame.Rect(432, 807, 1035, 162)
        stamp_destination = (stamp_source.x - AUDIT_SOURCE_RECT.x, stamp_source.y - AUDIT_SOURCE_RECT.y)
        self.audit_composite.blit(self.audit_surface, stamp_destination, stamp_source)
        scaled = pygame.transform.scale(self.audit_composite, view.size)
        surface.blit(scaled, view.topleft)
        self.audit_view_rect = view

    def _draw_browser(self, surface: pygame.Surface, window: DesktopWindow) -> None:
        client = window.client_rect
        pygame.draw.rect(surface, WINDOW_BG, client)
        toolbar = pygame.Rect(client.x + 8, client.y + 8, client.width - 16, 72)
        for index, symbol in enumerate(("←", "→", "⌂")):
            rect = pygame.Rect(toolbar.x + 8 + index * 42, toolbar.y + 4, 36, 30)
            state = "hover" if rect.collidepoint(self.input_manager.mouse_position or (-1, -1)) else "normal"
            self.theme.draw_button(surface, rect, state)
            self._text(surface, symbol, self.font_body_bold, (24, 59, 137), rect.center, "center")
        address = pygame.Rect(toolbar.x + 8, toolbar.y + 39, toolbar.width - 16, 28)
        self.theme.draw_field(surface, address)
        self._text(surface, "http://rede.local/noticias", self.font_small, WINDOW_INK, (address.x + 9, address.y + 5))
        page = pygame.Rect(client.x + 10, toolbar.bottom + 4, client.width - 20, client.bottom - toolbar.bottom - 14)
        pygame.draw.rect(surface, WHITE, page)
        self._text(surface, "REDE LOCAL", self.font_title, (34, 79, 152), (page.x + 38, page.y + 32))
        pygame.draw.line(surface, XP_ORANGE, (page.x + 38, page.y + 70), (page.right - 38, page.y + 70), 4)
        self._text(surface, "Notícias da estação", self._font(32, bold=True), WINDOW_INK, (page.x + 38, page.y + 98))
        self._text(surface, "Nenhuma notícia recebida hoje.", self.font_body, (76, 76, 76), (page.x + 38, page.y + 152))
        self._text(surface, "A rede externa será atualizada em breve.", self.font_small, (105, 105, 105), (page.x + 38, page.y + 192))

    def _draw_calculator(self, surface: pygame.Surface, window: DesktopWindow) -> None:
        client = window.client_rect
        pygame.draw.rect(surface, WINDOW_BG, client)
        display = pygame.Rect(client.x + 22, client.y + 24, client.width - 44, 78)
        self.theme.draw_field(surface, display)
        shown = self.font_title.render(self.calc_display, True, WINDOW_INK)
        surface.blit(shown, shown.get_rect(midright=(display.right - 15, display.centery)))
        for label, rect in self._calculator_buttons(window):
            target = f"calc:{label}"
            state = "pressed" if self.pressed_target == target else "hover" if self.hovered_target == target else "normal"
            self.theme.draw_button(surface, rect, state)
            color = (171, 34, 34) if label in {"C", "←"} else (27, 48, 119) if label in {"+", "-", "×", "÷", "%", "="} else WINDOW_INK
            self._text(surface, label, self.font_body_bold, color, rect.center, "center")

    def _draw_explorer(self, surface: pygame.Surface, window: DesktopWindow) -> None:
        client = window.client_rect
        pygame.draw.rect(surface, WINDOW_BG, client)
        new_folder, new_text = self._explorer_toolbar_buttons(window)
        for label, rect, target in (("Nova pasta", new_folder, "explorer:new_folder"), ("Novo texto", new_text, "explorer:new_text")):
            self.theme.draw_button(surface, rect, "hover" if self.hovered_target == target else "normal")
            self._text(surface, label, self.font_small, WINDOW_INK, rect.center, "center")
        content_top = client.y + 62
        sidebar_width = min(230, max(150, client.width // 4))
        sidebar = pygame.Rect(client.x + 10, content_top, sidebar_width, client.bottom - content_top - 10)
        pygame.draw.rect(surface, (214, 229, 252), sidebar)
        self._text(surface, "Tarefas", self.font_body_bold, (34, 79, 152), (sidebar.x + 18, sidebar.y + 20))
        self._text(surface, "Crie pastas e notas", self.font_small, (57, 78, 111), (sidebar.x + 18, sidebar.y + 62))
        content = pygame.Rect(sidebar.right + 6, sidebar.y, client.right - sidebar.right - 16, sidebar.height)
        pygame.draw.rect(surface, WHITE, content)
        for index, rect in self._entry_rects(window):
            entry = self.entries[index]
            if rect.collidepoint(self.input_manager.mouse_position or (-1, -1)):
                pygame.draw.rect(surface, (220, 235, 255), rect)
            self._draw_icon_art(surface, entry["kind"], (rect.x + 29, rect.centery), 28)
            self._text(surface, entry["name"], self.font_small, WINDOW_INK, (rect.x + 54, rect.y + 15))

    def _draw_notepad(self, surface: pygame.Surface, window: DesktopWindow) -> None:
        client = window.client_rect
        menu = pygame.Rect(client.x, client.y, client.width, 34)
        pygame.draw.rect(surface, WINDOW_BG, menu)
        self._text(surface, "Arquivo   Editar   Formatar   Ajuda", self.font_small, WINDOW_INK, (menu.x + 8, menu.y + 5))
        page = pygame.Rect(client.x + 3, menu.bottom, client.width - 6, client.bottom - menu.bottom - 3)
        pygame.draw.rect(surface, WHITE, page)
        wrap_width = max(20, (page.width - 28) // max(1, self.font_body.size("M")[0]))
        lines = self._wrap_notepad(self.notepad_text, wrap_width)
        visible_lines = max(1, (page.height - 32) // 27)
        for index, line in enumerate(lines[:visible_lines]):
            self._text(surface, line, self.font_body, WINDOW_INK, (page.x + 14, page.y + 12 + index * 27))
        cursor_line = min(visible_lines - 1, len(lines) - 1)
        if int(pygame.time.get_ticks() / 480) % 2 == 0:
            cursor_x = page.x + 14 + self.font_body.size(lines[cursor_line])[0]
            cursor_y = page.y + 12 + cursor_line * 27
            pygame.draw.line(surface, WINDOW_INK, (cursor_x, cursor_y), (cursor_x, cursor_y + 23), 2)
        if self.status_message:
            self._text(surface, self.status_message, self.font_small, (50, 110, 45), (page.right - 18, page.bottom - 15), "bottomright")

    def _draw_taskbar(self, surface: pygame.Surface) -> None:
        surface.blit(self.start_button_skin, START_RECT.topleft)
        if self.hovered_target == "start" or self.start_open:
            glow = pygame.Surface(START_RECT.size, pygame.SRCALPHA)
            glow.fill((255, 255, 255, 38))
            surface.blit(glow, START_RECT.topleft)
        self._text(surface, "iniciar", self.font_body_bold, WHITE, (START_RECT.x + 65, START_RECT.y + 28))
        focused = self.window_manager.focused_id
        for app_id, rect in self._taskbar_button_rects():
            window = self.window_manager.windows[app_id]
            active = focused == app_id and not window.minimized
            tile = pygame.Surface(rect.size, pygame.SRCALPHA)
            tile.fill((12, 55, 147, 190) if active else (39, 91, 180, 155))
            surface.blit(tile, rect.topleft)
            pygame.draw.rect(surface, (138, 188, 246) if active else (70, 130, 214), rect, 2)
            icon_kind = "documents" if app_id in {"explorer", "notepad"} else app_id
            icon = pygame.transform.scale(self.app_icon_images[icon_kind], (34, 34))
            surface.blit(icon, icon.get_rect(midleft=(rect.x + 10, rect.centery)))
            self._text(surface, window.title, self.font_small, WHITE, (rect.x + 52, rect.centery), "midleft")
        clock = datetime.now().strftime("%H:%M")
        self._text(surface, clock, self.font_body, WHITE, (TASKBAR_RECT.right - 58, TASKBAR_RECT.y + 28), "midtop")

    def _draw_start_menu(self, surface: pygame.Surface) -> None:
        surface.blit(self.start_menu_skin, START_MENU_RECT.topleft)
        avatar = pygame.transform.scale(self.user_avatar, (72, 72))
        surface.blit(avatar, (START_MENU_RECT.x + 15, START_MENU_RECT.y + 40))
        self._text(surface, "sob_analise", self.font_title, WHITE, (START_MENU_RECT.x + 102, START_MENU_RECT.y + 61))
        for app_id, rect in self._start_item_rects():
            active = self.hovered_target == f"start:{app_id}"
            if active:
                highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
                highlight.fill((36, 102, 203, 115))
                surface.blit(highlight, rect.topleft)
            kind = "documents" if app_id == "explorer" else app_id
            icon = pygame.transform.scale(self.app_icon_images[kind], (58, 58))
            surface.blit(icon, icon.get_rect(midleft=(rect.x + 10, rect.centery)))
            label = {"audit": "Sob Análise", "browser": "Google", "calculator": "Calculadora", "explorer": "Meus documentos"}[app_id]
            self._text(surface, label, self.font_body_bold, WHITE if active else WINDOW_INK, (rect.x + 78, rect.y + 28))
        self._text(surface, "Encerrar sessão", self.font_small, (18, 48, 104), (START_MENU_RECT.right - 70, START_MENU_RECT.bottom - 46), "midright")

    def _draw_name_dialog(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface(SCREEN_RECT.size, pygame.SRCALPHA)
        dim.fill((0, 0, 0, 80))
        surface.blit(dim, SCREEN_RECT.topleft)
        rect = pygame.Rect(684, 354, 548, 210)
        dialog = DesktopWindow("dialog", "Criar novo item", rect, (500, 200))
        self.theme.draw_window(surface, dialog, True, None, None, self.font_small)
        kind = "pasta" if self.naming_kind == "folder" else "documento de texto"
        self._text(surface, f"Nome da {kind}:", self.font_body, WINDOW_INK, (rect.x + 28, rect.y + 66))
        field = pygame.Rect(rect.x + 28, rect.y + 102, rect.width - 56, 44)
        self.theme.draw_field(surface, field, active=True)
        self._text(surface, self.name_buffer, self.font_body, WINDOW_INK, (field.x + 10, field.y + 9))
        self._text(surface, "ENTER confirma  |  ESC cancela", self.font_small, (90, 90, 90), (rect.centerx, rect.bottom - 31), "center")

    def _map_to_audit(self, pointer: tuple[int, int] | None) -> tuple[int, int] | None:
        window = self.window_manager.windows.get("audit")
        if pointer is None or window is None or window.minimized:
            return None
        view = self._fit_rect(AUDIT_SOURCE_RECT.size, window.client_rect)
        self.audit_view_rect = view
        if not view.collidepoint(pointer):
            return None
        relative_x = (pointer[0] - view.x) / max(1, view.width)
        relative_y = (pointer[1] - view.y) / max(1, view.height)
        return (
            AUDIT_SOURCE_RECT.x + min(AUDIT_SOURCE_RECT.width - 1, int(relative_x * AUDIT_SOURCE_RECT.width)),
            AUDIT_SOURCE_RECT.y + min(AUDIT_SOURCE_RECT.height - 1, int(relative_y * AUDIT_SOURCE_RECT.height)),
        )

    def _with_audit_pointer(self, pointer, callback):
        original = self.input_manager.mouse_position
        self.input_manager.mouse_position = self._map_to_audit(pointer)
        try:
            return callback()
        finally:
            self.input_manager.mouse_position = original

    def _forward_audit_event(self, event: pygame.event.Event, pointer: tuple[int, int] | None) -> None:
        if self.audit_scene is not None:
            self._with_audit_pointer(pointer, lambda: self.audit_scene.handle_event(event))

    def _calculator_buttons(self, window: DesktopWindow) -> tuple[tuple[str, pygame.Rect], ...]:
        client = window.client_rect
        labels = (("←", "C", "÷", "×"), ("7", "8", "9", "-"), ("4", "5", "6", "+"), ("1", "2", "3", "%"), ("0", ".", "", "="))
        left, top, gap = client.x + 22, client.y + 124, 10
        button_width = max(56, (client.width - 44 - gap * 3) // 4)
        button_height = max(48, (client.height - 154 - gap * 4) // 5)
        buttons: list[tuple[str, pygame.Rect]] = []
        for row, row_labels in enumerate(labels):
            for column, label in enumerate(row_labels):
                if not label:
                    continue
                rect = pygame.Rect(left + column * (button_width + gap), top + row * (button_height + gap), button_width, button_height)
                if label == "0":
                    rect.width = button_width * 2 + gap
                elif label == "." and row == 4:
                    rect.x = left + 2 * (button_width + gap)
                buttons.append((label, rect))
        return tuple(buttons)

    def _explorer_toolbar_buttons(self, window: DesktopWindow) -> tuple[pygame.Rect, pygame.Rect]:
        client = window.client_rect
        return pygame.Rect(client.x + 16, client.y + 11, 170, 40), pygame.Rect(client.x + 198, client.y + 11, 170, 40)

    def _entry_rects(self, window: DesktopWindow) -> tuple[tuple[int, pygame.Rect], ...]:
        client = window.client_rect
        sidebar_width = min(230, max(150, client.width // 4))
        content_x = client.x + 10 + sidebar_width + 16
        content_width = client.right - content_x - 10
        columns, gap = (2 if content_width >= 650 else 1), 12
        item_width = max(250, (content_width - gap * (columns - 1)) // columns)
        start_y = client.y + 72
        return tuple((index, pygame.Rect(content_x + (index % columns) * (item_width + gap), start_y + (index // columns) * 72, item_width, 62)) for index in range(len(self.entries)))

    def _taskbar_button_rects(self) -> tuple[tuple[str, pygame.Rect], ...]:
        app_ids = tuple(self.window_manager.task_order)
        if not app_ids:
            return tuple()
        available = TASKBAR_RECT.right - 168 - (START_RECT.right + 18)
        width = min(300, max(116, (available - 8 * (len(app_ids) - 1)) // len(app_ids)))
        return tuple((app_id, pygame.Rect(START_RECT.right + 18 + index * (width + 8), TASKBAR_RECT.y + 12, width, 58)) for index, app_id in enumerate(app_ids))

    def _start_item_rects(self) -> tuple[tuple[str, pygame.Rect], ...]:
        return tuple((app_id, pygame.Rect(START_MENU_RECT.x + 18, START_MENU_RECT.y + 166 + index * 99, START_MENU_RECT.width - 36, 84)) for index, app_id in enumerate(("audit", "browser", "calculator", "explorer")))

    def _target_at(self, pointer: tuple[int, int] | None) -> str | None:
        if pointer is None:
            return None
        if START_RECT.collidepoint(pointer):
            return "start"
        for app_id, rect in self._taskbar_button_rects():
            if rect.collidepoint(pointer):
                return f"taskbar:{app_id}"
        if self.start_open:
            for app_id, rect in self._start_item_rects():
                if rect.collidepoint(pointer):
                    return f"start:{app_id}"
        focused = self.window_manager.focused_window
        if focused is not None and focused.app_id == "calculator":
            for label, rect in self._calculator_buttons(focused):
                if rect.collidepoint(pointer):
                    return f"calc:{label}"
        if focused is not None and focused.app_id == "explorer":
            new_folder, new_text = self._explorer_toolbar_buttons(focused)
            if new_folder.collidepoint(pointer):
                return "explorer:new_folder"
            if new_text.collidepoint(pointer):
                return "explorer:new_text"
        return None

    def _build_icons(self) -> tuple[DesktopIcon, ...]:
        return (
            DesktopIcon("audit", "Sob Análise", pygame.Rect(182, 92, 168, 142), "audit"),
            DesktopIcon("browser", "Google", pygame.Rect(182, 242, 168, 142), "browser"),
            DesktopIcon("calculator", "Calculadora", pygame.Rect(182, 392, 168, 142), "calculator"),
            DesktopIcon("explorer", "Meus documentos", pygame.Rect(182, 542, 182, 142), "documents"),
        )

    def _begin_naming(self, kind: str) -> None:
        self.naming_kind = kind
        self.name_buffer = ""
        self._sound("forward", 0.45)

    def _draw_icon_art(self, surface: pygame.Surface, kind: str, center: tuple[int, int], size: int) -> None:
        x, y = center
        if kind == "folder":
            icon = pygame.transform.scale(self.app_icon_images["folder"], (size + 24, size + 24))
            surface.blit(icon, icon.get_rect(center=center))
            return
        pygame.draw.rect(surface, WHITE, (x - size // 3, y - size // 2, size * 2 // 3, size))
        pygame.draw.rect(surface, (73, 123, 197), (x - size // 4, y - size // 4, size // 2, 3))
        pygame.draw.rect(surface, (73, 123, 197), (x - size // 4, y - 5, size // 2, 3))

    @staticmethod
    def _fit_rect(source_size: tuple[int, int], destination: pygame.Rect) -> pygame.Rect:
        source_width, source_height = source_size
        scale = min(destination.width / source_width, destination.height / source_height)
        width, height = max(1, round(source_width * scale)), max(1, round(source_height * scale))
        return pygame.Rect(destination.centerx - width // 2, destination.centery - height // 2, width, height)

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
    def _text(surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple[int, int, int], position: tuple[int, int], anchor: str = "topleft") -> None:
        rendered = font.render(text, True, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
