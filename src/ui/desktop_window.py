from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.core.assets import AssetManager


FRAME_BORDER = 6
TITLEBAR_HEIGHT = 44
RESIZE_MARGIN = 9
CONTROL_SIZE = (36, 28)


@dataclass
class DesktopWindow:
    """State for one movable window in the simulated workstation."""

    app_id: str
    title: str
    rect: pygame.Rect
    min_size: tuple[int, int]
    minimized: bool = False
    maximized: bool = False
    restore_rect: pygame.Rect | None = None

    @property
    def titlebar_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.rect.x + FRAME_BORDER,
            self.rect.y + FRAME_BORDER,
            self.rect.width - FRAME_BORDER * 2,
            TITLEBAR_HEIGHT - FRAME_BORDER,
        )

    @property
    def client_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.rect.x + FRAME_BORDER,
            self.rect.y + TITLEBAR_HEIGHT,
            self.rect.width - FRAME_BORDER * 2,
            self.rect.height - TITLEBAR_HEIGHT - FRAME_BORDER,
        )

    def control_rects(self) -> dict[str, pygame.Rect]:
        width, height = CONTROL_SIZE
        y = self.rect.y + 9
        close = pygame.Rect(self.rect.right - FRAME_BORDER - width - 3, y, width, height)
        maximize = close.move(-(width + 3), 0)
        minimize = maximize.move(-(width + 3), 0)
        return {
            "minimize": minimize,
            "maximize": maximize,
            "close": close,
        }

    def resize_edges_at(self, position: tuple[int, int]) -> frozenset[str]:
        if self.maximized or not self.rect.inflate(RESIZE_MARGIN * 2, RESIZE_MARGIN * 2).collidepoint(position):
            return frozenset()
        x, y = position
        edges: set[str] = set()
        if abs(x - self.rect.left) <= RESIZE_MARGIN:
            edges.add("left")
        elif abs(x - self.rect.right) <= RESIZE_MARGIN:
            edges.add("right")
        if abs(y - self.rect.top) <= RESIZE_MARGIN:
            edges.add("top")
        elif abs(y - self.rect.bottom) <= RESIZE_MARGIN:
            edges.add("bottom")
        return frozenset(edges)


@dataclass(frozen=True)
class WindowHit:
    app_id: str
    area: str
    control: str | None = None


