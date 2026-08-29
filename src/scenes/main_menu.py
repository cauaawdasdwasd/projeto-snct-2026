from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.core.scene import Scene
from src.core.settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


class MainMenuScene(Scene):
    """Temporary technical main menu."""

    def __init__(
        self,
        manager: SceneManager,
        assets: AssetManager,
        input_manager: InputManager,
        audio: AudioManager | None = None,
    ) -> None:
        super().__init__(manager, assets, input_manager)
        self.audio = audio
        self.title_font = pygame.font.Font(None, 168)
        self.button_font = pygame.font.Font(None, 78)
        self.hint_font = pygame.font.Font(None, 48)
        self.button_rect = pygame.Rect(732, 618, 456, 126)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        mouse_position = self.input_manager.mouse_position
        if mouse_position is not None and self.button_rect.collidepoint(mouse_position):
            if self.audio is not None:
                self.audio.play("click")
            self.manager.switch_to("audit")

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 13, 18))

        title = self.title_font.render("SOB ANÁLISE", True, (230, 238, 220))
        title_rect = title.get_rect(center=(VIRTUAL_WIDTH // 2, 408))
        surface.blit(title, title_rect)

        mouse_position = self.input_manager.mouse_position
        is_hovered = mouse_position is not None and self.button_rect.collidepoint(mouse_position)
        button_fill = (48, 70, 66) if is_hovered else (32, 45, 48)
        button_outline = (169, 220, 198) if is_hovered else (93, 128, 123)

        pygame.draw.rect(surface, button_fill, self.button_rect)
        pygame.draw.rect(surface, button_outline, self.button_rect, 2)

        button_text = self.button_font.render("[ INICIAR ]", True, (230, 238, 220))
        button_text_rect = button_text.get_rect(center=self.button_rect.center)
        surface.blit(button_text, button_text_rect)

        hint = self.hint_font.render("Placeholder tecnico - UI final sera feita com PNGs externos", True, (116, 130, 132))
        hint_rect = hint.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 84))
        surface.blit(hint, hint_rect)
