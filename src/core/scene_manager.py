from __future__ import annotations

import pygame

from src.core.scene import Scene


class SceneManager:
    """Stores scenes and forwards lifecycle, event, update and render calls."""

    def __init__(self) -> None:
        self._scenes: dict[str, Scene] = {}
        self._current_scene_name: str | None = None

    @property
    def current_scene(self) -> Scene | None:
        if self._current_scene_name is None:
            return None

        return self._scenes[self._current_scene_name]

    def add_scene(self, name: str, scene: Scene) -> None:
        if name in self._scenes:
            raise ValueError(f"Scene already registered: {name}")

        self._scenes[name] = scene

    def switch_to(self, name: str) -> None:
        if name not in self._scenes:
            raise KeyError(f"Scene not registered: {name}")

        current_scene = self.current_scene
        if current_scene is not None:
            current_scene.on_exit()

        self._current_scene_name = name
        self._scenes[name].on_enter()

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current_scene is not None:
            self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if self.current_scene is not None:
            self.current_scene.render(surface)
