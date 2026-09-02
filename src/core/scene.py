from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


class Scene(ABC):
    """Base contract for game scenes."""

    def __init__(
        self,
        manager: SceneManager,
        assets: AssetManager,
        input_manager: InputManager,
    ) -> None:
        self.manager = manager
        self.assets = assets
        self.input_manager = input_manager

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_escape(self) -> bool:
        """Handle a back action and return whether the scene consumed it."""
        return False

    @property
    def camera_motion_enabled(self) -> bool:
        return False

    @property
    def screen_effect_rect(self) -> pygame.Rect | None:
        """Area occupied by the display, excluding its physical frame."""
        return None

    def custom_cursor_active(self, position: tuple[int, int] | None) -> bool:
        """Return whether the scene is drawing its own cursor at this position."""
        return False

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        pass
