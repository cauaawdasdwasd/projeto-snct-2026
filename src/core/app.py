from __future__ import annotations

import math

import pygame

from src.core.assets import AssetManager
from src.core.audio import AudioManager
from src.core.input_manager import InputManager
from src.core.preferences import UserPreferences
from src.core.scene_manager import SceneManager
from src.rendering.screen_effect import ScreenEffect
from src.core.settings import (
    ASSETS_DIR,
    CAMERA_BREATH_X,
    CAMERA_BREATH_Y,
    CAMERA_PARALLAX_X,
    CAMERA_PARALLAX_Y,
    CAMERA_RESPONSE,
    CAMERA_ZOOM,
    GAME_TITLE,
    LETTERBOX_COLOR,
    TARGET_FPS,
    VIRTUAL_HEIGHT,
    VIRTUAL_WIDTH,
)
from src.scenes.audit import AuditScene
from src.scenes.desktop import DesktopScene
from src.scenes.login import LoginScene
from src.scenes.main_menu import MainMenuScene


class Application:
    """Owns pygame startup, the main loop, scenes and virtual rendering."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)

        self.preferences = UserPreferences.load()
        self.window = self._set_display_mode(self.preferences)
        self.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT)).convert()
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.assets = AssetManager(ASSETS_DIR)
        self.screen_effect = ScreenEffect(self.assets)
        self.audio = AudioManager(self.assets)
        self.audio.set_music_volume(self.preferences.music_volume)
        self.audio.set_sfx_volume(self.preferences.sfx_volume)
        self.audio.start_music()
        self.input_manager = InputManager((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.scene_manager = SceneManager()

        self._viewport_rect = self.window.get_rect()
        self._viewport_scale = 1.0
        self._camera_rect = pygame.Rect(0, 0, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        self._camera_position = pygame.Vector2(0, 0)
        self._camera_time = 0.0
        self._system_cursor_visible = True
        self._update_viewport()
        self._register_scenes()

    def run(self) -> None:
        try:
            while self.is_running:
                dt = self.clock.tick(TARGET_FPS) / 1000.0
                self._handle_events()
                self.input_manager.update_mouse_position()
                self.scene_manager.update(dt)
                self._update_cursor_visibility()
                self._update_camera(dt)
                self._render()
        finally:
            pygame.mouse.set_visible(True)
            self.audio.stop()
            pygame.quit()

    def stop(self) -> None:
        self.is_running = False

    def get_preferences(self) -> UserPreferences:
        return self.preferences.copy()

    def apply_preferences(self, preferences: UserPreferences) -> bool:
        updated = preferences.copy()
        updated.normalize()
        display_changed = (
            updated.resolution != self.preferences.resolution
            or updated.display_mode != self.preferences.display_mode
        )

        if display_changed:
            try:
                self.window = self._set_display_mode(updated)
            except pygame.error:
                return False
            self._update_viewport()

        self.preferences = updated
        self.audio.set_music_volume(updated.music_volume)
        self.audio.set_sfx_volume(updated.sfx_volume)
        try:
            updated.save()
        except OSError:
            return False
        return True

    def _register_scenes(self) -> None:
        audit_scene = AuditScene(
            self.scene_manager,
            self.assets,
            self.input_manager,
            self.audio,
            self.get_preferences,
            self.apply_preferences,
        )
        self.scene_manager.add_scene(
            "main_menu",
            MainMenuScene(
                self.scene_manager,
                self.assets,
                self.input_manager,
                self.audio,
                self.get_preferences,
                self.apply_preferences,
            ),
        )
        self.scene_manager.add_scene(
            "login",
            LoginScene(
                self.scene_manager,
                self.assets,
                self.input_manager,
                self.audio,
            ),
        )
        self.scene_manager.add_scene(
            "desktop",
            DesktopScene(
                self.scene_manager,
                self.assets,
                self.input_manager,
                self.audio,
                audit_scene,
            ),
        )
        self.scene_manager.add_scene(
            "audit",
            audit_scene,
        )
        self.scene_manager.switch_to("main_menu")

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                continue

            if self.audio.handle_event(event):
                continue

            if event.type == pygame.VIDEORESIZE and self.preferences.display_mode == "windowed":
                self.window = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self._update_viewport()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_scene = self.scene_manager.current_scene
                if current_scene is not None:
                    current_scene.handle_escape()
                continue

            self.input_manager.handle_event(event)
            self.scene_manager.handle_event(event)

    def _render(self) -> None:
        self.virtual_surface.fill((0, 0, 0))
        self.scene_manager.render(self.virtual_surface)

        self.window.fill(LETTERBOX_COLOR)
        current_scene = self.scene_manager.current_scene
        if current_scene is not None and current_scene.screen_effect_rect is not None:
            self.screen_effect.apply(
                self.virtual_surface,
                self.preferences.screen_filter,
                current_scene.screen_effect_rect,
            )
        head_offset = getattr(current_scene, "head_offset", (0, 0))
        camera_view = self.virtual_surface.subsurface(self._camera_rect)
        if camera_view.get_size() == self._viewport_rect.size:
            scaled_surface = camera_view
        elif self._viewport_scale.is_integer():
            scaled_surface = pygame.transform.scale(camera_view, self._viewport_rect.size)
        else:
            # A small filter avoids harsh one-pixel shimmer at fractional sizes.
            scaled_surface = pygame.transform.smoothscale(camera_view, self._viewport_rect.size)

        if head_offset != (0, 0) and self._camera_rect.size == self.virtual_surface.get_size():
            display_offset = (
                round(head_offset[0] * self._viewport_scale),
                round(head_offset[1] * self._viewport_scale),
            )
            self._blit_head_motion(scaled_surface, display_offset)
        else:
            self.window.blit(scaled_surface, self._viewport_rect.topleft)
        pygame.display.flip()

    def _blit_head_motion(
        self,
        scaled_surface: pygame.Surface,
        display_offset: tuple[int, int],
    ) -> None:
        """Move the already-scaled frame without resampling its text again."""
        viewport = self.window.subsurface(self._viewport_rect)
        width, height = viewport.get_size()
        offset_x = max(-width + 1, min(width - 1, display_offset[0]))
        offset_y = max(-height + 1, min(height - 1, display_offset[1]))

        shifted = pygame.Surface((width, height)).convert()
        shifted.blit(scaled_surface, (offset_x, offset_y))

        # Repeat the nearest edge into the one-pixel exposed strips. This keeps
        # the physical monitor filled while the frame moves.
        if offset_x > 0:
            left_edge = pygame.transform.scale(
                scaled_surface.subsurface(pygame.Rect(0, 0, 1, height)),
                (offset_x, height),
            )
            shifted.blit(left_edge, (0, 0))
        elif offset_x < 0:
            right_edge = pygame.transform.scale(
                scaled_surface.subsurface(pygame.Rect(width - 1, 0, 1, height)),
                (-offset_x, height),
            )
            shifted.blit(right_edge, (width + offset_x, 0))
        if offset_y > 0:
            top_edge = pygame.transform.scale(
                scaled_surface.subsurface(pygame.Rect(0, 0, width, 1)),
                (width, offset_y),
            )
            shifted.blit(top_edge, (0, 0))
        elif offset_y < 0:
            bottom_edge = pygame.transform.scale(
                scaled_surface.subsurface(pygame.Rect(0, height - 1, width, 1)),
                (width, -offset_y),
            )
            shifted.blit(bottom_edge, (0, height + offset_y))
        viewport.blit(shifted, (0, 0))

    def _update_camera(self, dt: float) -> None:
        current_scene = self.scene_manager.current_scene
        if current_scene is None or not current_scene.camera_motion_enabled:
            self._camera_rect = pygame.Rect(0, 0, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
            self._camera_position.update(0, 0)
            self.input_manager.set_camera_rect(self._camera_rect)
            return

        self._camera_time += dt
        crop_width = max(1, round(VIRTUAL_WIDTH / CAMERA_ZOOM))
        crop_height = max(1, round(VIRTUAL_HEIGHT / CAMERA_ZOOM))
        base_x = (VIRTUAL_WIDTH - crop_width) / 2
        base_y = (VIRTUAL_HEIGHT - crop_height) / 2

        mouse_position = self.input_manager.mouse_position
        if mouse_position is None:
            mouse_x = 0.0
            mouse_y = 0.0
        else:
            mouse_x = (mouse_position[0] / VIRTUAL_WIDTH - 0.5) * 2
            mouse_y = (mouse_position[1] / VIRTUAL_HEIGHT - 0.5) * 2

        target_x = (
            base_x
            + mouse_x * CAMERA_PARALLAX_X
            + math.sin(self._camera_time * 0.83) * CAMERA_BREATH_X
        )
        target_y = (
            base_y
            + mouse_y * CAMERA_PARALLAX_Y
            + math.sin(self._camera_time * 0.61 + 1.2) * CAMERA_BREATH_Y
        )
        target_x = max(0.0, min(target_x, VIRTUAL_WIDTH - crop_width))
        target_y = max(0.0, min(target_y, VIRTUAL_HEIGHT - crop_height))

        smoothing = 1.0 - math.exp(-CAMERA_RESPONSE * dt)
        self._camera_position.x += (target_x - self._camera_position.x) * smoothing
        self._camera_position.y += (target_y - self._camera_position.y) * smoothing
        self._camera_rect = pygame.Rect(
            round(self._camera_position.x),
            round(self._camera_position.y),
            crop_width,
            crop_height,
        )
        self.input_manager.set_camera_rect(self._camera_rect)

    def _update_cursor_visibility(self) -> None:
        current_scene = self.scene_manager.current_scene
        custom_active = bool(
            current_scene is not None
            and current_scene.custom_cursor_active(self.input_manager.mouse_position)
        )
        should_show_system_cursor = not custom_active
        if should_show_system_cursor != self._system_cursor_visible:
            pygame.mouse.set_visible(should_show_system_cursor)
            self._system_cursor_visible = should_show_system_cursor

    def _update_viewport(self) -> None:
        window_width, window_height = self.window.get_size()
        integer_scale = min(window_width // VIRTUAL_WIDTH, window_height // VIRTUAL_HEIGHT)

        if integer_scale >= 1:
            scale = float(integer_scale)
            viewport_width = VIRTUAL_WIDTH * integer_scale
            viewport_height = VIRTUAL_HEIGHT * integer_scale
        else:
            scale = min(window_width / VIRTUAL_WIDTH, window_height / VIRTUAL_HEIGHT)
            viewport_width = max(1, int(VIRTUAL_WIDTH * scale))
            viewport_height = max(1, int(VIRTUAL_HEIGHT * scale))

        viewport_x = (window_width - viewport_width) // 2
        viewport_y = (window_height - viewport_height) // 2

        self._viewport_rect = pygame.Rect(viewport_x, viewport_y, viewport_width, viewport_height)
        self._viewport_scale = scale
        self.input_manager.set_viewport(self._viewport_rect, self._viewport_scale)

    @staticmethod
    def _set_display_mode(preferences: UserPreferences) -> pygame.Surface:
        if preferences.display_mode == "fullscreen":
            return pygame.display.set_mode(preferences.resolution, pygame.FULLSCREEN)
        return pygame.display.set_mode(preferences.resolution, pygame.RESIZABLE)