@dataclass
class DesktopWindowManager:
    """Owns z-order, focus and mouse manipulation for desktop windows."""

    work_area: pygame.Rect
    windows: dict[str, DesktopWindow] = field(default_factory=dict)
    z_order: list[str] = field(default_factory=list)
    task_order: list[str] = field(default_factory=list)
    interaction_app: str | None = None
    interaction_kind: str | None = None
    resize_edges: frozenset[str] = field(default_factory=frozenset)
    drag_offset: tuple[int, int] = (0, 0)
    interaction_start: tuple[int, int] = (0, 0)
    interaction_rect: pygame.Rect | None = None
    hovered_control: tuple[str, str] | None = None
    pressed_control: tuple[str, str] | None = None

    @property
    def focused_id(self) -> str | None:
        for app_id in reversed(self.z_order):
            window = self.windows.get(app_id)
            if window is not None and not window.minimized:
                return app_id
        return None

    @property
    def focused_window(self) -> DesktopWindow | None:
        focused_id = self.focused_id
        return self.windows.get(focused_id) if focused_id is not None else None

    def open(
        self,
        app_id: str,
        title: str,
        rect: pygame.Rect,
        min_size: tuple[int, int],
    ) -> DesktopWindow:
        if app_id in self.windows:
            window = self.windows[app_id]
            window.title = title
            window.minimized = False
            self.focus(app_id)
            return window
        window = DesktopWindow(app_id, title, rect.copy(), min_size)
        self._keep_titlebar_visible(window)
        self.windows[app_id] = window
        self.z_order.append(app_id)
        self.task_order.append(app_id)
        return window

    def close(self, app_id: str) -> DesktopWindow | None:
        window = self.windows.pop(app_id, None)
        if app_id in self.z_order:
            self.z_order.remove(app_id)
        if app_id in self.task_order:
            self.task_order.remove(app_id)
        if self.interaction_app == app_id:
            self.cancel_interaction()
        return window

    def focus(self, app_id: str) -> None:
        if app_id not in self.windows:
            return
        if app_id in self.z_order:
            self.z_order.remove(app_id)
        self.z_order.append(app_id)

    def minimize(self, app_id: str) -> None:
        window = self.windows.get(app_id)
        if window is not None:
            window.minimized = True
            self.cancel_interaction()

    def restore(self, app_id: str) -> None:
        window = self.windows.get(app_id)
        if window is not None:
            window.minimized = False
            self.focus(app_id)

    def toggle_taskbar(self, app_id: str) -> None:
        window = self.windows.get(app_id)
        if window is None:
            return
        if window.minimized:
            self.restore(app_id)
        elif self.focused_id == app_id:
            self.minimize(app_id)
        else:
            self.focus(app_id)

    def toggle_maximize(self, app_id: str) -> None:
        window = self.windows.get(app_id)
        if window is None:
            return
        if window.maximized:
            if window.restore_rect is not None:
                window.rect = window.restore_rect.copy()
            window.restore_rect = None
            window.maximized = False
        else:
            window.restore_rect = window.rect.copy()
            window.rect = self.work_area.copy()
            window.maximized = True
        window.minimized = False
        self.focus(app_id)

    def visible_windows(self) -> tuple[DesktopWindow, ...]:
        return tuple(
            self.windows[app_id]
            for app_id in self.z_order
            if app_id in self.windows and not self.windows[app_id].minimized
        )

    def window_at(self, position: tuple[int, int]) -> DesktopWindow | None:
        for window in reversed(self.visible_windows()):
            if window.rect.inflate(RESIZE_MARGIN * 2, RESIZE_MARGIN * 2).collidepoint(position):
                return window
        return None

    def hit_test(self, position: tuple[int, int]) -> WindowHit | None:
        window = self.window_at(position)
        if window is None:
            return None
        for control, rect in window.control_rects().items():
            if rect.collidepoint(position):
                return WindowHit(window.app_id, "control", control)
        edges = window.resize_edges_at(position)
        if edges:
            return WindowHit(window.app_id, "resize")
        if window.titlebar_rect.collidepoint(position):
            return WindowHit(window.app_id, "titlebar")
        if window.client_rect.collidepoint(position):
            return WindowHit(window.app_id, "client")
        return WindowHit(window.app_id, "frame")

    def begin_interaction(self, hit: WindowHit, position: tuple[int, int]) -> None:
        window = self.windows[hit.app_id]
        self.focus(hit.app_id)
        if hit.area == "control" and hit.control is not None:
            self.pressed_control = (hit.app_id, hit.control)
            return
        if hit.area == "titlebar":
            self.interaction_app = hit.app_id
            self.interaction_kind = "drag"
            self.drag_offset = (position[0] - window.rect.x, position[1] - window.rect.y)
            return
        if hit.area == "resize":
            self.interaction_app = hit.app_id
            self.interaction_kind = "resize"
            self.resize_edges = window.resize_edges_at(position)
            self.interaction_start = position
            self.interaction_rect = window.rect.copy()

    def update_pointer(self, position: tuple[int, int] | None) -> None:
        self.hovered_control = None
        if position is None:
            return
        hit = self.hit_test(position)
        if hit is not None and hit.area == "control" and hit.control is not None:
            self.hovered_control = (hit.app_id, hit.control)
        if self.interaction_app is None:
            return
        window = self.windows.get(self.interaction_app)
        if window is None:
            self.cancel_interaction()
            return
        if self.interaction_kind == "drag":
            if window.maximized:
                ratio = (position[0] - window.rect.x) / max(1, window.rect.width)
                self.toggle_maximize(window.app_id)
                self.drag_offset = (round(window.rect.width * ratio), TITLEBAR_HEIGHT // 2)
            window.rect.topleft = (
                position[0] - self.drag_offset[0],
                position[1] - self.drag_offset[1],
            )
            self._keep_titlebar_visible(window)
        elif self.interaction_kind == "resize" and self.interaction_rect is not None:
            self._resize_window(window, position)

    def end_interaction(self, position: tuple[int, int] | None) -> tuple[str, str] | None:
        activated: tuple[str, str] | None = None
        if self.pressed_control is not None and position is not None:
            app_id, control = self.pressed_control
            window = self.windows.get(app_id)
            if window is not None and window.control_rects()[control].collidepoint(position):
                activated = self.pressed_control
        self.cancel_interaction()
        return activated

    def cancel_interaction(self) -> None:
        self.interaction_app = None
        self.interaction_kind = None
        self.resize_edges = frozenset()
        self.interaction_rect = None
        self.pressed_control = None

    def _resize_window(self, window: DesktopWindow, position: tuple[int, int]) -> None:
        assert self.interaction_rect is not None
        dx = position[0] - self.interaction_start[0]
        dy = position[1] - self.interaction_start[1]
        min_width, min_height = window.min_size
        left = self.interaction_rect.left
        right = self.interaction_rect.right
        top = self.interaction_rect.top
        bottom = self.interaction_rect.bottom
        if "left" in self.resize_edges:
            left = min(right - min_width, left + dx)
        if "right" in self.resize_edges:
            right = max(left + min_width, right + dx)
        if "top" in self.resize_edges:
            top = min(bottom - min_height, top + dy)
        if "bottom" in self.resize_edges:
            bottom = max(top + min_height, bottom + dy)

        left = max(self.work_area.left, left)
        top = max(self.work_area.top, top)
        right = min(self.work_area.right, right)
        bottom = min(self.work_area.bottom, bottom)
        if right - left >= min_width and bottom - top >= min_height:
            window.rect = pygame.Rect(left, top, right - left, bottom - top)

    def _keep_titlebar_visible(self, window: DesktopWindow) -> None:
        window.rect.left = min(self.work_area.right - 160, max(self.work_area.left, window.rect.left))
        window.rect.top = min(self.work_area.bottom - TITLEBAR_HEIGHT, max(self.work_area.top, window.rect.top))
        if window.rect.right > self.work_area.right:
            window.rect.right = self.work_area.right
        if window.rect.bottom > self.work_area.bottom:
            window.rect.bottom = self.work_area.bottom


class RetroWindowTheme:
    """Classic pixel UI skin assembled from the provided asset packs."""

    def __init__(self, assets: AssetManager) -> None:
        self.window_base = assets.load_image("os/retro_gui/Window_Base.png")
        self.header = assets.load_image("os/retro_gui/Window_Header.png")
        self.header_inactive = assets.load_image("os/retro_gui/Window_Header_Inactive.png")
        self.header_resizable = assets.load_image("os/retro_gui/Window_Header_Resizable.png")
        self.button = assets.load_image("os/retro_gui/Windows_Button.png")
        self.button_focus = assets.load_image("os/retro_gui/Windows_Button_Focus.png")
        self.button_pressed = assets.load_image("os/retro_gui/Windows_Button_Pressed.png")
        self.button_inactive = assets.load_image("os/retro_gui/Windows_Button_Inactive.png")
        self.inner_frame = assets.load_image("os/retro_gui/Windows_Inner_Frame.png")
        self.inner_frame_inverted = assets.load_image("os/retro_gui/Windows_Inner_Frame_Inverted.png")
        controls = assets.load_image("os/window_buttons/web button.png")
        self.window_controls = {
            state: {
                control: controls.subsurface(pygame.Rect(x, y, 36, 28)).copy()
                for control, x in (("minimize", 512), ("maximize", 576), ("close", 640))
            }
            for state, y in (("normal", 64), ("hover", 320), ("pressed", 576))
        }

    def draw_window(
        self,
        surface: pygame.Surface,
        window: DesktopWindow,
        active: bool,
        hovered_control: tuple[str, str] | None,
        pressed_control: tuple[str, str] | None,
        title_font: pygame.font.Font,
        icon: pygame.Surface | None = None,
    ) -> None:
        self.draw_panel(surface, window.rect)
        titlebar = window.titlebar_rect
        header_source = self.header if active else self.header_inactive
        header_strip = header_source.subsurface(pygame.Rect(2, 3, 44, 19))
        self._nine_slice(surface, header_strip, titlebar, 3)

        title_x = titlebar.x + 10
        if icon is not None:
            scaled_icon = pygame.transform.scale(icon, (27, 27))
            surface.blit(scaled_icon, scaled_icon.get_rect(midleft=(titlebar.x + 7, titlebar.centery)))
            title_x += 32
        title = title_font.render(window.title, False, (255, 255, 255) if active else (220, 220, 220))
        max_title_right = window.control_rects()["minimize"].left - 8
        previous_clip = surface.get_clip()
        surface.set_clip(pygame.Rect(title_x, titlebar.y, max(1, max_title_right - title_x), titlebar.height))
        surface.blit(title, title.get_rect(midleft=(title_x, titlebar.centery)))
        surface.set_clip(previous_clip)

        for control, rect in window.control_rects().items():
            key = (window.app_id, control)
            state = "pressed" if pressed_control == key else "hover" if hovered_control == key else "normal"
            surface.blit(self.window_controls[state][control], rect.topleft)

        if not window.maximized:
            grip = self.header_resizable.subsurface(pygame.Rect(38, 38, 10, 10))
            grip = pygame.transform.scale(grip, (20, 20))
            surface.blit(grip, grip.get_rect(bottomright=(window.rect.right - 2, window.rect.bottom - 2)))

    def draw_panel(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        self._nine_slice(surface, self.window_base, rect, 4)

    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect, state: str = "normal") -> None:
        source = {
            "normal": self.button,
            "hover": self.button_focus,
            "pressed": self.button_pressed,
            "inactive": self.button_inactive,
        }.get(state, self.button)
        self._nine_slice(surface, source, rect, 4)

    def draw_field(self, surface: pygame.Surface, rect: pygame.Rect, active: bool = False) -> None:
        source = self.inner_frame_inverted if active else self.inner_frame
        self._nine_slice(surface, source, rect, 4)
        pygame.draw.rect(surface, (255, 255, 255), rect.inflate(-8, -8))

    @staticmethod
    def _nine_slice(
        target: pygame.Surface,
        source: pygame.Surface,
        destination: pygame.Rect,
        margin: int,
    ) -> None:
        source_width, source_height = source.get_size()
        margin_x = min(margin, source_width // 2)
        margin_y = min(margin, source_height // 2)
        destination_margin_x = min(margin_x * 2, destination.width // 2)
        destination_margin_y = min(margin_y * 2, destination.height // 2)
        source_x = (0, margin_x, source_width - margin_x)
        source_y = (0, margin_y, source_height - margin_y)
        source_w = (margin_x, source_width - margin_x * 2, margin_x)
        source_h = (margin_y, source_height - margin_y * 2, margin_y)
        dest_x = (destination.x, destination.x + destination_margin_x, destination.right - destination_margin_x)
        dest_y = (destination.y, destination.y + destination_margin_y, destination.bottom - destination_margin_y)
        dest_w = (destination_margin_x, destination.width - destination_margin_x * 2, destination_margin_x)
        dest_h = (destination_margin_y, destination.height - destination_margin_y * 2, destination_margin_y)

        for row in range(3):
            for column in range(3):
                if source_w[column] <= 0 or source_h[row] <= 0 or dest_w[column] <= 0 or dest_h[row] <= 0:
                    continue
                piece = source.subsurface(
                    pygame.Rect(source_x[column], source_y[row], source_w[column], source_h[row])
                )
                size = (dest_w[column], dest_h[row])
                if piece.get_size() != size:
                    piece = pygame.transform.scale(piece, size)
                target.blit(piece, (dest_x[column], dest_y[row]))
